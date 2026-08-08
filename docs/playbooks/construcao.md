# BALUARTE — Prompt de Construção

**Sequência de prompts para build real no Claude Code.**

---

## 0. Como usar este documento

Não existe "um prompt" que constrói o BALUARTE. Existe um **arquivo de contexto persistente** que fica no repositório e é lido a cada sessão, mais uma **sequência de prompts por fase**.

A razão é prática: sessões longas perdem contexto, e um fundador solo constrói ao longo de semanas, não numa tacada. O que sustenta a coerência é o arquivo, não a memória da conversa.

**Ordem de execução:**
1. Criar o repositório e o arquivo `CLAUDE.md` (seção 1)
2. Rodar o prompt de Fase 0 — validação da premissa técnica (seção 3)
3. Só então seguir para as fases seguintes

---

## 1. Arquivo `CLAUDE.md` — contexto persistente do repositório

> **Já existe.** O `CLAUDE.md` está na raiz do repositório e é lido
> automaticamente a cada sessão. A versão viva ganhou duas coisas que não estão
> no modelo abaixo: as regras de comunicação inegociáveis (nunca prometer
> conformidade, nunca vender soberania falsa, nunca usar o PL 2338 como urgência,
> nenhum fato sem registro em `docs/fontes.md`) e a seção "Status atual"
> preenchida.
>
> **Editar `/CLAUDE.md` diretamente, não este modelo.** Manter os dois em
> paralelo é como eles divergem.

O modelo original, mantido como registro:

````markdown
# BALUARTE

Gateway de IA com motor de conformidade LGPD. Proxy entre a aplicação do
cliente e provedores de LLM (Claude, GPT, Gemini) que detecta dado
pessoal sensível, aplica política configurada, e registra trilha de
auditoria.

## O que é o produto (e o que não é)

O proxy NÃO é o produto. O mascaramento NÃO é o produto.

LiteLLM + Presidio já resolvem detecção e mascaramento, são open source
e maduros. Qualquer engenheiro competente monta isso num fim de semana.

O produto é o que fica em volta:
- Matriz de Classificação por setor regulado
- Motor de política determinístico, versionado, com base normativa
- Trilha de auditoria com valor jurídico
- Dossiê de Conformidade

Tratar LiteLLM e Presidio como infraestrutura, igual a Postgres. Não
reconstruir o que já existe.

## Regras de arquitetura — inegociáveis

1. MOTOR DE POLÍTICA É DETERMINÍSTICO. Nunca usar LLM para decidir se um
   dado é sensível ou qual ação aplicar. Precisa ser auditável,
   reproduzível e explicável em juízo. Mesma entrada + mesma política =
   mesma saída, sempre.

2. LOG NUNCA REGISTRA VALOR EM CLARO. Registra que um CPF foi detectado,
   jamais qual CPF. Um produto de privacidade que constrói banco de PII
   em texto claro é uma bomba jurídica. Esta regra não tem exceção,
   nem em ambiente de desenvolvimento.

3. FAIL-CLOSED POR PADRÃO. Se o classificador estiver indisponível, a
   requisição é BLOQUEADA, não liberada. Fail-open só mediante opção
   explícita do cliente, registrada.

4. TODA REGRA DE POLÍTICA CARREGA BASE NORMATIVA. Artigo, resolução ou
   norma que a justifica. Não é enfeite — é o que transforma
   configuração técnica em evidência de conformidade.

5. POLÍTICA NUNCA É EDITADA, SÓ VERSIONADA. Mudança gera nova versão. O
   log registra qual versão estava vigente em cada requisição.

6. COMPATIBILIDADE DE API É SAGRADA. A API é deliberadamente idêntica à
   do provedor substituído. "Troca só a URL base" precisa ser verdade
   literal.

## Stack

- Proxy base: LiteLLM
- Detecção: Presidio + recognizers brasileiros customizados
- Motor de política: código próprio, determinístico
- Banco: Postgres
- Aplicação/dashboard: Next.js
- Hospedagem: território nacional, desde o dia 1

## Entidades brasileiras a detectar

CPF, CNPJ, RG, CNS (Cartão Nacional de Saúde), PIS/PASEP, título de
eleitor, CNH, telefone BR, CEP, e-mail, nome de pessoa, endereço.

CPF e CNPJ têm dígito verificador — validar o dígito, não só o formato.
Regex sozinho gera falso positivo em qualquer sequência numérica.

## Convenções

- Português nos nomes de domínio de negócio (politica, dossie,
  classificacao), inglês em código de infraestrutura
