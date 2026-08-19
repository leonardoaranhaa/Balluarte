from datetime import date

import pytest

from baluarte.politica.acoes import Acao
from baluarte.politica.avaliador import avaliar
from baluarte.politica.carregador import carregar_texto

HOJE = date(2026, 8, 15)


def politica(regras: str, sem_regra: str = "bloquear", sem_deteccao: str = "permitir"):
    return carregar_texto(
        f"""
nome: "Teste"
versao: 1
vigente_desde: 2026-01-01
regras:
{regras}
padrao:
  entidade_sem_regra:
    acao: {sem_regra}
    base_normativa: "LGPD art. 6º, VIII"
  nenhuma_deteccao:
    acao: {sem_deteccao}
    base_normativa: "sem tratamento a restringir"
"""
    )


UMA_REGRA = politica(
    """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
"""
)


# ── determinismo, o requisito central da fase ────────────────────────

def test_determinismo_em_cem_execucoes():
    """Mesma entrada, mesma política, mesma data → mesma saída, sempre.

    A comparação é por igualdade da decisão inteira, não só da ação: ordem das
    entidades, contagem, justificativas e identificação da política também
    precisam bater, senão "reconstituir a decisão" não é verificável.
    """
    entrada = ["BR_CPF", "EMAIL_ADDRESS", "BR_CPF", "PHONE_NUMBER"]
    pol = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: EMAIL_ADDRESS
    acao: mascarar
    base_normativa: "LGPD art. 5º, I"
"""
    )
    primeira = avaliar(entrada, pol, HOJE)
    for _ in range(100):
        assert avaliar(entrada, pol, HOJE) == primeira


def test_ordem_da_entrada_nao_muda_a_saida():
    pol = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: EMAIL_ADDRESS
    acao: mascarar
    base_normativa: "LGPD art. 5º, I"
"""
    )
    a = avaliar(["BR_CPF", "EMAIL_ADDRESS"], pol, HOJE)
    b = avaliar(["EMAIL_ADDRESS", "BR_CPF"], pol, HOJE)
    assert a == b


def test_avaliacao_nao_depende_do_relogio():
    """A data entra como argumento; o motor não consulta `date.today()`.

    Se consultasse, reavaliar a mesma requisição amanhã poderia dar outra
    resposta, e a pergunta "por que isso foi bloqueado em março?" ficaria sem
    resposta reconstituível.
    """
    d1 = avaliar(["BR_CPF"], UMA_REGRA, date(2026, 3, 10))
    d2 = avaliar(["BR_CPF"], UMA_REGRA, date(2026, 3, 10))
    assert d1 == d2
    assert d1.avaliada_em == date(2026, 3, 10)


# ── precedência ──────────────────────────────────────────────────────

def test_duas_regras_para_a_mesma_entidade_a_mais_restritiva_vence():
    pol = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: BR_CPF
    acao: mascarar
    base_normativa: "LGPD art. 6º, III"
"""
    )
    d = avaliar(["BR_CPF"], pol, HOJE)
    assert d.por_entidade[0].acao is Acao.MASCARAR
    assert d.acao is Acao.MASCARAR


def test_a_ordem_das_regras_no_arquivo_nao_muda_o_vencedor():
    invertida = politica(
        """  - entidade: BR_CPF
    acao: mascarar
    base_normativa: "LGPD art. 6º, III"
  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
"""
    )
    assert avaliar(["BR_CPF"], invertida, HOJE).por_entidade[0].acao is Acao.MASCARAR


def test_justificativa_cita_so_as_regras_que_pediram_a_acao_vencedora():
    """Regra que pedia coisa menos restritiva não justifica a decisão tomada."""
    pol = politica(
        """  - entidade: BR_CPF
    acao: permitir
    base_normativa: "NÃO DEVE APARECER"
  - entidade: BR_CPF
    acao: bloquear
    base_normativa: "Resolução BCB 4.658/2018"
