# Fase 3 — integração do proxy

**Data:** 16 de agosto de 2026
**Critério de saída:** troca de URL base sem alteração de código, e p95 medido.
**Resultado:** atingido. 183 testes. p95 do overhead: **52 ms** no pior cenário,
contra meta de 300 ms.

Reproduzir:

```bash
cd gateway
.venv/bin/python -m pytest tests -q      # 183 testes
.venv/bin/python -m fase3.latencia       # medição, não estimativa
```

---

## 1. Compatibilidade literal: o SDK oficial, trocando só a URL

`tests/test_proxy_sdk_anthropic.py` tem uma função que é código de cliente
comum — não importa nada do BALUARTE, não sabe que ele existe:

```python
def codigo_do_cliente(base_url, chave, texto):
    cliente = anthropic.Anthropic(api_key=chave, base_url=base_url)
    return cliente.messages.create(
        model="claude-opus-5", max_tokens=256,
        messages=[{"role": "user", "content": texto}],
    )
```

O mesmo código roda contra o provedor e contra o gateway, **em sockets de
verdade**, e o resultado é idêntico. Transporte em memória provaria que o app
ASGI responde; não provaria que o SDK, com o cliente HTTP dele e os cabeçalhos
dele, atravessa.

Coberto: formato de resposta, formato de erro (`anthropic.PermissionDeniedError`
para bloqueio — quem já trata continua tratando), cabeçalho `anthropic-version`,
e campos desconhecidos.

### A decisão de não usar a tradução do LiteLLM neste ponto

O `CLAUDE.md` manda tratar o LiteLLM como infraestrutura, e a Fase 0 confirmou
que ele resolve bem o ponto de interceptação. Mas a regra 6 diz que
compatibilidade de API é sagrada, e traduzir o corpo para um formato
intermediário e de volta introduz justamente o lugar onde um campo novo da
Anthropic se perde.

Então o corpo é repassado **como veio**, sem reserialização, com só os trechos
de texto substituídos. Há teste enviando `parametro_que_ainda_nao_existe` e
confirmando que chega intacto ao provedor — é o que sustenta "troca só a URL
base" quando a Anthropic acrescentar um parâmetro que não existia quando este
código foi escrito.

O LiteLLM continua no projeto: guardrail da Fase 0, e roteamento multi-provedor
quando ele entrar.

---

## 2. Tokenização reversível

**Determinístico e não invertível ao mesmo tempo.** O mesmo valor sempre gera o
mesmo token, senão o modelo não consegue raciocinar — "«CPF:7f3a» tem saldo
devedor e «CPF:7f3a» pediu renegociação" é uma frase útil; com token aleatório
por ocorrência, viram duas pessoas.

Determinismo ingênuo — hash do valor — seria invertível por força bruta: CPF tem
10¹¹ possibilidades, que uma máquina comum percorre. Por isso o token é **HMAC
com chave por tenant**, não hash puro.

Consequência: dois tenants com o mesmo CPF geram tokens diferentes. É o que se
quer — token de um cliente não diz nada sobre a base do outro.

O valor no cofre é cifrado com **AES-GCM**, com o tenant como dado autenticado,
e chaves separadas para derivar e para cifrar: quem obtiver a chave de derivação
consegue confirmar se um valor suspeito está na base, mas não consegue ler o
cofre.

**Mascarar não cria entrada no cofre** — há teste. É a razão de `mascarar` estar
acima de `tokenizar` na ordem de restritividade da Fase 1, agora com efeito
observável.

**Token desconhecido fica como está.** Modelos inventam token plausível na
resposta; substituir por um valor qualquer produziria dado errado com cara de
certo.

---

## 3. Fail-closed

Classificador fora do ar → **503**, requisição não sai, e o registro vai para a
trilha com base normativa própria:

> CLAUDE.md regra 3 — sem classificação não há como afirmar que a requisição não
> carrega dado pessoal, e a ausência de prova não é liberação.

Bloquear sem registrar deixaria o cliente sem como explicar, meses depois, por
que aquela requisição não passou.

---

## 4. Latência — medida, não estimada

Provedor local para isolar o custo do gateway; 60 medições por cenário,
descartando 5 de aquecimento.

| cenário | overhead p50 | p95 | p99 |
|---|---:|---:|---:|
| sem dado pessoal | 7,8 ms | 8,6 ms | 8,7 ms |
| um CPF | 10,4 ms | 11,4 ms | 12,4 ms |
| quatro entidades | 15,7 ms | 18,4 ms | 69,1 ms |
| prompt longo (2 KB) | 47,7 ms | **52,3 ms** | 51,6 ms |

Meta de 300 ms atingida com folga de 6×.

### As duas correções que a medição provocou

A primeira rodada deu p95 de **149 ms** e p50 de **61 ms** até para prompt sem
dado pessoal nenhum. Isso não batia com os 7,8 ms de spaCy medidos na Fase 0, e
foi o desencontro que valeu a investigação.

