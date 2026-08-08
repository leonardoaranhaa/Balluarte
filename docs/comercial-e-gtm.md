# BALUARTE — Comercial & GTM

*Documento vivo. Revisar após cada bloco de 10 calls de discovery.*

---

## 1. Estratégia de entrada

### 1.1 Princípio

BALUARTE vende para um comprador que **já tem o problema mas ainda não o nomeou**. Isso define tudo: a venda começa como diagnóstico, não como demonstração de produto.

A sequência mental do comprador precisa ser:
1. "Eu não sabia que isso era uma transferência internacional de dado."
2. "Eu não tenho ideia de quanto disso já aconteceu na minha empresa."
3. "Eu não teria como provar nada se me perguntassem."
4. "Quanto custa resolver?"

Vender feature antes do passo 3 é queimar a conversa. O produto só faz sentido depois que a lacuna está visível.

### 1.2 Motion de venda

**Founder-led sales, alto toque, baixo volume.** Não é PLG, não é self-service, não é inbound nessa fase. Um fundador solo com ICP estreito converte melhor com 20 conversas profundas que com 500 leads frios.

Transição para motion escalável só depois de 10 clientes pagantes com padrão de objeção estabilizado.

---

## 2. Segmentação e priorização

### 2.1 Os três segmentos

| Segmento | Perfil | Prioridade |
|---|---|---|
| **A — Fintech/Healthtech média** | 50–500 funcionários, DPO existente, IA já em uso, fiscalização setorial dupla (Bacen/ANS/CFM + LGPD) | **Foco total nas primeiras 8 semanas** |
| **B — Escritório de advocacia médio/grande** | Áreas trabalhista, saúde, contencioso. Comprador é sócio, não TI | Semana 6 em diante |
| **C — Integradoras que vendem para governo** | B2B2G. Precisam demonstrar soberania para vencer licitação | Não antes do 5º cliente pagante |

### 2.2 Por que essa ordem

**A é primeiro** porque o comprador é identificável (DPO/CISO), o orçamento de compliance já existe, e a dor é aguda por causa da fiscalização setorial.

**B é segundo** porque a alavanca é diferente e mais forte em certo sentido — sigilo profissional é regra anterior e mais rígida que a LGPD genérica, e qualquer sócio entende isso sem tradução técnica. Mas o ciclo de decisão em sociedade de advogados é político e lento.

**C é último** porque licitação é ciclo longo demais para financiar validação. É onde o negócio cresce, não onde ele nasce.

### 2.3 Anti-ICP (recusar ativamente)

- Desenvolvedor individual buscando economia em API de IA — paga pouco, não valoriza compliance, e distorce o roadmap.
- Empresa pré-seed sem orçamento formalizado de compliance.
- Grande banco ou seguradora nesta fase — ciclo de compra de 12+ meses que um fundador solo não sustenta.

Recusar cliente errado cedo é decisão comercial, não perda de receita.

---

## 3. Mensagem por persona

A mesma verdade, três traduções.

### 3.1 DPO / Encarregado de Dados

**Dor central:** responsabilidade sem visibilidade.

> "Você responde formalmente pelo tratamento de dado da empresa. Hoje, você tem como responder — com evidência — o que saiu da empresa em prompts de IA no último trimestre?"

**Gancho de credibilidade:** o estudo do CTS/FGV Direito Rio — sete plataformas de IA generativa avaliadas contra catorze critérios extraídos de guia da ANPD, e nenhuma cumpre os catorze. Só três critérios são cumpridos por todas. As melhores avaliadas ficam em onze de catorze, e entre as falhas que restam nelas está a falta de clareza sobre os países para onde o dado é enviado — que é exatamente o art. 33.

### 3.2 CISO / Head de Segurança

**Dor central:** shadow AI é superfície de ataque não mapeada.

> "Você tem inventário de todo SaaS que a empresa usa. Tem inventário do que sai em prompt de IA?"

**Gancho:** relatórios de mercado já quantificam shadow AI como fator que eleva de forma relevante o custo médio de um incidente de violação de dados.

### 3.3 Sócio de escritório de advocacia

**Dor central:** sigilo profissional, não LGPD.

> "Um associado seu colou peça de um cliente no ChatGPT semana passada. Isso é violação de sigilo profissional, e não existe registro nenhum de que aconteceu."

**Gancho:** entidades de classe já orientam explicitamente para evitar envio de dado de cliente a provedor de IA em nuvem sem base legal específica. Aqui não se argumenta com risco futuro de multa — se argumenta com dever profissional já vigente.