"""
    )
    d = avaliar(["BR_CPF"], pol, HOJE)
    bases = [j.base_normativa for j in d.por_entidade[0].justificativas]
    assert bases == ["Resolução BCB 4.658/2018"]


def test_empate_cita_todas_as_regras_empatadas():
    """Duas regras pedindo a mesma coisa: a explicação honesta cita as duas."""
    pol = politica(
        """  - entidade: BR_CPF
    acao: bloquear
    base_normativa: "primeira base"
  - entidade: BR_CPF
    acao: bloquear
    base_normativa: "segunda base"
"""
    )
    d = avaliar(["BR_CPF"], pol, HOJE)
    bases = [j.base_normativa for j in d.por_entidade[0].justificativas]
    assert bases == ["primeira base", "segunda base"]


def test_decisao_global_e_a_mais_restritiva_entre_as_entidades():
    pol = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: IBAN_CODE
    acao: bloquear
    base_normativa: "Resolução BCB 4.658/2018"
"""
    )
    d = avaliar(["BR_CPF", "IBAN_CODE"], pol, HOJE)
    assert d.acao is Acao.BLOQUEAR
    assert d.bloqueada


# ── fail-closed ──────────────────────────────────────────────────────

def test_entidade_sem_regra_cai_no_padrao_e_bloqueia():
    """Regra 3 do CLAUDE.md: ausência de regra não é autorização."""
    d = avaliar(["BR_CNS"], UMA_REGRA, HOJE)
    assert d.por_entidade[0].acao is Acao.BLOQUEAR
    assert d.acao is Acao.BLOQUEAR
    assert "sem regra" in d.por_entidade[0].justificativas[0].origem


def test_entidade_sem_regra_tambem_carrega_base_normativa():
    d = avaliar(["BR_CNS"], UMA_REGRA, HOJE)
    assert d.por_entidade[0].justificativas[0].base_normativa.strip()


def test_politica_pode_declarar_fail_open_mas_precisa_declarar():
    """Fail-open só mediante opção explícita do cliente, registrada.

    Continua sendo escolha da política, com base normativa própria — nunca
    default do código.
    """
    permissiva = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
""",
        sem_regra="permitir",
    )
    assert avaliar(["BR_CNS"], permissiva, HOJE).acao is Acao.PERMITIR


# ── ausência de detecção ─────────────────────────────────────────────

def test_sem_deteccao_usa_o_padrao_da_politica():
    d = avaliar([], UMA_REGRA, HOJE)
    assert d.acao is Acao.PERMITIR
    assert d.por_entidade == ()
    assert "Nenhum dado pessoal detectado" in d.explicacao()


def test_sem_deteccao_com_politica_restritiva():
    restritiva = politica(
        """  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
""",
        sem_deteccao="bloquear",
    )
    assert avaliar([], restritiva, HOJE).acao is Acao.BLOQUEAR


# ── contagem e explicabilidade ───────────────────────────────────────

def test_conta_ocorrencias_por_entidade():
    d = avaliar(["BR_CPF", "BR_CPF", "BR_CPF"], UMA_REGRA, HOJE)
    assert d.por_entidade[0].ocorrencias == 3


def test_explicacao_traz_politica_versao_hash_e_norma():
    d = avaliar(["BR_CPF"], UMA_REGRA, HOJE)
    texto = d.explicacao()
    assert "v1" in texto
    assert UMA_REGRA.sha256[:12] in texto
    assert "LGPD art. 33" in texto
    assert "2026-08-15" in texto


def test_decisao_nao_carrega_valor_de_dado_pessoal():
    """Regra 2 do CLAUDE.md, por formato da estrutura.

    O motor recebe tipos de entidade, nunca conteúdo — então não há caminho
    pelo qual um CPF chegue à decisão, e daí ao log da Fase 2.
    """
    d = avaliar(["BR_CPF", "BR_CPF"], UMA_REGRA, HOJE)
    campos = set(vars(d.por_entidade[0]))
    assert campos == {"entidade", "acao", "ocorrencias", "justificativas"}
    assert "valor" not in campos and "texto" not in campos
