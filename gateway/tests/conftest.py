"""Infra de teste do Postgres.

Os testes que precisam de banco pulam com mensagem clara quando não há um, em
vez de falharem: quem roda a suíte sem Postgres precisa saber que não rodou a
Fase 2, e não achar que quebrou algo.
"""

import os

import pytest

DSN = os.environ.get(
    "BALUARTE_DSN_TESTE",
    "postgresql://baluarte@/baluarte_teste?host=/var/run/postgresql",
)


@pytest.fixture(scope="session")
def dsn():
    psycopg = pytest.importorskip("psycopg")
    try:
        with psycopg.connect(DSN, connect_timeout=3):
            pass
    except Exception as erro:
        pytest.skip(f"Postgres indisponível em {DSN}: {erro}")
    return DSN


@pytest.fixture()
def conexao(dsn):
    import psycopg

    from baluarte.auditoria.esquema import aplicar

    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            # Cada teste começa de uma trilha vazia. DELETE está bloqueado pelo
            # gatilho de propósito, então a limpeza derruba e recria — o que é
            # o comportamento correto: nem o teste tem caminho para apagar.
            cur.execute("DROP TABLE IF EXISTS trilha_auditoria CASCADE")
            cur.execute("DROP TABLE IF EXISTS migracoes CASCADE")
            cur.execute("DROP ROLE IF EXISTS baluarte_app")
        conn.commit()
        aplicar(conn, "migrations")
        with conn.cursor() as cur:
            # Só para o teste conseguir assumir o papel da aplicação: em
            # produção a conexão já é feita como baluarte_app.
            cur.execute("GRANT baluarte_app TO CURRENT_USER")
        conn.commit()
        yield conn
