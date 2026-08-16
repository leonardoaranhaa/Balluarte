import pytest

from baluarte.analisador import montar_analisador
from baluarte.politica.carregador import carregar_texto
from baluarte.politica.catalogo import CatalogoDePoliticas
from baluarte.politica.cobertura import (
    conferir,
    entidades_que_o_analisador_emite,
)

POLITICA = carregar_texto(
    """
nome: "Teste"
versao: 1
vigente_desde: 2026-01-01
regras:
  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: BR_CNS
    acao: bloquear
    base_normativa: "LGPD art. 11"
padrao:
  entidade_sem_regra:
    acao: bloquear
    base_normativa: "LGPD art. 6º, VIII"
  nenhuma_deteccao:
    acao: permitir
    base_normativa: "sem tratamento a restringir"
"""
)


def test_aponta_entidade_emitida_sem_regra():
    c = conferir(POLITICA, ["BR_CPF", "PERSON", "URL"])
    assert c.descobertas == ("PERSON", "URL")
    assert c.cobertas == ("BR_CPF",)
    assert not c.completa


def test_aponta_regra_para_entidade_que_ninguem_emite():
    """Não é erro: pode ser recognizer ainda não construído."""
    c = conferir(POLITICA, ["BR_CPF"])
    assert c.regras_sem_uso == ("BR_CNS",)


def test_cobertura_completa():
    c = conferir(POLITICA, ["BR_CPF", "BR_CNS"])
    assert c.completa
    assert c.descobertas == ()
    assert "Cobertura completa" in c.relatorio()


def test_relatorio_explica_a_consequencia():
    c = conferir(POLITICA, ["PERSON"])
    assert "padrão de entidade sem regra" in c.relatorio()


def test_entrada_repetida_nao_duplica():
    c = conferir(POLITICA, ["PERSON", "PERSON", "PERSON"])
    assert c.descobertas == ("PERSON",)


# ── o encaixe real entre o analisador e as políticas do repositório ──

@pytest.fixture(scope="module")
def emitidas():
    return entidades_que_o_analisador_emite(montar_analisador())


def test_analisador_declara_as_entidades_brasileiras(emitidas):
    assert "BR_CPF" in emitidas
    assert "BR_CNPJ" in emitidas


def test_politicas_do_repositorio_ainda_nao_cobrem_o_classificador(emitidas):
    """Documenta a lacuna real, em vez de fingir que ela não existe.

    Enquanto este teste passar assim, toda requisição com nome de pessoa ou
    URL é bloqueada pelo padrão. A saída não é afrouxar o padrão — é fechar a
    cobertura, e antes disso resolver a qualidade do NER, medida na Fase 0.
    """
    catalogo = CatalogoDePoliticas.de_diretorio("politicas/financeiro")
    c = conferir(catalogo.versao(2), emitidas)
    assert not c.completa
    assert "PERSON" in c.descobertas