---

## 4. One-pager comercial

Estrutura de uma página, para enviar após a primeira call. Não é pitch deck, é resumo para o comprador circular internamente.

```
┌─────────────────────────────────────────┐
│ BALUARTE                                │
│ A camada de confiança entre sua         │
│ empresa e a IA.                         │
├─────────────────────────────────────────┤
│ O PROBLEMA (3 linhas)                   │
│ Art. 33 LGPD + IA em nuvem = transfe-   │
│ rência internacional sem base legal     │
│ documentada. Sem log. Sem prova.        │
├─────────────────────────────────────────┤
│ O QUE FAZEMOS (4 bullets)               │
│ • Detecta dado sensível antes de sair   │
│ • Aplica a política que você definiu    │
│ • Mascara, tokeniza ou roteia           │
│ • Gera trilha de auditoria assinada     │
├─────────────────────────────────────────┤
│ COMO IMPLANTA                           │
│ Troca de URL base. Sem reescrita de     │
│ código. Piloto em 2 semanas.            │
├─────────────────────────────────────────┤
│ O QUE NÃO FAZEMOS                       │
│ Não declaramos conformidade — isso é    │
│ decisão do seu encarregado. Damos       │
│ controle técnico e evidência.           │
├─────────────────────────────────────────┤
│ [nome] · [contato] · [site]             │
└─────────────────────────────────────────┘
```

A seção "O que não fazemos" é deliberada. Num mercado de promessa vaga, dizer o limite explicitamente é o que separa fornecedor sério de vendedor de compliance-teatro.

---

## 5. Pitch deck — estrutura (10 slides)

| # | Slide | Conteúdo central |
|---|---|---|
| 1 | Capa | Nome + a frase de uma linha |
| 2 | O gatilho | A ANPD colocou IA e tecnologias emergentes entre os eixos de fiscalização do biênio 2026-2027 (NT nº 54/2025/FIS/CGF), e já emitiu nota técnica sobre possíveis violações à LGPD pelo sistema Grok (NT nº 1/2026/FIS/CGF). Fiscalização anunciada, com número de documento — sem verbo de ameaça |
| 3 | O problema no Brasil | Art. 33 LGPD + estudo da FGV: sete plataformas avaliadas contra catorze critérios da ANPD, nenhuma cumpre todos |
| 4 | A pergunta sem resposta | "Quanto dado sensível saiu da sua empresa para IA no último trimestre, e sob qual base legal?" |
| 5 | A solução | Os 4 blocos: substituição transparente, classificação, política, auditoria |
| 6 | Demonstração | Screenshot real do dashboard — nunca mockup em pitch de venda |
| 7 | Implantação | Troca de URL, piloto em 2 semanas, sem reescrita |
| 8 | O que não fazemos | A restrição arquitetural, explícita |
| 9 | Planos | Tabela de preço, sem esconder valores |
| 10 | Próximo passo | Piloto pago de 30 dias, escopo definido |

**Regra:** deck é apoio de conversa, não documento autônomo. Se o deck funciona sozinho sem você, ele está longo demais.

---

## 6. Script de Discovery Call

Duração alvo: 30 minutos. Estrutura 70/30 — o comprador fala 70% do tempo.

### 6.1 Abertura (2 min)

> "Obrigado pelo tempo. Vou ser direto sobre o formato: quero entender como vocês lidam com IA hoje, e só no fim, se fizer sentido, te mostro o que construí. Se não fizer sentido, te digo isso na cara e a gente não perde tempo dos dois. Pode ser?"

Estabelece que você não vai empurrar produto. Baixa a guarda imediatamente.

### 6.2 Mapeamento de uso (8 min)

1. "Como a IA generativa entra na operação de vocês hoje — em produto, em processo interno, ou os dois?"
2. "Quem tem acesso? É liberado geral, ou tem alguma política?"
3. "Quais ferramentas? Provedor único ou vários?"

### 6.3 Descoberta da lacuna (10 min) — o núcleo da call

4. "Hoje, se alguém te perguntar quanto dado pessoal saiu da empresa via prompt de IA no último trimestre, você consegue responder?"
5. "Existe log disso em algum lugar?"
6. "Vocês têm base legal documentada para essa transferência? Quem definiu isso?"
7. "Já teve algum episódio — alguém colando algo que não devia, ou uma pergunta de cliente sobre isso?"

