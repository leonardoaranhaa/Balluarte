# Fase 0 — validação da premissa técnica

**Data:** 9 de agosto de 2026
**Critério de saída:** falso negativo **zero** em CPF e CNPJ formatados.
**Resultado:** atingido, com uma correção no caminho.

Reproduzir:

```bash
cd gateway
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download pt_core_news_sm
.venv/bin/python -m pytest tests -q      # 60 testes
.venv/bin/python -m fase0.avaliar        # o relatório abaixo
```

---

## 1. Resultado do conjunto de 50 casos

| entidade | esperados | VP | FN | FP | recall | precisão |
|---|---:|---:|---:|---:|---:|---:|
| `BR_CPF` | 23 | 23 | **0** | **0** | 100,0% | 100,0% |
| `BR_CNPJ` | 14 | 14 | **0** | **0** | 100,0% | 100,0% |

Por categoria do corpus:

| categoria | casos | VP | FN | FP |
|---|---:|---:|---:|---:|
| CPF formatado | 12 | 13 | 0 | 0 |
| CPF sem formatação | 8 | 10 | 0 | 0 |
| CNPJ formatado | 8 | 9 | 0 | 0 |
| CNPJ sem formatação | 5 | 5 | 0 | 0 |
| Quase-documento (DV reprova) | 10 | — | — | **0** |
| Texto limpo | 7 | — | — | **0** |

As dez armadilhas de dígito verificador e os sete textos sem dado pessoal não
produziram um único falso positivo. É o resultado que o dígito verificador
tinha que dar: ele é aritmética fechada, não heurística.

### Latência

| medição | p50 | p95 |
|---|---:|---:|
| Pipeline completo (spaCy NER + padrões) | 7,78 ms | 9,74 ms |
| Só os recognizers de documento | 0,03 ms | 0,06 ms |

250 medições, texto corporativo de uma a três linhas. **O custo é todo do NER:
o reconhecimento de CPF e CNPJ é 265 vezes mais barato que a passada de
linguagem natural.** Isso importa para a arquitetura — ver o item 4.

---

## 2. A correção no caminho

A primeira rodada deu **6 falsos negativos em CPF, 5 deles em CPF formatado** —
reprovando o critério de saída. A causa não foi o Presidio nem o dígito
verificador: foi a borda direita do meu regex.

Eu tinha escrito `(?![\d.\-/])` para impedir que onze dígitos casassem dentro
de um número maior. Só que ponto final de frase está nessa lista. Então:

```
"CPF 111.444.777-35, conta encerrada."   → detectava
"CPF: 028.446.391-43."                   → não detectava
```

Os cinco CPFs perdidos terminavam frase. **A forma mais comum de escrever um
documento era justamente a que passava batido**, e o erro não aparecia em teste
de unidade escrito com o valor solto — só aparece em texto de verdade, que é
para isso que o corpus existe.

A borda correta recusa dígito colado e recusa separador **seguido de dígito**:

```python
_BORDA_DIR = r"(?!\d)(?![.\-/]\d)"
```

Assim `12345678900.50` continua sendo um decimal e não um CPF, e o documento no
fim da frase é detectado. Está coberto por teste de regressão em
`tests/test_reconhecedores.py::test_acha_cpf_encostado_em_pontuacao`.

---

## 3. A premissa se sustenta?

**Sim, com três ressalvas que mudam o plano de construção.**

O `CLAUDE.md` diz: "LiteLLM + Presidio já resolvem detecção e mascaramento (…)
qualquer engenheiro competente monta isso num fim de semana". Isso está certo
sobre o **encanamento** e errado sobre o **conteúdo brasileiro**.

### Ressalva 1 — o guardrail de Presidio do LiteLLM não carrega recognizer nosso

O guardrail que vem pronto no LiteLLM conversa com o Presidio **por HTTP**
(`PRESIDIO_ANALYZER_API_BASE`), não pela biblioteca em processo. Para
customizar, ele aceita *ad hoc recognizers* declarados em JSON — e o JSON só
tem `regex`, `score` e `context`.

**Não existe campo para validação.** Por aquele caminho não há como exigir
dígito verificador, e "onze dígitos" volta a valer por CPF — que é exatamente
o falso positivo que o `CLAUDE.md` manda evitar.

Duas saídas, ambas com código nosso:

1. Publicar nossa própria imagem do servidor Presidio, com os recognizers
   registrados no processo.
2. Escrever nosso guardrail no LiteLLM, usando o analisador em processo.

Escolhi a **2** para a Fase 0 (`baluarte/guardrail.py`): mantém os recognizers
no nosso repositório, testáveis, sem um serviço a mais para operar. A decisão
merece revisão na Fase 3, quando houver medição de carga real.

### Ressalva 2 — o Presidio não traz nada do Brasil

Recognizers carregados por padrão para `pt`: Crypto, Date, Email, Iban, Ip,
MacAddress, MedicalLicense, Phone, Spacy, Url. **Nenhum documento brasileiro.**

