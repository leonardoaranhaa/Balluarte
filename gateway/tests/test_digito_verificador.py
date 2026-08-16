import pytest

from baluarte.reconhecedores.digito_verificador import cnpj_valido, cpf_valido

# Valores públicos de teste, os mesmos que circulam na documentação técnica
# brasileira. Não pertencem a ninguém.
CPFS_VALIDOS = ["111.444.777-35", "11144477735", "529.982.247-25", "52998224725"]
CNPJS_VALIDOS = ["11.222.333/0001-81", "11222333000181"]


@pytest.mark.parametrize("valor", CPFS_VALIDOS)
def test_cpf_valido_aceita(valor):
    assert cpf_valido(valor)


@pytest.mark.parametrize("valor", CNPJS_VALIDOS)
def test_cnpj_valido_aceita(valor):
    assert cnpj_valido(valor)


@pytest.mark.parametrize("valor", ["111.444.777-34", "11144477700", "529.982.247-20"])
def test_cpf_rejeita_dv_errado(valor):
    assert not cpf_valido(valor)


@pytest.mark.parametrize("valor", ["11.222.333/0001-82", "11222333000100"])
def test_cnpj_rejeita_dv_errado(valor):
    assert not cnpj_valido(valor)


@pytest.mark.parametrize("digito", "0123456789")
def test_cpf_rejeita_sequencia_repetida(digito):
    """A aritmética do DV aprova as onze sequências repetidas; a Receita não.

    Sem este corte, campo de formulário preenchido com 00000000000 passaria
    por documento válido.
    """
    assert not cpf_valido(digito * 11)


@pytest.mark.parametrize("digito", "0123456789")
def test_cnpj_rejeita_sequencia_repetida(digito):
    assert not cnpj_valido(digito * 14)


@pytest.mark.parametrize("valor", ["", "123", "1114447773", "111444777356"])
def test_cpf_rejeita_comprimento_errado(valor):
    assert not cpf_valido(valor)


def test_cpf_ignora_pontuacao_arbitraria():
    assert cpf_valido("111 444 777 35")
    assert cpf_valido("111-444-777.35")


def test_cnpj_nao_e_cpf_e_vice_versa():
    assert not cpf_valido("11222333000181")
    assert not cnpj_valido("11144477735")
