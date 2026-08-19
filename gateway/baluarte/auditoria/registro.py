"""O registro da trilha e o hash que o encadeia.

O hash precisa ser recomputável a partir da linha gravada, anos depois, por
quem não tem o código que gravou. Por isso a serialização canônica é explícita
e chata: campo por campo, em ordem fixa, com formato fixo. Nada de `repr`,
nada de `json.dumps` sobre dicionário de Python, nada que dependa de versão de
biblioteca — qualquer uma dessas escolhas transforma "verificar a integridade"
em "torcer para a serialização não ter mudado".

Os achados entram como tipo, quantidade e ação. Não existe campo para valor,
nem aqui nem no esquema. A regra 2 do CLAUDE.md fica sendo propriedade da
estrutura.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

# Primeiro elo da cadeia. Sessenta e quatro zeros é convenção legível: quem
# abre a trilha vê onde ela começa sem precisar de documentação.
HASH_GENESE = "0" * 64


@dataclass(frozen=True)
class AchadoRegistrado:
    entidade: str
    quantidade: int
    acao: str

    def como_dicionario(self) -> dict:
        return {
            "entidade": self.entidade,
            "quantidade": self.quantidade,
            "acao": self.acao,
        }


@dataclass(frozen=True)
class Registro:
    sequencia: int
    requisicao_id: UUID
    registrado_em: datetime
    tenant: str
    chave_origem: str
    provedor_destino: str
    politica_nome: str
    politica_versao: int
    politica_sha256: str
    acao_global: str
    achados: tuple[AchadoRegistrado, ...]
    hash_anterior: str

    def __post_init__(self):
        if self.registrado_em.tzinfo is None:
            raise ValueError("registrado_em precisa ser consciente de fuso (UTC)")

    @property
    def achados_canonicos(self) -> list[dict]:
        """Ordenado por entidade: a ordem de detecção não pode mudar o hash."""
        return [
            a.como_dicionario()
            for a in sorted(self.achados, key=lambda a: (a.entidade, a.acao))
        ]

    def texto_canonico(self) -> str:
        """A representação exata sobre a qual o hash é calculado.

        Uma linha por campo, `chave=valor`, em ordem fixa. Escolhido em vez de
        JSON porque é conferível a olho: quem audita consegue montar a mesma
        string no terminal e rodar sha256sum, sem escrever código.
        """
        instante = self.registrado_em.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%f+00:00"
        )
        campos = [
            ("sequencia", str(self.sequencia)),
            ("requisicao_id", str(self.requisicao_id)),
            ("registrado_em", instante),
            ("tenant", self.tenant),
            ("chave_origem", self.chave_origem),
            ("provedor_destino", self.provedor_destino),
            ("politica_nome", self.politica_nome),
            ("politica_versao", str(self.politica_versao)),
            ("politica_sha256", self.politica_sha256),
            ("acao_global", self.acao_global),
            (
                "achados",
                json.dumps(
                    self.achados_canonicos,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
            ("hash_anterior", self.hash_anterior),
        ]
        return "\n".join(f"{chave}={valor}" for chave, valor in campos)

    def hash_registro(self) -> str:
        return hashlib.sha256(self.texto_canonico().encode("utf-8")).hexdigest()


def registro_de_decisao(
    *,
    sequencia: int,
    requisicao_id: UUID,
    registrado_em: datetime,
    tenant: str,
    chave_origem: str,
    provedor_destino: str,
    decisao,
    hash_anterior: str,
) -> Registro:
    """Constrói o registro a partir de uma Decisao do motor de política.

    A conversão é aqui, num lugar só, para que não exista um segundo caminho
    onde alguém monte o registro à mão e acabe incluindo um campo a mais.
    """
    return Registro(
        sequencia=sequencia,
        requisicao_id=requisicao_id,
        registrado_em=registrado_em,
        tenant=tenant,
        chave_origem=chave_origem,
        provedor_destino=provedor_destino,
        politica_nome=decisao.politica_nome,
        politica_versao=decisao.politica_versao,
        politica_sha256=decisao.politica_sha256,
        acao_global=str(decisao.acao),
        achados=tuple(
            AchadoRegistrado(
                entidade=d.entidade,
                quantidade=d.ocorrencias,
                acao=str(d.acao),
            )
            for d in decisao.por_entidade
        ),
        hash_anterior=hash_anterior,
    )
