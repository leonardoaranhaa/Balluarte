from datetime import date

import pytest

from baluarte.politica.acoes import Acao
from baluarte.politica.avaliador import avaliar_com_catalogo
from baluarte.politica.carregador import carregar_texto
from baluarte.politica.catalogo import CatalogoDePoliticas, SemPoliticaVigente
from baluarte.politica.modelo import PoliticaInvalida

PASTA = "politicas/financeiro"


def versao(numero: int, desde: str, acao: str = "tokenizar", nome: str = "Teste"):
    return carregar_texto(
        f"""
nome: "{nome}"
versao: {numero}
vigente_desde: {desde}
regras:
  - entidade: BR_CPF
    acao: {acao}
    base_normativa: "LGPD art. 33"
padrao:
  entidade_sem_regra:
    acao: bloquear
    base_normativa: "LGPD art. 6º, VIII"
  nenhuma_deteccao:
    acao: permitir
    base_normativa: "sem tratamento a restringir"
"""
    )


# ── consulta histórica ───────────────────────────────────────────────

def test_consulta_por_data_devolve_a_versao_vigente():
    cat = CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-06-01")])
    assert cat.vigente_em(date(2026, 3, 15)).versao == 1
    assert cat.vigente_em(date(2026, 9, 15)).versao == 2


def test_vigencia_inclui_o_proprio_dia_de_inicio():
    cat = CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-06-01")])
    assert cat.vigente_em(date(2026, 5, 31)).versao == 1
    assert cat.vigente_em(date(2026, 6, 1)).versao == 2


def test_data_anterior_a_primeira_versao_nao_inventa_decisao():
    """Antes da primeira política não havia regra nenhuma.

    Responder qualquer ação aqui seria inventar uma decisão que o cliente
    nunca tomou.
    """
    cat = CatalogoDePoliticas([versao(1, "2026-01-01")])
    with pytest.raises(SemPoliticaVigente):
        cat.vigente_em(date(2025, 12, 31))


def test_requisicao_antiga_continua_julgada_pela_politica_da_epoca():
    """O caso que o requisito descreve: reconstituir março depois de mudar em junho."""
    cat = CatalogoDePoliticas(
        [versao(1, "2026-01-01", acao="tokenizar"), versao(2, "2026-06-01", acao="bloquear")]
    )
    marco = avaliar_com_catalogo(["BR_CPF"], cat, date(2026, 3, 10))
    assert marco.acao is Acao.TOKENIZAR
    assert marco.politica_versao == 1

    julho = avaliar_com_catalogo(["BR_CPF"], cat, date(2026, 7, 10))
    assert julho.acao is Acao.BLOQUEAR
    assert julho.politica_versao == 2

    # Reavaliar março depois da v2 existir continua devolvendo a v1.
    assert avaliar_com_catalogo(["BR_CPF"], cat, date(2026, 3, 10)) == marco


def test_hash_da_decisao_aponta_para_a_versao_certa():
    cat = CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-06-01")])
    d = avaliar_com_catalogo(["BR_CPF"], cat, date(2026, 3, 10))
    assert d.politica_sha256 == cat.versao(1).sha256
    assert d.politica_sha256 != cat.versao(2).sha256


# ── o que o catálogo recusa ao ser montado ───────────────────────────

def test_recusa_versoes_repetidas():
    with pytest.raises(PoliticaInvalida, match="v1"):
        CatalogoDePoliticas([versao(1, "2026-01-01"), versao(1, "2026-06-01")])


def test_recusa_mesma_data_de_vigencia():
    with pytest.raises(PoliticaInvalida, match="mesma data"):
        CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-01-01")])


def test_recusa_politica_andando_para_tras_no_tempo():
    with pytest.raises(PoliticaInvalida, match="para trás"):
        CatalogoDePoliticas([versao(1, "2026-06-01"), versao(2, "2026-01-01")])


def test_recusa_nomes_diferentes_no_mesmo_catalogo():
    with pytest.raises(PoliticaInvalida, match="nomes diferentes"):
        CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-06-01", nome="Outra")])


def test_recusa_catalogo_vazio():
    with pytest.raises(PoliticaInvalida):
        CatalogoDePoliticas([])


def test_consulta_nunca_levanta_por_politica_malformada():
    """As recusas acontecem ao montar, não ao consultar.

    Exceção de validação em tempo de requisição faria o caminho falhar de
    forma imprevisível, que é o oposto de fail-closed previsível.
    """
    cat = CatalogoDePoliticas([versao(1, "2026-01-01"), versao(2, "2026-06-01")])
    for dia in range(1, 29):
        assert cat.vigente_em(date(2026, 6, dia)).versao == 2


# ── as políticas versionadas do repositório ──────────────────────────

def test_politicas_do_repositorio_carregam():
    cat = CatalogoDePoliticas.de_diretorio(PASTA)
    assert [p.versao for p in cat.versoes] == [1, 2]
    assert cat.nome == "Financeiro — renegociação e cobrança"


def test_v1_do_repositorio_continua_intacta_ao_lado_da_v2():
    """Regra 5: a v2 não substitui a v1, fica ao lado dela."""
    cat = CatalogoDePoliticas.de_diretorio(PASTA)
    v1, v2 = cat.versao(1), cat.versao(2)
    assert v1.sha256 != v2.sha256
    # CNPJ mudou de permitir para tokenizar entre as duas versões.
    assert v1.regras_de("BR_CNPJ")[0].acao is Acao.PERMITIR
    assert v2.regras_de("BR_CNPJ")[0].acao is Acao.TOKENIZAR


def test_toda_regra_do_repositorio_tem_base_normativa():
    """Regra 4 do CLAUDE.md, cobrada sobre as políticas de verdade."""
    cat = CatalogoDePoliticas.de_diretorio(PASTA)
    for p in cat.versoes:
        for r in p.regras:
            assert len(r.base_normativa) > 20, f"{p.identificacao}: {r.entidade}"
        assert p.base_sem_regra.strip()
        assert p.base_sem_deteccao.strip()
