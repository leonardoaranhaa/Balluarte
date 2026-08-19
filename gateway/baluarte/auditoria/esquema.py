"""Aplicação de migrations. Versionadas, em ordem, uma vez cada.

A convenção do CLAUDE.md é "migrations versionadas, nunca alteração manual de
schema". Para isso valer, precisa existir quem registre o que já rodou — senão
"nunca manual" vira "manual quando der ruim".

Cada migration roda dentro da sua própria transação. Se a 002 falhar, a 001
fica aplicada e registrada, e a próxima execução retoma da 002. Rodar tudo
numa transação só pareceria mais seguro e deixaria o banco num estado que o
registro não descreve.
"""

import hashlib
from pathlib import Path

import psycopg

TABELA_DE_CONTROLE = """
CREATE TABLE IF NOT EXISTS migracoes (
    nome        TEXT PRIMARY KEY,
    sha256      CHAR(64) NOT NULL,
    aplicada_em TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


class MigrationAlterada(RuntimeError):
    """Uma migration já aplicada mudou de conteúdo.

    Editar migration aplicada é a forma silenciosa de o esquema de produção
    divergir do que o repositório diz. O sha256 de cada arquivo fica guardado
    justamente para essa divergência não passar despercebida.
    """


def aplicar(conexao: psycopg.Connection, diretorio: str | Path = "migrations") -> list[str]:
    diretorio = Path(diretorio)
    arquivos = sorted(diretorio.glob("*.sql"))
    if not arquivos:
        raise FileNotFoundError(f"nenhuma migration em {diretorio}")

    with conexao.cursor() as cur:
        cur.execute(TABELA_DE_CONTROLE)
        conexao.commit()
        cur.execute("SELECT nome, sha256 FROM migracoes")
        aplicadas = dict(cur.fetchall())

    novas = []
    for arquivo in arquivos:
        sql = arquivo.read_text(encoding="utf-8")
        digest = hashlib.sha256(sql.encode("utf-8")).hexdigest()

        if arquivo.name in aplicadas:
            if aplicadas[arquivo.name] != digest:
                raise MigrationAlterada(
                    f"{arquivo.name} já foi aplicada com outro conteúdo. "
                    "Migration aplicada não se edita: crie a próxima."
                )
            continue

        with conexao.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "INSERT INTO migracoes (nome, sha256) VALUES (%s, %s)",
                (arquivo.name, digest),
            )
        conexao.commit()
        novas.append(arquivo.name)

    return novas
