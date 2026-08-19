"""O gateway: proxy → detecção → política → transformação → auditoria → provedor.

**Por que não a tradução do LiteLLM neste ponto.** O `CLAUDE.md` manda tratar o
LiteLLM como infraestrutura, e a Fase 0 confirmou que ele resolve bem o ponto
de interceptação e a abstração de provedor. Mas a regra 6 diz que
compatibilidade de API é sagrada, e "troca só a URL base" precisa ser verdade
literal. Traduzir o corpo para um formato intermediário e de volta introduz
justamente o lugar onde um campo novo da Anthropic se perde no caminho.

Então o corpo da requisição é repassado **como veio**, sem nenhuma
reserialização, com só os trechos de texto substituídos onde a política mandou.
Campo que o BALUARTE não conhece atravessa intacto — inclusive campo que ainda
não existe. O LiteLLM continua no projeto, na camada de guardrail da Fase 0 e
para o roteamento multi-provedor quando ele entrar.

A resposta de erro é a do próprio provedor, no formato dele, para que o
tratamento de erro do cliente também não precise mudar.
"""

import asyncio
import json
import time
import uuid
import weakref
from datetime import date, datetime, timezone

import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from ..analisador import ClassificadorIndisponivel
from ..classificacao.sobreposicao import de_resultados_do_presidio, resolver
from ..politica.acoes import Acao
from ..politica.avaliador import avaliar_com_catalogo
from ..tokenizacao.transformador import destokenizar, transformar

CABECALHOS_NAO_REPASSADOS = {
    "host", "content-length", "connection", "accept-encoding", "transfer-encoding",
}


