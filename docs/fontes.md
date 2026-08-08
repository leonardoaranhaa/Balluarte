# BALUARTE — Registro de fontes

*Documento vivo. Atualizar sempre que um fato for verificado, refutado ou entrar em dúvida.*

---

## Por que este arquivo existe

Um material de venda cujo argumento central é precisão não sobrevive a uma
citação que não resiste a checagem. O risco não é parecer desatualizado — é
parecer compliance-teatro, que é exatamente o que o produto existe para
substituir.

**A regra:** nenhum número, caso ou norma vai para material público — site,
pitch deck, post, mensagem de prospecção, proposta — sem estar registrado
abaixo como confirmado, com link para fonte primária.

Se um fato não está aqui, ele não sai daqui.

---

## Confirmado

### Lei 13.709/2018 (LGPD), art. 33

Núcleo jurídico do produto. Só permite transferência internacional de dado
pessoal em hipóteses específicas — entre elas país com grau de proteção
adequado, cláusulas contratuais padrão aprovadas pela ANPD, e consentimento
específico e destacado do titular.

Fonte: <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm>
*Pendência: este link não pôde ser aberto do ambiente onde a verificação foi
feita (HTTP 503). Confirmar com um clique antes de usar em peça pública.*

### Estudo do CTS/FGV Direito Rio — *IA Generativa e LGPD*

O Centro de Tecnologia e Sociedade da FGV Direito Rio avaliou a **documentação**
de sete plataformas de IA generativa — ChatGPT, Gemini, Claude, Copilot, Grok,
DeepSeek e Meta AI — contra **catorze critérios** extraídos do Guia de Segurança
da Informação para Agentes de Tratamento de Pequeno Porte, publicado pela ANPD
em 2021.

O que pode ser afirmado:

- Nenhuma das sete cumpre os catorze critérios.
- Só três critérios são cumpridos por todas: ter política de privacidade
  publicada, identificar o controlador, informar quais dados são coletados.
- Melhores avaliadas: Claude, Gemini e Meta AI, com **onze de catorze**.
- Piores: DeepSeek com cinco, Grok com seis.
- Entre as falhas que restam nas melhores está a **falta de clareza sobre os
  países para onde o dado é enviado** — o achado mais útil para o argumento do
  art. 33.

**Não é uma auditoria de conformidade com a LGPD.** É análise de documentação
contra catorze critérios. Um DPO percebe a diferença, e descrever como auditoria
custa credibilidade.

**Divulgação obrigatória:** o BALUARTE integra o Claude, que está entre as
melhores avaliadas. Dizer isso antes que o comprador descubra. Não enfraquece o
argumento — política de privacidade boa do provedor não é base legal documentada
da empresa cliente, e o art. 33 cobra a segunda.

Fonte: <https://direitorio.fgv.br/conhecimento/livrosia-generativa-e-lgpd-transparencia-desafios-regulatorios-e-caminhos-para>
*Pendência: link não pôde ser aberto do ambiente de verificação (HTTP 503).*

### ANPD — Nota Técnica nº 54/2025/FIS/CGF/ANPD

"Mapa de Temas Prioritários – biênio 2026-2027 (MTP 2026-2027)". Publicada em
dezembro de 2025. Traz inteligência artificial e tecnologias emergentes como um
dos eixos de fiscalização do biênio.

Título conferido na central de conteúdo oficial da autoridade.
Fonte: <https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos>

### ANPD — Nota Técnica nº 1/2026/FIS/CGF/ANPD

"Sistema de inteligência artificial Grok. Possíveis violações à Lei nº 13.709, de
14 de agosto de 2018 (Lei Geral de Proteção de Dados Pessoais – LGPD)."

Título conferido na mesma página oficial. É o precedente de atuação concreta da
autoridade sobre uma plataforma de IA.

---

## Refutado — não usar, em nenhuma peça

### Multa de 450 mil euros à fintech de Viena

