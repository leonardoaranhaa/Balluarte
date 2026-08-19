"""Estruturas de política. Imutáveis por construção.

`frozen=True` não é preciosismo: a regra 5 do CLAUDE.md diz que política nunca
é editada, só versionada. Se o objeto em memória puder ser alterado, a regra
vira convenção — e convenção é o que se quebra às três da manhã consertando
produção. Aqui a tentativa levanta exceção.

O `sha256` da política é o que amarra uma decisão ao texto exato que a
produziu. Dizer "estava vigente a versão 2" é fraco se a versão 2 pôde ser
reescrita depois; dizer "estava vigente a versão 2, sha256 9f2c…" é
verificável contra o arquivo versionado.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import date

from .acoes import Acao


class PoliticaInvalida(ValueError):
    """Política que não pôde ser carregada.

    Carregar é o momento de recusar: uma política malformada não pode virar
    decisão degradada em tempo de requisição.
    """


@dataclass(frozen=True)
class Regra:
    entidade: str
    acao: Acao
    base_normativa: str

    def __post_init__(self):
        if not self.entidade.strip():
            raise PoliticaInvalida("regra sem entidade")
        # Regra 4 do CLAUDE.md: toda regra carrega base normativa. Sem ela a
        # decisão não é evidência de conformidade, é configuração técnica.
        if not self.base_normativa.strip():
            raise PoliticaInvalida(
                f"regra de {self.entidade} sem base normativa"
            )


@dataclass(frozen=True)
class Politica:
    nome: str
    versao: int
    vigente_desde: date
    regras: tuple[Regra, ...]
    acao_sem_regra: Acao
    base_sem_regra: str
    acao_sem_deteccao: Acao
    base_sem_deteccao: str
    sha256: str = field(default="", compare=False)

    def __post_init__(self):
        if self.versao < 1:
            raise PoliticaInvalida(f"versão precisa ser >= 1, veio {self.versao}")
        if not self.regras:
            raise PoliticaInvalida(f"política {self.nome!r} sem nenhuma regra")

    def regras_de(self, entidade: str) -> tuple[Regra, ...]:
        """Todas as regras que casam com a entidade, em ordem de documento.

        Devolve todas, e não a primeira: quando duas regras justificam a mesma
        decisão, a explicação honesta cita as duas. Guardar só uma faria a
        trilha parecer mais simples do que a política é.
        """
        return tuple(r for r in self.regras if r.entidade == entidade)

    @property
    def identificacao(self) -> str:
        return f"{self.nome} v{self.versao} ({self.sha256[:12]})"


def hash_do_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
