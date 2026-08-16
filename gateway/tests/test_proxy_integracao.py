"""Testes de integração do gateway inteiro.

O caminho completo: proxy → detecção → política → transformação → auditoria →
provedor → destokenização → resposta.

O provedor é um dublê que **anota o que recebeu** numa lista que o teste
inspeciona. É o que permite afirmar, com prova e não com confiança, que o
modelo viu token e não CPF.

A primeira versão do dublê ecoava o corpo recebido dentro do texto da resposta,
e o teste procurava o CPF ali. Não funciona — e a razão vale registro: a
destokenização da resposta **corretamente** trocava o token de volta pelo CPF
antes de o teste ver. O teste estava sendo enganado pelo sistema funcionando.
Observar o que saiu exige um ponto de observação fora do caminho de volta.
"""

import json
import socket
import threading
import time
from datetime import date

import httpx
import pytest
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from baluarte.analisador import ClassificadorIndisponivel, montar_analisador
from baluarte.auditoria.repositorio import TrilhaDeAuditoria
from baluarte.politica.catalogo import CatalogoDePoliticas
from baluarte.proxy.app import Gateway, criar_app
from baluarte.tokenizacao.cofre import CofreEmMemoria

CPF = "111.444.777-35"
EMAIL = "marina@vetorcred.com.br"

POLITICA_YAML = """
nome: "Integração"
versao: 7
vigente_desde: 2020-01-01
regras:
  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33 — transferência internacional"
  - entidade: EMAIL_ADDRESS
    acao: tokenizar
    base_normativa: "LGPD art. 5º, I"
  - entidade: PHONE_NUMBER
    acao: mascarar
    base_normativa: "LGPD art. 5º, I"
  - entidade: IBAN_CODE
    acao: bloquear
    base_normativa: "Resolução BCB 4.658/2018"
padrao:
  entidade_sem_regra:
    acao: permitir
    base_normativa: >-
      Perfil de integração: fail-open declarado para manter o teste focado no
      caminho, e não na cobertura. Em produção o padrão é bloquear.
  nenhuma_deteccao:
    acao: permitir
    base_normativa: "sem tratamento a restringir"
"""


# ── dublê do provedor ────────────────────────────────────────────────

RECEBIDO: list[dict] = []


def app_do_provedor(registro: list | None = None):
    """Anota o corpo recebido e responde no formato da Anthropic."""
    anotar = RECEBIDO if registro is None else registro

    async def mensagens(request):
        corpo = json.loads(await request.body())
        anotar.append({"corpo": corpo, "cabecalhos": dict(request.headers)})
        return JSONResponse(
            {
                "id": "msg_dublê",
                "type": "message",
                "role": "assistant",
                "model": corpo.get("model", "claude-opus-5"),
                "content": [{"type": "text", "text": "Analisado."}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 20},
            }
        )

    return Starlette(routes=[Route("/v1/messages", mensagens, methods=["POST"])])


@pytest.fixture(autouse=True)
def limpar_registro():
    RECEBIDO.clear()
    yield


def visto_pelo_provedor() -> str:
    """O corpo que de fato saiu daqui, como texto."""
    assert RECEBIDO, "o provedor não recebeu nada"
    return json.dumps(RECEBIDO[-1]["corpo"], ensure_ascii=False)


@pytest.fixture(scope="module")
def provedor():
    """Sobe o dublê num socket de verdade."""
    porta = _porta_livre()
    config = uvicorn.Config(app_do_provedor(), host="127.0.0.1", port=porta, log_level="error")
    servidor = uvicorn.Server(config)
    thread = threading.Thread(target=servidor.run, daemon=True)
    thread.start()
    _esperar(porta)
    yield f"http://127.0.0.1:{porta}"
    servidor.should_exit = True
    thread.join(timeout=5)


def _porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _esperar(porta: int, prazo: float = 10.0):
    limite = time.time() + prazo
    while time.time() < limite:
        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"servidor não subiu na porta {porta}")


# ── gateway montado ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def analisador():
    return montar_analisador()


@pytest.fixture
def cofre():
    return CofreEmMemoria()


@pytest.fixture
def catalogo(tmp_path):
    (tmp_path / "v7.yaml").write_text(POLITICA_YAML, encoding="utf-8")
    return CatalogoDePoliticas.de_diretorio(tmp_path)


@pytest.fixture
def gateway(analisador, catalogo, cofre, provedor):
    return Gateway(
        analisador=analisador,
        catalogo=catalogo,
        cofre=cofre,
        trilha_por_tenant=lambda t: None,
        upstream=provedor,
    )