- Sem comentário óbvio; comentário só onde a razão não é evidente
- Todo módulo do motor de política tem teste
- Migrations versionadas, nunca alteração manual de schema

## O que NÃO construir sem eu pedir

- Autenticação social / OAuth
- Sistema de billing
- Interface elaborada (dashboard funcional basta)
- Streaming de resposta
- Detecção em imagem ou anexo
- Modo Soberano (inferência nacional) — é v2

## Status atual

Fase: [atualizar a cada fase]
Última decisão relevante: [atualizar]
````

---

## 2. Prompt de abertura de sessão

Rodar no início de cada sessão de trabalho, depois de a primeira fase estar concluída:

```
Leia o CLAUDE.md e me diga em 3 linhas: onde o projeto está, qual foi a
última decisão relevante, e qual é o próximo passo lógico.

Não comece a codificar. Quero confirmar o alinhamento primeiro.
```

---

## 3. FASE 0 — Validar a premissa técnica

**Antes de construir qualquer coisa.** Esta fase existe para descobrir cedo se a premissa do documento técnico se sustenta na prática.

```
CONTEXTO
Estou construindo o BALUARTE — gateway de IA com motor de conformidade
LGPD. Leia o CLAUDE.md antes de responder.

TAREFA — FASE 0: VALIDAÇÃO DA PREMISSA

Minha premissa é que LiteLLM + Presidio já resolvem o núcleo de
detecção e mascaramento, e que meu trabalho é construir em volta disso.
Preciso confirmar ou derrubar essa premissa antes de investir semanas.

Faça, nesta ordem:

1. Suba localmente um ambiente com LiteLLM + Presidio, com o Presidio
   operando como guardrail em modo pre_call.

2. Crie recognizers customizados para CPF e CNPJ, com validação de
   dígito verificador — não apenas regex de formato.

3. Monte um conjunto de teste com 50 exemplos de texto corporativo
   brasileiro realista, contendo:
   - CPF formatado (123.456.789-00)
   - CPF sem formatação (12345678900)
   - CNPJ nos dois formatos
   - Números que PARECEM CPF mas não são (sequências de 11 dígitos que
     falham no dígito verificador)
   - Texto sem nenhum dado sensível

4. Rode o conjunto e me reporte:
   - Taxa de falso negativo por entidade
   - Taxa de falso positivo por entidade
   - Latência adicionada, p50 e p95

5. Me diga honestamente: a premissa se sustenta? O que o stack pronto
   NÃO resolve e vai exigir código meu?

CRITÉRIO DE APROVAÇÃO DA FASE
Falso negativo em CPF e CNPJ formatados precisa ser ZERO. Eles são
determinísticos — não há desculpa técnica para errar.

Se não atingir zero, me diga por quê antes de tentar contornar.
```

---

## 4. FASE 1 — Motor de política

O primeiro código que é de fato produto.

```
Leia o CLAUDE.md.

TAREFA — FASE 1: MOTOR DE POLÍTICA

Construir o motor de política. Este é o núcleo do produto, não o proxy.

REQUISITOS

1. Política declarativa em YAML, com estrutura:
   - nome, versão, vigente_desde
   - lista de regras: entidade → ação → base_normativa
   - ações possíveis: permitir, mascarar, tokenizar, bloquear
   - regra padrão para "nenhum dado sensível detectado"

2. Avaliador determinístico:
   - Recebe: lista de entidades detectadas + política
   - Retorna: decisão por entidade + decisão global da requisição
   - Mesma entrada sempre produz mesma saída
   - Zero uso de LLM nesta camada

3. Versionamento:
   - Política nunca é editada, só versionada
   - Consulta de "qual política estava vigente em [data]" precisa
     funcionar

4. Explicabilidade:
   - Toda decisão retorna a base normativa que a justifica
   - Precisa ser possível responder "por que essa requisição foi
     bloqueada em março?" reconstituindo a decisão

5. Precedência de regras:
   - Definir e documentar o que acontece quando duas regras conflitam
   - Onde houver ambiguidade, a ação mais restritiva vence

TESTES OBRIGATÓRIOS
- Determinismo: mesma entrada, 100 execuções, mesma saída
- Precedência: casos de conflito entre regras
- Versionamento: consulta histórica retorna a política correta
- Ação mais restritiva vence em empate

ENTREGA
Código + testes passando. Ao final, me mostre um exemplo completo:
uma requisição entrando, a política aplicada, e a decisão explicada
com base normativa.

NÃO construa ainda: proxy, dashboard, banco de dados, auditoria.
Só o motor, isolado e testável.
```

---

## 5. FASE 2 — Trilha de auditoria

