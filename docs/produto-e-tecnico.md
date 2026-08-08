# BALUARTE — Produto & Técnico

*Documento vivo. Revisar ao fim de cada ciclo de piloto.*

---

## 0. Aviso que precede tudo neste documento

Antes de qualquer decisão de arquitetura, é preciso registrar um achado que muda a estratégia de construção:

**O stack técnico base já existe, maduro e open source.** O LiteLLM (proxy de LLM) tem integração documentada e oficial com o Microsoft Presidio (detecção e anonimização de PII), operando como *guardrail* em modo `pre_call` — ou seja, interceptando e mascarando **antes** que a requisição chegue ao provedor de modelo. O Presidio é MIT, tem mais de 8.800 estrelas no GitHub, 183 contribuidores, oito anos de desenvolvimento e releases ativos em 2026, e foi construído explicitamente para receber *custom recognizers*.

Mais direto ainda: **já existe tutorial público, escrito por um brasileiro em 2026, ensinando exatamente a montar reconhecedor customizado de CPF no Presidio dentro do LiteLLM**, com regex para CPF pontuado e não-pontuado, operador de máscara customizado, e a arquitetura completa em quatro contêineres.

### O que isso significa

**Lado bom:** você não precisa construir o núcleo. Um MVP funcional de detecção e mascaramento é questão de dias, não de meses. Isso libera 100% do seu esforço para o que realmente é o produto.

**Lado ruim, e é o que importa:** qualquer engenheiro competente chega no mesmo lugar num fim de semana. **O proxy não é o produto. O mascaramento não é o produto.** Se o BALUARTE for vendido como "gateway que mascara CPF", ele é uma configuração de Docker Compose com preço em cima — e o primeiro CTO que fizer uma busca vai descobrir isso e derrubar a venda na hora.

### A conclusão arquitetural

> O produto é tudo o que fica **em volta** do stack open source: a matriz de classificação por setor regulado, o motor de política auditável, a trilha de evidência com valor jurídico, e o Dossiê de Conformidade. O LiteLLM e o Presidio são infraestrutura — como Postgres. Ninguém vende "Postgres com markup".

Todo o resto deste documento parte dessa premissa.

---

## 1. PRD do MVP

### 1.1 Objetivo do MVP

Provar, com tráfego real de três clientes-piloto, que:
1. A detecção de dado sensível brasileiro funciona com precisão aceitável em texto corporativo real.
2. O Dossiê de Conformidade tem valor percebido suficiente para justificar recorrência.

Não é objetivo do MVP: escalar, ter interface bonita, suportar todos os provedores, ou entregar inferência soberana.

### 1.2 Escopo — dentro

| # | Funcionalidade | Justificativa |
|---|---|---|
| F1 | Proxy compatível com formato OpenAI/Anthropic | Troca de URL base, sem reescrita de código no cliente |
| F2 | Detecção de PII brasileira (CPF, CNPJ, RG, CNS, telefone, e-mail, nome, endereço) | Núcleo da proposta |
| F3 | Mascaramento e tokenização reversível | Diferencial sobre redação simples — permite o dado voltar na resposta |
| F4 | Motor de política por regra declarativa | O que faz o produto ser configurável por setor |
| F5 | Log de auditoria imutável | Base do Dossiê |
| F6 | Dashboard mínimo: volume, tipos detectados, política aplicada | Visibilidade — o que o DPO compra |
| F7 | Geração do Dossiê de Conformidade em PDF | O entregável de maior valor percebido |
| F8 | Gestão de chaves de API por cliente | Requisito mínimo de multi-tenant |

### 1.3 Escopo — fora (explicitamente)

| Item | Por que fica fora do MVP |
|---|---|
| Inferência soberana (modelo hospedado no Brasil) | Componente mais caro e lento. Entra na v2, financiado pela receita do MVP |
| Detecção em imagem e documento anexo | Escopo grande, dor menos aguda no primeiro momento |
| Streaming de resposta | Complica o mascaramento de saída. Adiar |
| Self-service / signup automático | Venda é founder-led. Onboarding manual é aceitável e até desejável nos 10 primeiros clientes |
| Integrações com SIEM | Só quando um cliente pedir com contrato na mesa |
| App mobile | Nunca, provavelmente |

### 1.4 Critérios de aceitação do MVP

