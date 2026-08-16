"""As quatro ações de política, e a ordem de restritividade entre elas.

Esta ordem é a regra de desempate do motor inteiro. O requisito diz "onde
houver ambiguidade, a ação mais restritiva vence", e isso só é decidível se
"mais restritiva" tiver uma definição escrita, e não intuição de quem lê.

A definição adotada: **restritiva é a ação que deixa menos dado pessoal
disponível — no que sai e no que fica guardado.**

    permitir  <  tokenizar  <  mascarar  <  bloquear

O único degrau que costuma surpreender é `mascarar` acima de `tokenizar`.
Pelo que sai da empresa os dois se equivalem: o provedor não vê o valor em
nenhum dos dois. A diferença está no que fica para trás. Tokenizar é
reversível por construção — existe um cofre com o mapeamento, e cofre é
superfície de ataque e objeto de pedido de titular. Mascarar destrói o valor:
não há o que vazar depois, e não há o que devolver.

Ou seja, tokenizar é melhor para a utilidade do modelo e pior para o risco
residual. Como a ordem aqui é de proteção, e não de conveniência, mascarar
fica acima.

Esta escolha é discutível e é de produto, não de engenharia. Está isolada
neste arquivo de propósito: mudar a ordem é mudar uma linha, e o teste de
precedência falha alto se alguém mudar sem querer.
"""

from enum import Enum


class Acao(Enum):
    PERMITIR = "permitir"
    TOKENIZAR = "tokenizar"
    MASCARAR = "mascarar"
    BLOQUEAR = "bloquear"

    @property
    def restritividade(self) -> int:
        return _ORDEM[self]

    def __lt__(self, outra: "Acao") -> bool:
        if not isinstance(outra, Acao):
            return NotImplemented
        return self.restritividade < outra.restritividade

    def __str__(self) -> str:
        return self.value


_ORDEM: dict[Acao, int] = {
    Acao.PERMITIR: 0,
    Acao.TOKENIZAR: 1,
    Acao.MASCARAR: 2,
    Acao.BLOQUEAR: 3,
}


def mais_restritiva(acoes) -> Acao:
    """A ação vencedora de um conjunto. Sem ações, permitir.

    Chamar com conjunto vazio significa "nada a decidir", e nada a decidir
    não é motivo para restringir — o fail-closed do produto está em outro
    ponto, na entidade sem regra e no classificador indisponível, não aqui.
    """
    acoes = list(acoes)
    if not acoes:
        return Acao.PERMITIR
    return max(acoes, key=lambda a: a.restritividade)
