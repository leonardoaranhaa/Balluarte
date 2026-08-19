"""Resolução de achados sobrepostos.

A Fase 1 deixou isto pendente com um caso concreto: num prompt com o e-mail
`marina@vetorcred.com.br`, o Presidio devolve três achados encaixados —

    EMAIL_ADDRESS  score=1.00  'marina@vetorcred.com.br'
    ORGANIZATION   score=0.85  'marina@vetorcred.com.br'
    URL            score=0.50  'vetorcred.com.br'

É o mesmo dado contado três vezes. Passar assim ao motor de política infla a
contagem da trilha e cria entidade sem regra do nada, que sob fail-closed
bloqueia a requisição. O motor está certo em decidir sobre o que recebe; quem
tem que entregar um conjunto limpo é a classificação.

A resolução é determinística — mesma entrada, mesma saída — porque tudo daqui
para a frente depende disso, incluindo o hash da trilha.

Critério, nesta ordem:

1. **Trecho maior vence.** Ele descreve o dado inteiro; o menor é pedaço.
2. **Empatando em tamanho, maior score vence.** É o classificador dizendo de
   qual ele tem mais certeza.
3. **Empatando nos dois, ordem alfabética da entidade.** Critério arbitrário, e
   assumido como tal: o que importa é ser estável, não ser justo. Empate real
   entre duas entidades do mesmo tamanho e mesma confiança não tem resposta
   melhor, e sortear quebraria o determinismo.

Achado que apenas encosta em outro, sem invadir, não é sobreposição: dois CPFs
separados por vírgula continuam sendo dois achados.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Achado:
    entidade: str
    inicio: int
    fim: int
    score: float

    @property
    def tamanho(self) -> int:
        return self.fim - self.inicio

    def sobrepoe(self, outro: "Achado") -> bool:
        return self.inicio < outro.fim and outro.inicio < self.fim


def _prioridade(a: Achado) -> tuple:
    # Negativos para que `sorted` crescente coloque o vencedor primeiro.
    return (-a.tamanho, -a.score, a.entidade, a.inicio)


def resolver(achados) -> list[Achado]:
    """Devolve os achados sem sobreposição, ordenados por posição."""
    vencedores: list[Achado] = []
    for achado in sorted(achados, key=_prioridade):
        if not any(achado.sobrepoe(v) for v in vencedores):
            vencedores.append(achado)
    return sorted(vencedores, key=lambda a: (a.inicio, a.entidade))


def de_resultados_do_presidio(resultados) -> list[Achado]:
    return [
        Achado(entidade=r.entity_type, inicio=r.start, fim=r.end, score=r.score)
        for r in resultados
    ]