**A pergunta 4 é o ponto de virada da call.** Se o comprador hesitar ou rir, a dor está viva. Se responder com segurança e detalhe, ou ele já resolveu (raro) ou não entendeu a pergunta (comum — reformular).

### 6.4 Qualificação comercial (6 min)

8. "Se existisse ferramenta que desse essa visibilidade e gerasse relatório de auditoria pronto — isso teria orçamento hoje, ou é 'bom saber que existe' sem verba alocada?"
9. "Quem mais precisaria estar na conversa para isso avançar?"
10. "Vocês têm algum ciclo de auditoria, certificação ou renovação contratual nos próximos 6 meses que toque nisso?"

**A pergunta 8 decide se isso é validação real ou conversa educada.** A 10 identifica gatilho de urgência real — auditoria marcada é o melhor evento de compra que existe nesse mercado.

### 6.5 Fechamento (4 min)

Se qualificou:
> "Pelo que você descreveu, faz sentido. Minha proposta é um piloto pago de 30 dias, escopo fechado: a gente pluga em um fluxo só, você vê o que aparece, e no fim te entrego o primeiro Dossiê de Conformidade. Se não gerar valor, encerra sem contrato. Faz sentido eu mandar a proposta?"

Se não qualificou:
> "Sendo honesto — pelo que você descreveu, isso não é prioridade agora, e eu não acho que faça sentido você gastar tempo com isso. Se o tema mudar de patamar aí dentro, me chama."

Recusar avançar quando não qualificou constrói mais credibilidade que qualquer follow-up.

---

## 7. Matriz de objeções

| Objeção | Leitura real | Resposta |
|---|---|---|
| "Já bloqueamos IA por política interna" | Resolveu o risco criando outro | "Faz sentido como medida temporária. O problema é que política de bloqueio raramente é obedecida — as pessoas usam no celular. Você tem como verificar que o bloqueio funciona? E o custo de produtividade que os concorrentes de vocês estão capturando?" |
| "Não é prioridade agora" | Falta de gatilho, não falta de dor | "Entendo. A maioria só prioriza depois de um incidente ou de uma auditoria. Não estou pedindo orçamento hoje — queria só entender se isso entra no radar dos próximos 6 a 12 meses, e se tem alguma auditoria marcada nesse período." |
| "A política de privacidade do provedor já resolve" | Premissa factualmente frágil, e confunde duas coisas | "São coisas diferentes. A política do provedor governa o que ele faz; ela não documenta a base legal da sua empresa para a transferência, e é a sua que o art. 33 cobra. Sobre a política em si — o CTS da FGV avaliou sete plataformas contra catorze critérios da ANPD e nenhuma cumpre todos; as melhores ficam em onze, e uma das falhas que sobra é justamente não deixar claro para que país o dado vai. Posso te mandar o material, independente de a gente fazer negócio." |
| "Prefiro fornecedor internacional consolidado" | Aversão a risco de fornecedor pequeno | "Legítimo. A diferença concreta é que nenhum deles tem motor de política nativo para o art. 33 nem para sigilo profissional brasileiro. Isso normalmente vira trabalho manual do seu time depois. E sobre o risco de fornecedor pequeno — é real, e por isso o piloto é de 30 dias sem lock-in." |
| "Meu time consegue construir isso" | Verdade parcial, e é a objeção mais honesta | "Conseguem sim — o proxy é a parte fácil. A parte difícil é manter atualizada a tradução das normas por setor regulado e sustentar a trilha de auditoria. É trabalho contínuo, não projeto. A pergunta é se essa é a alocação certa dos seus engenheiros." |
| "Quanto custa?" (cedo demais) | Sinal de interesse, não de objeção | "Planos entre R$ 799 e R$ 2.900 por mês conforme volume. Mas antes de falar de preço, quero entender se faz sentido — não quero te vender algo que você não vai usar." |
| "Isso não deveria ser de graça / built-in?" | **Objeção de tese, não de venda** | Registrar. Se aparecer em mais de metade das calls, o modelo de monetização está errado e precisa girar antes de mais investimento. |

---

## 8. Estrutura da proposta comercial

Uma página. Enviada em até 24h após a call.

