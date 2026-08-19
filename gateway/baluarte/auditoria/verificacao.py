"""Verificação de integridade: percorre a cadeia e aponta onde ela quebrou.

Recalcula o hash de cada registro a partir dos campos gravados e confere duas
coisas: que o hash bate com o que está na linha, e que o `hash_anterior` bate
com o hash do registro anterior. A primeira pega alteração de conteúdo; a
segunda pega remoção e reordenação, que não mudam nenhum registro
individualmente.

O resultado diz **onde** quebrou, não só que quebrou. Numa discussão sobre
adulteração, "a trilha está corrompida" vale pouco; "os registros 1 a 417
conferem, o 418 tem conteúdo alterado, e do 419 em diante a cadeia segue
íntegra a partir do 418" é o que sustenta uma conclusão.
"""

from dataclasses import dataclass, field
from datetime import timezone
from uuid import UUID

from .registro import HASH_GENESE, AchadoRegistrado, Registro


@dataclass(frozen=True)
class Quebra:
    sequencia: int
    tipo: str
    detalhe: str

    def __str__(self) -> str:
        return f"registro {self.sequencia}: {self.tipo} — {self.detalhe}"


@dataclass
class Resultado:
    total: int = 0
    conferidos: int = 0
    quebras: list[Quebra] = field(default_factory=list)

    @property
    def integra(self) -> bool:
        return not self.quebras

    def relatorio(self) -> str:
        if self.total == 0:
            return "Trilha vazia: nada a verificar."
        if self.integra:
            return (
                f"Cadeia íntegra: {self.total} registros conferidos, "
                "cada hash recalculado e cada elo conferido com o anterior."
            )
        linhas = [
            f"Cadeia ADULTERADA: {len(self.quebras)} quebra(s) em {self.total} registros.",
            f"Conferidos até a primeira quebra: {self.conferidos}.",
        ]
        linhas += [f"  {q}" for q in self.quebras]
        return "\n".join(linhas)


def _registro_da_linha(linha: dict) -> Registro:
    return Registro(
        sequencia=linha["sequencia"],
        requisicao_id=linha["requisicao_id"]
        if isinstance(linha["requisicao_id"], UUID)
        else UUID(str(linha["requisicao_id"])),
        registrado_em=linha["registrado_em"].astimezone(timezone.utc),
        tenant=linha["tenant"],
        chave_origem=linha["chave_origem"],
        provedor_destino=linha["provedor_destino"],
        politica_nome=linha["politica_nome"],
        politica_versao=linha["politica_versao"],
        politica_sha256=linha["politica_sha256"],
        acao_global=linha["acao_global"],
        achados=tuple(
            AchadoRegistrado(
                entidade=a["entidade"], quantidade=a["quantidade"], acao=a["acao"]
            )
            for a in linha["achados"]
        ),
        hash_anterior=linha["hash_anterior"],
    )


def verificar(linhas) -> Resultado:
    resultado = Resultado()
    esperado_anterior = HASH_GENESE
    primeira_quebra = False

    linhas = sorted(linhas, key=lambda l: l["sequencia"])
    resultado.total = len(linhas)

    for linha in linhas:
        registro = _registro_da_linha(linha)
        sequencia = registro.sequencia

        recalculado = registro.hash_registro()
        gravado = linha["hash_registro"]

        if registro.hash_anterior != esperado_anterior:
            primeira_quebra = True
            resultado.quebras.append(
                Quebra(
                    sequencia=sequencia,
                    tipo="elo rompido",
                    detalhe=(
                        f"aponta para {registro.hash_anterior[:12]}…, mas o registro "
                        f"anterior tem hash {esperado_anterior[:12]}…. "
                        "Registro removido, reordenado ou inserido no meio."
                    ),
                )
            )

        if recalculado != gravado:
            primeira_quebra = True
            resultado.quebras.append(
                Quebra(
                    sequencia=sequencia,
                    tipo="conteúdo alterado",
                    detalhe=(
                        f"hash gravado {gravado[:12]}…, recalculado "
                        f"{recalculado[:12]}…. Algum campo mudou depois da gravação."
                    ),
                )
            )

        if not primeira_quebra:
            resultado.conferidos += 1

        # Segue a partir do que está gravado, e não do recalculado: assim uma
        # única alteração aparece como uma quebra, e não como todas as
        # seguintes também quebradas.
        esperado_anterior = gravado

    return resultado