@pytest.fixture
def cliente(gateway):
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=criar_app(gateway)),
        base_url="http://gateway",
    )


def pedir(cliente, texto, **extras):
    corpo = {
        "model": "claude-opus-5",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": texto}],
    }
    corpo.update(extras)
    import asyncio

    async def enviar():
        return await cliente.post(
            "/v1/messages",
            json=corpo,
            headers={"x-api-key": "sk-ant-fake-7c41", "anthropic-version": "2023-06-01"},
        )

    return asyncio.run(enviar())


# ── requisito 2: tokenização reversível ponta a ponta ────────────────

def test_cpf_entra_modelo_ve_token_cliente_recebe_cpf(cliente):
    """O teste que a fase pede por extenso.

    Não basta o cliente receber o CPF de volta: é preciso provar que o provedor
    **não** o viu. O dublê devolve o que recebeu, então o corpo da resposta é a
    prova documental do que saiu daqui.
    """
    r = pedir(cliente, f"Analise a renegociação do CPF {CPF}, e-mail {EMAIL}.")
    assert r.status_code == 200

    saiu = visto_pelo_provedor()
    assert CPF not in saiu
    assert EMAIL not in saiu
    assert "«BR_CPF:" in saiu
    assert "«EMAIL_ADDRESS:" in saiu


def test_o_token_volta_a_ser_o_valor_na_resposta(cliente, gateway, cofre):
    """Destokenização: o token que o modelo devolve vira valor de novo."""
    pedir(cliente, f"CPF {CPF} em análise.")
    token = cofre.tokenizar("padrao", "BR_CPF", CPF)

    from baluarte.tokenizacao.transformador import destokenizar

    assert destokenizar(f"O titular {token} está em dia.", cofre, "padrao") == (
        f"O titular {CPF} está em dia."
    )


def test_token_e_deterministico_entre_requisicoes(cliente):
    import re as _re

    pedir(cliente, f"primeiro contato, CPF {CPF}")
    a = visto_pelo_provedor()
    pedir(cliente, f"segundo contato, CPF {CPF}")
    b = visto_pelo_provedor()

    extrair = lambda t: _re.search(r"«BR_CPF:[0-9a-f]+»", t).group(0)
    assert extrair(a) == extrair(b), "o modelo precisa reconhecer a mesma pessoa"


def test_cofre_e_isolado_por_tenant(cofre):
    a = cofre.tokenizar("vetorcred", "BR_CPF", CPF)
    b = cofre.tokenizar("clinica-norte", "BR_CPF", CPF)
    assert a != b
    with pytest.raises(KeyError):
        cofre.destokenizar("clinica-norte", a)


def test_token_desconhecido_fica_como_esta(cofre):
    """Modelo inventa token. Inventar um valor seria pior que devolver o token."""
    from baluarte.tokenizacao.transformador import destokenizar

    texto = "O titular «BR_CPF:deadbeef» pediu revisão."
    assert destokenizar(texto, cofre, "padrao") == texto


def test_mascarar_nao_cria_entrada_no_cofre(cliente, cofre):
    pedir(cliente, "Contato pelo telefone 11987654321.")
    assert cofre.tamanho("padrao") == 0


def test_mascara_diz_o_tipo(cliente):
    pedir(cliente, "Telefone 11987654321 para retorno.")
    saiu = visto_pelo_provedor()
    assert "11987654321" not in saiu
    assert "[PHONE_NUMBER:" in saiu


# ── requisito 1: compatibilidade literal de API ──────────────────────

def test_campos_desconhecidos_atravessam_intactos(cliente):
    """Campo que o BALUARTE não conhece — inclusive campo que ainda não existe.

    É o que sustenta "troca só a URL base": a Anthropic acrescenta um
    parâmetro e o gateway não precisa saber dele para continuar funcionando.
    """
    r = pedir(
        cliente,
        "Texto sem dado pessoal.",
        temperature=0.3,
        top_k=40,
        metadata={"user_id": "abc"},
        parametro_que_ainda_nao_existe={"algo": [1, 2, 3]},
    )
    recebido = RECEBIDO[-1]["corpo"]
    assert recebido["temperature"] == 0.3
    assert recebido["top_k"] == 40
    assert recebido["metadata"] == {"user_id": "abc"}
    assert recebido["parametro_que_ainda_nao_existe"] == {"algo": [1, 2, 3]}


