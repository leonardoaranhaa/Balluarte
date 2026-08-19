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

## Regras de comunicação — inegociáveis

Valem para site, contrato, interface, pitch, post e mensagem. A defesa
jurídica depende de consistência entre esses seis pontos.

1. NUNCA PROMETER CONFORMIDADE. BALUARTE não deixa ninguém "em
   conformidade com a LGPD" — isso é decisão do encarregado de dados do
   cliente. Entregamos controle técnico e trilha de evidência.

2. NUNCA AFIRMAR QUE ROTEAR POR SERVIDOR NO BRASIL ELIMINA O CLOUD ACT
   quando o destino final continua sendo provedor americano. O ganho real
   vem do mascaramento, da tokenização ou do roteamento para modelo
   hospedado nacionalmente.

3. NUNCA USAR O PL 2338 COMO ARGUMENTO DE URGÊNCIA. Não é lei, está em
   tramitação na Câmara. Usar o art. 33 da LGPD, que já é vigente.

4. NUNCA USAR URGÊNCIA FABRICADA nem superlativo vazio.

5. NENHUM FATO VAI PARA MATERIAL PÚBLICO SEM ESTAR EM `docs/fontes.md`.
   Fonte secundária serve para achar o fato, nunca para confirmá-lo. Já
   perdemos uma citação por isso — ver a seção "Refutado" daquele arquivo.

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

## Documentos de referência

Antes de trabalhar em algo, ler o documento da área em `docs/`. O índice
está em `docs/README.md`.

| Área | Arquivo |
|---|---|
| Produto e arquitetura | `docs/produto-e-tecnico.md` |
| Marca, tom de voz, operação | `docs/marca-e-operacional.md` |
| Identidade visual, paleta, logo | `docs/guia-da-marca.md` |
| Venda, ICP, objeções | `docs/comercial-e-gtm.md` |
| Contratos, RIPD, risco | `docs/juridico-e-compliance.md` |
| Fatos verificados | `docs/fontes.md` |
| Prompts de build por fase | `docs/playbooks/construcao.md` |
| Prompts de marketing | `docs/playbooks/marketing.md` |

## Status atual

**Fase:** 3 de 5. Fases 0, 1 e 2 concluídas; o gateway ainda não intercepta
tráfego real.

**O que existe:** a landing page de validação (`index.html`, `styles.css`,
`app.js`, `obrigado.html`, `vercel.json`), no ar em
<https://baluarte-teal.vercel.app>, com formulário do Formspree capturando
pedido de call. Site estático, sem build.

**Como o site vai para o ar:** o projeto da Vercel está ligado ao repositório.
Push na branch gera preview, merge na `main` publica em produção. **Não usar
deploy manual.** O deploy manual exige transmitir a árvore de arquivos inteira
a cada publicação, e a truncagem já quebrou a produção três vezes seguidas —
uma servindo o literal `PLACEHOLDER`, outra com 404 na raiz, outra com a folha
de estilo vazia. Se algum dia precisar mesmo de deploy manual, conferir
byte a byte contra o repositório depois (`sha256` de cada arquivo servido).

O `index.html` foi separado de `styles.css` e `app.js` por causa disso: manter
CSS e JS embutidos deixava um arquivo de 38 KB que ninguém transmite à mão sem
errar. A separação continua valendo mesmo com o deploy automático.

**Última decisão relevante:** a identidade visual v1 entrou no repositório
(`assets/marca/`, `favicon/`, `docs/guia-da-marca.md`) e na landing. A paleta da
página passou a usar os hex oficiais — `#E6E6E6`, `#0E1113`, `#F5A623` — porque
os lockups do logo trazem placa de fundo embutida nessas cores exatas e qualquer
desvio cria emenda visível.

**Regra de cor que veio disso:** o `#B8770F` do guia mede 2,96:1 sobre o neutro
claro e reprova AA. Serve dentro do logo, onde a WCAG isenta marca; para texto
usar `#7E5200`, que dá 5,4:1.

