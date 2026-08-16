"""Recognizers de CPF e CNPJ para o Presidio.

O Presidio já traz recognizers brasileiros? Traz um de CPF, mas ele valida só
o formato. Estes aqui rejeitam o que não fecha no dígito verificador, que é a
diferença entre "onze dígitos" e "um CPF".

Sobre os lookarounds do regex: sem eles, o padrão de onze dígitos casa com um
pedaço de qualquer número maior — um CNPJ sem máscara vira um falso CPF
interno. A borda exige que a vizinhança não continue o número.

À direita a borda não pode ser um simples `(?![\\d.\\-/])`. Ponto final de frase
é separador nessa lista, então "CPF: 028.446.391-43." deixava de casar — e
documento no fim da frase é a forma mais comum de todas. A borda correta
recusa dígito colado, e recusa separador **seguido de dígito**, que é o caso
que interessa: `12345678900.50` continua sendo um decimal, não um CPF.
"""

from presidio_analyzer import Pattern, PatternRecognizer

from .digito_verificador import cnpj_valido, cpf_valido

# Score do padrão antes da validação. O valor final quem decide é o
# validate_result: DV correto sobe para 1.0, DV errado zera o achado.
_SCORE_PADRAO = 0.4

_BORDA_ESQ = r"(?<![\d.\-/])"
_BORDA_DIR = r"(?!\d)(?![.\-/]\d)"


class ReconhecedorCPF(PatternRecognizer):
    ENTIDADE = "BR_CPF"

    def __init__(self):
        super().__init__(
            supported_entity=self.ENTIDADE,
            supported_language="pt",
            name="ReconhecedorCPF",
            patterns=[
                Pattern(
                    name="cpf_formatado",
                    regex=_BORDA_ESQ + r"\d{3}\.\d{3}\.\d{3}-\d{2}" + _BORDA_DIR,
                    score=_SCORE_PADRAO,
                ),
                Pattern(
                    name="cpf_sem_formatacao",
                    regex=_BORDA_ESQ + r"\d{11}" + _BORDA_DIR,
                    score=_SCORE_PADRAO,
                ),
            ],
            context=["cpf", "documento", "titular", "portador", "inscrição"],
        )

    def validate_result(self, pattern_text: str):
        # True eleva o score a 1.0; False zera e o Presidio descarta o achado.
        # Nunca devolver None aqui: seria aceitar o número por formato, que é
        # exatamente o que estes recognizers existem para não fazer.
        return cpf_valido(pattern_text)


class ReconhecedorCNPJ(PatternRecognizer):
    ENTIDADE = "BR_CNPJ"

    def __init__(self):
        super().__init__(
            supported_entity=self.ENTIDADE,
            supported_language="pt",
            name="ReconhecedorCNPJ",
            patterns=[
                Pattern(
                    name="cnpj_formatado",
                    regex=_BORDA_ESQ + r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}" + _BORDA_DIR,
                    score=_SCORE_PADRAO,
                ),
                Pattern(
                    name="cnpj_sem_formatacao",
                    regex=_BORDA_ESQ + r"\d{14}" + _BORDA_DIR,
                    score=_SCORE_PADRAO,
                ),
            ],
            context=["cnpj", "empresa", "razão social", "matriz", "filial"],
        )

    def validate_result(self, pattern_text: str):
        return cnpj_valido(pattern_text)