CPF e CNPJ estão feitos. Continuam faltando RG, CNS, PIS/PASEP, título de
eleitor e CNH — todos nossos, e os que têm dígito verificador seguem o mesmo
molde. O que o Presidio entrega de verdade aqui é o *framework*
(`PatternRecognizer` + `validate_result`), e ele encaixa bem: a validação de DV
cabe no ponto exato onde o framework espera.

### Ressalva 3 — o guardrail nasce desligado

No LiteLLM um guardrail é opt-in: só roda se a requisição pedir por ele no
metadata. Para um gateway de conformidade isso é o avesso do que se quer —
quem está colando CPF no prompt não vai lembrar de pedir a checagem.

Corrigido com `default_on=True` no construtor, e coberto por teste. É uma linha,
mas é o tipo de padrão que desliga a proteção em silêncio.

---

## 4. O achado que não estava no roteiro: o NER em português é ruim aqui

Fora do escopo do critério de saída, mas grave o bastante para registrar.

O `pt_core_news_sm` disparou **26 achados de PERSON, LOCATION e ORGANIZATION no
corpus. Um está certo** — "Marina Alves". Os outros 25 são falso positivo, e
todos com score **0,85**, que é confiança alta.

O que ele marcou como nome de pessoa ou lugar:

> `Escreva`, `Redija`, `Classifique`, `Reformule`, `Explique`, `Verificar`,
> `Confirmar`, `Resumo`, `Garantia`, `Cadastro`, `Matriz`, `Beneficiário`,
> `hipertenso`, `carteira B`, `ME`, e três pedaços de CNPJ (`75.139.520/`)

O padrão é claro: **verbo no imperativo em começo de frase, com maiúscula, é
lido como nome próprio.** E prompt corporativo é feito disso — "Escreva…",
"Analise…", "Resuma…", "Classifique…". Não é artefato do meu corpus; é o
formato real do caso de uso.

Consequência prática: uma política com `NOME_PESSOA → tokenizar` hoje
destruiria o prompt, trocando os verbos por tokens e entregando ao modelo um
texto sem instrução. **Não dá para ligar detecção de nome com este modelo.**

Caminhos a testar na Fase 1, em ordem de custo:

1. `pt_core_news_lg` — modelo maior, medir o mesmo corpus.
2. Piso de score por entidade, com nome exigindo bem mais que 0,85 e apoio de
   contexto ("paciente", "titular", "cliente", "portador").
3. Tratar nome como decisão de política do cliente, desligada por padrão, com o
   número de falso positivo declarado no Dossiê.

Isso reforça, com medição própria, o que a landing já diz na seção "o que não
fazemos": documento com dígito verificador sai com confiança alta, nome em
texto corrido é bem mais difícil. Agora temos o número.

---

## 5. O que o stack pronto resolve, e o que é código nosso

**Resolve, e não vale reconstruir:**

- Ponto de interceptação no caminho da requisição (`pre_call`, `post_call`)
- Compatibilidade de formato entre provedores — a regra 6 do `CLAUDE.md`
  ("troca só a URL base") sai de graça
- Framework de recognizer do Presidio, com o gancho de validação no lugar certo
- Operadores de anonimização do Presidio para a etapa de transformação

**É código nosso, confirmado nesta fase:**

| o quê | por quê | fase |
|---|---|---|
| Recognizers brasileiros | O Presidio não traz nenhum | 0 ✅ CPF/CNPJ |
| Validação de dígito verificador | Não cabe em recognizer declarativo | 0 ✅ |
| Guardrail com analisador em processo | O guardrail pronto fala HTTP e não carrega validação | 0 ✅ |
| Semântica de fail-closed | O LiteLLM não tem opinião sobre isso | 0 ✅ parcial |
| Motor de política determinístico e versionado | É o produto | 1 |
| Tokenização reversível com cofre por tenant | O Presidio anonimiza, não tokeniza de forma reversível por tenant | 2 |
| Trilha de auditoria com hash encadeado | Não existe no stack | 2 |
| Matriz de Classificação por setor | É o produto | 4 |

**A premissa se sustenta**: o encanamento é de fato commodity e não deve ser
reconstruído. O que ela subestimava é quanto do conteúdo brasileiro é nosso —
não só a Matriz e o motor, mas a camada de detecção inteira para documentos
nacionais, e provavelmente o reconhecimento de nome, que o modelo aberto de
português não entrega em qualidade utilizável.

---

## 6. Pendências que esta fase deixa

1. Medir `pt_core_news_lg` no mesmo corpus antes de decidir sobre nome.
2. Recognizers de RG, CNS, PIS/PASEP, título de eleitor e CNH.
3. Reavaliar guardrail em processo × servidor Presidio próprio na Fase 3, com
   medição de carga.
4. A latência aqui é de classificação isolada, em máquina de desenvolvimento.
   O p95 ponta a ponta que o `docs/produto-e-tecnico.md` cobra só faz sentido
   medir na Fase 3, com o proxy completo.
5. O corpus tem 50 casos de uma só natureza (texto curto de negócio). Falta
   documento longo — contrato, prontuário — onde o custo do NER cresce com o
   tamanho do texto.
