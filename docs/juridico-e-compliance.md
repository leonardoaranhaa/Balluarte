# BALUARTE — Jurídico & Compliance

*Documento vivo. Revisão obrigatória a cada mudança normativa relevante ou a cada 6 meses.*

> **Aviso:** este documento é um mapa de estrutura e requisitos, não peça jurídica. Todos os instrumentos aqui descritos devem ser redigidos ou revisados por advogado antes de qualquer uso comercial. O que está aqui serve para você chegar na reunião com o advogado sabendo exatamente o que pedir — e economizar horas caras.

---

## 1. O paradoxo central

BALUARTE vende disciplina no tratamento de dado. Isso significa que a própria empresa opera sob um padrão mais alto que o cliente médio: **qualquer falha de compliance interna não é só um problema jurídico, é a destruição do argumento de venda.**

Um DPO que descobre que o fornecedor de governança de IA não tem RIPD próprio não renegocia — ele encerra e conta para a rede dele.

Esse é o princípio que ordena tudo abaixo.

---

## 2. Mapa normativo aplicável

### 2.1 Como controlador dos próprios dados

| Norma | O que impõe |
|---|---|
| LGPD (Lei 13.709/2018) | Base legal, direitos do titular, segurança, notificação de incidente |
| Marco Civil da Internet (Lei 12.965/2014), art. 15 | Guarda de registros de acesso a aplicação por prazo mínimo legal |
| Código de Defesa do Consumidor | Aplicável em parte à relação B2B com pequenas empresas |

### 2.2 Como operador de dados dos clientes

| Norma | O que impõe |
|---|---|
| LGPD art. 39 | Operador trata apenas conforme instrução do controlador |
| LGPD art. 42–45 | Responsabilidade solidária em caso de dano — motivo pelo qual o DPA precisa ser preciso |
| LGPD art. 46–49 | Medidas de segurança técnicas e administrativas |

### 2.3 Como produto que interage com transferência internacional

| Norma | O que impõe |
|---|---|
| **LGPD art. 33** | Núcleo jurídico do produto. Hipóteses autorizativas de transferência internacional |
| Resolução ANPD sobre transferência internacional | Cláusulas-padrão contratuais e requisitos formais |
| Nota Técnica nº 54/2025/FIS/CGF/ANPD — Mapa de Temas Prioritários 2026-2027 | IA e tecnologias emergentes entre os eixos de fiscalização do biênio |
| Nota Técnica nº 1/2026/FIS/CGF/ANPD — sistema Grok | Precedente de atuação da autoridade sobre plataforma de IA |

### 2.4 Normas setoriais que o produto precisa conhecer (não cumprir diretamente)

Estas não vinculam o BALUARTE — vinculam o cliente. Mas alimentam a Matriz de Classificação e por isso são parte do produto:

| Setor | Norma |
|---|---|
| Financeiro | Sigilo bancário (LC 105/2001), regulação Bacen aplicável |
| Saúde | LGPD art. 11 (dado sensível), resoluções CFM sobre prontuário eletrônico |
| Jurídico | Estatuto da OAB, sigilo profissional, segredo de justiça (CPC) |

### 2.5 Em observação (ainda não vigente)

**PL 2338/2023 — Marco Legal da IA.** Aprovado no Senado em dezembro de 2024, em tramitação na Câmara, com votação sucessivamente adiada e questionamento de vício de iniciativa. Não é lei.

Posição estratégica: **construir como se já fosse.** O modelo baseado em risco tende a exigir avaliação, rastreabilidade e explicabilidade — exatamente o que o BALUARTE produz como efeito natural do seu funcionamento. Isso é raro e é vantagem: a maioria dos produtos de IA vai ter que se adaptar; este já nasce alinhado.

**Regra de comunicação:** nunca usar o PL como argumento de urgência de venda enquanto não for lei. "A lei vai exigir" é promessa; "o art. 33 já exige" é fato. Vender com fato.

---

## 3. Instrumentos contratuais

### 3.1 Termos de Uso / Contrato de Prestação de Serviço SaaS

Cláusulas que precisam existir, com atenção especial às marcadas:

| Cláusula | Ponto de atenção |
|---|---|
| Objeto e escopo do serviço | Descrever como **ferramenta de controle técnico e registro**, jamais como certificação de conformidade |
| **Limitação de responsabilidade** ⚠️ | Teto de indenização vinculado ao valor pago nos últimos 12 meses. Sem isso, um fundador solo assume risco ilimitado |
| **Exclusão de garantia de conformidade** ⚠️ | Cláusula expressa: BALUARTE não declara nem garante conformidade do cliente com a LGPD; a decisão sobre base legal e risco residual é do encarregado do cliente |
| **Modo de falha** ⚠️ | Definir se o serviço opera em *fail-closed* (padrão) ou *fail-open*. Se o cliente optar por fail-open, isso precisa ser escolha registrada dele |
| SLA e disponibilidade | Ser conservador. Prometer 99,9% sem infraestrutura para sustentar é criar passivo |
| Precificação e reajuste | Reajuste anual por IPCA previsto desde o primeiro contrato |
| Vigência, rescisão, portabilidade | Sem lock-in. Exportação de dados garantida na saída — é argumento comercial e é exigência de LGPD |
| Confidencialidade mútua | — |
| Foro e lei aplicável | Brasil, comarca definida |

