import itertools

import pytest

from baluarte.politica.acoes import Acao, mais_restritiva


def test_ordem_de_restritividade_declarada():
    """A ordem é a regra de desempate do motor inteiro.

    Se alguém mudar `acoes.py` sem querer, este teste cai antes de a mudança
    virar decisão diferente em produção — e mudar quem vence um empate é
    mudar o que sai da empresa do cliente.
    """
    assert Acao.PERMITIR < Acao.TOKENIZAR < Acao.MASCARAR < Acao.BLOQUEAR


def test_mascarar_vence_tokenizar():
    """O degrau que surpreende, isolado num teste próprio.

    Pelo que sai da empresa os dois se equivalem. Mascarar ganha porque não
    deixa cofre para trás. Ver a justificativa em `baluarte/politica/acoes.py`.
    """
    assert mais_restritiva([Acao.TOKENIZAR, Acao.MASCARAR]) is Acao.MASCARAR


@pytest.mark.parametrize("par", list(itertools.combinations(list(Acao), 2)))
def test_mais_restritiva_independe_da_ordem_de_entrada(par):
    a, b = par
    assert mais_restritiva([a, b]) is mais_restritiva([b, a])


def test_bloquear_vence_qualquer_uma():
    for outra in Acao:
        assert mais_restritiva([outra, Acao.BLOQUEAR]) is Acao.BLOQUEAR


def test_conjunto_vazio_nao_restringe():
    assert mais_restritiva([]) is Acao.PERMITIR


def test_empate_devolve_a_propria_acao():
    for acao in Acao:
        assert mais_restritiva([acao, acao, acao]) is acao