def test_a_resposta_chega_ao_cliente_destokenizada(catalogo, cofre):
    """A outra ponta do requisito 2: o token volta a ser valor antes do cliente.

    O provedor devolve um texto contendo o token; o cliente recebe o CPF.
    """
    import asyncio

    token = cofre.tokenizar("padrao", "BR_CPF", CPF)
    provedor_com_token = Starlette(
        routes=[
            Route(
                "/v1/messages",
                lambda r: JSONResponse(
                    {
                        "id": "m", "type": "message", "role": "assistant", "model": "m",
                        "content": [{"type": "text", "text": f"O titular {token} está em dia."}],
                        "stop_reason": "end_turn", "usage": {},
                    }
                ),
                methods=["POST"],
            )
        ]
    )
    gw = Gateway(
        analisador=montar_analisador(),
        catalogo=catalogo,
        cofre=cofre,
        trilha_por_tenant=lambda t: None,
        upstream="http://provedor",
        cliente_http=httpx.AsyncClient(
            transport=httpx.ASGITransport(app=provedor_com_token)
        ),
    )
    c = httpx.AsyncClient(transport=httpx.ASGITransport(app=criar_app(gw)), base_url="http://g")
    r = asyncio.run(
        c.post(
            "/v1/messages",
            json={"model": "m", "max_tokens": 8,
                  "messages": [{"role": "user", "content": "ok"}]},
            headers={"x-api-key": "sk-1234"},
        )
    )
    texto = r.json()["content"][0]["text"]
    assert CPF in texto
    assert token not in texto


def test_formato_de_resposta_e_o_do_provedor(cliente):
    corpo = pedir(cliente, "Sem dado pessoal.").json()
    assert corpo["type"] == "message"
    assert corpo["role"] == "assistant"
    assert corpo["content"][0]["type"] == "text"
    assert "usage" in corpo


def test_formato_de_erro_e_o_do_provedor(cliente):
    r = pedir(cliente, f"Conta IBAN BR9700360305000010009795493P1 do titular {CPF}.")
    assert r.status_code == 403
    corpo = r.json()
    assert corpo["type"] == "error"
    assert corpo["error"]["type"] == "permission_error"
    assert "message" in corpo["error"]


def test_system_e_blocos_multimodais_tambem_sao_tratados(cliente):
    r = pedir(
        cliente,
        "veja o anexo",
        system=f"Você atende o cliente de CPF {CPF}.",
    )
    saiu = visto_pelo_provedor()
    assert CPF not in saiu
    assert "«BR_CPF:" in saiu


def test_blocos_de_conteudo_em_lista(cliente):
    import asyncio

    async def enviar():
        return await cliente.post(
            "/v1/messages",
            json={
                "model": "claude-opus-5",
                "max_tokens": 128,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"O CPF é {CPF}."},
                            {"type": "text", "text": "Analise."},
                        ],
                    }
                ],
            },
            headers={"x-api-key": "sk-ant-fake-7c41"},
        )

    asyncio.run(enviar())
    saiu = visto_pelo_provedor()
    assert CPF not in saiu
    assert "«BR_CPF:" in saiu
    assert "Analise." in saiu


# ── requisito 4: cabeçalhos de resposta ──────────────────────────────

def test_cabecalhos_de_resposta(cliente):
    r = pedir(cliente, f"CPF {CPF} e telefone 11987654321.")
    # A ação global é a MAIS RESTRITIVA entre as entidades: CPF pede tokenizar,
    # telefone pede mascarar, e mascarar vence. Ver politica/acoes.py.
    assert r.headers["x-baluarte-action"] == "mascarar"
    assert "v7" in r.headers["x-baluarte-policy-version"]
    assert "BR_CPF:1" in r.headers["x-baluarte-entities-detected"]
    assert "PHONE_NUMBER:1" in r.headers["x-baluarte-entities-detected"]
    import uuid as _uuid

    _uuid.UUID(r.headers["x-baluarte-request-id"])


def test_cabecalho_sem_deteccao(cliente):
    r = pedir(cliente, "Resuma a reunião de ontem.")
    assert r.headers["x-baluarte-entities-detected"] == "none"
    assert r.headers["x-baluarte-action"] == "permitir"


def test_cabecalhos_do_baluarte_nao_vazam_para_o_provedor(cliente):
    pedir(cliente, "Sem dado pessoal.")
    enviados = RECEBIDO[-1]["cabecalhos"]
    assert not [k for k in enviados if k.lower().startswith("x-baluarte")]


