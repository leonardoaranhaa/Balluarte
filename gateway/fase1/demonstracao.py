"""Uma requisição inteira, do texto à decisão explicada.

Uso:  .venv/bin/python -m fase1.demonstracao

Liga a classificação da Fase 0 ao motor da Fase 1 para mostrar o caminho
completo. Não é proxy: nada é enviado a lugar nenhum, nada é transformado e
nada é gravado. É a demonstração que o critério de entrega da fase pede.

O texto de exemplo é fictício e o CPF é o valor público de teste da
documentação técnica brasileira.
"""

from datetime import date

from baluarte.analisador import montar_analisador
from baluarte.politica.avaliador import avaliar_com_catalogo
from baluarte.politica.catalogo import CatalogoDePoliticas
from baluarte.politica.cobertura import conferir, entidades_que_o_analisador_emite

PROMPT = (
    "Analise a proposta de renegociação para Marina Alves, "
    "CPF 111.444.777-35, e-mail marina@vetorcred.com.br, telefone "
    "11987654321, da empresa 11.222.333/0001-81, com saldo devedor de "
    "R$ 84.200 em 14 parcelas."
)

# As duas datas existem para mostrar o mesmo prompt sendo julgado por versões
# diferentes da política — que é o requisito de consulta histórica.
DATAS = (date(2026, 8, 15), date(2026, 9, 15))


def entidades_detectadas(analisador, texto: str) -> list[str]:
    """Só os tipos. O motor de política nunca vê conteúdo."""
    return [r.entity_type for r in analisador.analyze(text=texto, language="pt")]


def main() -> int:
    analisador = montar_analisador()
    catalogo = CatalogoDePoliticas.de_diretorio("politicas/financeiro")

    print("=" * 74)
    print("REQUISIÇÃO QUE ENTRA")
    print("=" * 74)
    print(PROMPT)

    achados = entidades_detectadas(analisador, PROMPT)
    print()
    print("=" * 74)
    print("O QUE A CLASSIFICAÇÃO ACHOU  (tipo e contagem, nunca o valor)")
    print("=" * 74)
    for entidade in sorted(set(achados)):
        print(f"  {entidade:<18} {achados.count(entidade)}")

    print()
    print("=" * 74)
    print("POLÍTICAS DISPONÍVEIS")
    print("=" * 74)
    for p in catalogo.versoes:
        print(f"  v{p.versao}  vigente desde {p.vigente_desde.isoformat()}  "
              f"sha256 {p.sha256[:12]}…  {len(p.regras)} regras")

    for quando in DATAS:
        decisao = avaliar_com_catalogo(achados, catalogo, quando)
        print()
        print("=" * 74)
        print(f"DECISÃO PARA UMA REQUISIÇÃO DE {quando.isoformat()}")
        print("=" * 74)
        print(decisao.explicacao())

    print()
    print("=" * 74)
    print("POR QUE A REQUISIÇÃO FOI BLOQUEADA NAS DUAS DATAS")
    print("=" * 74)
    cobertura = conferir(catalogo.versao(2), entidades_que_o_analisador_emite(analisador))
    print(cobertura.relatorio())
    print()
    print("  Das três entidades sem regra que apareceram neste prompt, duas são")
    print("  sobreposição: ORGANIZATION e URL casaram dentro do próprio e-mail,")
    print("  que já tinha sido detectado como EMAIL_ADDRESS. Não são dados novos.")

    print()
    print("=" * 74)
    print("POR QUE AS DUAS DECISÕES DIFEREM ENTRE SI")
    print("=" * 74)
    v1, v2 = catalogo.versao(1), catalogo.versao(2)
    for entidade in sorted({r.entidade for r in v1.regras} | {r.entidade for r in v2.regras}):
        antes = sorted(str(r.acao) for r in v1.regras_de(entidade)) or ["—"]
        depois = sorted(str(r.acao) for r in v2.regras_de(entidade)) or ["—"]
        marca = "  " if antes == depois else "→ "
        print(f"  {marca}{entidade:<18} v1: {', '.join(antes):<22} v2: {', '.join(depois)}")

    print()
    print("A mesma requisição, reavaliada hoje com data de agosto, continua")
    print("devolvendo a decisão de agosto. É o que torna possível responder")
    print('"por que isso foi bloqueado em março?" meses depois.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