- Cliente troca a URL base e o tráfego funciona sem alteração de código de aplicação.
- Taxa de falso negativo em CPF/CNPJ formatados: **zero** (são determinísticos, não há desculpa).
- Latência adicional introduzida pelo gateway: **abaixo de 300ms** no percentil 95.
- Dossiê gerado com assinatura digital válida e verificável.
- Nenhum dado sensível em texto claro nos próprios logs do BALUARTE — o produto não pode ser o vazamento.

---

## 2. Arquitetura técnica

### 2.1 Visão geral

```
Aplicação do cliente
        │  (troca só a URL base)
        ▼
┌───────────────────────────────────────┐
│  BALUARTE                             │
│                                       │
│  1. Autenticação e roteamento         │
│  2. Classificação (Presidio + custom) │
│  3. MOTOR DE POLÍTICA  ← o produto    │
│  4. Transformação (máscara/token)     │
│  5. Registro de auditoria             │
└───────────────┬───────────────────────┘
                │
      ┌─────────┴─────────┐
      ▼                   ▼
 Provedor externo    Modelo nacional
 (Claude, GPT...)    (v2 — Modo Soberano)
                │
                ▼
      Destokenização na resposta
                │
                ▼
      Retorno à aplicação
```

### 2.2 Decisões de stack e a razão de cada uma

| Camada | Escolha | Racional |
|---|---|---|
| Proxy base | **LiteLLM** (open source) | Integração nativa com Presidio, suporte multi-provedor pronto, compatibilidade de formato resolvida. Construir do zero seria vaidade de engenharia. |
| Detecção | **Presidio** + recognizers customizados brasileiros | MIT, extensível por design, oito anos de maturidade. Os recognizers de CPF/CNPJ/RG/CNS são nossos. |
| Motor de política | **Código próprio, determinístico e versionado** | **Não pode ser LLM.** Precisa ser auditável, reproduzível e explicável em juízo. |
| Tokenização | Criptografia simétrica + cofre de mapeamento por tenant | Padrão de mercado. Determinística — mesmo valor sempre gera mesmo token, para o modelo conseguir raciocinar sobre ele. |
| Auditoria | Postgres com tabela append-only + hash encadeado | Imutabilidade verificável sem overengineering de blockchain |
| Aplicação/dashboard | Next.js | Solo-buildable, rápido |
| Hospedagem | Infraestrutura em território nacional desde o dia 1 | Coerência com o discurso. Vender soberania rodando em us-east-1 é indefensável. |

### 2.3 A camada que é o produto: Motor de Política

Regra declarativa, versionada, legível por humano não-técnico. Formato conceitual:

```yaml
politica:
  nome: "Saúde — CFM/LGPD"
  versao: 3
  vigente_desde: 2026-08-01
  regras:
    - entidade: DADO_SAUDE
      acao: bloquear
      base_normativa: "Resolução CFM sobre prontuário eletrônico"
    - entidade: CPF
      acao: tokenizar
      base_normativa: "LGPD art. 33"
    - entidade: NOME_PACIENTE
      acao: tokenizar
    - padrao: nenhum_dado_sensivel
      acao: permitir
```

**Três propriedades inegociáveis dessa camada:**

1. **Determinismo.** Mesma entrada, mesma política, mesma saída. Sempre. Se um auditor perguntar "por que essa requisição foi bloqueada em março?", a resposta precisa ser reconstituível.
2. **Versionamento.** Toda mudança de política gera nova versão. O log de auditoria registra qual versão estava vigente em cada requisição.
3. **Base normativa em cada regra.** Toda regra carrega o artigo, resolução ou norma que a justifica. Isso não é enfeite — é o que transforma configuração técnica em evidência de conformidade.

### 2.4 Trilha de auditoria — o que registrar

Por requisição:

| Campo | Observação |
|---|---|
| ID da requisição, timestamp (UTC) | — |
| Tenant, usuário/chave de origem | — |
| Provedor de destino | — |
| Entidades detectadas (tipo + quantidade) | **Nunca o valor em claro** |
| Ação aplicada por entidade | mascarado / tokenizado / bloqueado / permitido |
| Versão da política vigente | Crítico para reconstituição |
| Hash do registro anterior | Encadeamento para provar não-adulteração |