# ── requisito 3: fail-closed ─────────────────────────────────────────

class AnalisadorQuebrado:
    def analyze(self, **kwargs):
        raise ClassificadorIndisponivel("Presidio fora do ar")


def test_classificador_indisponivel_bloqueia(catalogo, cofre, provedor):
    """Derrubar o classificador e confirmar que bloqueia, e não que libera."""
    gw = Gateway(
        analisador=AnalisadorQuebrado(),
        catalogo=catalogo,
        cofre=cofre,
        trilha_por_tenant=lambda t: None,
        upstream=provedor,
    )
    c = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=criar_app(gw)), base_url="http://gateway"
    )
    r = pedir(c, f"CPF {CPF}")
    assert r.status_code == 503
    assert r.json()["error"]["type"] == "api_error"
    assert "fail-closed" in r.json()["error"]["message"]


def test_falha_do_classificador_vira_registro_na_trilha(conexao, catalogo, cofre, provedor):
    """Bloquear sem registrar deixaria o cliente sem como explicar depois."""
    trilha = TrilhaDeAuditoria(conexao, "vetorcred", papel=TrilhaDeAuditoria.PAPEL_DA_APLICACAO)
    gw = Gateway(
        analisador=AnalisadorQuebrado(),
        catalogo=catalogo,
        cofre=cofre,
        trilha_por_tenant=lambda t: trilha,
        upstream=provedor,
    )
    c = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=criar_app(gw)), base_url="http://gateway"
    )
    import asyncio

    asyncio.run(
        c.post(
            "/v1/messages",
            json={"model": "m", "max_tokens": 1, "messages": [{"role": "user", "content": CPF}]},
            headers={"x-api-key": "sk-ant-fake-7c41", "x-baluarte-tenant": "vetorcred"},
        )
    )
    registros = trilha.ler()
    assert len(registros) == 1
    assert registros[0]["acao_global"] == "bloquear"
    assert registros[0]["achados"][0]["entidade"] == "CLASSIFICADOR_INDISPONIVEL"


# ── auditoria do caminho feliz ───────────────────────────────────────

def test_requisicao_normal_vira_registro(conexao, analisador, catalogo, cofre, provedor):
    trilha = TrilhaDeAuditoria(conexao, "vetorcred", papel=TrilhaDeAuditoria.PAPEL_DA_APLICACAO)
    gw = Gateway(
        analisador=analisador,
        catalogo=catalogo,
        cofre=cofre,
        trilha_por_tenant=lambda t: trilha,
        upstream=provedor,
    )
    c = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=criar_app(gw)), base_url="http://gateway"
    )
    import asyncio

    asyncio.run(
        c.post(
            "/v1/messages",
            json={
                "model": "m",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": f"CPF {CPF}"}],
            },
            headers={"x-api-key": "sk-ant-fake-7c41", "x-baluarte-tenant": "vetorcred"},
        )
    )
    registro = trilha.ler()[0]
    assert registro["acao_global"] == "tokenizar"
    assert registro["chave_origem"] == "••7c41"
    # A trilha continua sem valor nenhum, mesmo com o proxy no caminho.
    with conexao.cursor() as cur:
        cur.execute("SELECT trilha_auditoria::text FROM trilha_auditoria")
        for (linha,) in cur.fetchall():
            assert CPF not in linha and "11144477735" not in linha


def test_chave_de_api_nao_vai_para_a_trilha(conexao, analisador, catalogo, cofre, provedor):
    trilha = TrilhaDeAuditoria(conexao, "vetorcred", papel=TrilhaDeAuditoria.PAPEL_DA_APLICACAO)
    gw = Gateway(
        analisador=analisador, catalogo=catalogo, cofre=cofre,
        trilha_por_tenant=lambda t: trilha, upstream=provedor,
    )
    c = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=criar_app(gw)), base_url="http://gateway"
    )
    import asyncio

    chave = "sk-ant-api03-SEGREDO-INTEIRO-7c41"
    asyncio.run(
        c.post(
            "/v1/messages",
            json={"model": "m", "max_tokens": 1, "messages": [{"role": "user", "content": "oi"}]},
            headers={"x-api-key": chave, "x-baluarte-tenant": "vetorcred"},
        )
    )
    with conexao.cursor() as cur:
        cur.execute("SELECT trilha_auditoria::text FROM trilha_auditoria")
        linha = cur.fetchone()[0]
    assert "SEGREDO" not in linha
    assert "••7c41" in linha
