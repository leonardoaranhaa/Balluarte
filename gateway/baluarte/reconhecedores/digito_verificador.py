"""Validação de dígito verificador de CPF e CNPJ.

Regex sozinho reconhece formato, não documento. Qualquer sequência de onze
dígitos casa com a máscara de CPF — número de telefone com DDD, código de
protocolo, matrícula. O dígito verificador é o que separa documento de
coincidência, e é aritmética fechada: não depende de contexto, de modelo nem
de lista externa, então cabe na regra 1 do CLAUDE.md sem ressalva.
"""

CPF_DIGITOS = 11
CNPJ_DIGITOS = 14


def _digito(numeros: list[int], pesos: list[int]) -> int:
    resto = sum(n * p for n, p in zip(numeros, pesos)) % 11
    return 0 if resto < 2 else 11 - resto


def _somente_digitos(valor: str) -> str:
    return "".join(c for c in valor if c.isdigit())


def _repetido(digitos: str) -> bool:
    """000.000.000-00 e os outros dez passam na aritmética do DV.

    São inválidos por convenção da Receita, não por cálculo. Sem este corte o
    validador aprova onze zeros, que é exatamente o tipo de sequência que
    aparece em campo de formulário mal preenchido.
    """
    return digitos == digitos[0] * len(digitos)


def cpf_valido(valor: str) -> bool:
    d = _somente_digitos(valor)
    if len(d) != CPF_DIGITOS or _repetido(d):
        return False

    numeros = [int(c) for c in d]
    dv1 = _digito(numeros[:9], list(range(10, 1, -1)))
    dv2 = _digito(numeros[:10], list(range(11, 1, -1)))
    return numeros[9] == dv1 and numeros[10] == dv2


def cnpj_valido(valor: str) -> bool:
    d = _somente_digitos(valor)
    if len(d) != CNPJ_DIGITOS or _repetido(d):
        return False

    numeros = [int(c) for c in d]
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    dv1 = _digito(numeros[:12], pesos1)
    dv2 = _digito(numeros[:13], pesos2)
    return numeros[12] == dv1 and numeros[13] == dv2