**Regra absoluta:** o log registra *que* um CPF foi detectado, nunca *qual* CPF. Um produto de privacidade que constrói um banco de dados de PII em texto claro é uma bomba jurídica com a própria marca estampada.

---

## 3. Matriz de Classificação por Setor

Este é o ativo central da empresa. Tudo o mais é replicável; isto não é — porque exige entender norma, não só código.

### 3.1 Estrutura

Para cada setor regulado: entidades de dado relevantes, ação padrão, base normativa, e nível de confiança mínimo para acionar a regra.

### 3.2 Perfil — Financeiro (fintechs)

| Entidade | Ação padrão | Base normativa |
|---|---|---|
| CPF / CNPJ | Tokenizar | LGPD art. 33 |
| Dado de conta, agência, cartão | Bloquear | Sigilo bancário (LC 105/2001) |
| Score, histórico de crédito | Bloquear | LGPD art. 5º + regulação Bacen |
| Nome + endereço combinados | Tokenizar | LGPD art. 33 |
| Texto sem PII | Permitir | — |

### 3.3 Perfil — Saúde (healthtechs, clínicas)

| Entidade | Ação padrão | Base normativa |
|---|---|---|
| Diagnóstico, CID, prescrição | Bloquear ou rotear para Modo Soberano | LGPD art. 11 (dado sensível) + resoluções CFM |
| CNS (Cartão Nacional de Saúde) | Tokenizar | LGPD art. 11 |
| Nome de paciente | Tokenizar | Sigilo médico |
| CPF | Tokenizar | LGPD art. 33 |

### 3.4 Perfil — Jurídico (escritórios)

| Entidade | Ação padrão | Base normativa |
|---|---|---|
| Nome de cliente / parte | Tokenizar | Sigilo profissional (EOAB) |
| Número de processo | Tokenizar | Sigilo + segredo de justiça quando aplicável |
| Conteúdo de peça em segredo de justiça | Bloquear | CPC + EOAB |
| Documento de identificação | Tokenizar | LGPD art. 33 |

### 3.5 Governança da matriz

- Toda entrada da matriz tem **um responsável nomeado** — o curador jurídico, não o fundador.
- Revisão trimestral obrigatória.
- Mudança de norma gera nova versão da política, nunca edição silenciosa da anterior.
- **Onde a norma for ambígua, o padrão é a ação mais restritiva**, com a ambiguidade documentada. Nunca chutar para o lado permissivo.

---

## 4. Especificação de API

### 4.1 Princípio de compatibilidade

A API do BALUARTE é **deliberadamente idêntica** à do provedor que ela substitui. Isso não é preguiça — é a única forma de a promessa "troca só a URL base" ser verdadeira.

```
Antes:  https://api.anthropic.com/v1/messages
Depois: https://api.baluarte.com.br/v1/messages
```

Mesmo corpo de requisição. Mesmo formato de resposta. Mesma estrutura de erro.

### 4.2 Cabeçalhos próprios (opcionais)

| Cabeçalho | Função |
|---|---|
| `X-Baluarte-Policy` | Sobrescreve a política padrão do tenant para esta requisição |
| `X-Baluarte-Trace-Id` | ID de correlação fornecido pelo cliente, para amarrar ao sistema dele |

### 4.3 Metadados de resposta

Cabeçalhos adicionados na resposta, sem alterar o corpo:

```
X-Baluarte-Entities-Detected: CPF:2,EMAIL:1
X-Baluarte-Action: tokenized
X-Baluarte-Policy-Version: 3
X-Baluarte-Request-Id: blt_xxxxx
```

### 4.4 Endpoints administrativos

| Método | Rota | Função |
|---|---|---|
| `GET` | `/admin/audit` | Consulta paginada da trilha de auditoria |
| `POST` | `/admin/dossier` | Gera Dossiê de Conformidade para um período |
| `GET` | `/admin/policies` | Lista políticas e versões |
| `POST` | `/admin/policies` | Cria nova versão de política (nunca edita existente) |

### 4.5 Comportamento em falha

Decisão de produto, não técnica, e precisa estar no contrato:

**Padrão: fail-closed.** Se o classificador estiver indisponível, a requisição é **bloqueada**, não liberada. Um produto de proteção que degrada para "deixa passar tudo" é pior que não existir, porque cria confiança falsa.

