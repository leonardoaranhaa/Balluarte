# Documentos operacionais do BALUARTE

Estes documentos não são anotação — são o que vai ser executado conforme o
projeto avança. Cada um define a sua própria cadência de revisão e é documento
vivo.

O contexto que o Claude Code carrega em toda sessão está em `/CLAUDE.md`, na
raiz. Ele resume as regras inegociáveis e aponta para cá.

---

## O que é cada arquivo

| Arquivo | Serve para | Revisar |
|---|---|---|
| [`produto-e-tecnico.md`](produto-e-tecnico.md) | PRD do MVP, arquitetura, Matriz de Classificação por setor, API, roadmap, riscos técnicos | A cada ciclo de piloto |
| [`marca-e-operacional.md`](marca-e-operacional.md) | Nome, posicionamento, tom de voz, identidade visual, estrutura societária, preço e desconto, rotina, políticas internas | A cada 90 dias ou mudança material |
| [`comercial-e-gtm.md`](comercial-e-gtm.md) | Segmentação, mensagem por persona, one-pager, pitch deck, script de discovery, matriz de objeções, funil e metas | A cada bloco de 10 discovery calls |
| [`juridico-e-compliance.md`](juridico-e-compliance.md) | Mapa normativo, contratos, DPA, RIPD, riscos de compliance, plano de incidente, calendário | A cada mudança normativa ou 6 meses |
| [`fontes.md`](fontes.md) | Registro do que foi verificado, do que foi refutado e do que está em aberto | Sempre que um fato entrar, cair ou virar dúvida |
| [`playbooks/construcao.md`](playbooks/construcao.md) | Sequência de prompts de build, Fase 0 a 5, com critério de saída por fase | Ao fim de cada fase |
| [`playbooks/marketing.md`](playbooks/marketing.md) | Bloco de contexto mestre, prompts de landing, perfil LinkedIn e prospecção | Quando o contexto mestre mudar |

---

## Ordem de execução

A ordem importa. Cada documento define regras de sequenciamento próprias, e
todas convergem no mesmo princípio: **fundador solo que constrói
horizontalmente termina com cinco coisas pela metade e nada vendável.**

### Trilha de produto — `playbooks/construcao.md`

| Fase | Entrega | Critério de saída |
|---|---|---|
| 0 | Validação da premissa (LiteLLM + Presidio + recognizers BR) | Falso negativo **zero** em CPF/CNPJ formatados |
| 1 | Motor de política | Determinismo provado em teste, explicabilidade funcionando |
| 2 | Trilha de auditoria | Teste de vazamento de PII passando, integridade verificável |
| 3 | Integração do proxy | Troca de URL base sem alteração de código, p95 medido |
| 4 | Perfis de política + Dossiê | Três perfis implementados, Dossiê com declaração de escopo |
| 5 | Dashboard | Quatro telas funcionais |

Nada da v2 (Modo Soberano, inferência nacional) começa antes de três clientes
pagantes recorrentes na v1.

### Trilha comercial — `comercial-e-gtm.md`

Founder-led, alto toque, baixo volume. Segmento A (fintech/healthtech média) nas
primeiras oito semanas; B (escritórios) da semana 6; C (integradoras para
governo) só depois do quinto cliente pagante.

O gate dos 90 dias: menos de dois pilotos assinados significa girar a tese,
não trabalhar mais horas.

### Trilha de constituição — `marca-e-operacional.md` §11 e `juridico-e-compliance.md` §10

Nenhum dado real de cliente antes de: empresa constituída, encarregado nomeado,
Política de Privacidade publicada, Termos revisados por advogado, DPA modelo,
RIPD elaborado, contratos de não-treinamento confirmados, plano de incidente
escrito, verificação manual de que nenhum PII em claro aparece em log, e
produção em território nacional.

---

## Duas regras que atravessam todos os documentos

**Sobre conformidade.** BALUARTE não declara conformidade. Fornece controle
técnico e trilha de evidência. A decisão sobre base legal, adequação e risco
residual é do encarregado de dados do cliente. Isso precisa aparecer com o mesmo
rigor em contrato, DPA, política de privacidade, site, interface e material
comercial — a consistência entre esses seis pontos é o que sustenta a defesa se
algo der errado.

**Sobre soberania.** Rotear por servidor em território nacional não elimina, por
si só, exposição jurisdicional quando o destino final é provedor estrangeiro. O
ganho real vem do mascaramento, da tokenização ou do roteamento para modelo
hospedado nacionalmente.

---

## Sobre as correções aplicadas na entrada

Estes documentos entraram no repositório com três correções factuais, feitas
depois de verificação contra fonte primária:

1. **Removida** a multa de 450 mil euros à fintech de Viena — não existe em
   fonte primária. Saiu do slide 2 do pitch deck, do bloco de contexto mestre de
   marketing e do Post 2 de aquecimento.
2. **Corrigida** a descrição do estudo da FGV — é análise de documentação contra
   catorze critérios da ANPD, não auditoria de conformidade.
3. **Corrigidas** as notas técnicas da ANPD para as duas que constam da central
   de conteúdo oficial.

O motivo, o rastro e o que continua em aberto estão em [`fontes.md`](fontes.md).
Ele não é documentação sobre o passado: é o filtro que qualquer fato precisa
passar antes de sair em material público.