**Não existe registro em fonte primária.** A afirmação de que a autoridade
austríaca de proteção de dados multou uma fintech vienense em €450 mil, em março
de 2026, por usar API de IA americana em scoring de crédito.

O que existe de real na Áustria não guarda relação com API de IA nem com o CLOUD
Act: o caso KSV1870, sobre scoring de crédito totalmente automatizado sob o art.
22 do GDPR, e uma decisão do Supremo Tribunal Administrativo de junho de 2026
sobre parâmetros estatísticos de scoring não serem dado pessoal. O levantamento
de multas do primeiro trimestre de 2026 lista Intesa Sanpaolo, Reddit, MediaLab
e Iliad/CNIL — nenhuma fintech vienense.

A origem da informação foi um blog de consultoria que vende "IA soberana" — uma
fonte com incentivo direto para inflar o caso.

**Não buscar caso substituto.** O argumento sobre CLOUD Act se sustenta no
raciocínio jurisdicional e não precisa de multa para existir. Foi justamente a
procura por um caso concreto que produziu esta citação.

Removida de: `index.html`, `docs/comercial-e-gtm.md` (slide 2 do pitch deck),
`docs/playbooks/marketing.md` (bloco de contexto mestre e Post 2 de aquecimento).

### "Política de privacidade sequer disponível em português"

Atribuída ao estudo da FGV como falha recorrente das plataformas avaliadas.
Nenhuma fonte confirma. Ao contrário: ter política de privacidade publicada é um
dos três critérios cumpridos por **todas** as sete.

### ANPD — Nota Técnica nº 12/2025/CON1/CGN/ANPD

Citada em rascunhos como consolidação da Tomada de Subsídios sobre IA. **Não
consta** da central de conteúdo da ANPD — as notas técnicas de 2025 listadas lá
são a 1, 6, 11, 17 e 54. A referência veio de blog de escritório de advocacia,
não do primário. Mesmo modo de falha do caso austríaco.

Se o documento existir em outra seção do site da ANPD, ele pode voltar — mas só
com link para a página oficial que o hospeda.

---

## Em aberto

| Item | Situação |
|---|---|
| **Placar da FGV: 11 ou 10 de 14** | O portal da própria FGV indica onze para Claude, Gemini e Meta AI, em duas buscas independentes. O Poder360 publicou dez. O material usa **onze**. Bater no PDF do estudo quando for possível abri-lo. |
| **Links do planalto e da FGV** | Ambos os domínios recusaram conexão (HTTP 503) do ambiente onde a verificação foi feita. Abrir os dois num navegador antes de qualquer publicação nova. |
| **Custo de violação de dados / shadow AI** | O documento comercial usa "relatórios de mercado já quantificam shadow AI como fator que eleva o custo médio de um incidente". Ainda **sem fonte identificada**. Não usar número específico até haver uma. |
| **Orientação de entidades de classe** | A afirmação de que entidades de classe orientam advogados e profissionais de saúde a não enviar dado de cliente a provedor de IA em nuvem é usada como gancho para o segmento jurídico. Falta identificar a peça específica — parecer, provimento ou recomendação — com link. |

---

## Como usar este arquivo

**Antes de publicar qualquer peça:** rodar os fatos dela contra a seção
"Confirmado". Qualquer coisa que não esteja lá, ou sai da peça, ou vira uma
entrada nova aqui — com link primário — antes de sair.

**Ao encontrar um fato novo:** verificar no primário antes de registrar. Fonte
secundária (jornal, blog de consultoria, escritório de advocacia) serve para
*achar* o fato, nunca para *confirmá-lo*. Os dois itens refutados acima entraram
por essa porta.

**Ao refutar algo:** mover para "Refutado" com o motivo e a lista de onde a
afirmação apareceu. Não apagar — o registro é o que impede a informação de voltar
por um rascunho antigo daqui a três meses.
