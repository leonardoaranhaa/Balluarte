"""O resultado de uma avaliação, em forma explicável.

O requisito de explicabilidade não é "logar o motivo". É conseguir responder,
meses depois, por que uma requisição foi bloqueada — com a norma na mão. Para
isso a decisão carrega, além da ação: quais regras pesaram, a base normativa
de cada uma, e a identificação exata da política vigente naquela data,
incluindo o sha256 do arquivo.

O que a decisão **não** carrega é valor de dado pessoal. Ela fala de tipo de
entidade e de quantidade, nunca de conteúdo. Isso é a regra 2 do CLAUDE.md
valendo por formato da estrutura, e não por cuidado de quem for serializar.
"""

from dataclasses import dataclass
from datetime import date

from .acoes import Acao


@dataclass(frozen=True)
class Justificativa:
    origem: str
    base_normativa: str

    def __str__(self) -> str:
        return f"{self.origem} — {self.base_normativa}"


@dataclass(frozen=True)
class DecisaoEntidade:
    entidade: str
    acao: Acao
    ocorrencias: int
    justificativas: tuple[Justificativa, ...]


@dataclass(frozen=True)
class Decisao:
    acao: Acao
    politica_nome: str
    politica_versao: int
    politica_sha256: str
    politica_vigente_desde: date
    avaliada_em: date
    por_entidade: tuple[DecisaoEntidade, ...]

    @property
    def bloqueada(self) -> bool:
        return self.acao is Acao.BLOQUEAR

    @property
    def identificacao_da_politica(self) -> str:
        return f"{self.politica_nome} v{self.politica_versao} ({self.politica_sha256[:12]})"

    def explicacao(self) -> str:
        linhas = [
            f"Decisão: {self.acao}",
            f"Política vigente em {self.avaliada_em.isoformat()}: "
            f"{self.identificacao_da_politica}, em vigor desde "
            f"{self.politica_vigente_desde.isoformat()}",
        ]
        if not self.por_entidade:
            linhas.append("Nenhum dado pessoal detectado.")
        for d in self.por_entidade:
            plural = "ocorrência" if d.ocorrencias == 1 else "ocorrências"
            linhas.append(f"  {d.entidade} ({d.ocorrencias} {plural}) → {d.acao}")
            for j in d.justificativas:
                linhas.append(f"      {j}")
        return "\n".join(linhas)
