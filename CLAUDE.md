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
| Venda, ICP, objeções | `docs/comercial-e-gtm.md` |
| Contratos, RIPD, risco | `docs/juridico-e-compliance.md` |
| Fatos verificados | `docs/fontes.md` |
| Prompts de build por fase | `docs/playbooks/construcao.md` |
| Prompts de marketing | `docs/playbooks/marketing.md` |

## Status atual

**Fase:** pré-Fase 0. O gateway não começou.

**O que existe:** a landing page de validação (`index.html`, `obrigado.html`,
`vercel.json`), no ar em <https://baluarte-teal.vercel.app>, com formulário
do Formspree capturando pedido de call. Site estático, sem build.

**Última decisão relevante:** as fontes citadas em material público foram
verificadas contra o primário. A multa austríaca de €450 mil foi refutada e
removida de todos os documentos; o estudo da FGV passou a ser descrito com
precisão; as notas técnicas da ANPD foram corrigidas. Registro em
`docs/fontes.md`.

**Próximo passo lógico:** Fase 0 do `docs/playbooks/construcao.md` — validar
a premissa técnica (LiteLLM + Presidio, recognizers de CPF/CNPJ com dígito
verificador, conjunto de teste de 50 exemplos). Critério de saída: falso
negativo zero em CPF e CNPJ formatados.

**Atenção ao estruturar código:** o site estático vive na raiz e a Vercel
está apontada para a raiz. Quando o dashboard Next.js entrar (Fase 5), os
dois vão colidir. Decidir na hora se o site vai para `site/` com ajuste da
Vercel, ou se o dashboard fica em repositório separado.
