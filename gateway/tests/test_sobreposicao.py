import pytest

from baluarte.analisador import montar_analisador
from baluarte.classificacao.sobreposicao import (
    Achado,
    de_resultados_do_presidio,
    resolver,
)


def test_o_caso_que_a_fase_1_deixou_pendente():
    """O e-mail contado três vezes.

    EMAIL_ADDRESS cobre o endereço inteiro; ORGANIZATION casa o mesmo trecho;
    URL casa o domínio dentro dele. É um dado, não três.
    """
    achados = [
        Achado("EMAIL_ADDRESS", 10, 33, 1.00),
        Achado("ORGANIZATION", 10, 33, 0.85),
        Achado("URL", 17, 33, 0.50),
    ]
    assert [a.entidade for a in resolver(achados)] == ["EMAIL_ADDRESS"]


def test_trecho_maior_vence_o_menor():
    assert [a.entidade for a in resolver(
        [Achado("PEQUENO", 5, 10, 0.99), Achado("GRANDE", 0, 20, 0.40)]
    )] == ["GRANDE"]


def test_empatando_em_tamanho_o_score_decide():
    assert [a.entidade for a in resolver(
        [Achado("FRACO", 0, 10, 0.40), Achado("FORTE", 0, 10, 0.95)]
    )] == ["FORTE"]


def test_empate_total_e_desempatado_por_ordem_alfabetica():
    """Critério arbitrário e assumido como tal: o que importa é ser estável."""
    achados = [Achado("ZETA", 0, 10, 0.8), Achado("ALFA", 0, 10, 0.8)]
    assert [a.entidade for a in resolver(achados)] == ["ALFA"]
    assert [a.entidade for a in resolver(list(reversed(achados)))] == ["ALFA"]


def test_achados_separados_continuam_dois():
    """Dois CPFs separados por vírgula não são sobreposição."""
    resolvidos = resolver([Achado("BR_CPF", 0, 14, 1.0), Achado("BR_CPF", 16, 30, 1.0)])
    assert len(resolvidos) == 2


def test_achados_que_apenas_encostam_nao_sao_sobreposicao():
    resolvidos = resolver([Achado("A", 0, 10, 1.0), Achado("B", 10, 20, 1.0)])
    assert len(resolvidos) == 2


def test_saida_ordenada_por_posicao():
    resolvidos = resolver(
        [Achado("C", 40, 50, 1.0), Achado("A", 0, 10, 1.0), Achado("B", 20, 30, 1.0)]
    )
    assert [a.inicio for a in resolvidos] == [0, 20, 40]


def test_resolucao_e_deterministica():
    """Tudo daqui para a frente depende disso, incluindo o hash da trilha."""
    import itertools

    achados = [
        Achado("EMAIL_ADDRESS", 10, 33, 1.00),
        Achado("ORGANIZATION", 10, 33, 0.85),
        Achado("URL", 17, 33, 0.50),
        Achado("BR_CPF", 40, 54, 1.00),
    ]
    esperado = resolver(achados)
    for ordem in itertools.permutations(achados):
        assert resolver(list(ordem)) == esperado


def test_lista_vazia():
    assert resolver([]) == []


def test_no_texto_de_verdade_o_email_vira_um_achado_so():
    analisador = montar_analisador()
    texto = "Contato: marina@vetorcred.com.br para retorno."
    brutos = de_resultados_do_presidio(analisador.analyze(text=texto, language="pt"))
    # O teste só tem valor se houver sobreposição de verdade para resolver.
    houve_sobreposicao = any(
        a.sobrepoe(b) for i, a in enumerate(brutos) for b in brutos[i + 1 :]
    )
    assert houve_sobreposicao, "o teste precisa que o Presidio sobreponha"
    resolvidos = resolver(brutos)
    assert sum(1 for a in resolvidos if a.entidade == "EMAIL_ADDRESS") == 1
    assert not any(a.entidade == "URL" for a in resolvidos)
