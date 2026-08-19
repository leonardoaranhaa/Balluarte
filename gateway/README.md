# gateway

O gateway do BALUARTE. Fases 0 a 3 concluídas — ver
[`fase0/`](fase0/RELATORIO.md), [`fase1/`](fase1/RELATORIO.md),
[`fase2/`](fase2/RELATORIO.md) e [`fase3/`](fase3/RELATORIO.md).

Vive em `gateway/` e não na raiz de propósito: a raiz é o site estático
publicado pela Vercel, e um `requirements.txt` lá em cima faria a Vercel
tentar detectar o projeto como Python.

## Rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download pt_core_news_sm

.venv/bin/python -m pytest tests -q        # 183 testes
.venv/bin/python -m fase0.avaliar          # 50 casos, falso negativo e latência
.venv/bin/python -m fase1.demonstracao     # requisição inteira, decidida e explicada
.venv/bin/python -m fase2.demonstracao     # integridade: íntegra passa, adulterada falha
.venv/bin/python -m fase3.latencia         # overhead medido, não estimado
```

A Fase 2 precisa de Postgres. Sem ele, os 24 testes de banco **pulam com
mensagem** em vez de falhar — quem roda sem banco precisa saber que não rodou
a Fase 2, e não achar que quebrou algo. Para apontar para outro servidor:
`BALUARTE_DSN_TESTE=postgresql://…`

## O que existe

```
baluarte/
  analisador.py                     fábrica única do AnalyzerEngine
  guardrail.py                      guardrail do LiteLLM, em pre_call
  reconhecedores/
    digito_verificador.py           aritmética de DV de CPF e CNPJ
    documentos_br.py                recognizers do Presidio
  politica/                         o motor — é aqui que mora o produto
    acoes.py                        as quatro ações e a ordem de restritividade
    modelo.py                       Politica e Regra, imutáveis, com sha256
    carregador.py                   YAML → Politica, recusando o que falta
    catalogo.py                     versões e "qual valia em tal data"
    avaliador.py                    determinístico, sem LLM e sem relógio
    decisao.py                      o resultado explicável
    cobertura.py                    a política cobre o que o classificador acha?
  auditoria/                        a trilha — é o que dá valor jurídico
    registro.py                     serialização canônica e hash do elo
    esquema.py                      migrations versionadas, uma vez cada
    repositorio.py                  grava e lê, sempre dentro de um tenant
    verificacao.py                  percorre a cadeia e diz ONDE quebrou
  tokenizacao/                      cofre com chave por tenant, e transformação
  classificacao/                    resolução de achados sobrepostos
  proxy/                            o gateway HTTP, compatível com a Anthropic
migrations/                         001 trilha append-only, 002 segregação
politicas/financeiro/               v1 e v2, lado a lado, nunca sobrescritas
fase0/ … fase3/                     relatórios e demonstrações de cada fase
tests/                              183 testes
```

## Duas coisas que o código faz de propósito e parecem exagero

**O relatório mascara documento.** Os números do corpus são sintéticos e estão
versionados — imprimi-los não vazaria nada. Mesmo assim o avaliador mascara,
porque a regra 2 do `CLAUDE.md` não abre exceção para desenvolvimento, e
ferramenta que imprime valor em claro "só no teste" é como o hábito entra.

**O guardrail devolve posição, nunca valor.** `classificar()` entrega tipo,
início, fim e score. Assim a regra 2 vale por construção da estrutura de dados,
e não por disciplina de quem for escrever o log depois.

**A ordem de restritividade é decisão de produto.** `permitir < tokenizar <
mascarar < bloquear`. O degrau discutível é mascarar acima de tokenizar: pelo
que sai da empresa os dois se equivalem, mas tokenizar deixa um cofre para
trás e mascarar não. Está isolada em `politica/acoes.py` — inverter é mudar
uma linha, e um teste falha alto se alguém mudar sem querer.

**A trilha não tem onde guardar valor.** Não é que a aplicação evite
preencher: não existe coluna. A regra 2 vira propriedade do esquema, e há
teste varrendo a linha inteira em SQL — assim coluna nova entra na varredura
sozinha, sem ninguém lembrar de atualizar o teste.

**A segregação é do banco, não do `WHERE`.** Row-level security por tenant,
com o valor vindo de `SET LOCAL`. Um `WHERE` esquecido no repositório deixa de
ser vazamento entre clientes, e sessão sem tenant declarado vê zero linhas em
vez da base toda.

**O corpo da requisição não é reserializado.** Campo que o BALUARTE não conhece
atravessa intacto — inclusive campo que ainda não existe. É o que sustenta
"troca só a URL base" quando a Anthropic acrescentar um parâmetro. Há teste com
`parametro_que_ainda_nao_existe`.

## O que ainda não existe

Perfis por setor, Dossiê e dashboard. Fases 4 e 5 do
[`docs/playbooks/construcao.md`](../docs/playbooks/construcao.md).

Este gateway ainda **não** intercepta tráfego real: classifica, decide e
explica — não transforma, não grava e não encaminha.
