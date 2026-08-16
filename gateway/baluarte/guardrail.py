"""Guardrail do LiteLLM que roda a classificação brasileira em pre_call.

Por que não usar o guardrail de Presidio que já vem no LiteLLM: ele conversa
com o Presidio por HTTP (`PRESIDIO_ANALYZER_API_BASE`) e só sabe declarar
recognizers ad hoc em JSON — regex e score, nada mais. Não existe campo para
`validate_result`, então por aquele caminho não há como exigir dígito
verificador, e "onze dígitos" volta a valer por CPF. Ver o relatório da
Fase 0 em `fase0/RELATORIO.md`.

Este guardrail usa o analisador em processo. Ele não decide nada: só anota o
que achou. A decisão é do motor de política, na Fase 1 — aqui o comportamento
é o mínimo que a regra 3 do CLAUDE.md exige, que é falhar fechado.
"""

from typing import Any, Literal

from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.types.guardrails import GuardrailEventHooks

from .analisador import ClassificadorIndisponivel, montar_analisador


class ClassificacaoIndisponivel(Exception):
    """Erguida no pre_call quando não deu para classificar.

    Erguer interrompe a requisição antes de ela sair para o provedor. É a
    tradução literal da regra 3: sem classificador, bloqueia. Um `return None`
    aqui deixaria a requisição seguir — fail-open silencioso, que é o modo de
    falha que este produto existe para não ter.
    """


class GuardrailBaluarte(CustomGuardrail):
    ENTIDADES_BR = ("BR_CPF", "BR_CNPJ")

    def __init__(self, **kwargs):
        kwargs.setdefault("guardrail_name", "baluarte")
        # Ligado por padrão, e em pre_call. No LiteLLM um guardrail nasce
        # opt-in: só roda se a requisição pedir por ele no metadata. Para um
        # gateway de conformidade isso é o avesso do que se quer — quem está
        # colando CPF no prompt não vai lembrar de pedir a checagem. A mesma
        # lógica do fail-closed: o padrão protege, a exceção é que se declara.
        kwargs.setdefault("default_on", True)
        kwargs.setdefault("event_hook", GuardrailEventHooks.pre_call)
        super().__init__(**kwargs)
        self._analisador = None

    @property
    def analisador(self):
        if self._analisador is None:
            self._analisador = montar_analisador()
        return self._analisador

    def classificar(self, texto: str) -> list[dict[str, Any]]:
        """Devolve os achados sem o valor — só tipo, posição e score.

        A posição é o que o transformador vai precisar para mascarar ou
        tokenizar. O valor não sobe para camada nenhuma que registre, o que
        mantém a regra 2 válida por construção, e não por disciplina de quem
        escreve o log depois.
        """
        try:
            resultados = self.analisador.analyze(text=texto, language="pt")
        except ClassificadorIndisponivel:
            raise
        except Exception as erro:
            raise ClassificadorIndisponivel(
                "o classificador falhou durante a análise"
            ) from erro

        return [
            {
                "entidade": r.entity_type,
                "inicio": r.start,
                "fim": r.end,
                "score": r.score,
            }
            for r in sorted(resultados, key=lambda r: r.start)
        ]

    @staticmethod
    def _textos(data: dict) -> list[str]:
        textos = []
        for mensagem in data.get("messages") or []:
            conteudo = mensagem.get("content")
            if isinstance(conteudo, str):
                textos.append(conteudo)
            elif isinstance(conteudo, list):
                textos.extend(
                    parte.get("text", "")
                    for parte in conteudo
                    if isinstance(parte, dict) and parte.get("type") == "text"
                )
        return textos

    async def async_pre_call_hook(
        self,
        user_api_key_dict,
        cache,
        data: dict,
        call_type: Literal["completion", "acompletion", "embedding"],  # noqa: ARG002
    ):
        try:
            achados = [a for texto in self._textos(data) for a in self.classificar(texto)]
        except ClassificadorIndisponivel as erro:
            raise ClassificacaoIndisponivel(str(erro)) from erro

        # Fase 0 não transforma nem bloqueia: só prova que a classificação
        # roda no ponto certo do caminho e deixa o resultado disponível para
        # a camada seguinte.
        data.setdefault("metadata", {})["baluarte_achados"] = achados
        return data
