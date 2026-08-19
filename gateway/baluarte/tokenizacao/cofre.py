"""Tokenização reversível, com cofre isolado por tenant.

O token precisa de duas propriedades que puxam em direções opostas:

**Determinístico** — o mesmo valor sempre gera o mesmo token, senão o modelo
não consegue raciocinar sobre ele. "«CPF:7f3a» tem saldo devedor e «CPF:7f3a»
pediu renegociação" é uma frase útil; com token aleatório a cada ocorrência,
vira duas pessoas diferentes.

**Não invertível sem o cofre** — o token não pode carregar o valor. Determinismo
ingênuo (hash do valor, sem chave) é invertível por força bruta em qualquer
espaço pequeno: CPF tem 10^11 possibilidades, o que uma máquina comum percorre.
Por isso o token é HMAC com chave por tenant, e não hash puro.

A consequência: dois tenants com o mesmo CPF geram tokens diferentes. Isso é o
que se quer — token de um cliente não diz nada sobre a base do outro, e
comprometer uma chave não abre as outras.

O valor guardado é cifrado com AES-GCM, não só o token derivado. O cofre em
claro seria um banco de PII com índice, que é exatamente a bomba jurídica que
a regra 2 do CLAUDE.md descreve.
"""

import hashlib
import hmac
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Prefixo do token no texto. Delimitadores «» são escolhidos por não
# aparecerem em prompt corporativo brasileiro e por sobreviverem à
# tokenização do modelo como bloco reconhecível.
ABERTURA = "«"
FECHAMENTO = "»"

# Comprimento do sufixo em hex. Quatro bytes dão 4 bilhões de valores por
# tipo e por tenant; colisão exigiria bilhões de valores distintos do mesmo
# tipo no mesmo cliente. O cofre detecta colisão na gravação de qualquer forma.
DIGITOS_DO_TOKEN = 8


class ColisaoDeToken(RuntimeError):
    """Dois valores distintos derivaram o mesmo token no mesmo tenant.

    Improvável, e ainda assim tratado: silenciar uma colisão significa
    destokenizar a resposta com o valor de outra pessoa.
    """


class ValorDesconhecido(KeyError):
    """Token que não existe no cofre deste tenant.

    Acontece legitimamente quando o modelo inventa um token na resposta, o que
    modelos fazem. A destokenização deixa o texto como está — inventar um valor
    seria pior que devolver o token.
    """


@dataclass(frozen=True)
class ChaveDeTenant:
    """As duas chaves de um tenant. Nunca compartilhadas entre tenants.

    Chaves separadas para derivar e para cifrar: quem obtiver a chave de
    derivação consegue confirmar se um valor suspeito está na base (ataque de
    confirmação), mas não consegue ler o cofre.
    """

    tenant: str
    derivacao: bytes
    cifragem: bytes

    @classmethod
    def gerar(cls, tenant: str) -> "ChaveDeTenant":
        return cls(tenant=tenant, derivacao=os.urandom(32), cifragem=AESGCM.generate_key(256))


class CofreEmMemoria:
    """Cofre de mapeamento. Implementação de referência, em memória.

    A Fase 3 usa esta; a persistente é da Fase 4, quando houver decisão sobre
    retenção e sobre onde a chave mestra vive. A interface é a mesma para que a
    troca não toque no transformador.
    """

    def __init__(self):
        self._chaves: dict[str, ChaveDeTenant] = {}
        self._por_token: dict[tuple[str, str], bytes] = {}
        self._por_valor: dict[tuple[str, str], str] = {}

    def chave_de(self, tenant: str) -> ChaveDeTenant:
        if tenant not in self._chaves:
            self._chaves[tenant] = ChaveDeTenant.gerar(tenant)
        return self._chaves[tenant]

    def _derivar(self, tenant: str, entidade: str, valor: str) -> str:
        chave = self.chave_de(tenant)
        # A entidade entra na derivação para que o mesmo texto classificado de
        # dois jeitos não colapse no mesmo token.
        mensagem = f"{entidade}\x00{valor}".encode("utf-8")
        digest = hmac.new(chave.derivacao, mensagem, hashlib.sha256).hexdigest()
        return f"{ABERTURA}{entidade}:{digest[:DIGITOS_DO_TOKEN]}{FECHAMENTO}"

    def tokenizar(self, tenant: str, entidade: str, valor: str) -> str:
        chave_indice = (tenant, valor)
        if chave_indice in self._por_valor:
            return self._por_valor[chave_indice]

        token = self._derivar(tenant, entidade, valor)
        existente = self._por_token.get((tenant, token))
        if existente is not None and self._decifrar(tenant, existente) != valor:
            raise ColisaoDeToken(f"token {token} já mapeia outro valor no tenant {tenant!r}")

        self._por_token[(tenant, token)] = self._cifrar(tenant, valor)
        self._por_valor[chave_indice] = token
        return token

    def destokenizar(self, tenant: str, token: str) -> str:
        cifrado = self._por_token.get((tenant, token))
        if cifrado is None:
            raise ValorDesconhecido(token)
        return self._decifrar(tenant, cifrado)

    def _cifrar(self, tenant: str, valor: str) -> bytes:
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.chave_de(tenant).cifragem)
        # O tenant entra como dado autenticado: um registro movido de cofre
        # falha a decifragem em vez de decifrar no lugar errado.
        return nonce + aesgcm.encrypt(nonce, valor.encode("utf-8"), tenant.encode("utf-8"))

    def _decifrar(self, tenant: str, cifrado: bytes) -> str:
        aesgcm = AESGCM(self.chave_de(tenant).cifragem)
        return aesgcm.decrypt(cifrado[:12], cifrado[12:], tenant.encode("utf-8")).decode("utf-8")

    def tamanho(self, tenant: str) -> int:
        return sum(1 for t, _ in self._por_token if t == tenant)
