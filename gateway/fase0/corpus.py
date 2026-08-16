"""Conjunto de teste da Fase 0 — 50 trechos de texto corporativo brasileiro.

Todos os documentos são sintéticos, gerados com semente fixa (20260809) a
partir do próprio algoritmo de dígito verificador. Nenhum número aqui
pertence a alguém: os válidos foram construídos para fechar o DV, os
"quase" foram construídos para reprovar nele.

A anotação é por valor, não por posição. Guardar deslocamento em corpus
escrito à mão é como se erra: basta alguém corrigir uma vírgula do texto
para todos os offsets seguintes mentirem. O avaliador localiza as
ocorrências no texto e compara por conjunto.

Categorias existem para o relatório separar o que o critério de saída cobra
(`cpf_formatado`, `cnpj_formatado`) do que é bônus (`cpf_cru`, `cnpj_cru`) e
do que mede falso positivo (`quase`, `limpo`).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Caso:
    id: str
    categoria: str
    texto: str
    esperado: list[tuple[str, str]] = field(default_factory=list)


CPF = "BR_CPF"
CNPJ = "BR_CNPJ"

CASOS: list[Caso] = [
    # ── CPF formatado ────────────────────────────────────────────────
    Caso("cpf-f-01", "cpf_formatado",
         "Prezada equipe, segue para análise a proposta de renegociação do cliente "
         "Marina Alves, CPF 160.177.813-91, com saldo devedor de R$ 84.200 em 14 parcelas.",
         [(CPF, "160.177.813-91")]),
    Caso("cpf-f-02", "cpf_formatado",
         "O titular 553.615.258-04 solicitou portabilidade da conta salário para outra "
         "instituição. Prazo regulatório de resposta: cinco dias úteis.",
         [(CPF, "553.615.258-04")]),
    Caso("cpf-f-03", "cpf_formatado",
         "Chamado #4417 — cliente informa cobrança indevida de tarifa de manutenção. "
         "CPF: 028.446.391-43. Conta encerrada em março, tarifa lançada em abril.",
         [(CPF, "028.446.391-43")]),
    Caso("cpf-f-04", "cpf_formatado",
         "Resumo da consulta: paciente relatou dor torácica atípica há três dias. "
         "Documento 335.378.553-11. Encaminhado para eletrocardiograma de urgência.",
         [(CPF, "335.378.553-11")]),
    Caso("cpf-f-05", "cpf_formatado",
         "Minuta de acordo trabalhista. Reclamante portador do CPF 831.010.317-45, "
         "admitido em fevereiro de 2021, desligado sem justa causa em janeiro de 2026.",
         [(CPF, "831.010.317-45")]),
    Caso("cpf-f-06", "cpf_formatado",
         "Análise de crédito reprovada por comprometimento de renda acima de 40%. "
         "Proponente 223.894.173-88. Sugerir limite reduzido ou entrada maior.",
         [(CPF, "223.894.173-88")]),
    Caso("cpf-f-07", "cpf_formatado",
         "Dois titulares na mesma apólice: 203.137.068-59 e 843.363.526-31. "
         "Confirmar se a cobertura de invalidez vale para os dois ou só para o principal.",
         [(CPF, "203.137.068-59"), (CPF, "843.363.526-31")]),
    Caso("cpf-f-08", "cpf_formatado",
         "Pedido de exclusão de dados recebido pelo canal do encarregado. "
         "Titular: 033.593.355-62. Prazo do art. 18 da LGPD começa a contar hoje.",
         [(CPF, "033.593.355-62")]),
    Caso("cpf-f-09", "cpf_formatado",
         "Escreva um e-mail cordial cobrando a parcela vencida do cliente de CPF "
         "073.029.420-05, sem tom ameaçador e mencionando a opção de parcelamento.",
         [(CPF, "073.029.420-05")]),
    Caso("cpf-f-10", "cpf_formatado",
         "Auditoria interna: divergência entre o cadastro (768.866.937-51) e o "
         "comprovante de residência anexado. Solicitar novo documento ao cliente.",
         [(CPF, "768.866.937-51")]),
    Caso("cpf-f-11", "cpf_formatado",
         "Protocolo de atendimento 2026-88214, aberto em 03/08. Cliente 373.254.139-80 "
         "contesta o score de crédito e pede revisão manual da decisão automatizada.",
         [(CPF, "373.254.139-80")]),
    Caso("cpf-f-12", "cpf_formatado",
         "Resuma este prontuário para o encaminhamento: paciente de CPF 160.177.813-91, "
         "hipertenso, em uso contínuo de losartana, sem internações no último ano.",
         [(CPF, "160.177.813-91")]),

    # ── CPF sem formatação ───────────────────────────────────────────
    Caso("cpf-c-01", "cpf_cru",
         "Importação da planilha de inadimplentes concluída. Primeira linha divergente: "
         "documento 48007543309, valor em aberto R$ 1.240,00, vencido há 62 dias.",
         [(CPF, "48007543309")]),
    Caso("cpf-c-02", "cpf_cru",
         "O sistema legado grava sem máscara. Exemplo do retorno da API: "
         "{\"documento\": \"16379915680\", \"situacao\": \"ativo\"}. Precisamos normalizar.",
         [(CPF, "16379915680")]),
    Caso("cpf-c-03", "cpf_cru",
         "Conciliação bancária: o pagamento de R$ 3.508,33 veio identificado apenas "
         "pelo documento 49071370798, sem número de contrato.",
         [(CPF, "49071370798")]),
    Caso("cpf-c-04", "cpf_cru",
         "Cadastro duplicado detectado. Registros 11973558475 e 54574776226 têm o mesmo "
         "endereço e o mesmo telefone. Verificar antes de mesclar.",
         [(CPF, "11973558475"), (CPF, "54574776226")]),
    Caso("cpf-c-05", "cpf_cru",
         "Classifique o risco deste proponente: documento 19262575530, renda declarada "
         "R$ 7.400, sem restrições em birô, primeiro relacionamento com a casa.",
         [(CPF, "19262575530")]),
    Caso("cpf-c-06", "cpf_cru",
         "Log de erro do batch noturno: falha ao validar 29915510977 na rotina de KYC. "
         "Reprocessar após corrigir o mapeamento de campos.",
         [(CPF, "29915510977")]),
    Caso("cpf-c-07", "cpf_cru",
         "Beneficiário do plano: 94205303378. Solicita inclusão de dependente menor de "
         "idade. Documentação de guarda ainda não foi anexada ao processo.",
         [(CPF, "94205303378")]),
    Caso("cpf-c-08", "cpf_cru",
         "Migração de base: 15942078440 e 28480806710 vieram sem data de nascimento. "
         "Sem esse campo a política de retenção não consegue ser aplicada.",
         [(CPF, "15942078440"), (CPF, "28480806710")]),

    # ── CNPJ formatado ───────────────────────────────────────────────
    Caso("cnpj-f-01", "cnpj_formatado",
         "Contrato de prestação de serviços firmado com a fornecedora inscrita no CNPJ "
         "78.952.860/0001-12, com vigência de doze meses e reajuste anual pelo IPCA.",
         [(CNPJ, "78.952.860/0001-12")]),
    Caso("cnpj-f-02", "cnpj_formatado",
         "Nota fiscal rejeitada pela SEFAZ: divergência de inscrição estadual para o "
         "CNPJ 81.717.879/0001-99. Reemitir após correção cadastral.",
         [(CNPJ, "81.717.879/0001-99")]),
    Caso("cnpj-f-03", "cnpj_formatado",
         "Due diligence do fornecedor 75.139.520/0001-89: certidão negativa de débitos "
         "federais válida, certidão trabalhista vencida em julho.",
         [(CNPJ, "75.139.520/0001-89")]),
    Caso("cnpj-f-04", "cnpj_formatado",
         "Redija a cláusula de confidencialidade do contrato entre a nossa empresa e a "
         "51.090.867/0001-16, prevendo vigência de cinco anos após o término.",
         [(CNPJ, "51.090.867/0001-16")]),
    Caso("cnpj-f-05", "cnpj_formatado",
         "Matriz 72.502.266/0001-43 e filial 71.323.940/0001-60 aparecem com o mesmo "
         "responsável legal no cadastro. Confirmar se é erro de digitação.",
         [(CNPJ, "72.502.266/0001-43"), (CNPJ, "71.323.940/0001-60")]),
    Caso("cnpj-f-06", "cnpj_formatado",
         "Bloqueio cautelar aplicado ao recebível da 66.191.930/0001-88 até a conclusão "
         "da apuração de fraude no faturamento antecipado.",
         [(CNPJ, "66.191.930/0001-88")]),
    Caso("cnpj-f-07", "cnpj_formatado",
         "Proposta comercial para 93.783.507/0001-40: mil chamadas por dia, três "
         "ambientes, suporte em horário comercial. Preparar minuta com o DPA anexo.",
         [(CNPJ, "93.783.507/0001-40")]),
    Caso("cnpj-f-08", "cnpj_formatado",
         "O contrato social da 67.539.530/0001-83 não confere com a procuração "
         "apresentada. Suspender a assinatura até esclarecimento do jurídico.",
         [(CNPJ, "67.539.530/0001-83")]),

    # ── CNPJ sem formatação ──────────────────────────────────────────
    Caso("cnpj-c-01", "cnpj_cru",
         "Retorno do webservice da Receita para 36219870000101: situação cadastral "
         "ativa, natureza jurídica 206-2, porte demonstrado como ME.",
         [(CNPJ, "36219870000101")]),
    Caso("cnpj-c-02", "cnpj_cru",
         "Arquivo de remessa com o campo sem máscara: 33814726000117 aparece em 14 "
         "linhas distintas, todas com o mesmo valor de duplicata.",
         [(CNPJ, "33814726000117")]),
    Caso("cnpj-c-03", "cnpj_cru",
         "Conciliar 85727241000190 com o extrato de repasse do dia 05. A diferença de "
         "R$ 217,40 pode ser tarifa de antecipação não provisionada.",
         [(CNPJ, "85727241000190")]),
    Caso("cnpj-c-04", "cnpj_cru",
         "Cadastro de parceiro incompleto: 46404034000142 sem endereço de cobrança e "
         "sem contato do responsável financeiro.",
         [(CNPJ, "46404034000142")]),
    Caso("cnpj-c-05", "cnpj_cru",
         "Analise a exposição da carteira ao grupo econômico de 31615546000180, "
         "considerando as coligadas informadas no último balanço auditado.",
         [(CNPJ, "31615546000180")]),

    # ── Quase-documentos: onze ou catorze dígitos que reprovam no DV ──
    Caso("quase-01", "quase",
         "Protocolo de atendimento 09076944934 registrado no canal do consumidor. "
         "Nenhum dado do titular foi informado nesta abertura.",
         []),
    Caso("quase-02", "quase",
         "Número de série do equipamento: 88058548779. Garantia expira em outubro, "
         "conforme a nota de compra anexada ao chamado.",
         []),
    Caso("quase-03", "quase",
         "Código de rastreio interno 42652109896 e lote 34098536994 — os dois vieram "
         "truncados na integração e precisam ser reenviados.",
         []),
    Caso("quase-04", "quase",
         "Matrícula funcional 81577506770 no sistema de ponto. Sem relação com o "
         "cadastro de clientes, é numeração própria do RH.",
         []),
    Caso("quase-05", "quase",
         "O campo veio preenchido com 376.108.708-13, mas a validação recusou. "
         "Provável erro de digitação no atendimento por telefone.",
         []),
    Caso("quase-06", "quase",
         "Sequências de teste usadas na homologação: 546.022.003-07, 675.047.977-90 e "
         "977.814.427-35. Nenhuma deve entrar em base de produção.",
         []),
    Caso("quase-07", "quase",
         "Identificador da transação 25826802645, timestamp 2026-08-09T11:20:03-03:00, "
         "gateway de pagamento retornou recusa por saldo insuficiente.",
         []),
    Caso("quase-08", "quase",
         "Chave de integração legada 18231336841 e token de sessão 74529167744 foram "
         "rotacionados na manutenção da madrugada.",
         []),
    Caso("quase-09", "quase",
         "Inscrição municipal 08347535291174 divergente do cadastro. A prefeitura usa "
         "numeração própria, com catorze dígitos, que não é CNPJ.",
         []),
    Caso("quase-10", "quase",
         "Registro de exportação 84687375306655 e averbação 37344618631642 pendentes "
         "de baixa no sistema aduaneiro.",
         []),

    # ── Texto corporativo sem dado pessoal ───────────────────────────
    Caso("limpo-01", "limpo",
         "Resuma as três principais objeções levantadas na reunião de ontem com a área "
         "de risco e sugira uma resposta objetiva para cada uma.",
         []),
    Caso("limpo-02", "limpo",
         "Qual é o desconto máximo que posso oferecer na carteira B sem aprovação do "
         "comitê de crédito? Considere apenas juros e multa, não o principal.",
         []),
    Caso("limpo-03", "limpo",
         "Escreva a política interna de uso de ferramentas de inteligência artificial, "
         "em linguagem acessível, para circular entre as áreas de negócio.",
         []),
    Caso("limpo-04", "limpo",
         "Reformule este parágrafo do contrato para deixar claro que o prazo de "
         "carência conta a partir da assinatura, não da vigência.",
         []),
    Caso("limpo-05", "limpo",
         "Liste os indicadores que a diretoria costuma pedir no fechamento mensal e "
         "diga quais deles já saem prontos do nosso relatório atual.",
         []),
    Caso("limpo-06", "limpo",
         "Compare as duas propostas de fornecedor considerando prazo de implantação, "
         "custo recorrente e dependência de serviço externo.",
         []),
    Caso("limpo-07", "limpo",
         "Explique, para alguém sem formação jurídica, a diferença entre controlador e "
         "operador na Lei Geral de Proteção de Dados.",
         []),
]

assert len(CASOS) == 50, f"o conjunto precisa ter 50 casos, tem {len(CASOS)}"
