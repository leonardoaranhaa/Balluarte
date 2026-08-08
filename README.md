# BALUARTE — landing page de validação

Página única de validação comercial. Um arquivo, sem framework, sem build,
sem dependência de rede.

**Objetivo único:** converter um DPO ou CISO cético em uma conversa de 20
minutos. A métrica é número de agendamentos, não de visitas. Por isso a página
tem um só CTA — sem captura de e-mail, sem newsletter, sem material para
download.

## Como abrir

```
open index.html
```

É um arquivo estático. Abre por duplo clique, funciona em `file://`, não
precisa de servidor. Para publicar, suba o arquivo em qualquer host estático.

## Deploy

Projeto `baluarte` na Vercel, time `hsantiagodebem-5408s-projects`.

O site é estático: sem build, sem framework, sem instalação de dependência.
O `vercel.json` só define cabeçalhos de resposta.

**Cabeçalhos aplicados** (confirmados na resposta real do deploy):

| Cabeçalho | Valor |
|---|---|
| `Content-Security-Policy` | `default-src 'none'` com `style-src`/`script-src` em `'self' 'unsafe-inline'`, mais `base-uri`, `form-action`, `frame-ancestors` e `object-src` em `'none'` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | câmera, microfone, geolocalização, pagamento, USB e sensores desligados |

Duas decisões que valem explicação, já que o produto vende disciplina de dado:

- **`'unsafe-inline'` em `script-src` e `style-src` é deliberado.** A página é um
  arquivo só, com CSS e JS embutidos e zero recurso externo. Fixar o hash de cada
  bloco inline daria uma CSP mais estrita, mas quebraria a página em silêncio a
  cada ajuste de texto — o script para de rodar, ou o estilo some inteiro. Numa
  landing editada com frequência, esse é um risco pior que o ganho. Não há
  entrada de usuário nem conteúdo de terceiro em lugar nenhum da página, então a
  superfície de XSS que o hash fecharia é nula. As diretivas que de fato importam
  aqui (`default-src 'none'`, `frame-ancestors 'none'`, `base-uri 'none'`,
  `object-src 'none'`) estão fechadas.
- **`Strict-Transport-Security` não está no `vercel.json`.** A Vercel já envia
  HSTS com `max-age` maior e `preload`. Declarar o nosso criava dois cabeçalhos
  HSTS na mesma resposta, com o valor mais fraco na frente — exatamente o tipo de
  achado que aparece num scan de cabeçalhos.

**Proteção de deploy:** o projeto está com Vercel Authentication (SSO) ligada
para tudo que não seja domínio próprio. Isso significa que a URL de preview
**não abre para quem não estiver logado no time.** Para mandar a página a um
prospect, ou se gera um link temporário de compartilhamento na Vercel, ou se
desliga a proteção nas configurações do projeto.

## Decisões de construção

- **Sem webfont.** A página usa a stack de fontes nativa do sistema. Nada
  quebra se um CDN cair, e não há FOUT. Auto-hospedar IBM Plex Sans + Mono
  (subset latin, woff2) é o upgrade previsto para depois da validação.
- **Um acento cromático só**, âmbar, em duas profundidades: `#E9A23B` sobre
  fundo escuro e `#8A5A00` sobre fundo claro. O âmbar claro reprova AA em texto
  sobre fundo claro, por isso o mesmo acento existe em duas versões.
- **Claro é o seu lado, escuro é dentro do gateway.** Painéis escuros aparecem
  exatamente três vezes: o plano de passagem, o diff de configuração e o
  rodapé. A cor carrega a metáfora do produto.
- **Mono marca o que a máquina produziu ou consumiu** — prompt, token, linha de
  auditoria, linha de config. Prosa nunca é mono.
- **O plano de passagem** (o elemento interativo do topo) é um
  `<input type="range">` sobre duas camadas de texto travadas na mesma largura.
  Ser um `range` é o que dá foco de teclado, navegação por ←/→, suporte a toque
  e anúncio de estado para leitor de tela sem código extra.

## Verificado

| Item | Resultado |
|---|---|
| Renderização em Chromium, 1280px e 360px | sem overflow horizontal |
| Erros de JavaScript no console | nenhum |
| Sem JavaScript | prompt cru legível, controles ocultos, nota explicativa |
| Teclado (Tab e ←/→) | plano navegável, foco visível em todo elemento |
| `prefers-reduced-motion` | nenhuma transição roda; a interação continua |
| Contraste AA | ink/paper 14,9 · mist/paper 5,25 · âmbar-fundo/paper 5,34 · paper/grafite 16,0 · âmbar/grafite 8,22 |

## Pendências antes de publicar

Estas não são bugs. São decisões que a página carrega como `TODO` no HTML.

1. **Link do CTA.** Hoje aponta para `mailto:contato@baluarte.com.br`. Precisa
   de uma URL real de agenda — um CTA que não agenda zera a métrica da página.
2. **Dois links do rodapé pedem um clique de confirmação.** As quatro fontes
   estão linkadas. A página da ANPD foi verificada e as duas notas técnicas
   conferem com o título exato. Já `planalto.gov.br` e `fgv.br` recusaram
   conexão do container onde a página foi construída (HTTP 503), então esses
   dois links não puderam ser abertos aqui. Abra os dois num navegador antes de
   publicar.
3. **O placar do estudo da FGV.** A página diz que Claude, Gemini e Meta AI
   cumprem 11 dos 14 critérios, número que aparece no portal da própria FGV.
   O Poder360 publicou 10. Bata no PDF do estudo quando conseguir abri-lo.
4. **Domínio.** `gw.baluarte.com.br` no diff é placeholder. O checklist de
   constituição coloca a busca de anterioridade no INPI antes de qualquer
   investimento em identidade.
5. **CNPJ e endereço** no rodapé, quando a SLU sair.

## Fontes citadas

Toda afirmação factual da página é rastreável a uma destas:

- [Lei 13.709/2018 (LGPD), art. 33](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [CTS/FGV Direito Rio — *IA Generativa e LGPD*](https://direitorio.fgv.br/conhecimento/livrosia-generativa-e-lgpd-transparencia-desafios-regulatorios-e-caminhos-para)
- [ANPD — Nota Técnica nº 54/2025/FIS/CGF/ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos), Mapa de Temas Prioritários 2026-2027
- [ANPD — Nota Técnica nº 1/2026/FIS/CGF/ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos), sistema Grok

Uma afirmação que constava de rascunhos anteriores — multa de 450 mil euros
aplicada pela autoridade austríaca a uma fintech de Viena por uso de API de IA
americana — **não se sustenta em fonte primária e foi removida.** Não reintroduza.

## Restrições de marca respeitadas

A página não promete conformidade, não afirma que roteamento nacional elimina
a exposição ao CLOUD Act, não cita o PL 2338 (ainda em tramitação — o argumento
é o art. 33 da LGPD, vigente), não usa urgência fabricada e não usa superlativo.
A seção "o que não fazemos" declara cinco limites sem suavização.
