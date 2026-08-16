import pytest

from baluarte.analisador import montar_analisador


@pytest.fixture(scope="module")
def analisador():
    return montar_analisador()


def achados(analisador, texto: str, entidade: str) -> list[str]:
    return [
        texto[r.start : r.end]
        for r in analisador.analyze(text=texto, language="pt")
        if r.entity_type == entidade
    ]


# ── o que tem que ser achado ─────────────────────────────────────────

def test_acha_cpf_formatado(analisador):
    assert achados(analisador, "O CPF é 111.444.777-35 mesmo.", "BR_CPF") == ["111.444.777-35"]


def test_acha_cpf_sem_formatacao(analisador):
    assert achados(analisador, "documento 11144477735 no cadastro", "BR_CPF") == ["11144477735"]


def test_acha_cnpj_nos_dois_formatos(analisador):
    assert achados(analisador, "CNPJ 11.222.333/0001-81", "BR_CNPJ") == ["11.222.333/0001-81"]
    assert achados(analisador, "CNPJ 11222333000181", "BR_CNPJ") == ["11222333000181"]


@pytest.mark.parametrize(
    "texto",
    [
        "O CPF do titular é 111.444.777-35.",
        "O CPF do titular é 111.444.777-35!",
        "O CPF do titular é 111.444.777-35?",
        "Titular: 111.444.777-35, conta encerrada.",
        "Cadastro (111.444.777-35) divergente.",
        "Documento 111.444.777-35; verificar.",
        "111.444.777-35",
    ],
)
def test_acha_cpf_encostado_em_pontuacao(analisador, texto):
    """Regressão da Fase 0.

    A borda direita do padrão era `(?![\\d.\\-/])`, que trata ponto final de
    frase como continuação do número. Cinco dos treze CPFs formatados do corpus
    terminavam frase, e os cinco passavam batido — a forma mais comum de
    escrever um documento era justamente a que não era detectada.
    """
    assert achados(analisador, texto, "BR_CPF") == ["111.444.777-35"]


def test_acha_cnpj_no_fim_da_frase(analisador):
    assert achados(analisador, "Fornecedora de CNPJ 11.222.333/0001-81.", "BR_CNPJ") == [
        "11.222.333/0001-81"
    ]


# ── o que não pode ser achado ────────────────────────────────────────

def test_ignora_onze_digitos_que_reprovam_no_dv(analisador):
    assert achados(analisador, "protocolo 12345678900 aberto", "BR_CPF") == []


def test_ignora_cpf_formatado_com_dv_errado(analisador):
    assert achados(analisador, "o campo veio 111.444.777-34 e foi recusado", "BR_CPF") == []


def test_nao_extrai_cpf_de_dentro_de_cnpj(analisador):
    """Onze dígitos cabem dentro de catorze; a borda esquerda impede a leitura."""
    assert achados(analisador, "CNPJ 11222333000181 ativo", "BR_CPF") == []


def test_nao_confunde_decimal_com_documento(analisador):
    """Separador seguido de dígito continua sendo número, não fim de documento."""
    assert achados(analisador, "valor 12345678900.50 lancado", "BR_CPF") == []


def test_texto_sem_documento_nao_produz_achado(analisador):
    texto = "Explique a diferenca entre controlador e operador na LGPD."
    assert achados(analisador, texto, "BR_CPF") == []
    assert achados(analisador, texto, "BR_CNPJ") == []


# ── determinismo, que é a regra 1 do CLAUDE.md ───────────────────────

def test_mesma_entrada_produz_mesma_saida(analisador):
    texto = "Titular 111.444.777-35 e fornecedora 11.222.333/0001-81."
    primeira = [
        (r.entity_type, r.start, r.end, r.score)
        for r in sorted(analisador.analyze(text=texto, language="pt"), key=lambda r: r.start)
    ]
    for _ in range(5):
        repetida = [
            (r.entity_type, r.start, r.end, r.score)
            for r in sorted(analisador.analyze(text=texto, language="pt"), key=lambda r: r.start)
        ]
        assert repetida == primeira
