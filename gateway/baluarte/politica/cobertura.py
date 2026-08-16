"""Cobertura: a política menciona tudo que o classificador sabe achar?

A pergunta parece burocrática e não é. O padrão `entidade_sem_regra` costuma
ser `bloquear`, porque ausência de regra não é autorização. A consequência é
que **uma entidade esquecida na política bloqueia toda requisição em que ela
aparecer** — e o cliente vai atribuir isso a defeito do gateway, não a lacuna
da própria política.

Os dois lados estão certos sozinhos e errados juntos. A saída não é afrouxar
o padrão: é conferir a cobertura antes de a política entrar em vigor, que é o
que esta função faz.

Isto não é validação de política — uma política pode ser válida e incompleta.
É conferência de encaixe entre duas coisas que evoluem separadas: o conjunto
de entidades que o classificador emite e o conjunto que a política decide.
"""

from dataclasses import dataclass

from .modelo import Politica


@dataclass(frozen=True)
class Cobertura:
    entidades_do_classificador: tuple[str, ...]
    cobertas: tuple[str, ...]
    descobertas: tuple[str, ...]
    regras_sem_uso: tuple[str, ...]

    @property
    def completa(self) -> bool:
        return not self.descobertas

    def relatorio(self) -> str:
        linhas = []
        if self.descobertas:
            linhas.append(
                "Entidades que o classificador emite e a política não menciona "
                f"({len(self.descobertas)}):"
            )
            linhas += [f"  {e}" for e in self.descobertas]
            linhas.append(
                "  → cada uma destas cai no padrão de entidade sem regra."
            )
        else:
            linhas.append("Cobertura completa: toda entidade emitida tem regra.")

        if self.regras_sem_uso:
            linhas.append("")
            linhas.append(
                "Regras para entidades que este classificador não emite "
                f"({len(self.regras_sem_uso)}):"
            )
            linhas += [f"  {e}" for e in self.regras_sem_uso]
            linhas.append(
                "  → não é erro. Pode ser entidade de outro perfil, ou recognizer "
                "ainda não construído."
            )
        return "\n".join(linhas)


def conferir(politica: Politica, entidades_do_classificador) -> Cobertura:
    emitidas = tuple(sorted(set(entidades_do_classificador)))
    decididas = {r.entidade for r in politica.regras}
    return Cobertura(
        entidades_do_classificador=emitidas,
        cobertas=tuple(e for e in emitidas if e in decididas),
        descobertas=tuple(e for e in emitidas if e not in decididas),
        regras_sem_uso=tuple(sorted(decididas - set(emitidas))),
    )


def entidades_que_o_analisador_emite(analisador) -> tuple[str, ...]:
    """O conjunto declarado pelos recognizers registrados.

    Vem do registro, não de uma lista escrita à mão: lista à mão envelhece no
    primeiro recognizer novo, e envelhecer aqui significa voltar a bloquear
    requisição por lacuna que ninguém viu.
    """
    entidades: set[str] = set()
    for recognizer in analisador.registry.recognizers:
        entidades.update(recognizer.supported_entities)
    return tuple(sorted(entidades))
