"""Versões de uma política, e a consulta "qual valia em tal data".

A regra 5 do CLAUDE.md — política nunca é editada, só versionada — só tem
efeito prático se existir alguém guardando as versões e sabendo dizer qual
estava em vigor em cada momento. É este arquivo.

O catálogo recusa, no carregamento:

- duas versões com o mesmo número (não dá para saber qual valia);
- duas versões com a mesma data de vigência (empate sem desempate honesto);
- versão maior com vigência anterior à de uma versão menor, o que significaria
  que a política andou para trás no tempo;
- nomes diferentes no mesmo catálogo, que seria misturar duas políticas.

Todas essas recusas acontecem ao montar, nunca ao consultar. Consulta que
levanta exceção em tempo de requisição é exatamente o que não se quer num
caminho que precisa falhar fechado de forma previsível.
"""

from datetime import date
from pathlib import Path

from .carregador import carregar_arquivo
from .modelo import Politica, PoliticaInvalida


class SemPoliticaVigente(LookupError):
    """Consulta a uma data anterior à primeira versão.

    Não é o mesmo que "permitir". Antes da primeira política não havia regra
    nenhuma, e responder qualquer ação aqui seria inventar uma decisão que o
    cliente nunca tomou.
    """


class CatalogoDePoliticas:
    def __init__(self, versoes: list[Politica]):
        if not versoes:
            raise PoliticaInvalida("catálogo vazio")

        nomes = {p.nome for p in versoes}
        if len(nomes) > 1:
            raise PoliticaInvalida(
                f"catálogo com nomes diferentes: {', '.join(sorted(nomes))}"
            )

        numeros = [p.versao for p in versoes]
        if len(set(numeros)) != len(numeros):
            repetidos = sorted({v for v in numeros if numeros.count(v) > 1})
            raise PoliticaInvalida(
                f"versões repetidas: {', '.join(f'v{v}' for v in repetidos)}"
            )

        datas = [p.vigente_desde for p in versoes]
        if len(set(datas)) != len(datas):
            raise PoliticaInvalida("duas versões com a mesma data de vigência")

        ordenadas = tuple(sorted(versoes, key=lambda p: p.versao))
        for anterior, seguinte in zip(ordenadas, ordenadas[1:]):
            if seguinte.vigente_desde <= anterior.vigente_desde:
                raise PoliticaInvalida(
                    f"v{seguinte.versao} entra em vigor em "
                    f"{seguinte.vigente_desde.isoformat()}, antes da v{anterior.versao} "
                    f"({anterior.vigente_desde.isoformat()}): a política andaria para trás"
                )

        self.nome = ordenadas[0].nome
        self._por_versao = ordenadas
        self._por_data = tuple(sorted(versoes, key=lambda p: p.vigente_desde))

    @classmethod
    def de_diretorio(cls, caminho: str | Path, padrao: str = "*.yaml") -> "CatalogoDePoliticas":
        caminho = Path(caminho)
        arquivos = sorted(caminho.glob(padrao))
        if not arquivos:
            raise PoliticaInvalida(f"nenhuma política em {caminho} com padrão {padrao!r}")
        return cls([carregar_arquivo(a) for a in arquivos])

    @property
    def versoes(self) -> tuple[Politica, ...]:
        return self._por_versao

    def versao(self, numero: int) -> Politica:
        for p in self._por_versao:
            if p.versao == numero:
                return p
        raise LookupError(f"{self.nome} não tem versão {numero}")

    def vigente_em(self, quando: date) -> Politica:
        """A versão em vigor na data. Vigência inclui o próprio dia de início.

        Percorre do mais recente para o mais antigo e devolve a primeira cuja
        vigência já começou.
        """
        for politica in reversed(self._por_data):
            if politica.vigente_desde <= quando:
                return politica
        primeira = self._por_data[0]
        raise SemPoliticaVigente(
            f"em {quando.isoformat()} não havia política {self.nome!r} vigente; "
            f"a primeira versão só entra em {primeira.vigente_desde.isoformat()}"
        )
