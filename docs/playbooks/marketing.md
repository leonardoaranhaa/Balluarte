# BALUARTE — Prompts de Marketing

**Landing page · Perfil LinkedIn · Prospecção**

*Todos os prompts abaixo são para copiar e colar. O bloco de contexto da seção 1 é pré-requisito de todos os outros — cole ele primeiro, sempre.*

---

## 1. Bloco de contexto mestre

Este bloco vai no início de qualquer prompt de marketing. Ele carrega tudo que o modelo precisa saber e, mais importante, as restrições que ele não pode violar.

```
CONTEXTO — BALUARTE

O QUE É
BALUARTE é um gateway de IA: um proxy que fica entre a aplicação de uma
empresa e os provedores de modelo (Claude, GPT, Gemini). Detecta dado
pessoal sensível antes que a requisição saia, aplica a política que o
cliente configurou (mascarar, tokenizar ou bloquear), e registra tudo
numa trilha de auditoria que vira um relatório assinado: o Dossiê de
Conformidade.

O PROBLEMA QUE RESOLVE
Toda vez que alguém cola um contrato, um prontuário ou uma planilha de
clientes num chat de IA hospedado fora do Brasil, isso é tecnicamente
uma transferência internacional de dado pessoal sob o art. 33 da LGPD —
e quase nunca existe base legal documentada. Não há log. Não há prova.

FATOS VERIFICADOS QUE PODEM SER USADOS
Só entra aqui o que está registrado como confirmado em docs/fontes.md.
Se um fato não está lá, ele não vai para material público.

- O Centro de Tecnologia e Sociedade da FGV Direito Rio avaliou a
  documentação de sete plataformas de IA generativa (ChatGPT, Gemini,
  Claude, Copilot, Grok, DeepSeek, Meta AI) contra catorze critérios
  extraídos do Guia de Segurança da Informação para Agentes de Tratamento
  de Pequeno Porte, publicado pela ANPD em 2021. Nenhuma cumpre os
  catorze. Só três critérios são cumpridos por todas: ter política de
  privacidade publicada, identificar o controlador e informar quais dados
  são coletados. DeepSeek cumpre cinco; Grok, seis.
- As melhores avaliadas — Claude, Gemini e Meta AI — cumprem onze dos
  catorze. Entre as falhas que restam nelas está a falta de clareza sobre
  os países para onde o dado é enviado. O BALUARTE integra o Claude, e
  isso deve ser dito: política de privacidade boa do provedor não é base
  legal documentada da empresa cliente, e o art. 33 cobra a segunda.
- Em dezembro de 2025 a ANPD publicou o Mapa de Temas Prioritários do
  biênio 2026-2027 (Nota Técnica nº 54/2025/FIS/CGF/ANPD), que traz
  inteligência artificial e tecnologias emergentes como um dos eixos de
  fiscalização.
- Em 2026 a ANPD emitiu nota técnica sobre possíveis violações à LGPD
  pelo sistema Grok (Nota Técnica nº 1/2026/FIS/CGF/ANPD).
- Entidades de classe já orientam advogados e profissionais de saúde a
  não enviar dado de cliente/paciente a provedor de IA em nuvem sem base
  legal específica.

FATOS QUE NÃO PODEM SER USADOS — já foram refutados
- Multa de 450 mil euros aplicada pela autoridade austríaca a uma fintech
  de Viena por uso de API de IA americana. NÃO EXISTE em fonte primária.
  Ver docs/fontes.md. Não reintroduzir, em nenhuma peça.
- "Política de privacidade sequer disponível em português" como achado do
  estudo da FGV. Nenhuma fonte confirma.
- Nota Técnica nº 12/2025 da ANPD. Não consta da central de conteúdo da
  autoridade.

PÚBLICO
Primário: DPO, Encarregado de Dados, CISO e Head de Compliance em
fintechs e healthtechs brasileiras de 50 a 500 funcionários.
Secundário: sócios de escritórios de advocacia de porte médio/grande.

TOM DE VOZ
Preciso (cita artigo e norma, nunca "a legislação exige"), sóbrio (sem
alarmismo, sem urgência fabricada, sem contagem regressiva), direto
(frase curta, voz ativa) e honesto sobre limites (diz o que o produto
não faz).

RESTRIÇÕES INEGOCIÁVEIS — violar qualquer uma invalida o resultado
1. NUNCA prometer conformidade. BALUARTE não deixa ninguém "em
   conformidade com a LGPD" — isso é decisão do encarregado de dados do
   cliente. BALUARTE entrega controle técnico e trilha de evidência.
2. NUNCA afirmar que rotear por servidor brasileiro elimina exposição ao
   CLOUD Act quando o destino final continua sendo provedor americano. O
   ganho real vem do mascaramento, da tokenização, ou do roteamento para
   modelo hospedado nacionalmente.
3. NUNCA usar o PL 2338 (Marco Legal da IA) como argumento de urgência —
   ele ainda não é lei, está em tramitação na Câmara. Usar o art. 33 da
   LGPD, que já é vigente.
4. NUNCA usar urgência fabricada: "não perca tempo", "última chance",
   contagem regressiva, escassez artificial.
5. NUNCA usar superlativo vazio: "revolucionário", "líder de mercado",
   "solução definitiva", "100% seguro".
```