**Fase 0 concluída.** O gateway vive em `gateway/`, fora da raiz, porque a
Vercel publica a raiz como site estático e um `requirements.txt` lá em cima a
faria detectar o projeto como Python. Recognizers de CPF e CNPJ com dígito
verificador, corpus de 50 casos, 60 testes, guardrail do LiteLLM em `pre_call`.
Critério de saída atingido: falso negativo **zero** em CPF e CNPJ, formatados e
crus, e falso positivo zero nas dez armadilhas de DV. Relatório em
`gateway/fase0/RELATORIO.md`.

**Três coisas que a Fase 0 descobriu e mudam o plano:**

1. O guardrail de Presidio que vem no LiteLLM fala HTTP e só aceita recognizer
   declarado em JSON — regex e score, sem campo de validação. Por ele não há
   como exigir dígito verificador. Daí o guardrail próprio, com analisador em
   processo.
2. O Presidio não traz nenhum documento brasileiro. CPF e CNPJ estão feitos;
   RG, CNS, PIS/PASEP, título e CNH continuam nossos.
3. **O `pt_core_news_sm` não serve para detectar nome.** Disparou 26 achados de
   PERSON/LOCATION no corpus, um correto, todos com score 0,85 — lê verbo no
   imperativo em começo de frase ("Escreva", "Analise", "Redija") como nome
   próprio, que é a forma de todo prompt corporativo. Não ligar detecção de
   nome antes de medir `pt_core_news_lg` e definir piso de score.

**Fase 1 concluída.** Motor de política em `gateway/baluarte/politica/`:
política declarativa em YAML, avaliador determinístico, catálogo versionado com
consulta por data, e decisão explicável com base normativa e sha256 da política
vigente. 122 testes. Relatório em `gateway/fase1/RELATORIO.md`.

**Ordem de restritividade — decisão de produto, confirmar:**
`permitir < tokenizar < mascarar < bloquear`. O degrau discutível é mascarar
acima de tokenizar: pelo que sai da empresa os dois se equivalem, mas tokenizar
deixa cofre de mapeamento para trás e mascarar destrói o valor. Isolada em
`politica/acoes.py`; inverter é uma linha e um teste avisa.

**O que a Fase 1 descobriu:** fail-closed e classificador ruim não convivem. O
classificador emite 15 tipos de entidade e a política decide sobre 5; as outras
13 caem no padrão `entidade_sem_regra`, que é bloquear. Some-se a isso que o
Presidio devolve achados sobrepostos — `ORGANIZATION` e `URL` casam dentro do
próprio e-mail já detectado — e o resultado é requisição legítima bloqueada.
Daí `politica/cobertura.py`, que confere o encaixe antes de a política entrar
em vigor. Resolver sobreposição é da camada de classificação, fica para a
Fase 3.

**Fase 2 concluída.** Trilha de auditoria em `gateway/baluarte/auditoria/` e
`gateway/migrations/`: tabela append-only no Postgres, encadeamento por sha256,
segregação por tenant em row-level security. 146 testes, 24 contra Postgres de
verdade. Relatório em `gateway/fase2/RELATORIO.md`.

**O que a Fase 2 fixou como propriedade de esquema, não de disciplina:** a
trilha não tem coluna onde um valor caberia, e há teste varrendo a linha
inteira em SQL — coluna nova entra na varredura sozinha. A segregação é row-level
security e não `WHERE`: sessão sem tenant declarado vê zero linhas, nunca a base
toda. A cadeia é **por tenant**, senão verificar a própria trilha exigiria ler
o hash da alheia.

**Lição da fase, que vale para todo teste de adulteração:** o primeiro
`UPDATE` da demonstração foi no-op — troquei `permitir` por `permitir` — e a
verificação disse "íntegra", corretamente. Um teste de adulteração que vira
no-op passa para sempre e não prova nada. Agora tanto a demo quanto o teste
abortam se a alteração não mudar nada.

**Próximo passo lógico:** Fase 3 do `docs/playbooks/construcao.md` — integração
do proxy. Critério de saída: troca de URL base sem alteração de código e p95
medido. É também onde entra a resolução de achados sobrepostos que a Fase 1
deixou pendente.

**Atenção ao estruturar código:** o site estático vive na raiz e a Vercel
está apontada para a raiz. Quando o dashboard Next.js entrar (Fase 5), os
dois vão colidir. Decidir na hora se o site vai para `site/` com ajuste da
Vercel, ou se o dashboard fica em repositório separado.
