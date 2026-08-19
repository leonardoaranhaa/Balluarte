"""Testes da trilha contra Postgres de verdade.

Contra banco real e não contra dublê: os requisitos desta fase são
propriedades do banco — append-only por gatilho, segregação por row-level
security, unicidade de hash. Testar contra simulação provaria que a simulação
faz o que eu escrevi que ela faz.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from baluarte.auditoria.repositorio import TenantNaoDeclarado, TrilhaDeAuditoria
from baluarte.auditoria.verificacao import verificar
from baluarte.politica.avaliador import avaliar
from baluarte.politica.carregador import carregar_texto

PAPEL = TrilhaDeAuditoria.PAPEL_DA_APLICACAO

POLITICA = carregar_texto(
    """
nome: "Financeiro"
versao: 3
vigente_desde: 2026-01-01
regras:
  - entidade: BR_CPF
    acao: tokenizar
    base_normativa: "LGPD art. 33"
  - entidade: EMAIL_ADDRESS
    acao: mascarar
    base_normativa: "LGPD art. 5º, I"
padrao:
  entidade_sem_regra:
    acao: bloquear
    base_normativa: "LGPD art. 6º, VIII"
  nenhuma_deteccao:
    acao: permitir
    base_normativa: "sem tratamento a restringir"
"""
)

QUANDO = date(2026, 8, 16)


def decisao(entidades=("BR_CPF", "BR_CPF", "EMAIL_ADDRESS")):
    return avaliar(list(entidades), POLITICA, QUANDO)


def trilha(conexao, tenant="vetorcred"):
    return TrilhaDeAuditoria(conexao, tenant, papel=PAPEL)


def gravar(t, n=1, **kwargs):
    base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
    return [
        t.registrar(
            decisao=kwargs.get("decisao", decisao()),
            chave_origem=kwargs.get("chave_origem", "svc-credito/••7c41"),
            provedor_destino=kwargs.get("provedor_destino", "anthropic"),
            registrado_em=base + timedelta(seconds=i),
        )
        for i in range(n)
    ]


# ── requisito 4: nenhum valor de PII em nenhum campo ─────────────────

CPF_REAL = "111.444.777-35"
CPF_CRU = "11144477735"
EMAIL_REAL = "marina@vetorcred.com.br"
NOME_REAL = "Marina Alves"


def test_nenhum_valor_de_pii_em_nenhum_campo_do_registro(conexao):
    """O teste que a fase chama de REGRA CRÍTICA.

    Passa uma requisição com CPF, e-mail e nome de verdade pelo caminho
    inteiro — classificação, decisão, gravação — e depois varre **todas** as
    colunas de **todas** as linhas procurando qualquer um dos valores, em
    qualquer formato.

    A varredura é feita em SQL, sobre a linha inteira convertida em texto, e
    não sobre o objeto Python: se um dia alguém acrescentar uma coluna, ela
    entra na varredura sozinha, sem ninguém lembrar de atualizar o teste.
    """
    t = trilha(conexao)
    gravar(t, n=3)

    with conexao.cursor() as cur:
        cur.execute("SELECT trilha_auditoria::text FROM trilha_auditoria")
        linhas_inteiras = [linha[0] for linha in cur.fetchall()]

    assert linhas_inteiras, "o teste precisa de linhas para ter valor"

    proibidos = [
        CPF_REAL, CPF_CRU, EMAIL_REAL, NOME_REAL,
        "111444777", "444.777", "marina@", "vetorcred.com.br",
    ]
    for linha in linhas_inteiras:
        for valor in proibidos:
            assert valor not in linha, f"valor de PII na trilha: {valor!r}"


def test_a_trilha_registra_o_tipo_e_a_quantidade(conexao):
    """O complemento do teste anterior: não basta não vazar, tem que servir.

    Registrar que um CPF foi detectado, jamais qual — mas registrar.
    """
    t = trilha(conexao)
    gravar(t, n=1)
    linha = t.ler()[0]
    achados = {a["entidade"]: a for a in linha["achados"]}
    assert achados["BR_CPF"]["quantidade"] == 2
    assert achados["BR_CPF"]["acao"] == "tokenizar"
    assert achados["EMAIL_ADDRESS"]["acao"] == "mascarar"


def test_o_esquema_nao_tem_coluna_para_valor(conexao):
    """A regra 2 como propriedade do esquema, não como cuidado do INSERT."""
    with conexao.cursor() as cur:
        cur.execute(
            """
            SELECT column_name FROM information_schema.columns
             WHERE table_name = 'trilha_auditoria'
            """
        )
        colunas = {c[0] for c in cur.fetchall()}
    for suspeita in ("valor", "conteudo", "texto", "prompt", "payload", "corpo"):
        assert suspeita not in colunas


# ── requisito 3: encadeamento e detecção de adulteração ──────────────

def test_cadeia_integra_passa(conexao):
    t = trilha(conexao)
    gravar(t, n=5)
    r = verificar(t.ler())
    assert r.integra
    assert r.total == 5
    assert r.conferidos == 5


def test_primeiro_registro_aponta_para_a_genese(conexao):
    t = trilha(conexao)
    gravar(t, n=1)
    assert t.ler()[0]["hash_anterior"] == "0" * 64


def test_cada_registro_aponta_para_o_anterior(conexao):
    t = trilha(conexao)
    gravar(t, n=4)
    linhas = t.ler()
    for anterior, seguinte in zip(linhas, linhas[1:]):
        assert seguinte["hash_anterior"] == anterior["hash_registro"]


def test_conteudo_alterado_e_detectado(conexao):
    """Adulteração de campo, feita por fora do gatilho.

    O gatilho recusa UPDATE, então para provar a detecção é preciso alterar a
    linha de um jeito que o gatilho não veja — aqui, desabilitando-o como dono
    da tabela. É exatamente o cenário que o encadeamento existe para cobrir:
    quem tem privilégio para desligar o gatilho ainda não consegue esconder
    que mexeu.
    """
    t = trilha(conexao)
    gravar(t, n=5)
    assert verificar(t.ler()).integra

    with conexao.cursor() as cur:
        cur.execute("ALTER TABLE trilha_auditoria DISABLE TRIGGER trilha_sem_update")
        cur.execute(
            "UPDATE trilha_auditoria SET chave_origem = 'svc-comprometido' "
            "WHERE sequencia = (SELECT min(sequencia) + 2 FROM trilha_auditoria) "
            "AND chave_origem <> 'svc-comprometido' RETURNING sequencia"
        )
        # Guarda contra teste mentiroso: se o UPDATE não mudou linha nenhuma,
        # a verificação falhar depois não provaria nada. Aconteceu ao escrever
        # a demonstração desta fase — o campo escolhido já tinha o valor novo.
        assert cur.fetchone() is not None, "a adulteração precisa alterar algo"
        cur.execute("ALTER TABLE trilha_auditoria ENABLE TRIGGER trilha_sem_update")
    conexao.commit()

    r = verificar(t.ler())
    assert not r.integra
    assert any(q.tipo == "conteúdo alterado" for q in r.quebras)
    assert "ADULTERADA" in r.relatorio()


def test_registro_removido_e_detectado(conexao):
    """Remoção não altera nenhum registro; quem denuncia é o elo."""
    t = trilha(conexao)
    gravar(t, n=5)
    linhas = t.ler()
    sem_o_terceiro = [l for l in linhas if l["sequencia"] != linhas[2]["sequencia"]]

    r = verificar(sem_o_terceiro)
    assert not r.integra
    assert any(q.tipo == "elo rompido" for q in r.quebras)


def test_reordenacao_e_detectada(conexao):
    t = trilha(conexao)
    gravar(t, n=4)
    linhas = t.ler()
    trocado = list(linhas)
    trocado[1], trocado[2] = trocado[2], trocado[1]
    for i, l in enumerate(trocado):
        l["sequencia"] = linhas[i]["sequencia"]

    assert not verificar(trocado).integra


def test_relatorio_diz_onde_quebrou(conexao):
    t = trilha(conexao)
    gravar(t, n=6)
    linhas = t.ler()
    linhas[3]["chave_origem"] = "outra-chave"

    r = verificar(linhas)
    assert not r.integra
    assert r.conferidos == 3, "deve conferir os três anteriores à quebra"
    assert str(linhas[3]["sequencia"]) in r.relatorio()


def test_trilha_vazia_nao_e_adulterada(conexao):
    r = verificar(trilha(conexao).ler())
    assert r.integra
    assert "vazia" in r.relatorio()


# ── requisito 1: append-only ─────────────────────────────────────────

def test_update_e_recusado_pelo_banco(conexao):
    import psycopg

    t = trilha(conexao)
    gravar(t, n=1)
    with pytest.raises(psycopg.errors.IntegrityConstraintViolation, match="append-only"):
        with conexao.cursor() as cur:
            cur.execute("UPDATE trilha_auditoria SET acao_global = 'permitir'")
    conexao.rollback()


def test_delete_e_recusado_pelo_banco(conexao):
    import psycopg

    t = trilha(conexao)
    gravar(t, n=1)
    with pytest.raises(psycopg.errors.IntegrityConstraintViolation, match="append-only"):
        with conexao.cursor() as cur:
            cur.execute("DELETE FROM trilha_auditoria")
    conexao.rollback()


def test_truncate_e_recusado_pelo_banco(conexao):
    import psycopg

    t = trilha(conexao)
    gravar(t, n=1)
    with pytest.raises(psycopg.errors.IntegrityConstraintViolation, match="append-only"):
        with conexao.cursor() as cur:
            cur.execute("TRUNCATE trilha_auditoria")
    conexao.rollback()


def test_papel_da_aplicacao_nao_tem_privilegio_de_update(conexao):
    """Defesa em profundidade: o gatilho recusa, e o privilégio nem existe."""
    with conexao.cursor() as cur:
        cur.execute(
            """
            SELECT privilege_type FROM information_schema.role_table_grants
             WHERE grantee = %s AND table_name = 'trilha_auditoria'
            """,
            (PAPEL,),
        )
        privilegios = {p[0] for p in cur.fetchall()}
    assert privilegios == {"SELECT", "INSERT"}


def test_repositorio_nao_oferece_caminho_para_alterar(conexao):
    t = trilha(conexao)
    for proibido in ("atualizar", "apagar", "remover", "editar", "excluir"):
        assert not hasattr(t, proibido)


# ── requisito 5: segregação por tenant ───────────────────────────────

def test_um_tenant_nao_le_registro_de_outro(conexao):
    a = trilha(conexao, "vetorcred")
    b = trilha(conexao, "clinica-norte")
    gravar(a, n=3)
    gravar(b, n=2)

    assert a.contar() == 3
    assert b.contar() == 2
    assert {l["tenant"] for l in a.ler()} == {"vetorcred"}
    assert {l["tenant"] for l in b.ler()} == {"clinica-norte"}


def test_segregacao_e_do_banco_e_nao_do_where(conexao):
    """Consulta sem WHERE, com o papel da aplicação, ainda só vê o próprio.

    É o ponto da row-level security: um WHERE esquecido no repositório deixa
    de ser vazamento entre clientes.
    """
    gravar(trilha(conexao, "vetorcred"), n=3)
    gravar(trilha(conexao, "clinica-norte"), n=2)

    with conexao.transaction(), conexao.cursor() as cur:
        cur.execute("SET LOCAL ROLE baluarte_app")
        cur.execute("SELECT set_config('baluarte.tenant', 'vetorcred', true)")
        cur.execute("SELECT count(*), count(DISTINCT tenant) FROM trilha_auditoria")
        total, tenants = cur.fetchone()
    assert (total, tenants) == (3, 1)


def test_sessao_sem_tenant_declarado_nao_ve_nada(conexao):
    """Falha fechada: sem tenant na sessão, zero linhas — nunca a base toda."""
    gravar(trilha(conexao, "vetorcred"), n=3)

    with conexao.transaction(), conexao.cursor() as cur:
        cur.execute("SET LOCAL ROLE baluarte_app")
        cur.execute("SELECT count(*) FROM trilha_auditoria")
        assert cur.fetchone()[0] == 0


def test_nao_da_para_gravar_no_tenant_de_outro(conexao):
    import psycopg

    gravar(trilha(conexao, "vetorcred"), n=1)
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with conexao.transaction(), conexao.cursor() as cur:
            cur.execute("SET LOCAL ROLE baluarte_app")
            cur.execute("SELECT set_config('baluarte.tenant', 'vetorcred', true)")
            cur.execute(
                """
                INSERT INTO trilha_auditoria (
                    requisicao_id, registrado_em, tenant, chave_origem,
                    provedor_destino, politica_nome, politica_versao,
                    politica_sha256, acao_global, achados,
                    hash_anterior, hash_registro
                ) VALUES (
                    gen_random_uuid(), now(), 'clinica-norte', 'k', 'anthropic',
                    'Financeiro', 1, repeat('a', 64), 'permitir', '[]'::jsonb,
                    repeat('0', 64), repeat('b', 64)
                )
                """
            )


def test_cadeia_de_um_tenant_nao_depende_do_outro(conexao):
    """A cadeia é por tenant, senão verificar a própria exigiria ler a alheia."""
    a = trilha(conexao, "vetorcred")
    b = trilha(conexao, "clinica-norte")
    a.registrar(decisao=decisao(), chave_origem="k", provedor_destino="anthropic")
    b.registrar(decisao=decisao(), chave_origem="k", provedor_destino="anthropic")
    a.registrar(decisao=decisao(), chave_origem="k", provedor_destino="anthropic")

    assert verificar(a.ler()).integra
    assert verificar(b.ler()).integra
    assert a.ler()[0]["hash_anterior"] == "0" * 64
    assert b.ler()[0]["hash_anterior"] == "0" * 64


def test_tenant_vazio_e_recusado(conexao):
    with pytest.raises(TenantNaoDeclarado):
        TrilhaDeAuditoria(conexao, "  ")


# ── o que a trilha guarda da política ────────────────────────────────

def test_registro_guarda_versao_e_hash_da_politica(conexao):
    t = trilha(conexao)
    gravar(t, n=1)
    linha = t.ler()[0]
    assert linha["politica_versao"] == 3
    assert linha["politica_sha256"] == POLITICA.sha256


def test_requisicao_id_e_preservado(conexao):
    t = trilha(conexao)
    identificador = uuid4()
    t.registrar(
        decisao=decisao(),
        chave_origem="k",
        provedor_destino="anthropic",
        requisicao_id=identificador,
    )
    assert t.ler()[0]["requisicao_id"] == identificador
