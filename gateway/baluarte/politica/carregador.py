"""Leitura de política em YAML.

Tudo que pode ser recusado é recusado aqui, no carregamento, e não na
avaliação. Uma política que chega incompleta ao motor vira decisão degradada
em tempo de requisição — que é o modo de falha que a regra 3 do CLAUDE.md
manda evitar. Melhor o gateway não subir do que subir decidindo por omissão.

Nenhum campo tem valor implícito. Em especial os dois padrões: o que fazer com
entidade detectada que a política não menciona, e o que fazer quando nada foi
detectado. Deixar qualquer um deles com default no código seria decidir pelo
encarregado de dados do cliente sem ele saber — e ainda por cima sem base
normativa, o que quebra a regra 4.
"""

from datetime import date, datetime
from pathlib import Path

import yaml

from .acoes import Acao
from .modelo import Politica, PoliticaInvalida, Regra, hash_do_texto

CAMPOS_OBRIGATORIOS = ("nome", "versao", "vigente_desde", "regras", "padrao")
PADROES_OBRIGATORIOS = ("entidade_sem_regra", "nenhuma_deteccao")


def _acao(valor, onde: str) -> Acao:
    try:
        return Acao(str(valor).strip().lower())
    except ValueError:
        validas = ", ".join(a.value for a in Acao)
        raise PoliticaInvalida(
            f"{onde}: ação {valor!r} não existe. Válidas: {validas}"
        ) from None


def _data(valor, onde: str) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        raise PoliticaInvalida(
            f"{onde}: data {valor!r} não está em AAAA-MM-DD"
        ) from None


def _bloco_padrao(bruto: dict, chave: str) -> tuple[Acao, str]:
    bloco = bruto.get(chave)
    if not isinstance(bloco, dict):
        raise PoliticaInvalida(f"padrao.{chave} ausente ou malformado")
    if "acao" not in bloco or "base_normativa" not in bloco:
        raise PoliticaInvalida(
            f"padrao.{chave} precisa de 'acao' e 'base_normativa'"
        )
    base = str(bloco["base_normativa"]).strip()
    if not base:
        raise PoliticaInvalida(f"padrao.{chave} sem base normativa")
    return _acao(bloco["acao"], f"padrao.{chave}"), base


def carregar_texto(texto: str, origem: str = "<texto>") -> Politica:
    try:
        bruto = yaml.safe_load(texto)
    except yaml.YAMLError as erro:
        raise PoliticaInvalida(f"{origem}: YAML inválido — {erro}") from erro

    if not isinstance(bruto, dict):
        raise PoliticaInvalida(f"{origem}: a política precisa ser um mapa YAML")

    faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in bruto]
    if faltando:
        raise PoliticaInvalida(f"{origem}: faltam campos {', '.join(faltando)}")

    padrao = bruto["padrao"]
    if not isinstance(padrao, dict):
        raise PoliticaInvalida(f"{origem}: 'padrao' precisa ser um mapa")
    ausentes = [c for c in PADROES_OBRIGATORIOS if c not in padrao]
    if ausentes:
        raise PoliticaInvalida(
            f"{origem}: falta declarar padrao.{' e padrao.'.join(ausentes)}. "
            "Nenhum dos dois tem valor implícito — quem decide é a política."
        )

    regras_brutas = bruto["regras"]
    if not isinstance(regras_brutas, list) or not regras_brutas:
        raise PoliticaInvalida(f"{origem}: 'regras' precisa ser uma lista não vazia")

    regras = []
    for i, r in enumerate(regras_brutas, start=1):
        if not isinstance(r, dict):
            raise PoliticaInvalida(f"{origem}: regra {i} não é um mapa")
        faltam = [c for c in ("entidade", "acao", "base_normativa") if c not in r]
        if faltam:
            raise PoliticaInvalida(
                f"{origem}: regra {i} sem {', '.join(faltam)}"
            )
        regras.append(
            Regra(
                entidade=str(r["entidade"]).strip(),
                acao=_acao(r["acao"], f"{origem}: regra {i}"),
                base_normativa=str(r["base_normativa"]).strip(),
            )
        )

    acao_sem_regra, base_sem_regra = _bloco_padrao(padrao, "entidade_sem_regra")
    acao_sem_deteccao, base_sem_deteccao = _bloco_padrao(padrao, "nenhuma_deteccao")

    try:
        versao = int(bruto["versao"])
    except (TypeError, ValueError):
        raise PoliticaInvalida(
            f"{origem}: versão {bruto['versao']!r} não é inteiro"
        ) from None

    return Politica(
        nome=str(bruto["nome"]).strip(),
        versao=versao,
        vigente_desde=_data(bruto["vigente_desde"], f"{origem}: vigente_desde"),
        regras=tuple(regras),
        acao_sem_regra=acao_sem_regra,
        base_sem_regra=base_sem_regra,
        acao_sem_deteccao=acao_sem_deteccao,
        base_sem_deteccao=base_sem_deteccao,
        # O hash é do texto do arquivo, não da estrutura carregada: é o que
        # permite conferir uma decisão antiga contra o que está versionado.
        sha256=hash_do_texto(texto),
    )


def carregar_arquivo(caminho: str | Path) -> Politica:
    caminho = Path(caminho)
    try:
        texto = caminho.read_text(encoding="utf-8")
    except OSError as erro:
        raise PoliticaInvalida(f"não foi possível ler {caminho}: {erro}") from erro
    return carregar_texto(texto, origem=caminho.name)