```
PROPOSTA — PILOTO BALUARTE
[Empresa] · [Data]

ESCOPO
• Integração em 1 fluxo de IA definido em conjunto
• Detecção e classificação de dado sensível
• Motor de política configurado para o setor de [X]
• Dashboard de auditoria
• 1 Dossiê de Conformidade ao fim do período

PRAZO: 30 dias, a partir de [data]

INVESTIMENTO: R$ [valor] (piloto)
Preço de tabela pós-piloto: R$ [valor]/mês

O QUE ESPERAMOS DE VOCÊS
• 1 ponto focal técnico
• 2 sessões de 30 min (kickoff e encerramento)
• Feedback estruturado ao fim

SEM LOCK-IN
Encerrado o piloto, seguir ou não é decisão de vocês.
Sem multa, sem carência, exportação de dados garantida.

VALIDADE DESTA PROPOSTA: 15 dias
```

**Por que "sem lock-in" em destaque:** é a maior objeção não-verbalizada ao comprar de fornecedor pequeno. Antecipar remove atrito sem precisar ser perguntado.

---

## 9. Canais além do LinkedIn

Ordem de prioridade após o LinkedIn estabilizar.

| Canal | Por quê | Quando ativar |
|---|---|---|
| **Conteúdo próprio (LinkedIn + blog)** | Compliance é venda por autoridade. Cada post que explica o art. 33 com precisão vale mais que 50 convites | Imediato, em paralelo |
| **Associações e comunidades de DPO** | Onde o ICP já está reunido e discutindo exatamente isso | Semana 4 |
| **Eventos de proteção de dados e segurança** | Alto custo de tempo, altíssima qualificação | Após 3 clientes pagantes |
| **Parceria com escritórios de advocacia de proteção de dados** | Eles já auditam clientes e encontram essa lacuna. Indicação natural | Semana 8 — e o curador jurídico é a ponte |
| **Contadores e consultorias de compliance** | Canal de indicação de baixo custo | Após motion estabilizada |

**O canal de maior retorno oculto:** o próprio curador jurídico. Um DPO experiente ou advogado de proteção de dados traz rede pronta e credibilidade emprestada — outra razão para essa contratação vir antes da venda, não depois.

---

## 10. Funil e metas

### 10.1 Estágios

```
Lista qualificada
      ↓
Conexão aceita          (meta: 30–40%)
      ↓
Resposta ao follow-up   (meta: 15–25%)
      ↓
Discovery call          (meta: 8–12% da conexão aceita)
      ↓
Qualificado (pergunta 8 positiva)  (meta: 30% das calls)
      ↓
Proposta enviada
      ↓
Piloto pago             (meta: 50% das propostas)
      ↓
Contrato recorrente     (meta: 60% dos pilotos)
```

### 10.2 Metas dos primeiros 90 dias

| Marco | Meta | Prazo |
|---|---|---|
| Discovery calls realizadas | 10–15 | Dia 45 |
| Leads qualificados | 5+ | Dia 60 |
| Pilotos pagos assinados | 3 | Dia 75 |
| Conversão de piloto em contrato | 2 | Dia 90 |

### 10.3 O gate de decisão

**Aos 90 dias, três cenários:**

| Cenário | Leitura | Ação |
|---|---|---|
| 3 pilotos, 2 convertidos | Tese validada | Investir em produto e escalar motion |
| 3 pilotos, 0 convertidos | Dor real, valor não entregue | Problema é produto — iterar, não desistir |
| Menos de 2 pilotos assinados | Dor não é aguda o suficiente, ou ICP errado | **Girar a tese antes de investir mais** |

E o sinal de alerta transversal: se "isso deveria ser de graça" aparecer em mais da metade das calls, o problema não é execução comercial — é o modelo de monetização. Nesse caso, o giro certo provavelmente é para consultoria de implementação com ticket alto, não para SaaS de auto-serviço.

---

## 11. O que medir toda sexta-feira

Trinta minutos, planilha simples, cinco números:

1. Convites enviados / aceitos na semana
2. Calls realizadas
3. Leads qualificados (pergunta 8 positiva)
4. Objeção mais repetida da semana
5. Custo total da semana (ferramentas + tempo alocado)

O item 4 é o mais valioso e o mais ignorado. Padrão de objeção é o sinal mais rápido de que a mensagem ou a tese precisa mudar — muito antes de o número de vendas mostrar isso.

---

*Documento Comercial & GTM — BALUARTE. Elaborado em agosto de 2026, com as fontes corrigidas após verificação (ver `docs/fontes.md`). Nenhum número ou caso entra em material de venda sem estar registrado como confirmado lá. Referências de mercado ainda não verificadas — como relatórios de custo de violação de dados — precisam ser confirmadas antes do uso.*
