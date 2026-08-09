# BALUARTE — Guia da Marca

> **A camada de confiança entre sua empresa e a IA.**

Referência da identidade visual e verbal. Consultar antes de qualquer peça nova — landing, dashboard, apresentação, post, imagem gerada por IA.

**Versão:** 1.0 · **Agosto de 2026**

---

## 1. O nome

**BALUARTE** — fortificação avançada de uma defesa, construída para proteger o que está atrás dela **sem impedir a passagem de quem tem autorização.**

A metáfora não é decorativa. É a arquitetura do produto:

> Empresas que "resolvem" o risco de IA proibindo IA não são clientes. São o cenário que o produto existe para substituir.

Um baluarte não é um muro. É um ponto de controle com passagem.

**Por que funciona comercialmente:** palavra do português culto, não anglicismo — coerente com um produto cujo argumento central é soberania de dado nacional. Soa institucional sem soar burocrático. Um DPO lê o nome e entende o setor antes de ler a descrição.

### ⚠️ Pendência

Busca de anterioridade no **INPI, classes 09 (software) e 42 (serviços de tecnologia)** ainda não realizada. Verificar também domínio, LinkedIn e GitHub antes de qualquer investimento adicional.

Alternativas testadas, caso haja colisão: **GUARITA**, **ALFÂNDEGA**, **CIDADELA**.

---

## 2. O símbolo

Duas anteparas angulares convergindo para um vão central, com pilares verticais e luz âmbar atravessando a passagem em direção ao observador.

A leitura acontece em três tempos: **estrutura defensiva** (as anteparas) → **passagem** (o vão) → **inspeção** (a luz que atravessa e revela).

### A regra estrutural

> **O vão nunca fecha. A passagem central é a marca inteira.**

Se em alguma iteração futura as anteparas se juntarem, ou a luz sumir, a marca passa a comunicar bloqueio — e contradiz o produto. Qualquer variante que perca a passagem deve ser rejeitada, mesmo que fique mais bonita.

### O que o símbolo deliberadamente não é

| Clichê evitado | Por quê |
|---|---|
| Cadeado | Saturado no setor. Comunica bloqueio, não controle. |
| Escudo | Default de qualquer marca de compliance. |
| Cérebro / rede neural | Clichê de "logo de IA". Não diz nada. |
| Circuito / chip | Comunica hardware. O produto é camada de política. |
| Olho | Comunica vigilância. O produto protege o titular. |

Proposta futura que caia em qualquer uma das cinco está errada por definição.

---

## 3. Arquivos do pacote

```
/svg     vetorial, autocontido (texto convertido em contornos)
/png     exportações rasterizadas
/favicon conjunto completo para web e PWA
```

### Qual usar

| Contexto | Arquivo |
|---|---|
| Cabeçalho de site (fundo escuro) | `baluarte-logo-horizontal-dark.svg` |
| Cabeçalho de site (fundo claro) | `baluarte-logo-horizontal-light.svg` |
| Espaço estreito, rodapé | `*-horizontal-*-simples.svg` (sem tagline) |
| Redes sociais, formato quadrado | `baluarte-logo-stacked-*.svg` |
| Avatar, app icon | `baluarte-mark-tile-dark.svg` |
| Favicon, 16–64px | `baluarte-mark-simplificado-*` |
| Gravação, fax, fundo colorido | `baluarte-mark-mono-*` |

### A variante simplificada existe por um motivo

Os três pilares do símbolo completo **embaralham abaixo de 64px.** A versão simplificada reduz a três elementos — duas anteparas e um vão âmbar cheio — e foi testada em 16px real, não em preview ampliado.

Nunca usar o símbolo completo em favicon.

---

## 4. Uso do logotipo

**Área de respiro:** margem mínima igual à altura da letra "B" do wordmark, em todos os lados. Nada invade essa área.

**Tamanho mínimo:** lockup horizontal, 180px de largura. Abaixo disso, usar só o símbolo.

> **Nota de implementação — o nome não some junto com o wordmark.**
>
> Em telefone não sobram 180px ao lado do botão do cabeçalho, então a landing
> troca o lockup pelo símbolo, como esta regra manda. Só que aí a marca ficava
> sem nome escrito justamente na largura onde a maior parte das visitas
> acontece — só o símbolo, sem dizer de quem é.
>
> A regra vale para a arte: o wordmark desenhado não pode ser reduzido abaixo
> do que foi desenhado para aguentar. O nome escrito pode. Abaixo de 30em a
> landing põe **BALUARTE** como texto vivo ao lado do símbolo, em 15px, peso
> 700, entreletra 0,09em — proporção próxima à do wordmark no lockup, onde a
> altura de caixa alta fica em torno de metade da altura do símbolo.
>
> Quando o lockup volta a caber, o texto sai: quem traz o nome de novo é o
> wordmark desenhado, e ter os dois seria repetição.

### Proibições

