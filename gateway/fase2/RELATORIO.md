# Fase 2 — trilha de auditoria

**Data:** 16 de agosto de 2026
**Critério de saída:** teste de vazamento de PII passando e integridade verificável.
**Resultado:** atingido. 146 testes, 24 deles contra Postgres de verdade.

Reproduzir:

```bash
cd gateway
.venv/bin/python -m pytest tests -q        # 146 testes
.venv/bin/python -m fase2.demonstracao     # íntegra passa, adulterada falha
```

Os testes de banco **pulam com mensagem** quando não há Postgres, em vez de
falharem: quem roda a suíte sem banco precisa saber que não rodou a Fase 2, e
não achar que quebrou alguma coisa.

---

## 1. A regra crítica: nenhum valor de PII em campo nenhum

O requisito 4 pede um teste que passe uma requisição com CPF real e varra
**todos** os campos do registro procurando o valor. Está em
`test_nenhum_valor_de_pii_em_nenhum_campo_do_registro`, e a varredura é feita
em SQL sobre a linha inteira convertida em texto:

```sql
SELECT trilha_auditoria::text FROM trilha_auditoria
```

Escolhido assim de propósito. Varrer o objeto Python só cobriria os campos que
alguém lembrou de listar; varrer a linha inteira cobre **também as colunas que
ainda não existem** — quando alguém acrescentar uma, ela entra na varredura
sozinha. O teste procura CPF formatado, CPF cru, e-mail, nome e fragmentos de
cada um.

Mas o teste é a segunda linha de defesa. A primeira é o esquema: **não existe
coluna onde um valor caberia.** Há um teste que confere isso contra o
`information_schema`, procurando `valor`, `conteudo`, `texto`, `prompt`,
`payload` e `corpo`. A regra 2 do `CLAUDE.md` vira propriedade da tabela, e não
disciplina de quem escreve o `INSERT`.

O que fica registrado é tipo, quantidade e ação:

```json
[{"acao": "tokenizar", "entidade": "BR_CPF", "quantidade": 2},
 {"acao": "mascarar",  "entidade": "EMAIL_ADDRESS", "quantidade": 1}]
```

Que um CPF foi detectado, jamais qual. E também: **não basta não vazar, tem que
servir** — há teste cobrando que a quantidade e a ação estejam lá.

---

## 2. Append-only, em duas camadas

| camada | o que faz | de quem protege |
|---|---|---|
| `GRANT SELECT, INSERT` | o papel da aplicação não tem `UPDATE` nem `DELETE` | do código da aplicação |
| Gatilho `BEFORE UPDATE/DELETE/TRUNCATE` | levanta exceção | de quem entra com `psql` e privilégio demais |

As duas de propósito. O privilégio protege do caminho normal; o gatilho protege
da mão que de fato altera trilha quando alguém quer alterar trilha. `TRUNCATE`
tem gatilho próprio porque não passa por gatilho de linha — é o buraco que se
esquece.

O repositório **não tem método** de alterar nem de apagar. Não é esquecimento:
oferecer o método faria o chamador acreditar que o caminho existe.

---

## 3. Encadeamento por hash

Cada registro carrega o `sha256` do anterior; o primeiro aponta para 64 zeros.
O hash é calculado sobre uma **serialização canônica explícita** — campo por
campo, `chave=valor`, uma por linha, em ordem fixa.

Escolhida em vez de JSON de objeto Python porque precisa ser recomputável anos
depois por quem não tem o código que gravou. Qualquer forma que dependa de
`repr`, de ordem de dicionário ou de versão de biblioteca transforma "verificar
a integridade" em "torcer para a serialização não ter mudado". Do jeito que
está, quem audita monta a mesma string no terminal e roda `sha256sum`.

A verificação diz **onde** quebrou, não só que quebrou. Numa discussão sobre
adulteração, "a trilha está corrompida" vale pouco:

```
Cadeia ADULTERADA: 1 quebra(s) em 4 registros.
Conferidos até a primeira quebra: 2.
  registro 3: conteúdo alterado — hash gravado 76a0fe25d644…, recalculado
  43c37c325d7c…. Algum campo mudou depois da gravação.
```

Detecta três coisas distintas, e distingue entre elas:

| o que aconteceu | como aparece |
|---|---|
| Campo alterado | `conteúdo alterado` — o hash recalculado não bate com o gravado |
| Registro removido | `elo rompido` — nenhum registro mudou, o encadeamento é que denuncia |
| Registros reordenados | `elo rompido` |

