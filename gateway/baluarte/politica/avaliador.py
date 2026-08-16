"""O motor. Determinístico, sem LLM, sem relógio.

Duas decisões de projeto sustentam o determinismo, e as duas são restrições
sobre o que esta função **não** pode fazer:

1. **Não lê o relógio.** A data de avaliação entra como argumento. Se o motor
   consultasse `date.today()`, reavaliar a mesma requisição amanhã poderia dar
   outra resposta, e a pergunta "por que isso foi bloqueado em março?" ficaria
   sem resposta reconstituível.

2. **Não recebe texto, recebe tipos.** A entrada é a lista de entidades
   detectadas, não o conteúdo. Além de manter a regra 2 do CLAUDE.md, isso
   torna a decisão auditável sem que o auditor precise ver dado de ninguém.

Precedência, na ordem em que é aplicada:

    a) Toda regra cuja entidade casa é coletada — todas, não a primeira.
    b) Vence a ação mais restritiva entre elas (ver `acoes.py`).
    c) As justificativas citadas são as das regras que pediram a ação
       vencedora. Regra que pedia coisa menos restritiva não entra: ela não
       justifica a decisão tomada.
    d) Entidade detectada sem nenhuma regra cai no padrão declarado pela
       política para esse caso, com a base normativa desse padrão.
    e) A decisão global é a mais restritiva entre as decisões por entidade.
       Sem entidade nenhuma, vale o padrão de "nenhuma detecção".
"""

from collections import Counter
from datetime import date
from typing import Iterable

from .acoes import Acao, mais_restritiva
from .decisao import Decisao, DecisaoEntidade, Justificativa
from .modelo import Politica


def avaliar(
    entidades_detectadas: Iterable[str],
    politica: Politica,
    avaliada_em: date,
) -> Decisao:
    # Counter fixa a contagem; sorted fixa a ordem. Sem os dois, duas execuções
    # com a mesma entrada podem devolver a mesma informação em ordem diferente,
    # e "mesma saída" deixa de ser verificável por igualdade.
    contagem = Counter(e for e in entidades_detectadas)

    por_entidade = []
    for entidade in sorted(contagem):
        regras = politica.regras_de(entidade)

        if regras:
            vencedora = mais_restritiva(r.acao for r in regras)
            justificativas = tuple(
                Justificativa(
                    origem=f"regra de {r.entidade} → {r.acao}",
                    base_normativa=r.base_normativa,
                )
                for r in regras
                if r.acao is vencedora
            )
        else:
            vencedora = politica.acao_sem_regra
            justificativas = (
                Justificativa(
                    origem=f"padrão para entidade sem regra → {vencedora}",
                    base_normativa=politica.base_sem_regra,
                ),
            )

        por_entidade.append(
            DecisaoEntidade(
                entidade=entidade,
                acao=vencedora,
                ocorrencias=contagem[entidade],
                justificativas=justificativas,
            )
        )

    if por_entidade:
        global_ = mais_restritiva(d.acao for d in por_entidade)
    else:
        global_ = politica.acao_sem_deteccao

    return Decisao(
        acao=global_,
        politica_nome=politica.nome,
        politica_versao=politica.versao,
        politica_sha256=politica.sha256,
        politica_vigente_desde=politica.vigente_desde,
        avaliada_em=avaliada_em,
        por_entidade=tuple(por_entidade),
    )


def avaliar_com_catalogo(entidades_detectadas, catalogo, avaliada_em: date) -> Decisao:
    """Atalho para o caminho real: descobrir a política vigente e avaliar.

    Existe para que o chamador não precise fazer a busca por data na mão — é
    onde se erraria, usando a versão mais recente em vez da vigente na data.
    """
    return avaliar(entidades_detectadas, catalogo.vigente_em(avaliada_em), avaliada_em)


__all__ = ["avaliar", "avaliar_com_catalogo", "Acao"]