- ❌ Alterar a proporção entre símbolo e wordmark
- ❌ Recolorir fora da paleta oficial
- ❌ Sombra, contorno, bisel ou brilho externo
- ❌ Rotacionar ou espelhar
- ❌ Aplicar a variante escura sobre fundo claro (e vice-versa)
- ❌ Reescrever a tagline
- ❌ Usar o símbolo completo abaixo de 64px

---

## 5. Paleta

| Papel | Hex | Uso |
|---|---|---|
| Base escura | `#0E1113` | Fundos, cabeçalhos, superfícies do dashboard |
| Neutro claro | `#E6E6E6` | Texto sobre escuro, wordmark, superfícies claras |
| Acento âmbar | `#F5A623` | Tagline, luz do símbolo, ações primárias |
| Âmbar escuro | `#B8770F` | Tagline sobre fundo claro — ver a nota de contraste abaixo |

> **Nota de implementação — contraste do âmbar escuro.**
> Medido, `#B8770F` sobre `#E6E6E6` dá **2,96:1**. Isso reprova o AA de texto
> normal (4,5:1) e também o limiar de texto grande (3:1). A tabela original
> dizia "contraste AA"; a medição não sustenta.
>
> Onde ele continua válido: **dentro do logo**. A WCAG isenta texto que faz
> parte de marca ou logotipo de requisito de contraste, e é exatamente aí que a
> tagline em âmbar escuro aparece nos lockups.
>
> Onde não serve: qualquer texto da página ou da interface. Para isso a landing
> usa `#7E5200`, que dá 5,4:1 sobre `#E6E6E6` e mantém a mesma família de cor.
> Se a marca ganhar uma segunda passada com designer, vale reconciliar os dois
> valores num só.

**Regra do acento único:** um acento cromático só. Se uma tela tem âmbar em mais de três lugares, provavelmente dois estão sobrando. Paleta de compliance com cinco cores vibrantes parece dashboard de marketing — e o comprador é um DPO, que confia no que parece ferramenta de engenharia.

### Cores semânticas do dashboard

Derivadas, não adicionadas à paleta de marca:

| Estado | Direção |
|---|---|
| Permitido | Verde sóbrio, dessaturado — nunca verde-ácido |
| Mascarado / Tokenizado | Âmbar `#F5A623` |
| Bloqueado | Vermelho contido, dessaturado — nunca vermelhão |

### Nota sobre o halo

O brilho radial atrás do vão existe apenas nas variantes para fundo escuro. Sobre fundo claro ele vira uma mancha amarelada suja — por isso as variantes `light` trazem só o facho, sem halo.

---

## 6. Tipografia

**IBM Plex Sans** — interface, títulos e corpo. Bold / SemiBold / Medium / Regular.
**IBM Plex Mono** — logs, tokens, hashes, timestamps, código, unidades técnicas.

Open source, credibilidade de engenharia, e legibilidade excelente em tabela densa — que é o que o dashboard de auditoria vai ser.

**Regra do mono:** nunca decorativo. Se um texto está em mono, é porque é dado técnico literal. Usar mono para "dar clima de tecnologia" quebra a convenção.

**Convenções:** sentence case em títulos e botões, não Title Case. Frase curta, voz ativa. Sem emoji em interface ou material comercial.

O wordmark do pacote já está convertido em contornos — os SVGs não dependem da fonte estar instalada.

---

## 7. Voz

| Atributo | Na prática |
|---|---|
| **Preciso** | Cita artigo e norma. Nunca "a legislação exige" — sempre "o art. 33 da LGPD estabelece". |
| **Sóbrio** | Sem alarmismo, sem urgência fabricada. |
| **Direto** | Frase curta. Voz ativa. |
| **Honesto sobre limites** | Diz o que o produto não faz. É o diferencial de credibilidade. |

### As cinco restrições inegociáveis

Valem para toda peça — copy, interface, imagem, apresentação, post.

1. **Nunca prometer conformidade.** BALUARTE entrega controle técnico e trilha de evidência. A decisão sobre base legal é do encarregado de dados do cliente.
2. **Nunca afirmar que rotear por servidor brasileiro elimina exposição ao CLOUD Act** quando o destino final continua sendo provedor americano. O ganho real vem do mascaramento, da tokenização ou do roteamento nacional.
3. **Nunca usar o PL 2338 como argumento de urgência** — ainda não é lei. Usar o art. 33 da LGPD, que já é vigente.
4. **Nunca usar urgência fabricada.**
5. **Nunca usar superlativo vazio** — "revolucionário", "líder de mercado", "100% seguro".

### A tagline

> **A camada de confiança entre sua empresa e a IA.**

Não reescrever. "Camada" comunica que o produto fica *entre*, não que substitui. "Confiança" não é "segurança" (promete demais) nem "conformidade" (viola a restrição 1).

---

## 8. Geração de imagem com IA

### Bloco de estilo — colar em todo prompt