---

## 2. Prompt — Landing Page

Este é o prompt mais longo do documento porque é o que mais depende de contexto e restrição. Rodar no Claude Code.

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

---

TAREFA
Construir a landing page de validação do BALUARTE. Arquivo único HTML
com CSS e JS embutidos, responsivo, sem dependência de framework.

OBJETIVO ÚNICO DA PÁGINA
Converter um DPO ou CISO cético em uma conversa de 20 minutos. Não é
vender, não é explicar tudo, não é capturar e-mail em massa. É gerar
uma reunião qualificada.

MÉTRICA DE SUCESSO: número de agendamentos, não número de visitas.

PROCESSO OBRIGATÓRIO — não pule etapas
Antes de escrever qualquer código, produza e me mostre um plano de
design compacto contendo:
  1. PALETA: 4 a 6 valores hex nomeados, com justificativa de cada um
  2. TIPOGRAFIA: pelo menos duas famílias com papéis distintos (display
     e corpo), com racional da escolha
  3. LAYOUT: descrição em uma frase por seção + wireframe em ASCII
  4. ELEMENTO-ASSINATURA: o único elemento pelo qual essa página será
     lembrada

Depois de montar o plano, critique-o antes de codificar: se alguma
parte pareceria igual ao que você produziria para qualquer outra
landing de SaaS B2B, revise e me diga o que mudou e por quê.

Só comece o código depois de eu aprovar o plano.

DIREÇÃO ESTÉTICA
Estética de infraestrutura e engenharia, não de startup de consumo. O
leitor é um DPO ou CISO — confia no que parece sério, desconfia do que
parece marketing.

O que evitar deliberadamente (são defaults, não escolhas):
- Fundo creme com serifada de alto contraste e acento terracota
- Fundo quase-preto com um único acento verde-ácido ou vermelhão
- Layout de jornal com fios capilares e zero border-radius
- Gradiente roxo-azul de SaaS genérico
- Ilustração 3D abstrata sem relação com o assunto
- Ícone de cadeado ou escudo (clichê saturado no setor de segurança)

Um acento cromático só, usado com parcimônia. Paleta de compliance com
cinco cores vibrantes parece dashboard de marketing.

ESTRUTURA DE CONTEÚDO
1. HERO
   A tese da página. Não um número grande com label pequeno — isso é a
   resposta template. Considere abrir com a demonstração do próprio
   problema: um prompt real com CPF visível, e o mesmo prompt depois do
   BALUARTE. Se encontrar algo melhor, use, mas justifique.
   Headline candidata (pode melhorar): "Você sabe o que sai da sua
   empresa em prompts de IA?"

2. O PROBLEMA
   Art. 33 da LGPD + o achado da FGV. Fato, sem alarmismo.

3. O QUE ACONTECE HOJE
   Sem log. Sem base legal documentada. Sem como provar nada depois.

4. O QUE O BALUARTE FAZ
   Quatro blocos: detecta, aplica política, transforma, registra.

5. IMPLANTAÇÃO
   Troca da URL base. Sem reescrita de código. Mostrar o "antes e
   depois" de uma linha de configuração — é o argumento mais forte da
   página e merece tratamento visual.

6. O QUE NÃO FAZEMOS
   Seção deliberada e obrigatória. Num mercado de promessa vaga, dizer o
   limite explicitamente é o que separa fornecedor sério de vendedor de
   compliance-teatro. Não suavizar essa seção.

