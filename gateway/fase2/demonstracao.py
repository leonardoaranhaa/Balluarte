"""Verificação de integridade funcionando: cadeia íntegra passa, adulterada falha.

Uso:  .venv/bin/python -m fase2.demonstracao

Precisa de um Postgres. Por padrão usa o socket local; para apontar para outro:

    BALUARTE_DSN_TESTE=postgresql://... .venv/bin/python -m fase2.demonstracao

A demonstração cria a trilha do zero, grava seis requisições de dois tenants,
verifica, adultera um registro por fora do gatilho e verifica de novo.
"""

import os
import sys
from datetime import date, datetime, timedelta, timezone

import psycopg

from baluarte.auditoria.esquema import aplicar
from baluarte.auditoria.repositorio import TrilhaDeAuditoria
from baluarte.auditoria.verificacao import verificar
from baluarte.politica.avaliador import avaliar
from baluarte.politica.catalogo import CatalogoDePoliticas

DSN = os.environ.get(
    "BALUARTE_DSN_TESTE",
    "postgresql://baluarte@/baluarte_teste?host=/var/run/postgresql",
)

QUANDO = date(2026, 8, 16)
REQUISICOES = [
    (["BR_CPF", "BR_CPF", "EMAIL_ADDRESS"], "svc-credito/••7c41", "anthropic"),
    (["BR_CPF"], "svc-credito/••7c41", "anthropic"),
    ([], "svc-relatorios/••1a09", "openai"),
    (["BR_CNPJ", "PHONE_NUMBER"], "svc-cobranca/••3f77", "anthropic"),
]


def titulo(texto: str) -> None:
    print()
    print("=" * 74)
    print(texto)
    print("=" * 74)


def main() -> int:
    try:
        conexao = psycopg.connect(DSN, connect_timeout=3)
    except Exception as erro:
        print(f"Postgres indisponível em {DSN}\n  {erro}", file=sys.stderr)
        return 2

    with conexao:
        with conexao.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS trilha_auditoria CASCADE")
            cur.execute("DROP TABLE IF EXISTS migracoes CASCADE")
            cur.execute("DROP ROLE IF EXISTS baluarte_app")
        conexao.commit()

        titulo("MIGRATIONS")
        for nome in aplicar(conexao, "migrations"):
            print(f"  aplicada  {nome}")
        with conexao.cursor() as cur:
            cur.execute("GRANT baluarte_app TO CURRENT_USER")
        conexao.commit()

        politica = CatalogoDePoliticas.de_diretorio("politicas/financeiro").vigente_em(QUANDO)
        papel = TrilhaDeAuditoria.PAPEL_DA_APLICACAO
        vetorcred = TrilhaDeAuditoria(conexao, "vetorcred", papel=papel)
        clinica = TrilhaDeAuditoria(conexao, "clinica-norte", papel=papel)

        titulo("GRAVANDO REQUISIÇÕES")
        instante = datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc)
        for i, (entidades, chave, provedor) in enumerate(REQUISICOES):
            decisao = avaliar(entidades, politica, QUANDO)
            r = vetorcred.registrar(
                decisao=decisao,
                chave_origem=chave,
                provedor_destino=provedor,
                registrado_em=instante + timedelta(minutes=i * 7),
            )
            achados = ", ".join(f"{a.entidade}×{a.quantidade}" for a in r.achados) or "—"
            print(f"  vetorcred      seq {r.sequencia}  {r.acao_global:<10} {achados}")

        for i in range(2):
            decisao = avaliar(["BR_CPF"], politica, QUANDO)
            r = clinica.registrar(
                decisao=decisao,
                chave_origem="svc-prontuario/••9b12",
                provedor_destino="anthropic",
                registrado_em=instante + timedelta(minutes=i * 11),
            )
            print(f"  clinica-norte  seq {r.sequencia}  {r.acao_global:<10} "
                  f"BR_CPF×{r.achados[0].quantidade}")

        titulo("O QUE FICOU GRAVADO  (tipo e quantidade, nunca valor)")
        linha = vetorcred.ler()[0]
        for campo, valor in linha.items():
            print(f"  {campo:<18} {valor}")

        titulo("SEGREGAÇÃO POR TENANT")
        print(f"  vetorcred enxerga      {vetorcred.contar()} registros")
        print(f"  clinica-norte enxerga  {clinica.contar()} registros")
        with conexao.transaction(), conexao.cursor() as cur:
            cur.execute("SET LOCAL ROLE baluarte_app")
            cur.execute("SELECT count(*) FROM trilha_auditoria")
            print(f"  sessão sem tenant      {cur.fetchone()[0]} registros "
                  "(falha fechada: zero, nunca a base toda)")

        titulo("VERIFICAÇÃO — CADEIA ÍNTEGRA")
        print(verificar(vetorcred.ler()).relatorio())

        titulo("ADULTERANDO UM REGISTRO POR FORA DO GATILHO")
        with conexao.cursor() as cur:
            cur.execute("SELECT sequencia, chave_origem FROM trilha_auditoria "
                        "WHERE tenant='vetorcred' ORDER BY sequencia OFFSET 2 LIMIT 1")
            alvo, chave_antes = cur.fetchone()
            print("  UPDATE recusado pelo gatilho? ", end="")
            try:
                cur.execute("UPDATE trilha_auditoria SET chave_origem='outra' "
                            "WHERE sequencia=%s", (alvo,))
                print("não — o gatilho falhou")
            except psycopg.errors.IntegrityConstraintViolation as erro:
                print("sim")
                print(f"    {str(erro).splitlines()[0]}")
        conexao.rollback()

        print(f"  Desligando o gatilho como dono da tabela e alterando o registro {alvo}.")
        print("  É o cenário que o encadeamento existe para cobrir: quem tem")
        print("  privilégio para desligar o gatilho ainda não consegue esconder.")
        chave_depois = "svc-comprometido/••0000"
        with conexao.cursor() as cur:
            cur.execute("ALTER TABLE trilha_auditoria DISABLE TRIGGER trilha_sem_update")
            cur.execute("UPDATE trilha_auditoria SET chave_origem=%s WHERE sequencia=%s",
                        (chave_depois, alvo))
            cur.execute("ALTER TABLE trilha_auditoria ENABLE TRIGGER trilha_sem_update")
        conexao.commit()

        # Guarda contra demonstração mentirosa: se a alteração não mudou nada,
        # a verificação passar não prova coisa alguma. Aconteceu ao escrever
        # esta demo — o campo escolhido já tinha o valor novo.
        if chave_antes == chave_depois:
            print("  ERRO: a alteração foi no-op, a demonstração não vale.", file=sys.stderr)
            return 3
        print(f"    chave_origem: {chave_antes!r} → {chave_depois!r}")

        titulo("VERIFICAÇÃO — CADEIA ADULTERADA")
        print(verificar(vetorcred.ler()).relatorio())

        titulo("A TRILHA DO OUTRO TENANT NÃO FOI AFETADA")
        print(verificar(clinica.ler()).relatorio())
        print()
        print("  A cadeia é por tenant. Adulterar a trilha de um cliente não")
        print("  invalida a do outro, e verificar a própria não exige ler a alheia.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
