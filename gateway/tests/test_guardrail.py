import asyncio

import pytest

from baluarte.guardrail import ClassificacaoIndisponivel, GuardrailBaluarte
from baluarte.analisador import ClassificadorIndisponivel


@pytest.fixture(scope="module")
def guardrail():
    g = GuardrailBaluarte()
    g.analisador  # força a montagem uma vez só
    return g


def rodar(guardrail, data):
    return asyncio.run(
        guardrail.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion"
        )
    )


def test_pre_call_anota_achados_sem_valor(guardrail):
    data = {
        "model": "claude-opus-5",
        "messages": [
            {"role": "user", "content": "Analise a proposta de Marina, CPF 111.444.777-35."}
        ],
    }
    saida = rodar(guardrail, data)
    achados = saida["metadata"]["baluarte_achados"]

    cpfs = [a for a in achados if a["entidade"] == "BR_CPF"]
    assert len(cpfs) == 1
    assert cpfs[0]["score"] == 1.0

    # A regra 2 do CLAUDE.md tem que valer por construção: o achado carrega
    # posição, não conteúdo. Se algum dia alguém acrescentar o valor aqui,
    # este teste cai.
    assert set(cpfs[0]) == {"entidade", "inicio", "fim", "score"}
    serializado = repr(achados)
    assert "111.444.777-35" not in serializado
    assert "11144477735" not in serializado


def test_pre_call_le_conteudo_multimodal(guardrail):
    data = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Fornecedora de CNPJ 11.222.333/0001-81."},
                    {"type": "image_url", "image_url": {"url": "https://exemplo/x.png"}},
                ],
            }
        ]
    }
    achados = rodar(guardrail, data)["metadata"]["baluarte_achados"]
    assert [a["entidade"] for a in achados if a["entidade"].startswith("BR_")] == ["BR_CNPJ"]


def test_pre_call_sem_dado_pessoal_nao_inventa_achado(guardrail):
    data = {"messages": [{"role": "user", "content": "Resuma a reuniao de ontem."}]}
    achados = rodar(guardrail, data)["metadata"]["baluarte_achados"]
    assert [a for a in achados if a["entidade"].startswith("BR_")] == []


def test_falha_do_classificador_bloqueia_em_vez_de_liberar():
    """Regra 3 do CLAUDE.md: fail-closed.

    Um classificador quebrado não pode virar "nenhum dado pessoal encontrado".
    """

    class Quebrado(GuardrailBaluarte):
        @property
        def analisador(self):
            raise ClassificadorIndisponivel("modelo ausente")

    data = {"messages": [{"role": "user", "content": "CPF 111.444.777-35"}]}
    with pytest.raises(ClassificacaoIndisponivel):
        rodar(Quebrado(), data)


def test_guardrail_roda_em_pre_call_sem_ninguem_pedir():
    """No LiteLLM um guardrail nasce opt-in; este precisa nascer ligado.

    Quem cola CPF no prompt não vai lembrar de pedir a checagem no metadata
    da requisição. Se a proteção depender do pedido, ela não protege.
    """
    from litellm.types.guardrails import GuardrailEventHooks

    g = GuardrailBaluarte()
    assert g.default_on is True
    assert g.should_run_guardrail(data={}, event_type=GuardrailEventHooks.pre_call)


def test_guardrail_nao_roda_fora_do_pre_call():
    from litellm.types.guardrails import GuardrailEventHooks

    g = GuardrailBaluarte()
    assert not g.should_run_guardrail(data={}, event_type=GuardrailEventHooks.post_call)