Cliente pode optar por `fail-open` explicitamente, com registro em contrato e no log de auditoria de que essa escolha foi dele.

---

## 5. Roadmap

### v0 — Protótipo interno (semanas 1–3)
LiteLLM + Presidio + recognizers brasileiros + log básico. Rodando localmente com tráfego sintético. Objetivo: validar precisão de detecção, não vender.

### v1 — MVP de piloto (semanas 4–10)
As oito funcionalidades da seção 1.2. Multi-tenant mínimo, dashboard funcional, Dossiê em PDF assinado. Objetivo: sustentar três clientes-piloto pagos.

### v2 — Modo Soberano (mês 4–8, financiado pela receita da v1)
Roteamento de tráfego classificado como sensível para modelo aberto hospedado em infraestrutura nacional. **Esta é a entrega que fecha o argumento de soberania de verdade** — até aqui, o produto entrega controle e evidência, não soberania plena.

### v3 — Profundidade (mês 9+)
Detecção em documento anexo, streaming, integrações com SIEM, perfis de política adicionais por setor, e possivelmente self-service.

**Regra de sequenciamento:** nada da v2 começa antes de três clientes pagantes recorrentes na v1. Construir a camada cara antes de validar a barata é o erro clássico de fundador técnico.

---

## 6. Riscos técnicos e mitigações

| Risco | Gravidade | Mitigação |
|---|---|---|
| **Falso negativo em PII** — dado sensível passa sem detecção | Crítica | CPF/CNPJ formatados são determinísticos (regex + validação de dígito verificador): zero tolerância. Nome e endereço dependem de NER, onde falso negativo é inevitável — **isso precisa estar no contrato e na interface, não escondido.** |
| **Falso positivo** — bloqueia tráfego legítimo e o cliente desliga o produto | Alta | Limiar de confiança configurável por entidade. Modo "observar" antes de "bloquear" no onboarding de cada cliente. |
| **Latência** degrada a experiência e vira motivo de churn | Alta | Classificação em paralelo quando possível, cache de decisão para padrões repetidos, meta de 300ms no p95 monitorada. |
| **O próprio BALUARTE vazar dados** | Existencial | Nunca logar valor em claro. Cofre de tokenização isolado por tenant. Criptografia em repouso e em trânsito. Auditoria de acesso a produção. |
| **Provedor de IA muda formato de API** e quebra a compatibilidade | Média | Herdada do LiteLLM, que já mantém isso — uma das razões de não construir do zero. |
| **Replicabilidade do stack** (ver seção 0) | Estratégica | Único mitigante real: profundidade da matriz de classificação e valor jurídico do Dossiê. Não é problema de engenharia. |

---

## 7. Ambiente e operação

| Item | Definição |
|---|---|
| Ambientes | Desenvolvimento local, staging, produção |
| Infraestrutura | Território nacional, desde o dia 1 |
| Backup | Diário, retenção mínima alinhada ao Marco Civil (art. 15) |
| Monitoramento | Latência p50/p95/p99, taxa de erro, volume por tenant |
| Alertas | Falha de classificador, latência acima do SLO, erro de provedor |
| Acesso a produção | Só o fundador nesta fase, com log de acesso ativo |

---

## 8. Definição de "pronto para vender"

Checklist objetivo. Não marcar reunião comercial de piloto antes de todos os itens estarem verdadeiros:

- [ ] Detecção de CPF e CNPJ com zero falso negativo em conjunto de teste
- [ ] Tokenização reversível funcionando ponta a ponta
- [ ] Três perfis de política prontos (financeiro, saúde, jurídico), validados pelo curador jurídico
- [ ] Trilha de auditoria com encadeamento de hash funcionando
- [ ] Dossiê de Conformidade gerado com assinatura digital verificável
- [ ] Latência p95 abaixo de 300ms medida, não estimada
- [ ] Nenhum PII em texto claro em nenhum log do sistema — verificado por inspeção manual
- [ ] Ambiente de produção hospedado em território nacional

---

*Documento Produto & Técnico — BALUARTE. Elaborado em agosto de 2026. Referências de stack (LiteLLM, Presidio) verificadas na data; ambos são projetos ativos com releases frequentes — reconfirmar compatibilidade antes de decisões de arquitetura.*
