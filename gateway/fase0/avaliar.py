"""Roda o conjunto da Fase 0 e reporta falso negativo, falso positivo e latência.

Uso:  .venv/bin/python -m fase0.avaliar

Sobre o mascaramento no relatório: os documentos deste corpus são sintéticos e
estão versionados, então imprimi-los não vazaria nada. Mesmo assim o relatório
mascara. A regra 2 do CLAUDE.md não abre exceção para ambiente de
desenvolvimento, e ferramenta que imprime valor em claro "só no teste" é
exatamente como o hábito se instala. O identificador do caso mais o prefixo e
o sufixo bastam para localizar qualquer falha no corpus.
"""

import statistics
import sys
import time
from collections import Counter, defaultdict

from baluarte.analisador import ClassificadorIndisponivel, montar_analisador
from fase0.corpus import CASOS, CNPJ, CPF

ENTIDADES_AVALIADAS = (CPF, CNPJ)
REPETICOES_LATENCIA = 5


def mascarar(valor: str) -> str:
    if len(valor) <= 6:
        return "*" * len(valor)
    return f"{valor[:3]}{'*' * (len(valor) - 5)}{valor[-2:]}"


def achados_por_entidade(analisador, texto: str) -> dict[str, list[str]]:
    encontrados = defaultdict(list)
    for r in analisador.analyze(text=texto, language="pt"):
        encontrados[r.entity_type].append(texto[r.start : r.end])
    return encontrados


def avaliar():
    try:
        analisador = montar_analisador()
    except ClassificadorIndisponivel as erro:
        print(f"FALHA: {erro}", file=sys.stderr)
        return 2

    # Primeira chamada carrega pipeline e cache do spaCy; medir isso junto
    # inflaria a p95 com um custo que só existe uma vez por processo.
    analisador.analyze(text="aquecimento", language="pt")

    vp = Counter()   # verdadeiro positivo
    fn = Counter()   # falso negativo — esperado e não achado
    fp = Counter()   # falso positivo — achado e não esperado
    por_categoria = defaultdict(lambda: Counter())
    falhas = []
    outros = Counter()
    latencias = []

    for caso in CASOS:
        for _ in range(REPETICOES_LATENCIA):
            inicio = time.perf_counter()
            encontrados = achados_por_entidade(analisador, caso.texto)
            latencias.append((time.perf_counter() - inicio) * 1000)

        for entidade, valores in encontrados.items():
            if entidade not in ENTIDADES_AVALIADAS:
                outros[entidade] += len(valores)

        for entidade in ENTIDADES_AVALIADAS:
            esperados = Counter(v for e, v in caso.esperado if e == entidade)
            obtidos = Counter(encontrados.get(entidade, []))

            acertos = esperados & obtidos
            perdidos = esperados - obtidos
            sobrando = obtidos - esperados

            vp[entidade] += sum(acertos.values())
            fn[entidade] += sum(perdidos.values())
            fp[entidade] += sum(sobrando.values())
            por_categoria[caso.categoria][f"{entidade}:vp"] += sum(acertos.values())
            por_categoria[caso.categoria][f"{entidade}:fn"] += sum(perdidos.values())
            por_categoria[caso.categoria][f"{entidade}:fp"] += sum(sobrando.values())

            for valor in perdidos.elements():
                falhas.append(("falso negativo", caso.id, entidade, mascarar(valor)))
            for valor in sobrando.elements():
                falhas.append(("falso positivo", caso.id, entidade, mascarar(valor)))

    _relatorio(vp, fn, fp, por_categoria, falhas, outros, latencias)

    criticas = sum(
        por_categoria[cat][f"{ent}:fn"]
        for cat in ("cpf_formatado", "cnpj_formatado")
        for ent in ENTIDADES_AVALIADAS
    )
    return 0 if criticas == 0 else 1


def _relatorio(vp, fn, fp, por_categoria, falhas, outros, latencias):
    print(f"\nFASE 0 — {len(CASOS)} casos, {REPETICOES_LATENCIA} repetições por caso\n")

    print("Por entidade")
    print(f"  {'entidade':<10} {'esperados':>9} {'VP':>4} {'FN':>4} {'FP':>4} "
          f"{'recall':>8} {'precisão':>9}")
    for entidade in ENTIDADES_AVALIADAS:
        esperados = vp[entidade] + fn[entidade]
        recall = vp[entidade] / esperados if esperados else 1.0
        precisao = vp[entidade] / (vp[entidade] + fp[entidade]) if (vp[entidade] + fp[entidade]) else 1.0
        print(f"  {entidade:<10} {esperados:>9} {vp[entidade]:>4} {fn[entidade]:>4} "
              f"{fp[entidade]:>4} {recall:>7.1%} {precisao:>8.1%}")

    print("\nPor categoria do corpus")
    for categoria in ("cpf_formatado", "cpf_cru", "cnpj_formatado", "cnpj_cru", "quase", "limpo"):
        c = por_categoria[categoria]
        v = c["BR_CPF:vp"] + c["BR_CNPJ:vp"]
        n = c["BR_CPF:fn"] + c["BR_CNPJ:fn"]
        p = c["BR_CPF:fp"] + c["BR_CNPJ:fp"]
        print(f"  {categoria:<16} VP={v:>3}  FN={n:>3}  FP={p:>3}")

    if falhas:
        print("\nFalhas")
        for tipo, caso_id, entidade, valor in falhas:
            print(f"  {tipo:<15} {caso_id:<12} {entidade:<8} {valor}")
    else:
        print("\nFalhas: nenhuma.")

    if outros:
        print("\nOutras entidades disparadas (fora do escopo da Fase 0)")
        for entidade, n in outros.most_common():
            print(f"  {entidade:<20} {n // REPETICOES_LATENCIA:>3} ocorrências")

    latencias.sort()
    p50 = statistics.median(latencias)
    p95 = latencias[int(len(latencias) * 0.95) - 1]
    print(f"\nLatência da classificação ({len(latencias)} medições)")
    print(f"  p50 {p50:>7.2f} ms")
    print(f"  p95 {p95:>7.2f} ms")
    print(f"  máx {latencias[-1]:>7.2f} ms")


if __name__ == "__main__":
    sys.exit(avaliar())