### 3.2 DPA — Acordo de Tratamento de Dados

Instrumento separado, anexo ao contrato principal. É o documento que o DPO do cliente vai ler com atenção — e é onde a venda se ganha ou se perde tecnicamente.

**Conteúdo mínimo:**

1. **Papéis** — cliente é controlador, BALUARTE é operador. Sem ambiguidade.
2. **Objeto e finalidade** — tratar dado exclusivamente para prestar o serviço contratado.
3. **Categorias de dado e de titulares** — descrição realista do que trafega.
4. **Instruções documentadas** — BALUARTE trata apenas conforme instrução do controlador, materializada na política configurada.
5. **Medidas de segurança** — criptografia em trânsito e repouso, controle de acesso, segregação por tenant, log de acesso a produção.
6. **Suboperadores** ⚠️ — **lista nominal dos provedores de IA integrados**, com direito do cliente de objetar à inclusão de novos. Esta é a cláusula mais escrutinada e a que mais gera pergunta em call comercial.
7. **Transferência internacional** ⚠️ — descrição precisa de quando ocorre, sob qual hipótese do art. 33, e quais salvaguardas técnicas se aplicam (mascaramento, tokenização, roteamento nacional).
8. **Notificação de incidente** — prazo definido em horas, não em "prazo razoável".
9. **Suporte aos direitos do titular** — como BALUARTE auxilia o cliente a responder solicitações.
10. **Eliminação ou devolução** ao fim do contrato.
11. **Direito de auditoria** — o cliente pode auditar; definir formato (relatório, questionário, ou auditoria presencial mediante aviso) para não virar custo operacional inviável.

### 3.3 Política de Privacidade

Da própria empresa, para visitantes do site e usuários do produto. Requisitos: linguagem clara, **disponível em português**, bases legais explícitas por finalidade, canal do encarregado, e política de cookies.

Um dos catorze critérios do estudo da FGV é ter política de privacidade publicada, e as sete plataformas avaliadas cumprem esse. O padrão a superar não é publicar — é o que as melhores ainda erram: deixar claro **para que países o dado é enviado**. Essa é a lacuna que o BALUARTE cobra dos outros, então é a que a nossa própria política precisa fechar primeiro.

### 3.4 Contrato com o curador jurídico

Duas modalidades, decidir antes do primeiro cliente:

| Modalidade | Instrumento | Quando faz sentido |
|---|---|---|
| Equity | Acordo de sócios com vesting (4 anos, cliff de 1) + alteração de contrato social | Caixa curto, alinhamento de longo prazo |
| Retainer | Contrato de prestação de serviço com escopo e SLA de revisão | Preservar controle societário |

Em qualquer modalidade: definir explicitamente que a responsabilidade técnica pela Matriz de Classificação é dessa pessoa, com registro nominal por entrada da matriz.

---

## 4. RIPD — Relatório de Impacto à Proteção de Dados

**Obrigatório antes de processar qualquer dado real de cliente.** Não é formalidade — é o documento que um DPO vai pedir para ver, e não ter é sinal vermelho imediato.

### Estrutura

| Seção | Conteúdo |
|---|---|
| 1. Descrição do tratamento | Fluxo completo: entrada da requisição → classificação → política → transformação → provedor → resposta |
| 2. Necessidade e proporcionalidade | Por que o tratamento é necessário e por que é o mínimo necessário |
| 3. Categorias de dado | Incluindo dado sensível (art. 11) quando o cliente for do setor de saúde |
| 4. Fluxo de dados e suboperadores | Diagrama + lista nominal de provedores |
| 5. Transferência internacional | Quando ocorre, hipótese do art. 33, salvaguardas aplicadas |
| 6. Riscos identificados | Ver seção 5 abaixo |
| 7. Medidas mitigadoras | Técnicas e administrativas, por risco |
| 8. Risco residual | Avaliação honesta do que sobra depois das mitigações |
| 9. Responsável e data | Encarregado nomeado |

---

## 5. Riscos de compliance da própria operação

