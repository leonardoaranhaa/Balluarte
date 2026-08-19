"""Compatibilidade literal: o SDK oficial da Anthropic, trocando só a URL base.

O requisito 1 da fase pede exatamente isto — "pegar código real que chama a API
da Anthropic, trocar só a URL base, confirmar que funciona sem nenhuma outra
alteração". A função `codigo_do_cliente` abaixo é código de cliente comum: ela
não sabe que o BALUARTE existe, não importa nada nosso, e o único parâmetro que
muda é `base_url`.

O teste roda contra **socket de verdade**, com o gateway e o dublê do provedor
em servidores HTTP reais. Testar por transporte em memória provaria que o app
ASGI responde; não provaria que o SDK, com o cliente HTTP dele e os cabeçalhos
dele, atravessa o gateway.
"""

import json
import socket
import threading
import time

import anthropic
import pytest
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from baluarte.analisador import montar_analisador
from baluarte.politica.catalogo import CatalogoDePoliticas
from baluarte.proxy.app import Gateway, criar_app
from baluarte.tokenizacao.cofre import CofreEmMemoria

from .test_proxy_integracao import CPF, POLITICA_YAML, _esperar, _porta_livre

RECEBIDO: list[dict] = []


# ── código de cliente, sem nenhuma consciência do BALUARTE ───────────

def codigo_do_cliente(base_url: str, chave: str, texto: str):
    """Uso normal do SDK. A única coisa que muda entre um caso e outro é a URL."""
    cliente = anthropic.Anthropic(api_key=chave, base_url=base_url)
    return cliente.messages.create(
        model="claude-opus-5",
        max_tokens=256,
        messages=[{"role": "user", "content": texto}],
    )


# ── servidores de verdade ────────────────────────────────────────────

def _subir(app, porta):
    config = uvicorn.Config(app, host="127.0.0.1", port=porta, log_level="error")
    servidor = uvicorn.Server(config)
    thread = threading.Thread(target=servidor.run, daemon=True)
    thread.start()
    _esperar(porta)
    return servidor, thread


@pytest.fixture(scope="module")
def provedor_real():
    async def mensagens(request):
        corpo = json.loads(await request.body())
        RECEBIDO.append({"corpo": corpo, "cabecalhos": dict(request.headers)})
        return JSONResponse(
            {
                "id": "msg_01",
                "type": "message",
                "role": "assistant",
                "model": corpo.get("model"),
                "content": [{"type": "text", "text": "Analisado com sucesso."}],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 12, "output_tokens": 7},
            }
        )

    porta = _porta_livre()
    servidor, thread = _subir(
        Starlette(routes=[Route("/v1/messages", mensagens, methods=["POST"])]), porta
    )
    yield f"http://127.0.0.1:{porta}"
    servidor.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="module")
def gateway_real(provedor_real, tmp_path_factory):
    pasta = tmp_path_factory.mktemp("politicas")
    (pasta / "v7.yaml").write_text(POLITICA_YAML, encoding="utf-8")
    gw = Gateway(
        analisador=montar_analisador(),
        catalogo=CatalogoDePoliticas.de_diretorio(pasta),
        cofre=CofreEmMemoria(),
        trilha_por_tenant=lambda t: None,
        upstream=provedor_real,
    )
    porta = _porta_livre()
    servidor, thread = _subir(criar_app(gw), porta)
    yield f"http://127.0.0.1:{porta}"
    servidor.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(autouse=True)
def limpar():
    RECEBIDO.clear()
    yield


# ── os testes ────────────────────────────────────────────────────────

def test_o_sdk_funciona_direto_contra_o_provedor(provedor_real):
    """Linha de base: sem o gateway no caminho, o SDK funciona."""
    resposta = codigo_do_cliente(provedor_real, "sk-ant-teste-7c41", "Bom dia.")
    assert resposta.content[0].text == "Analisado com sucesso."
    assert resposta.stop_reason == "end_turn"


def test_o_mesmo_codigo_funciona_trocando_so_a_url_base(gateway_real):
    """O requisito, literalmente.

    Mesma função, mesmos argumentos, só a URL muda. Se algo além da URL
    precisasse mudar, a promessa comercial do produto seria falsa.
    """
    resposta = codigo_do_cliente(gateway_real, "sk-ant-teste-7c41", "Bom dia.")
    assert resposta.content[0].text == "Analisado com sucesso."
    assert resposta.stop_reason == "end_turn"
    assert resposta.usage.input_tokens == 12
    assert resposta.type == "message"
    assert resposta.role == "assistant"


def test_o_sdk_nao_percebe_a_tokenizacao(gateway_real):
    """O cliente escreve CPF e o SDK devolve resposta normal; o provedor viu token."""
    resposta = codigo_do_cliente(
        gateway_real, "sk-ant-teste-7c41", f"Analise o cliente de CPF {CPF}."
    )
    assert resposta.content[0].text == "Analisado com sucesso."

    saiu = json.dumps(RECEBIDO[-1]["corpo"], ensure_ascii=False)
    assert CPF not in saiu
    assert "«BR_CPF:" in saiu


def test_o_erro_de_bloqueio_chega_como_erro_do_sdk(gateway_real):
    """Tratamento de erro do cliente também não precisa mudar.

    Quem já captura `anthropic.PermissionDeniedError` continua capturando; não
    é preciso conhecer nenhum tipo de erro do BALUARTE.
    """
    with pytest.raises(anthropic.PermissionDeniedError) as capturado:
        codigo_do_cliente(
            gateway_real,
            "sk-ant-teste-7c41",
            "Conta IBAN BR9700360305000010009795493P1 para transferência.",
        )
    assert "bloqueado pela política" in str(capturado.value)


def test_cabecalhos_do_baluarte_chegam_ao_cliente(gateway_real):
    cliente = anthropic.Anthropic(api_key="sk-ant-teste-7c41", base_url=gateway_real)
    bruta = cliente.messages.with_raw_response.create(
        model="claude-opus-5",
        max_tokens=64,
        messages=[{"role": "user", "content": f"CPF {CPF} em análise."}],
    )
    assert bruta.headers["x-baluarte-action"] == "tokenizar"
    assert "BR_CPF:1" in bruta.headers["x-baluarte-entities-detected"]
    assert bruta.headers["x-baluarte-request-id"]


def test_a_chave_do_cliente_atravessa_para_o_provedor(gateway_real):
    """O gateway não guarda a chave nem a substitui: ela passa.

    Na Fase 4, quando a chave do provedor passar a viver no BALUARTE, isto
    muda — e vai precisar de teste dizendo o contrário.
    """
    codigo_do_cliente(gateway_real, "sk-ant-teste-7c41", "Bom dia.")
    assert RECEBIDO[-1]["cabecalhos"].get("x-api-key") == "sk-ant-teste-7c41"


def test_cabecalho_de_versao_da_api_atravessa(gateway_real):
    codigo_do_cliente(gateway_real, "sk-ant-teste-7c41", "Bom dia.")
    assert RECEBIDO[-1]["cabecalhos"].get("anthropic-version")
