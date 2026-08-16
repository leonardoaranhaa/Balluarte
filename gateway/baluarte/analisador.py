"""Montagem do AnalyzerEngine do Presidio com os recognizers brasileiros.

Fábrica única, para não existirem dois analisadores configurados diferente em
lugares diferentes do código — a regra 1 do CLAUDE.md (mesma entrada, mesma
saída, sempre) começa a valer aqui, antes do motor de política.

Nada nesta camada decide o que fazer com um achado. Ela só diz o que achou e
onde. A decisão é do motor de política, na Fase 1.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from .reconhecedores.documentos_br import ReconhecedorCNPJ, ReconhecedorCPF

IDIOMA = "pt"
MODELO_SPACY = "pt_core_news_sm"


class ClassificadorIndisponivel(RuntimeError):
    """Erguido quando o analisador não pôde ser montado.

    Existe para o chamador não conseguir confundir "não achei dado pessoal"
    com "não consegui procurar". A regra 3 do CLAUDE.md (fail-closed) depende
    dessa distinção: sem classificador, a requisição é bloqueada, e um retorno
    vazio silencioso viraria liberação.
    """


def montar_analisador(idioma: str = IDIOMA, modelo: str = MODELO_SPACY) -> AnalyzerEngine:
    try:
        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": idioma, "model_name": modelo}],
            }
        )
        motor_nlp = provider.create_engine()
    except Exception as erro:  # modelo ausente, spaCy quebrado, disco cheio
        raise ClassificadorIndisponivel(
            f"não foi possível carregar o modelo {modelo!r} para {idioma!r}"
        ) from erro

    analisador = AnalyzerEngine(nlp_engine=motor_nlp, supported_languages=[idioma])
    analisador.registry.add_recognizer(ReconhecedorCPF())
    analisador.registry.add_recognizer(ReconhecedorCNPJ())
    return analisador