7. CTA FINAL
   "Agendar 20 minutos" — não "solicite uma demonstração", não
   "comece grátis".

REGRAS DE ESCRITA
- Frase curta. Voz ativa. Sentence case, não Title Case.
- Nomear as coisas pelo que a pessoa reconhece, não pela arquitetura
  interna. "O que sai da sua empresa", não "payload de requisição".
- Ser específico é sempre melhor que ser esperto.
- Cada elemento faz exatamente um trabalho. Um rótulo rotula, um exemplo
  demonstra. Nada faz dois trabalhos disfarçadamente.

PISO DE QUALIDADE (não anunciar, apenas cumprir)
- Responsivo até 360px de largura
- Foco de teclado visível em todos os elementos interativos
- prefers-reduced-motion respeitado
- Contraste mínimo AA em todo texto
- Sem dependência externa que quebre se um CDN cair

ENTREGA
Um arquivo HTML. Ao final, liste em três bullets as decisões de design
que você tomou e que eu deveria questionar.
```

### 2.1 Prompt de refinamento (rodar depois da primeira versão)

```
Revise a landing page com estes três filtros, um de cada vez:

1. TESTE DO CÉTICO
Leia como um CISO com 15 anos de experiência que já viu 40 fornecedores
prometerem segurança. Marque cada frase que ele revira os olhos.
Reescreva essas.

2. TESTE DA PROMESSA
Encontre qualquer lugar onde a página sugere, mesmo indiretamente, que
o BALUARTE garante conformidade ou soberania plena. Corrija sem
suavizar o produto.

3. CONSELHO DE CHANEL
Antes de sair de casa, olhe no espelho e tire um acessório. Identifique
o elemento visual ou de copy que menos serve ao objetivo da página e
remova.

Me mostre o diff do que mudou e por quê.
```

---

## 3. Prompt — Perfil LinkedIn

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

---

TAREFA
Escrever o perfil LinkedIn do fundador do BALUARTE.

PREMISSA IMPORTANTE
O perfil não é currículo. É a página que um DPO abre para decidir se
aceita um convite de conexão de um desconhecido. Ele tem 8 segundos
para decidir se você é alguém que entende o problema dele ou mais um
vendedor.

ENTREGAS

1. HEADLINE (220 caracteres)
Três variações. Nenhuma delas pode ser "Fundador da BALUARTE" — cargo
não comunica nada. A headline nomeia o problema que eu resolvo.
Referência de direção (melhore se conseguir):
"Ajudando empresas a usar IA sem virar réu da LGPD | Fundador, BALUARTE"

2. SEÇÃO "SOBRE" (máximo 5 linhas)
Duas variações. Estrutura: abrir com a dor observada, não com quem eu
sou. Terminar com convite implícito a conversar, nunca com CTA de venda.
Sem emoji. Sem lista de bullet com foguetinho.

3. TEXTO DA EXPERIÊNCIA ATUAL
Três linhas descrevendo o BALUARTE de forma que um comprador entenda o
valor, não a arquitetura.

4. TRÊS IDEIAS DE CONTEÚDO PARA A SEÇÃO "EM DESTAQUE"
O que fixar no topo do perfil para dar credibilidade antes da primeira
conversa.

RESTRIÇÃO ADICIONAL
Nada de "apaixonado por tecnologia", "transformando o mercado",
"conectando pessoas e inovação". Se a frase caberia no perfil de
qualquer outra pessoa, ela está errada.
```

---

## 4. Prompts — Prospecção

### 4.1 Notas de convite de conexão

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

---

TAREFA
Escrever notas de convite de conexão no LinkedIn.

REGRA ABSOLUTA
A nota de convite NUNCA menciona o produto. O convite abre porta, não
vende. Quem vende no convite é ignorado.

LIMITE: 300 caracteres.

ENTREGA
Três variações para cada perfil abaixo:

A) DPO / Encarregado de Dados em fintech ou healthtech
B) CISO / Head de Segurança da Informação
C) Sócio de escritório de advocacia (áreas trabalhista, saúde,
   contencioso)

Para o perfil C, a alavanca é sigilo profissional, não LGPD — um sócio
entende dever profissional sem precisar de tradução técnica.