**1. O cliente HTTP era criado por requisição** — pool novo, conexão TCP nova,
nenhum keep-alive. Custava cerca de **45 ms**, mais que todo o resto somado.
Era o maior item da conta e estava onde eu não suspeitava: eu esperava que o
gargalo fosse a classificação.

O conserto trouxe uma sutileza: um `AsyncClient` carrega o pool preso ao event
loop em que nasceu, e reusá-lo em outro loop quebra. Em produção existe um loop
só e a distinção não aparece — mas invariante que só vale em produção é
invariante que ninguém verifica. O cache é por loop, com `WeakKeyDictionary`.

**2. O texto era classificado duas vezes** — uma no concatenado para decidir,
outra por trecho para transformar. Além do custo, **era incorreto**: a
concatenação cria vizinhança que não existe na requisição, e o classificador
acha entidade na emenda entre duas mensagens — entidade que ninguém escreveu.
Agora cada trecho é classificado uma vez e o resultado é reaproveitado.

### Onde o tempo é gasto hoje

A classificação do spaCy domina e cresce com o tamanho do texto: é o que separa
8 ms de 48 ms entre o menor e o maior cenário. Recognizers de documento (0,03
ms), motor de política (< 0,1 ms) e tokenização (0,05 ms por valor) são
desprezíveis.

**A medição é de máquina de desenvolvimento, com provedor local.** Não inclui
rede, TLS até o provedor real, nem concorrência. O número que vale para
contrato só sai da Fase 5, com carga.

---

## 5. Sobreposição de achados — a pendência da Fase 1, fechada

A Fase 1 registrou o caso: no e-mail `marina@vetorcred.com.br`, o Presidio
devolve três achados encaixados.

```
EMAIL_ADDRESS  score=1.00  'marina@vetorcred.com.br'
ORGANIZATION   score=0.85  'marina@vetorcred.com.br'
URL            score=0.50  'vetorcred.com.br'
```

Critério de resolução, nesta ordem: **trecho maior vence**; empatando em
tamanho, **maior score**; empatando nos dois, **ordem alfabética da entidade**.

O terceiro critério é arbitrário e está assumido como tal no código: o que
importa é ser estável, não ser justo. Empate real entre duas entidades do mesmo
tamanho e mesma confiança não tem resposta melhor, e sortear quebraria o
determinismo do qual o hash da trilha depende. Há teste rodando todas as
permutações da entrada e exigindo a mesma saída.

---

## 6. O erro que quase passou: o teste enganado pelo sistema funcionando

A primeira versão do dublê do provedor **ecoava** o corpo recebido dentro do
texto da resposta, e o teste procurava o CPF ali para provar que só o token
tinha saído. O teste falhava dizendo que o CPF estava presente.

Não era bug. A destokenização da resposta **corretamente** trocava o token de
volta pelo CPF antes de o teste ver — o sistema fazia exatamente o que deve
fazer, e o teste estava lendo o lado errado do caminho.

A lição não é o erro, é o método: **observar o que saiu exige um ponto de
observação fora do caminho de volta.** O dublê agora anota o que recebeu numa
lista que o teste inspeciona diretamente.

---

## 7. Cabeçalhos

`X-Baluarte-Request-Id`, `X-Baluarte-Action`, `X-Baluarte-Policy-Version`,
`X-Baluarte-Entities-Detected` (tipo e contagem, nunca valor) e
`X-Baluarte-Overhead-Ms`. Há teste confirmando que cabeçalho `x-baluarte-*`
**não** vaza para o provedor.

---

## 8. Pendências

1. **Streaming.** O `CLAUDE.md` lista streaming como "não construir sem pedir",
   e o gateway hoje recusa implicitamente: `stream: true` atravessa e a resposta
   volta sem destokenização. Precisa ser recusado **explicitamente**, com erro
   claro, antes de qualquer cliente tentar.
2. **Cofre persistente.** Hoje é em memória — reiniciar o processo perde o
   mapeamento e a destokenização para de funcionar para tokens antigos. A
   persistência depende de decidir onde a chave mestra vive.
3. **Chave do provedor.** Hoje a chave do cliente atravessa para o provedor. O
   `docs/produto-e-tecnico.md` prevê que ela passe a viver no BALUARTE; quando
   mudar, o teste que hoje afirma a passagem precisa afirmar o contrário.
4. **A cobertura de política continua aberta.** O perfil usado nos testes
   declara `entidade_sem_regra: permitir` para manter o foco no caminho. **Em
   produção o padrão é bloquear**, e com o NER como está isso bloqueia quase
   tudo — ver a Fase 1.
5. **`date.today()` no proxy.** O motor não lê o relógio, mas o proxy lê para
   escolher a política vigente. É o lugar certo, e ainda assim merece virar
   parâmetro injetável para teste de virada de vigência à meia-noite.
