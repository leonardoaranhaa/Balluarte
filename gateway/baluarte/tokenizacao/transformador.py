"""Aplica ao texto a decisão que o motor de política tomou.

O transformador não decide nada. Ele recebe os achados já resolvidos e a
decisão por entidade, e executa. Separado do motor de propósito: o motor
precisa ser auditável sem que ninguém rode texto por ele, e o transformador
precisa mexer em texto, que é justamente o que o motor não pode fazer.

Substituições são aplicadas **da direita para a esquerda**. Da esquerda para a
direita, a primeira troca desloca todos os deslocamentos seguintes, e o
segundo achado é recortado no lugar errado — erro que produz texto plausível e
por isso passa despercebido em revisão.
"""

from dataclasses import dataclass

from ..politica.acoes import Acao

MASCARA = "▮"
TAMANHO_DA_MASCARA = 6


@dataclass(frozen=True)
class Transformacao:
    texto: str
    tokens_criados: dict[str, str]
    bloqueada: bool
    entidade_bloqueadora: str | None = None


def _mascarar(entidade: str) -> str:
    """Máscara com o tipo, não só tarja.

    `▮▮▮▮▮▮` sozinho tira do modelo a informação de que ali havia um CPF, e o
    modelo passa a responder sobre um texto truncado. Dizendo o tipo, a
    instrução continua legível e o valor continua fora.
    """
    return f"[{entidade}:{MASCARA * TAMANHO_DA_MASCARA}]"


def transformar(texto: str, achados, decisao, cofre, tenant: str) -> Transformacao:
    acao_por_entidade = {d.entidade: d.acao for d in decisao.por_entidade}

    bloqueadoras = [a for a in achados if acao_por_entidade.get(a.entidade) is Acao.BLOQUEAR]
    if bloqueadoras:
        # Bloqueio interrompe antes de transformar qualquer coisa: não faz
        # sentido gastar entrada de cofre numa requisição que não vai sair.
        return Transformacao(
            texto="",
            tokens_criados={},
            bloqueada=True,
            entidade_bloqueadora=sorted(a.entidade for a in bloqueadoras)[0],
        )

    tokens: dict[str, str] = {}
    resultado = texto
    for achado in sorted(achados, key=lambda a: a.inicio, reverse=True):
        acao = acao_por_entidade.get(achado.entidade)
        if acao is None or acao is Acao.PERMITIR:
            continue

        original = texto[achado.inicio : achado.fim]
        if acao is Acao.TOKENIZAR:
            substituto = cofre.tokenizar(tenant, achado.entidade, original)
            tokens[substituto] = achado.entidade
        elif acao is Acao.MASCARAR:
            substituto = _mascarar(achado.entidade)
        else:
            continue

        resultado = resultado[: achado.inicio] + substituto + resultado[achado.fim :]

    return Transformacao(texto=resultado, tokens_criados=tokens, bloqueada=False)


def destokenizar(texto: str, cofre, tenant: str) -> str:
    """Devolve os valores originais no texto da resposta.

    Token que o cofre não conhece fica como está. Modelos inventam token
    plausível; substituir por um valor qualquer seria pior que devolver o
    token, porque produziria dado errado com cara de certo.
    """
    import re

    from .cofre import ABERTURA, FECHAMENTO

    padrao = re.compile(
        re.escape(ABERTURA) + r"([A-Z_]+):([0-9a-f]+)" + re.escape(FECHAMENTO)
    )

    def trocar(casamento):
        try:
            return cofre.destokenizar(tenant, casamento.group(0))
        except KeyError:
            return casamento.group(0)

    return padrao.sub(trocar, texto)
