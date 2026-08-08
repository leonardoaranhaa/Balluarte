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
2. **Fontes primárias.** A página cita a LGPD, um estudo da FGV, uma nota
   técnica da ANPD e a decisão da autoridade austríaca. O rodapé nomeia as
   quatro, mas sem link. **Não publique antes de preencher.** Uma página cujo
   argumento é precisão não cita sem referência, e é a primeira coisa que um
   comprador técnico confere.
3. **Domínio.** `gw.baluarte.com.br` no diff é placeholder. O checklist de
   constituição coloca a busca de anterioridade no INPI antes de qualquer
   investimento em identidade.
4. **CNPJ e endereço** no rodapé, quando a SLU sair.

## Restrições de marca respeitadas

A página não promete conformidade, não afirma que roteamento nacional elimina
a exposição ao CLOUD Act, não cita o PL 2338 (ainda em tramitação — o argumento
é o art. 33 da LGPD, vigente), não usa urgência fabricada e não usa superlativo.
A seção "o que não fazemos" declara cinco limites sem suavização.
