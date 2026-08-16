"""Gravação e leitura da trilha, sempre no contexto de um tenant.

Toda operação passa por `SET LOCAL baluarte.tenant`, que é o que a política de
row-level security da migration 002 consulta. `LOCAL` e não `SESSION`: o valor
morre com a transação, então uma conexão devolvida ao pool não carrega o
tenant anterior para quem pegar ela depois — que seria o vazamento entre
clientes mais fácil de escrever e mais difícil de enxergar.

O repositório não tem método de alterar nem de apagar. Não é esquecimento: a
tabela é append-only, e oferecer o método faria o chamador acreditar que existe
o caminho.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from .registro import HASH_GENESE, Registro, registro_de_decisao


class TenantNaoDeclarado(RuntimeError):
    """Operação sem tenant. Nunca deve virar 'todos os tenants'."""


class TrilhaDeAuditoria:
    # Em produção a aplicação conecta direto como este papel. O parâmetro
    # existe porque em teste a conexão é do dono da tabela, e dono da tabela
    # com superusuário passa por cima de row-level security — o que faria o
    # teste de segregação passar sem a segregação existir.
    PAPEL_DA_APLICACAO = "baluarte_app"

    def __init__(self, conexao: psycopg.Connection, tenant: str, papel: str | None = None):
        if not tenant or not tenant.strip():
            raise TenantNaoDeclarado("tenant vazio")
        self.conexao = conexao
        self.tenant = tenant
        self.papel = papel

    def _fixar_tenant(self, cur) -> None:
        if self.papel:
            # Identificador não pode ser parâmetro ligado; o valor vem de
            # constante do código, nunca de entrada externa.
            cur.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(self.papel)))
        # SET LOCAL não aceita parâmetro ligado; set_config faz o mesmo com
        # valor parametrizado, sem interpolar string em SQL.
        cur.execute("SELECT set_config('baluarte.tenant', %s, true)", (self.tenant,))

    def _ultimo_hash(self, cur) -> tuple[int, str]:
        cur.execute(
            """
            SELECT sequencia, hash_registro
              FROM trilha_auditoria
             WHERE tenant = %s
             ORDER BY sequencia DESC
             LIMIT 1
            """,
            (self.tenant,),
        )
        linha = cur.fetchone()
        return (0, HASH_GENESE) if linha is None else (linha[0], linha[1])

    def registrar(
        self,
        *,
        decisao,
        chave_origem: str,
        provedor_destino: str,
        requisicao_id: UUID | None = None,
        registrado_em: datetime | None = None,
    ) -> Registro:
        requisicao_id = requisicao_id or uuid4()
        registrado_em = registrado_em or datetime.now(timezone.utc)

        with self.conexao.transaction(), self.conexao.cursor() as cur:
            self._fixar_tenant(cur)

            # O bloqueio serializa a leitura do último hash com a inserção do
            # próximo. Sem ele, duas requisições simultâneas do mesmo tenant
            # leem o mesmo `hash_anterior` e a cadeia se bifurca — e cadeia
            # bifurcada é indistinguível de cadeia adulterada na verificação.
            cur.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))", (f"trilha:{self.tenant}",)
            )
            _, hash_anterior = self._ultimo_hash(cur)

            cur.execute("SELECT nextval('trilha_auditoria_sequencia_seq')")
            sequencia = cur.fetchone()[0]

            registro = registro_de_decisao(
                sequencia=sequencia,
                requisicao_id=requisicao_id,
                registrado_em=registrado_em,
                tenant=self.tenant,
                chave_origem=chave_origem,
                provedor_destino=provedor_destino,
                decisao=decisao,
                hash_anterior=hash_anterior,
            )

            cur.execute(
                """
                INSERT INTO trilha_auditoria (
                    sequencia, requisicao_id, registrado_em, tenant,
                    chave_origem, provedor_destino,
                    politica_nome, politica_versao, politica_sha256,
                    acao_global, achados, hash_anterior, hash_registro
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    registro.sequencia,
                    registro.requisicao_id,
                    registro.registrado_em,
                    registro.tenant,
                    registro.chave_origem,
                    registro.provedor_destino,
                    registro.politica_nome,
                    registro.politica_versao,
                    registro.politica_sha256,
                    registro.acao_global,
                    Jsonb(registro.achados_canonicos),
                    registro.hash_anterior,
                    registro.hash_registro(),
                ),
            )

        return registro

    def ler(self, limite: int | None = None) -> list[dict]:
        with self.conexao.transaction(), self.conexao.cursor() as cur:
            self._fixar_tenant(cur)
            cur.execute(
                """
                SELECT sequencia, requisicao_id, registrado_em, tenant,
                       chave_origem, provedor_destino,
                       politica_nome, politica_versao, politica_sha256,
                       acao_global, achados, hash_anterior, hash_registro
                  FROM trilha_auditoria
                 ORDER BY sequencia
                """
                + (" LIMIT %s" if limite else ""),
                (limite,) if limite else (),
            )
            colunas = [d.name for d in cur.description]
            return [dict(zip(colunas, linha)) for linha in cur.fetchall()]

    def contar(self) -> int:
        with self.conexao.transaction(), self.conexao.cursor() as cur:
            self._fixar_tenant(cur)
            cur.execute("SELECT count(*) FROM trilha_auditoria")
            return cur.fetchone()[0]