Cada variação deve deixar um espaço marcado como [GANCHO] onde eu
insiro uma referência pessoal real (post recente, artigo, palestra).
Convite genérico converte mal.
```

### 4.2 Sequência de follow-up

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

---

TAREFA
Escrever a sequência de 3 mensagens que vem depois do aceite do convite.

TOQUE 1 — 24 a 48h após o aceite
Objetivo: qualificar interesse, não vender. Pode mencionar o problema e
o achado da FGV. Termina com convite a uma conversa de 15 minutos, sem
pressão.

TOQUE 2 — 5 a 7 dias depois, apenas se não houve resposta
Objetivo: entregar valor sem pedir nada. Compartilhar algo útil de fato.
Não repetir o pedido de call.

TOQUE 3 — 10 a 14 dias depois, apenas se ainda sem resposta
Objetivo: fechar o loop com elegância. Reconhecer que não é o momento,
deixar a porta aberta, e parar. Depois desta mensagem, não envio mais
nada sem gatilho novo.

RESTRIÇÃO
Nenhuma das três pode soar como sequência automatizada. Se as três
juntas parecerem uma cadência de ferramenta de automação, refaça.
```

### 4.3 Posts de aquecimento

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

---

TAREFA
Escrever 4 posts para o LinkedIn, a serem publicados nas duas semanas
que antecedem o início da prospecção ativa.

FUNÇÃO DOS POSTS
Dar a quem receber meu convite algo para conferir antes de aceitar. E
gerar conexão inbound — que não consome minha cota semanal de convites.

TEMAS
Post 1: O achado da FGV — sete plataformas avaliadas contra catorze
        critérios da ANPD, nenhuma cumpre todos. Incluir que as melhores
        avaliadas (entre elas o Claude, que o BALUARTE integra) ainda
        falham em dizer para que país o dado vai
Post 2: Soberania de fachada — por que rotear por servidor no Brasil não
        elimina a exposição ao CLOUD Act quando o destino final é
        provedor americano. Argumentar pelo raciocínio jurisdicional, sem
        apoiar em caso concreto: foi a busca por um caso que produziu a
        citação falsa que já tivemos que remover
Post 3: A pergunta que quase nenhuma empresa consegue responder — quanto
        dado sensível saiu em prompt de IA no último trimestre
Post 4: Por que bloquear IA por política interna não resolve (e cria
        outro problema)

FORMATO
- Entre 150 e 250 palavras
- Primeira linha precisa funcionar sozinha (é o que aparece antes do
  "ver mais")
- Sem emoji decorativo
- Sem "🚀 Bora?" no final
- Sem CTA de venda. No máximo, uma pergunta genuína ao leitor
- Sem hashtag em excesso — no máximo três, e só se relevantes

RESTRIÇÃO
Não escrever no formato "thread de LinkedIn" com uma frase por linha e
espaçamento artificial para ocupar tela. Isso é reconhecido como truque
de engajamento e queima credibilidade com esse público específico.
```

### 4.4 Adaptação para caso concreto

Prompt curto, para usar antes de cada envio real:

```
[COLE O BLOCO DE CONTEXTO MESTRE DA SEÇÃO 1 AQUI]

Vou enviar convite para esta pessoa:

Nome: [nome]
Cargo: [cargo]
Empresa: [empresa] — [setor, porte]
Sinal observado: [post recente, artigo, mudança de cargo, ou "nenhum"]

Escreva a nota de convite (máximo 300 caracteres) e o Toque 1
personalizado para este caso específico. Se o sinal observado for
"nenhum", me diga se vale a pena enviar mesmo assim ou se é melhor
esperar um gancho.
```

---

## 5. Regra que vale para todos os prompts acima

Se o resultado gerado violar qualquer uma das cinco restrições inegociáveis do bloco de contexto, **não corrija manualmente — devolva para o modelo apontando qual restrição foi violada.** Corrigir na mão ensina você a aceitar output ruim; devolver ensina o prompt a melhorar.

E o teste final de qualquer peça de comunicação do BALUARTE, antes de publicar:

> Um DPO cético leria isso e pensaria "essa pessoa entende meu problema", ou pensaria "mais um vendendo compliance"?

Se houver dúvida, é a segunda.

---

*Prompts de Marketing — BALUARTE. Elaborado em agosto de 2026. Os fatos citados no bloco de contexto devem ser reconfirmados antes de uso em material público.*