---

## 4. A cadeia é por tenant, e isso não é detalhe

Uma cadeia única para todos os clientes obrigaria o tenant A a ler o hash de
registros do tenant B para verificar a própria integridade. Isso colide de
frente com a segregação: ou o cliente enxerga metadado alheio, ou não consegue
verificar a própria trilha.

Com uma cadeia por tenant, as duas propriedades coexistem. Há teste provando
que adulterar a trilha de um cliente não invalida a do outro.

---

## 5. Segregação imposta pelo banco, não pelo `WHERE`

A segregação podia viver no repositório, com um `WHERE tenant = %s` em toda
consulta. Não vive, porque **um `WHERE` esquecido é um vazamento entre clientes
e nada avisa.**

Está em row-level security, com o tenant vindo de `SET LOCAL baluarte.tenant`:

- `LOCAL` e não `SESSION`: o valor morre com a transação, então conexão
  devolvida ao pool não carrega o tenant anterior para quem pegar depois — o
  vazamento mais fácil de escrever e mais difícil de enxergar.
- Sessão que **não declarou** tenant vê **zero linhas**, nunca a base toda.
  `current_setting(..., true)` devolve `NULL`, a comparação dá `NULL`, e a
  política trata como falso. Falha fechada.
- `FORCE ROW LEVEL SECURITY` para valer também para o dono da tabela.

Provado com uma consulta **sem `WHERE`**, rodando como o papel da aplicação,
que ainda assim só enxerga o próprio tenant.

---

## 6. O erro que a demonstração pegou e os testes não

Ao escrever a demonstração, adulterei um registro e a verificação continuou
dizendo **cadeia íntegra**. Parecia bug na verificação. Não era: o registro
escolhido tinha `acao_global = 'permitir'` e eu o alterei para `'permitir'`. A
alteração foi no-op, o conteúdo não mudou, e o hash — corretamente — não mudou.

O risco não é o erro de digitação. É que **um teste de adulteração que vira
no-op passa para sempre e não prova nada**. Se a fixture mudar de um jeito que
faça o `UPDATE` não casar nenhuma linha, o teste continua verde enquanto para
de testar.

Consertado nos dois lugares: a demonstração aborta se o valor antes e depois
forem iguais, e o teste usa `RETURNING` com um `assert` de que alguma linha foi
alterada.

---

## 7. Concorrência

O `registrar` toma `pg_advisory_xact_lock` por tenant antes de ler o último
hash. Sem isso, duas requisições simultâneas do mesmo tenant leem o mesmo
`hash_anterior` e a cadeia se bifurca — e cadeia bifurcada é **indistinguível
de cadeia adulterada** na verificação. Seria um falso positivo de adulteração
sob carga, que é o pior tipo de defeito para este produto.

O bloqueio é por tenant, não global: dois clientes distintos não se serializam
entre si.

---

## 8. Migrations

`migrations/001_trilha_auditoria.sql` e `002_segregacao_por_tenant.sql`,
aplicadas em ordem e registradas em `migracoes` com o `sha256` de cada arquivo.
Editar migration já aplicada levanta `MigrationAlterada` — é a forma silenciosa
de o esquema de produção divergir do que o repositório diz.

Cada migration roda na sua própria transação. Rodar tudo numa transação só
pareceria mais seguro e deixaria o banco num estado que o registro não
descreve.

---

## 9. O que esta fase deliberadamente não fez

Proxy e dashboard, conforme as fases seguintes. A trilha grava a decisão do
motor; ainda não existe requisição real chegando, porque isso é a Fase 3.

## 10. Pendências

1. **Retenção.** A trilha cresce sem limite e não há política de descarte. O
   art. 16 da LGPD cobra eliminação após o fim do tratamento — mas apagar
   registro de trilha append-only exige decidir antes o que significa
   "eliminar" numa cadeia encadeada. É decisão jurídica antes de técnica.
2. **Exportação assinada.** O Dossiê da Fase 4 vai precisar de um recorte da
   trilha que o cliente possa entregar a um auditor sem entregar o banco.
3. **Verificação incremental.** Hoje `verificar` percorre a cadeia inteira.
   Com milhões de registros isso deixa de caber numa requisição; vai precisar
   de âncora periódica.
4. **Relógio.** `registrado_em` vem da aplicação. Para trilha com valor
   jurídico, vale avaliar carimbo do próprio banco ou fonte externa, e
   registrar a diferença entre os dois.
