import dataclasses
from datetime import date

import pytest

from baluarte.politica.acoes import Acao
from baluarte.politica.carregador import carregar_texto
from baluarte.politica.modelo import PoliticaInvalida

MINIMA = """
nome: "Teste"
versao: 1
vigente_desde: 2026-01-01
regras:
  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
padrao:
  entidade_sem_regra:
    acao: bloquear
    base_normativa: "LGPD art. 6º, VIII"
  nenhuma_deteccao:
    acao: permitir
    base_normativa: "sem tratamento a restringir"
"""


def test_carrega_politica_minima():
    p = carregar_texto(MINIMA)
    assert p.nome == "Teste"
    assert p.versao == 1
    assert p.vigente_desde == date(2026, 1, 1)
    assert p.regras[0].acao is Acao.TOKENIZAR
    assert p.acao_sem_regra is Acao.BLOQUEAR
    assert p.acao_sem_deteccao is Acao.PERMITIR
    assert len(p.sha256) == 64


def test_politica_e_imutavel():
    """Regra 5 do CLAUDE.md, cobrada pelo objeto e não pela boa vontade."""
    p = carregar_texto(MINIMA)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.versao = 2
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.regras[0].acao = Acao.PERMITIR


def test_hash_muda_quando_o_texto_muda():
    outro = MINIMA.replace('nome: "Teste"', 'nome: "Teste "')
    assert carregar_texto(MINIMA).sha256 != carregar_texto(outro).sha256


def test_hash_e_estavel_entre_leituras():
    assert carregar_texto(MINIMA).sha256 == carregar_texto(MINIMA).sha256


# ── o que precisa ser recusado no carregamento ───────────────────────

def test_recusa_regra_sem_base_normativa():
    """Regra 4 do CLAUDE.md: sem norma, não é evidência de conformidade."""
    texto = MINIMA.replace('base_normativa: "LGPD art. 33"', 'base_normativa: "  "')
    with pytest.raises(PoliticaInvalida, match="base normativa"):
        carregar_texto(texto)


def test_recusa_regra_sem_campo_de_base_normativa():
    texto = MINIMA.replace('    base_normativa: "LGPD art. 33"\n', "")
    with pytest.raises(PoliticaInvalida, match="base_normativa"):
        carregar_texto(texto)


@pytest.mark.parametrize("bloco", ["entidade_sem_regra", "nenhuma_deteccao"])
def test_recusa_politica_sem_os_padroes_declarados(bloco):
    """Nenhum dos dois padrões tem valor implícito.

    Assumir um default no código seria decidir pelo encarregado de dados do
    cliente sem ele saber, e ainda sem base normativa.
    """
    linhas = MINIMA.splitlines(keepends=True)
    corte = [i for i, l in enumerate(linhas) if l.strip().startswith(f"{bloco}:")][0]
    texto = "".join(linhas[:corte] + linhas[corte + 3 :])
    with pytest.raises(PoliticaInvalida, match=bloco):
        carregar_texto(texto)


def test_recusa_acao_inexistente():
    texto = MINIMA.replace("acao: tokenizar", "acao: criptografar")
    with pytest.raises(PoliticaInvalida, match="criptografar"):
        carregar_texto(texto)


def test_recusa_politica_sem_regras():
    texto = MINIMA.replace(
        '  - entidade: BR_CPF\n    acao: tokenizar\n    base_normativa: "LGPD art. 33"\n',
        "  []\n",
    )
    with pytest.raises(PoliticaInvalida):
        carregar_texto(texto)


def test_recusa_versao_zero():
    with pytest.raises(PoliticaInvalida, match="versão"):
        carregar_texto(MINIMA.replace("versao: 1", "versao: 0"))


def test_recusa_data_malformada():
    with pytest.raises(PoliticaInvalida, match="AAAA-MM-DD"):
        carregar_texto(MINIMA.replace("vigente_desde: 2026-01-01", 'vigente_desde: "01/01/2026"'))


def test_recusa_yaml_quebrado():
    with pytest.raises(PoliticaInvalida, match="YAML"):
        carregar_texto("nome: [nao fecha\n")


def test_mensagem_de_erro_nomeia_o_arquivo():
    with pytest.raises(PoliticaInvalida, match="financeiro-v9.yaml"):
        carregar_texto("nome: só isso", origem="financeiro-v9.yaml")