```
ESTILO BALUARTE
Paleta restrita: quase-preto #0E1113, cinza neutro #E6E6E6,
um único acento âmbar #F5A623 usado com parcimônia.
Iluminação direcional e dura, com sombra definida.
Composição geométrica, ângulos retos e diagonais francas.
Textura de concreto, aço escovado, pedra.
Sem pessoas. Sem rostos. Sem texto na imagem.
Estética de fotografia arquitetônica e instrumento técnico —
não ilustração de startup, não render 3D lustroso.
Grão fino aceitável. Nada de brilho neon ou bloom.
```

### Nunca gerar

Cadeado, escudo, cofre · cérebro, rede neural, nós conectados · circuito, chip · olho, câmera, mira · robô, mão de robô tocando mão humana · gradiente roxo-azul · pessoa sorrindo em escritório · bandeira do Brasil ou verde-amarelo · texto renderizado dentro da imagem.

> Sobre a bandeira: soberania se comunica pela arquitetura do produto, não por símbolo patriótico. Verde-amarelo em material de compliance lê como apelo, e o comprador é um CISO cético.

### Prompts prontos

**Hero da landing**
```
Corte transversal de uma estrutura defensiva de concreto, duas
anteparas angulares abrindo para fora com um vão estreito ao centro,
luz âmbar atravessando o vão da esquerda para a direita, resto da
cena em quase-preto. Ângulo frontal, simetria imperfeita.
Fotografia arquitetônica, lente 35mm, luz dura.
[+ BLOCO DE ESTILO]
```

**Imagem OG / compartilhamento (1200×630)**
```
Vista superior de um portão fortificado de pedra escura, passagem
central estreita iluminada por uma faixa âmbar contínua, restante
em sombra profunda. Composição horizontal, muito espaço negativo
à direita para sobreposição de texto.
[+ BLOCO DE ESTILO]
```

**Seção "O problema" — dado saindo sem controle**
```
Corredor de concreto escuro com uma abertura na parede lateral,
luz âmbar vazando de forma difusa e descontrolada pela fresta.
Sensação de brecha, não de ataque. Sem alarme, sem vermelho.
[+ BLOCO DE ESTILO]
```

**Seção "O que fazemos" — inspeção**
```
Feixe de luz âmbar estreito atravessando uma chapa de aço escovado
perfurada, projetando um padrão nítido e ordenado na superfície
atrás. Macro, profundidade de campo rasa.
[+ BLOCO DE ESTILO]
```

**Seção "Trilha de auditoria"**
```
Camadas sobrepostas de placas de pedra escura levemente
desalinhadas, cada uma com uma borda fina iluminada em âmbar,
formando uma sequência contínua. Luz rasante.
[+ BLOCO DE ESTILO]
```

**Fundo abstrato para apresentação**
```
Textura de concreto escuro com uma única linha âmbar horizontal
atravessando o quadro fora do centro. Minimalista, muito espaço
negativo. Alto contraste, baixa saturação.
[+ BLOCO DE ESTILO]
```

### Regra de aceitação

Antes de usar qualquer imagem gerada, três perguntas:

1. Cairia bem numa apresentação de auditoria, ou parece landing de SaaS genérico?
2. Comunica passagem controlada, ou comunica bloqueio?
3. Um CISO cético olharia e pensaria "sério" ou "marketing"?

Duas erradas em três: descartar e refazer.

**Licenciamento:** verificar os termos do gerador usado e registrar em `/imagens/PROMPTS.md` qual ferramenta gerou cada asset. Se a marca for para o INPI, a origem dos assets pode ser questionada.

---

## 9. Implementação web

```html
<link rel="icon" href="/favicon/favicon.ico" sizes="any">
<link rel="icon" href="/favicon/favicon-dark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon/apple-touch-icon.png">
<meta name="theme-color" content="#0E1113">
```

Tokens de cor sugeridos:

```css
:root {
  --base:    #0E1113;
  --neutro:  #E6E6E6;
  --ambar:   #F5A623;
  --ambar-escuro: #B8770F;
}
```

---

## 10. Pendências

- [ ] Busca de anterioridade no INPI (classes 09 e 42)
- [ ] Verificar domínio, LinkedIn e GitHub
- [ ] Definir hex exatos das cores semânticas do dashboard
- [ ] Registrar tokens em `tokens.json`
- [ ] Testar o favicon em aba real de navegador, claro e escuro

---

## 11. Sobre esta versão

Esta é a v1, nascida junto com a fase de validação do produto. Foi desenhada para ser sólida o suficiente para usar hoje — não necessariamente a versão definitiva para os próximos dez anos.

Quando houver receita, vale uma segunda passada com designer, especialmente para: refinamento do símbolo em tamanhos pequenos, sistema de ícones do dashboard, e ajuste ótico do espacejamento do wordmark.

**A única coisa que não deve mudar nessa segunda passada:** o vão.