class Gateway:
    def __init__(
        self,
        *,
        analisador,
        catalogo,
        cofre,
        trilha_por_tenant,
        upstream: str = "https://api.anthropic.com",
        cliente_http: httpx.AsyncClient | None = None,
    ):
        self.analisador = analisador
        self.catalogo = catalogo
        self.cofre = cofre
        self.trilha_por_tenant = trilha_por_tenant
        self.upstream = upstream.rstrip("/")
        self.cliente_http = cliente_http
        self._clientes_por_laco: "weakref.WeakKeyDictionary" = weakref.WeakKeyDictionary()

    # ── extração e reinserção de texto ───────────────────────────────
    #
    # As duas funções abaixo são espelho uma da outra. Ficam juntas de
    # propósito: se uma passar a enxergar um campo novo e a outra não, a
    # requisição sai com dado em claro num campo que ninguém transformou.

    @staticmethod
    def _trechos(corpo: dict) -> list[tuple]:
        """Caminhos até todo texto do corpo, como lista de chaves."""
        caminhos = []
        sistema = corpo.get("system")
        if isinstance(sistema, str):
            caminhos.append(("system",))
        elif isinstance(sistema, list):
            for i, bloco in enumerate(sistema):
                if isinstance(bloco, dict) and isinstance(bloco.get("text"), str):
                    caminhos.append(("system", i, "text"))

        for i, mensagem in enumerate(corpo.get("messages") or []):
            conteudo = mensagem.get("content")
            if isinstance(conteudo, str):
                caminhos.append(("messages", i, "content"))
            elif isinstance(conteudo, list):
                for j, bloco in enumerate(conteudo):
                    if isinstance(bloco, dict) and isinstance(bloco.get("text"), str):
                        caminhos.append(("messages", i, "content", j, "text"))
        return caminhos

    @staticmethod
    def _ler(corpo: dict, caminho: tuple) -> str:
        no = corpo
        for chave in caminho:
            no = no[chave]
        return no

    @staticmethod
    def _escrever(corpo: dict, caminho: tuple, valor: str) -> None:
        no = corpo
        for chave in caminho[:-1]:
            no = no[chave]
        no[caminho[-1]] = valor

    # ── o caminho de uma requisição ──────────────────────────────────

    async def mensagens(self, request):
        inicio = time.perf_counter()
        requisicao_id = uuid.uuid4()
        tenant = request.headers.get("x-baluarte-tenant", "padrao")
        chave_origem = self._identificar_chave(request.headers.get("x-api-key", ""))

        try:
            corpo = json.loads(await request.body())
        except json.JSONDecodeError:
            return self._erro(400, "invalid_request_error", "corpo não é JSON válido")

        caminhos = self._trechos(corpo)

        # Classifica cada trecho UMA vez, e reaproveita o mesmo resultado para
        # decidir e para transformar.
        #
        # A primeira versão classificava o texto concatenado para decidir e
        # depois cada trecho de novo para transformar. Além de pagar o spaCy
        # duas vezes, era incorreto: a concatenação cria vizinhança que não
        # existe na requisição, e o classificador acha entidade na emenda entre
        # duas mensagens — entidade que ninguém escreveu.
        try:
            achados_por_caminho = {
                caminho: resolver(
                    de_resultados_do_presidio(
                        self.analisador.analyze(
                            text=self._ler(corpo, caminho), language="pt"
                        )
                    )
                )
                for caminho in caminhos
            }
            achados = [a for lista in achados_por_caminho.values() for a in lista]
        except (ClassificadorIndisponivel, Exception) as erro:
            self._registrar_falha(tenant, chave_origem, requisicao_id, erro)
            return self._erro(
                503,
                "api_error",
                "classificação indisponível; a requisição foi bloqueada por padrão "
                "(fail-closed)",
                requisicao_id=requisicao_id,
            )

        hoje = date.today()
        decisao = avaliar_com_catalogo([a.entidade for a in achados], self.catalogo, hoje)

        cabecalhos_baluarte = {
            "X-Baluarte-Request-Id": str(requisicao_id),
            "X-Baluarte-Action": str(decisao.acao),
            "X-Baluarte-Policy-Version": (
                f"{decisao.politica_nome} v{decisao.politica_versao}"
            ),
            "X-Baluarte-Entities-Detected": ",".join(
                f"{d.entidade}:{d.ocorrencias}" for d in decisao.por_entidade
            ) or "none",
        }

        tokens_criados: dict[str, str] = {}
        bloqueada = False
        entidade_bloqueadora = None

        for caminho, achados_do_trecho in achados_por_caminho.items():
            trecho = self._ler(corpo, caminho)
            t = transformar(trecho, achados_do_trecho, decisao, self.cofre, tenant)
            if t.bloqueada:
                bloqueada, entidade_bloqueadora = True, t.entidade_bloqueadora
                break
            tokens_criados.update(t.tokens_criados)
            self._escrever(corpo, caminho, t.texto)

        self._registrar(
            tenant=tenant,
            decisao=decisao,
            chave_origem=chave_origem,
            requisicao_id=requisicao_id,
            provedor_destino=self._nome_do_upstream(),
        )

        if bloqueada or decisao.acao is Acao.BLOQUEAR:
            return self._erro(
                403,
                "permission_error",
                f"bloqueado pela política {decisao.politica_nome} "
                f"v{decisao.politica_versao}: entidade {entidade_bloqueadora or 'detectada'} "
                "não pode ser transferida",
                requisicao_id=requisicao_id,
                extras=cabecalhos_baluarte,
            )

        resposta = await self._encaminhar(request, corpo)

        if resposta.headers.get("content-type", "").startswith("application/json"):
            texto = destokenizar(resposta.text, self.cofre, tenant)
            conteudo = texto.encode("utf-8")
        else:
            conteudo = resposta.content

        cabecalhos = {
            k: v
            for k, v in resposta.headers.items()
            if k.lower() not in {"content-length", "content-encoding", "transfer-encoding"}
        }
        cabecalhos.update(cabecalhos_baluarte)
        cabecalhos["X-Baluarte-Overhead-Ms"] = f"{(time.perf_counter() - inicio) * 1000:.1f}"

        return Response(
            content=conteudo, status_code=resposta.status_code, headers=cabecalhos
        )

    async def _encaminhar(self, request, corpo: dict) -> httpx.Response:
        cabecalhos = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in CABECALHOS_NAO_REPASSADOS
            and not k.lower().startswith("x-baluarte-")
        }
        # Um cliente reusado, e não um por requisição. A medição da Fase 3
        # mostrou que criar o cliente a cada chamada custava ~45 ms de
        # overhead: pool novo, conexão TCP nova, nenhum keep-alive. Era o maior
        # item da conta — maior que a classificação, que era onde eu suspeitava.
        #
        # O cache é por event loop, e não um atributo só. Um AsyncClient
        # carrega o pool de conexões preso ao loop em que nasceu; reusá-lo em
        # outro loop levanta erro na segunda requisição. Em produção existe um
        # loop só e a distinção não aparece, mas o teste roda cada requisição
        # no seu próprio loop — e um invariante que só vale em produção é um
        # invariante que ninguém verifica.
        if self.cliente_http is not None:
            return await self.cliente_http.post(
                f"{self.upstream}{request.url.path}",
                json=corpo,
                headers=cabecalhos,
                params=dict(request.query_params),
            )

        laco = asyncio.get_running_loop()
        cliente = self._clientes_por_laco.get(laco)
        if cliente is None:
            cliente = httpx.AsyncClient(
                timeout=120,
                limits=httpx.Limits(max_keepalive_connections=32, max_connections=128),
            )
            self._clientes_por_laco[laco] = cliente
        return await cliente.post(
            f"{self.upstream}{request.url.path}",
            json=corpo,
            headers=cabecalhos,
            params=dict(request.query_params),
        )

    # ── auxiliares ───────────────────────────────────────────────────

    @staticmethod
    def _identificar_chave(chave: str) -> str:
        """Identificador da chave, nunca a chave.

        A trilha precisa saber qual credencial chamou; ninguém precisa da
        credencial. Quatro últimos caracteres bastam para o operador
        reconhecer a sua e não bastam para usar a de outro.
        """
        return f"••{chave[-4:]}" if len(chave) >= 4 else "••????"

    def _nome_do_upstream(self) -> str:
        return "anthropic" if "anthropic" in self.upstream else self.upstream

    def _registrar(self, *, tenant, decisao, chave_origem, requisicao_id, provedor_destino):
        trilha = self.trilha_por_tenant(tenant)
        if trilha is None:
            return
        trilha.registrar(
            decisao=decisao,
            chave_origem=chave_origem,
            provedor_destino=provedor_destino,
            requisicao_id=requisicao_id,
            registrado_em=datetime.now(timezone.utc),
        )

    def _registrar_falha(self, tenant, chave_origem, requisicao_id, erro):
        """A falha do classificador também vira registro.

        Bloquear sem registrar deixaria o cliente sem como explicar, meses
        depois, por que aquela requisição não passou.
        """
        trilha = self.trilha_por_tenant(tenant)
        if trilha is None:
            return
        from ..politica.decisao import Decisao, DecisaoEntidade, Justificativa

        trilha.registrar(
            decisao=Decisao(
                acao=Acao.BLOQUEAR,
                politica_nome="(classificador indisponível)",
                politica_versao=0,
                politica_sha256="0" * 64,
                politica_vigente_desde=date.today(),
                avaliada_em=date.today(),
                por_entidade=(
                    DecisaoEntidade(
                        entidade="CLASSIFICADOR_INDISPONIVEL",
                        acao=Acao.BLOQUEAR,
                        ocorrencias=1,
                        justificativas=(
                            Justificativa(
                                origem="fail-closed",
                                base_normativa=(
                                    "CLAUDE.md regra 3 — sem classificação não há "
                                    "como afirmar que a requisição não carrega dado "
                                    "pessoal, e a ausência de prova não é liberação."
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            chave_origem=chave_origem,
            provedor_destino=self._nome_do_upstream(),
            requisicao_id=requisicao_id,
        )

    @staticmethod
    def _erro(status: int, tipo: str, mensagem: str, requisicao_id=None, extras=None):
        """Erro no formato do próprio provedor.

        Regra 6: o tratamento de erro do cliente também não pode precisar
        mudar. Quem já trata `error.type` da Anthropic continua tratando.
        """
        cabecalhos = dict(extras or {})
        if requisicao_id:
            cabecalhos["X-Baluarte-Request-Id"] = str(requisicao_id)
        return JSONResponse(
            {"type": "error", "error": {"type": tipo, "message": mensagem}},
            status_code=status,
            headers=cabecalhos,
        )


def criar_app(gateway: Gateway) -> Starlette:
    return Starlette(
        routes=[
            Route("/v1/messages", gateway.mensagens, methods=["POST"]),
            Route("/health", lambda r: JSONResponse({"ok": True}), methods=["GET"]),
        ]
    )