```
Leia o CLAUDE.md.

TAREFA — FASE 2: TRILHA DE AUDITORIA

Construir o registro de auditoria. Este é o que dá valor jurídico ao
produto.

REQUISITOS

1. Tabela append-only no Postgres. Sem UPDATE, sem DELETE.

2. Campos por registro:
   - id da requisição, timestamp UTC
   - tenant, chave de origem
   - provedor de destino
   - entidades detectadas: TIPO e QUANTIDADE apenas
   - ação aplicada por entidade
   - versão da política vigente
   - hash do registro anterior (encadeamento)

3. Encadeamento por hash:
   - Cada registro contém o hash do anterior
   - Função de verificação que percorre a cadeia e detecta adulteração
   - Teste que prova a detecção: altere um registro e confirme que a
     verificação falha

4. REGRA CRÍTICA — verificar explicitamente:
   Nenhum valor de PII em texto claro em NENHUM campo, em nenhuma
   circunstância. Registrar que um CPF foi detectado, jamais qual.
   Escreva um teste que faz uma requisição com CPF real e varre TODOS
   os campos do registro procurando o valor. Se encontrar, falha.

5. Segregação por tenant: um cliente nunca consegue ler registro de
   outro. Teste isso explicitamente.

ENTREGA
Schema + migrations + código + testes. Ao final, demonstre a
verificação de integridade funcionando: cadeia íntegra passa, cadeia
adulterada falha.
```

---

## 6. FASE 3 — Integração do proxy

```
Leia o CLAUDE.md.

TAREFA — FASE 3: INTEGRAÇÃO

Amarrar as peças: proxy → detecção → política → transformação →
auditoria → provedor → resposta.

REQUISITOS

1. Compatibilidade literal de API:
   - Mesmo corpo de requisição do provedor original
   - Mesmo formato de resposta
   - Mesma estrutura de erro
   - Teste: pegar código real que chama a API da Anthropic, trocar só a
     URL base, confirmar que funciona sem nenhuma outra alteração

2. Tokenização reversível:
   - Determinística: mesmo valor sempre gera mesmo token
   - Cofre de mapeamento isolado por tenant, com chave própria
   - Destokenização na resposta: o token volta a ser o valor original
     antes de a resposta chegar ao cliente
   - Teste ponta a ponta: CPF entra, modelo vê token, cliente recebe CPF

3. Fail-closed:
   - Classificador indisponível → requisição bloqueada
   - Erro registrado na auditoria
   - Teste: derrubar o Presidio e confirmar que bloqueia

4. Cabeçalhos de resposta:
   X-Baluarte-Entities-Detected, X-Baluarte-Action,
   X-Baluarte-Policy-Version, X-Baluarte-Request-Id

5. Latência: medir e reportar p50, p95, p99. Meta: p95 abaixo de 300ms
   de overhead. Se não atingir, me diga onde está o gargalo antes de
   otimizar.

ENTREGA
Fluxo completo funcionando + testes de integração + relatório de
latência medida (não estimada).
```

---

## 7. FASE 4 — Perfis de política e Dossiê

```
Leia o CLAUDE.md.

TAREFA — FASE 4: PERFIS E DOSSIÊ

PARTE A — Três perfis de política prontos

Implementar como YAML versionado, seguindo a Matriz de Classificação:

FINANCEIRO: CPF/CNPJ tokenizar (LGPD art. 33); dado de conta, agência e
cartão bloquear (LC 105/2001 - sigilo bancário); score e histórico de
crédito bloquear.

SAÚDE: diagnóstico, CID e prescrição bloquear (LGPD art. 11 + CFM); CNS
tokenizar; nome de paciente tokenizar (sigilo médico); CPF tokenizar.

JURÍDICO: nome de cliente/parte tokenizar (EOAB - sigilo profissional);
número de processo tokenizar; conteúdo em segredo de justiça bloquear;
documento de identificação tokenizar.

IMPORTANTE: estes perfis são rascunho técnico. Eles precisam ser
validados pelo curador jurídico antes de qualquer uso com cliente real.
Marque isso claramente no código e na documentação.

PARTE B — Dossiê de Conformidade

Gerar PDF a partir da trilha de auditoria de um período.

Conteúdo:
- Identificação do cliente e período coberto
- Volume total de requisições governadas
- Entidades detectadas por tipo e quantidade agregada
- Ações aplicadas, com distribuição
- Políticas vigentes no período, com versão e base normativa
- Verificação de integridade da cadeia de hash
- Declaração de escopo

REGRA CRÍTICA — texto obrigatório no Dossiê:
"Este documento registra os controles técnicos aplicados e a trilha de
evidência correspondente. Não constitui declaração de conformidade com
a LGPD. A avaliação de base legal, adequação e risco residual é de
responsabilidade do encarregado de dados do controlador."

Este texto não é negociável e não pode ser suavizado.

ENTREGA
Perfis implementados e testados + gerador de Dossiê + exemplo de PDF
gerado a partir de dados de teste.
```

