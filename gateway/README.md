# gateway

O gateway do BALUARTE. Fases 0 e 1 concluídas — ver
[`fase0/RELATORIO.md`](fase0/RELATORIO.md) e
[`fase1/RELATORIO.md`](fase1/RELATORIO.md).

Vive em `gateway/` e não na raiz de propósito: a raiz é o site estático
publicado pela Vercel, e um `requirements.txt` lá em cima faria a Vercel
tentar detectar o projeto como Python.

## Rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download pt_core_news_sm

.venv/bin/python -m pytest tests -q        # 122 testes
.venv/bin/python -m fase0.avaliar          # 50 casos, falso negativo e latência
.venv/bin/python -m fase1.demonstracao     # requisição inteira, decidida e explicada
```

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
politicas/financeiro/               v1 e v2, lado a lado, nunca sobrescritas
fase0/                              corpus, métricas e relatório da premissa
fase1/                              demonstração ponta a ponta e relatório
tests/                              122 testes
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

## O que ainda não existe

Tokenização, trilha de auditoria, proxy e dashboard. Fases 2 a 5 do
[`docs/playbooks/construcao.md`](../docs/playbooks/construcao.md).

Este gateway ainda **não** intercepta tráfego real: classifica, decide e
explica — não transforma, não grava e não encaminha.
