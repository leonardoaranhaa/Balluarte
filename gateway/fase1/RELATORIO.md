# Fase 1 — motor de política

**Data:** 16 de agosto de 2026
**Critério de saída:** determinismo provado em teste e explicabilidade funcionando.
**Resultado:** atingido. 122 testes, 62 deles do motor.

Reproduzir:

```bash
cd gateway
.venv/bin/python -m pytest tests -q        # 122 testes
.venv/bin/python -m fase1.demonstracao     # requisição inteira, explicada
```

---

## 1. O que foi construído

```
baluarte/politica/
  acoes.py        as quatro ações e a ordem de restritividade
  modelo.py       Politica e Regra, imutáveis, com sha256 do texto
  carregador.py   YAML → Politica, recusando tudo que falta
  catalogo.py     versões e a consulta "qual valia em tal data"
  avaliador.py    o motor
  decisao.py      o resultado explicável
  cobertura.py    a política menciona tudo que o classificador acha?
politicas/financeiro/
  v1.yaml         vigente desde 2026-08-01
  v2.yaml         vigente desde 2026-09-01, ao lado da v1, não no lugar dela
```

---

## 2. Precedência — a decisão que precisa da sua confirmação

O requisito diz "onde houver ambiguidade, a ação mais restritiva vence". Isso
só é decidível com uma definição escrita de "mais restritiva". A adotada:

> Restritiva é a ação que deixa menos dado pessoal disponível — no que sai e
> no que fica guardado.

```
permitir  <  tokenizar  <  mascarar  <  bloquear
```

**O degrau discutível é `mascarar` acima de `tokenizar`.** Pelo que sai da
empresa os dois se equivalem: o provedor não vê o valor em nenhum dos dois. A
diferença é o que fica para trás. Tokenizar é reversível por construção —
existe um cofre com o mapeamento, e cofre é superfície de ataque e objeto de
pedido de titular. Mascarar destrói o valor: não há o que vazar depois.

Tokenizar é melhor para a utilidade do modelo e pior para o risco residual.
Como a ordem é de proteção, e não de conveniência, mascarar ficou acima.

**Isto é decisão de produto, não de engenharia.** Está isolada em
`acoes.py`: inverter os dois é mudar uma linha, e há teste que falha alto se
alguém mudar sem querer. Se você discordar, é aqui que se muda.

A precedência completa, na ordem em que é aplicada:

| passo | regra |
|---|---|
| a | Toda regra cuja entidade casa é coletada — todas, não a primeira |
| b | Vence a ação mais restritiva entre elas |
| c | As justificativas citadas são só as das regras que pediram a ação vencedora |
| d | Entidade detectada sem regra cai no padrão declarado pela política |
| e | A decisão global é a mais restritiva entre as decisões por entidade |

O passo **c** merece nota: regra que pedia coisa menos restritiva não aparece
na explicação, porque não justifica a decisão tomada. Já o empate cita todas
as regras empatadas — quando duas regras pedem a mesma coisa, a explicação
honesta cita as duas.

---

## 3. Determinismo — o que o motor não pode fazer

Determinismo aqui é sustentado por três proibições, e não por cuidado:

**Não lê o relógio.** A data de avaliação entra como argumento. Se o motor
consultasse `date.today()`, reavaliar a mesma requisição amanhã poderia dar
outra resposta, e a pergunta "por que isso foi bloqueado em março?" ficaria
sem resposta reconstituível.

**Não recebe texto, recebe tipos.** A entrada é a lista de entidades
detectadas, nunca o conteúdo. Além de manter a regra 2 do `CLAUDE.md`, torna a
decisão auditável sem que o auditor precise ver dado de ninguém.

**Não tem estado nem ordem implícita.** `Counter` fixa a contagem, `sorted`
fixa a ordem de saída. Sem os dois, duas execuções com a mesma entrada podem
devolver a mesma informação em ordem diferente, e "mesma saída" deixa de ser
verificável por igualdade.

Provado por: 100 execuções idênticas comparando a decisão inteira — não só a
ação, mas ordem, contagem, justificativas e identificação da política.

---

## 4. Versionamento

Política é `frozen=True`. Não é preciosismo: a regra 5 diz que política nunca
é editada, só versionada. Se o objeto em memória puder ser alterado, a regra
vira convenção — e convenção é o que se quebra às três da manhã consertando
produção.

O catálogo recusa, **ao montar e nunca ao consultar**: versões repetidas,
duas versões com a mesma data de vigência, versão maior com vigência anterior
à de uma menor, e nomes diferentes no mesmo catálogo. Exceção de validação em
tempo de requisição faria o caminho falhar de forma imprevisível, que é o
oposto de fail-closed previsível.

Consulta a data anterior à primeira versão levanta `SemPoliticaVigente`, e não
devolve "permitir". Antes da primeira política não havia regra nenhuma;
responder qualquer ação seria inventar uma decisão que o cliente nunca tomou.