---

## 8. FASE 5 — Dashboard mínimo

```
Leia o CLAUDE.md.

TAREFA — FASE 5: DASHBOARD

Interface mínima funcional. Next.js. O comprador é um DPO — ele precisa
de densidade de informação e clareza, não de estética de startup.

TELAS

1. VISÃO GERAL
   Volume de requisições, entidades detectadas por tipo, distribuição de
   ações aplicadas, no período selecionado.

2. AUDITORIA
   Tabela paginada e filtrável dos registros. Filtro por data, tipo de
   entidade, ação aplicada. Densa, não espaçada.

3. POLÍTICAS
   Lista de políticas e versões. Visualização da política vigente com
   base normativa por regra. Criação de nova versão — nunca edição da
   existente.

4. DOSSIÊ
   Seleção de período e geração.

DIRETRIZ VISUAL
Estética de ferramenta de engenharia, não de produto de consumo. Um
acento cromático só. Tipografia com boa legibilidade em tabela densa
(IBM Plex Sans + IBM Plex Mono, ou Inter + JetBrains Mono).

Sem gráfico decorativo. Todo gráfico precisa responder a uma pergunta
que o DPO realmente faz.

NÃO CONSTRUIR
Onboarding self-service, billing, temas claro/escuro elaborados,
animação. A venda é founder-led — onboarding manual é aceitável.
```

---

## 9. Prompt de auditoria de código

Rodar ao fim de cada fase, antes de seguir:

```
Leia o CLAUDE.md.

Audite o código escrito nesta fase contra as seis regras de arquitetura
inegociáveis. Para cada regra, me diga: cumprida, violada, ou não se
aplica — com o trecho de código como evidência.

Depois, três perguntas específicas:

1. Existe QUALQUER caminho de código onde um valor de PII em claro pode
   chegar a um log, a uma mensagem de erro, a um trace, ou ao banco?
   Procure especificamente em: tratamento de exceção, logs de debug,
   mensagens de erro retornadas ao cliente.

2. Existe algum ponto onde uma decisão de política depende de algo
   não-determinístico — timestamp, ordem de iteração de dicionário,
   chamada externa, aleatoriedade?

3. Se o classificador falhar de forma inesperada (não indisponível, mas
   retornando resultado malformado), o sistema falha fechado ou aberto?

Seja rigoroso. Prefiro descobrir um problema agora a descobrir com
cliente rodando.
```

---

## 10. Ordem e critérios de aceitação

| Fase | Entrega | Critério de saída |
|---|---|---|
| 0 | Validação da premissa | Falso negativo zero em CPF/CNPJ formatados |
| 1 | Motor de política | Determinismo provado em teste, explicabilidade funcionando |
| 2 | Trilha de auditoria | Teste de vazamento de PII passando, integridade verificável |
| 3 | Integração | Troca de URL base funcionando sem alteração de código, p95 medido |
| 4 | Perfis + Dossiê | Três perfis implementados, Dossiê gerado com a declaração de escopo |
| 5 | Dashboard | Quatro telas funcionais |

**Regra de sequenciamento:** não avançar de fase sem o critério de saída atendido. Fundador solo que constrói horizontalmente termina com cinco coisas pela metade e nada vendável.

**Regra de escopo:** nada da v2 (Modo Soberano, inferência nacional) começa antes de três clientes pagantes recorrentes. Construir a camada cara antes de validar a barata é o erro clássico de fundador técnico.

---

## 11. Checklist "pronto para vender"

Não marcar reunião de piloto antes de todos verdadeiros:

- [ ] Falso negativo zero em CPF e CNPJ formatados
- [ ] Tokenização reversível ponta a ponta
- [ ] Três perfis de política validados pelo curador jurídico
- [ ] Trilha de auditoria com encadeamento de hash verificável
- [ ] Dossiê gerado com assinatura digital válida
- [ ] Latência p95 abaixo de 300ms, medida
- [ ] Teste de vazamento de PII em logs passando
- [ ] Produção hospedada em território nacional

---

*Prompt de Construção — BALUARTE. Elaborado em agosto de 2026. LiteLLM e Presidio são projetos ativos com releases frequentes — reconfirmar compatibilidade e nomes de configuração antes de começar a Fase 0.*