| Risco | Gravidade | Mitigação |
|---|---|---|
| **Log do BALUARTE conter PII em texto claro** | Existencial | Registrar apenas tipo e quantidade de entidade, nunca valor. Auditoria manual dos logs antes de qualquer produção. Este é o risco que mata a empresa. |
| **Cofre de tokenização comprometido** | Existencial | Isolamento por tenant, criptografia com chave separada por cliente, acesso auditado |
| Provedor de IA usar dado para treinamento | Alta | Contrato de não-treinamento verificado por escrito antes da integração entrar em produção. Revisão trimestral. |
| Cliente alegar que BALUARTE "garantiu" conformidade | Alta | Cláusula expressa de exclusão + linguagem consistente em contrato, site, interface e fala do fundador |
| Incidente de segurança sem plano de resposta | Alta | Plano de resposta escrito antes do primeiro cliente, com prazo de notificação definido |
| Ausência de RIPD ao ser questionado em due diligence | Média | Elaborar antes do primeiro dado real, não depois |
| Prospecção com scraping automatizado | Média | Proibição interna absoluta. Além de violar Termos de Uso do LinkedIn, é incoerência fatal com o produto |

---

## 6. Gestão de fornecedores de IA

Cada provedor integrado é suboperador. Antes de qualquer integração entrar em produção:

**Checklist por provedor:**

- [ ] Contrato de não-treinamento sobre dado de API, verificado por escrito
- [ ] Política de retenção conhecida e documentada
- [ ] Localização de processamento identificada
- [ ] Exposição jurisdicional avaliada (CLOUD Act ou equivalente)
- [ ] Provedor listado nominalmente no DPA
- [ ] Clientes notificados antes da inclusão de novo provedor

**Revisão trimestral:** políticas de privacidade e termos de provedores mudam sem aviso, e o produto inteiro depende delas. Data fixa no calendário.

---

## 7. A regra que atravessa tudo

Já registrada nos documentos de marca e produto, repetida aqui porque é cláusula contratual antes de ser mensagem:

> **BALUARTE não declara conformidade. BALUARTE fornece controle técnico e trilha de evidência. A decisão sobre base legal, adequação e risco residual é do encarregado de dados do cliente.**

E a variação sobre soberania:

> Rotear por servidor em território nacional **não elimina, por si só**, exposição jurisdicional quando o destino final é provedor estrangeiro. O ganho real vem do mascaramento, da tokenização ou do roteamento para modelo hospedado nacionalmente.

Ambas precisam aparecer, com esse rigor, em: contrato, DPA, política de privacidade, site, interface do produto e material comercial. Consistência entre esses seis pontos é o que sustenta a defesa se algo der errado — e inconsistência entre eles é o que a destrói.

---

## 8. Plano de resposta a incidente

Escrito antes do primeiro cliente. Versão mínima viável:

| Fase | Ação | Prazo |
|---|---|---|
| 1. Detecção | Alerta automático ou reporte | Imediato |
| 2. Contenção | Isolar tenant afetado, revogar chaves comprometidas | 1h |
| 3. Avaliação | Escopo, dados envolvidos, titulares afetados | 24h |
| 4. Notificação ao cliente | Comunicação formal ao controlador | Prazo definido em DPA |
| 5. Notificação à ANPD | Quando houver risco relevante, via canal oficial | Prazo regulatório vigente |
| 6. Registro e post-mortem | Documentação completa do incidente e correções | 7 dias |

---

## 9. Calendário de compliance

| Frequência | Item |
|---|---|
| Trimestral | Revisão de políticas dos provedores de IA |
| Trimestral | Revisão da Matriz de Classificação com o curador jurídico |
| Semestral | Revisão do RIPD |
| Semestral | Teste do plano de resposta a incidente |
| Anual | Revisão completa de contratos e DPA |
| Contínuo | Acompanhamento da tramitação do PL 2338 e de novas notas técnicas da ANPD |

---

## 10. Checklist de partida

Nada de dado real de cliente antes de todos os itens estarem verdadeiros:

- [ ] Empresa constituída, CNPJ ativo
- [ ] Encarregado de dados (DPO) nomeado — pode ser o próprio fundador nesta fase, formalmente designado
- [ ] Política de Privacidade publicada, em português
- [ ] Termos de Uso revisados por advogado
- [ ] DPA modelo pronto
- [ ] RIPD elaborado
- [ ] Contratos de não-treinamento confirmados com cada provedor integrado
- [ ] Plano de resposta a incidente escrito
- [ ] Verificação manual: nenhum PII em texto claro em nenhum log
- [ ] Infraestrutura de produção em território nacional
- [ ] Relação com o curador jurídico formalizada

---

*Documento Jurídico & Compliance — BALUARTE. Elaborado em agosto de 2026. Mapa de requisitos, não peça jurídica — todos os instrumentos exigem redação ou revisão por advogado. Status do PL 2338/2023 e das resoluções da ANPD verificados na data de elaboração; reconfirmar antes de uso.*