Cada decisão carrega o **sha256 do texto do arquivo**. Dizer "estava vigente a
v2" é fraco se a v2 pôde ser reescrita depois. Dizer "v2, sha256 2425a1f166f8"
é verificável contra o que está no repositório.

---

## 5. O achado da fase: fail-closed e classificador ruim não convivem

A demonstração roda um prompt de renegociação com CPF, CNPJ, e-mail e
telefone — todos com regra na política — e o resultado é **bloquear**, nas
duas datas.

O motivo não é defeito do motor. É que o classificador também emitiu
`PERSON`, `ORGANIZATION` e `URL`, que a política não menciona, e o padrão
`entidade_sem_regra` é `bloquear`.

Os dois lados estão certos sozinhos:

- **Fail-closed está certo.** Ausência de regra não é autorização. Afrouxar
  isso é o mesmo que deixar sair dado sobre o qual ninguém decidiu.
- **O padrão está certo.** É o que a regra 3 do `CLAUDE.md` manda.

E juntos são inutilizáveis, por dois motivos distintos:

**a) Lacuna de cobertura.** O classificador emite 15 tipos de entidade; a
política decide sobre 5. As outras 13 caem no padrão. Uma entidade esquecida
na política bloqueia toda requisição em que ela aparecer — e o cliente vai
atribuir isso a defeito do gateway, não a lacuna da própria política. Por isso
`cobertura.py`: confere o encaixe **antes** da política entrar em vigor.

**b) Achados sobrepostos.** Das três entidades sem regra que apareceram no
prompt, duas são sobreposição: `ORGANIZATION` e `URL` casaram **dentro do
próprio e-mail**, que já tinha sido detectado como `EMAIL_ADDRESS`.

```
EMAIL_ADDRESS  score=1.00  'marina@vetorcred.com.br'
ORGANIZATION   score=0.85  'marina@vetorcred.com.br'
URL            score=0.50  'vetorcred.com.br'
```

Não são dados novos, é o mesmo dado contado três vezes. Passar isso ao motor
infla a contagem e cria entidade sem regra do nada. **Resolver sobreposição é
trabalho da camada de classificação, não do motor** — o motor está certo em
decidir sobre o que recebe. Fica para a Fase 3, quando o proxy integrar as
duas camadas.

Somado ao que a Fase 0 já tinha medido — 25 de 26 achados de `PERSON` errados,
todos com score 0,85 — o quadro é claro: **enquanto o NER estiver assim, ligar
`PERSON` na política transforma o gateway numa parede.** Não é motivo para
afrouxar o padrão; é motivo para resolver o NER antes de prometer detecção de
nome a alguém.

---

## 6. Exemplo completo, como a fase pede

`fase1/demonstracao.py` mostra o caminho inteiro: o prompt que entra, o que a
classificação achou (tipo e contagem, nunca valor), as políticas disponíveis,
e a decisão explicada nas duas datas. Trecho da saída:

```
Decisão: tokenizar
Política vigente em 2026-08-15: Financeiro — renegociação e cobrança v1
(c895fb8f1cf9), em vigor desde 2026-08-01
  BR_CPF (1 ocorrência) → tokenizar
      regra de BR_CPF → tokenizar — LGPD art. 33 — enviar CPF a provedor fora
      do país é transferência internacional de dado pessoal e exige hipótese
      legal registrada.
  BR_CNPJ (1 ocorrência) → permitir
      regra de BR_CNPJ → permitir — CNPJ de pessoa jurídica não é dado pessoal
      na acepção do art. 5º, I, da LGPD. Permitido de forma explícita para que
      a decisão fique registrada como escolha, e não como omissão da política.
```

O mesmo prompt em setembro cai na v2 e o CPF vira `mascarar`, porque a v2
acrescentou uma segunda regra de CPF para a rota de cobrança em massa e
mascarar vence tokenizar. A v1 continua intacta ao lado da v2 — reavaliar
agosto hoje devolve exatamente a decisão de agosto.

---

## 7. O que esta fase deliberadamente não fez

Proxy, dashboard, banco e trilha de auditoria, conforme a instrução da fase. O
motor é isolado e testável: não abre conexão, não grava, não transforma texto.
Decide e explica.

## 8. Pendências

1. **Confirmar a ordem `mascarar` > `tokenizar`.** É decisão de produto.
2. Resolver sobreposição de achados na camada de classificação — Fase 3.
3. Fechar a cobertura das políticas, o que depende de resolver o NER.
4. Escopo de regra por rota e por provedor de destino. O
   `docs/produto-e-tecnico.md` prevê ("por classe de dado, por rota, por
   provedor"); esta fase entregou só por classe de dado. Quando entrar, a
   precedência ganha um segundo eixo — especificidade — e a regra de desempate
   precisa ser reescrita antes, não depois.
5. A Matriz de Classificação por setor (saúde, jurídico) é Fase 4. Só o perfil
   financeiro existe como exemplo.
