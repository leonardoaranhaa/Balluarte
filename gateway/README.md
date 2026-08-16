# gateway

O gateway do BALUARTE. Fase 0 concluída — ver
[`fase0/RELATORIO.md`](fase0/RELATORIO.md).

Vive em `gateway/` e não na raiz de propósito: a raiz é o site estático
publicado pela Vercel, e um `requirements.txt` lá em cima faria a Vercel
tentar detectar o projeto como Python.

## Rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download pt_core_news_sm

.venv/bin/python -m pytest tests -q   # 60 testes
.venv/bin/python -m fase0.avaliar     # conjunto de 50 casos, com métricas
```

## O que existe

```
baluarte/
  analisador.py                     fábrica única do AnalyzerEngine
  guardrail.py                      guardrail do LiteLLM, em pre_call
  reconhecedores/
    digito_verificador.py           aritmética de DV de CPF e CNPJ
    documentos_br.py                recognizers do Presidio
fase0/
  corpus.py                         50 casos anotados, documentos sintéticos
  avaliar.py                        falso negativo, falso positivo, latência
  RELATORIO.md                      o resultado e a avaliação da premissa
tests/                              60 testes
```

## Duas coisas que o código faz de propósito e parecem exagero

**O relatório mascara documento.** Os números do corpus são sintéticos e estão
versionados — imprimi-los não vazaria nada. Mesmo assim o avaliador mascara,
porque a regra 2 do `CLAUDE.md` não abre exceção para desenvolvimento, e
ferramenta que imprime valor em claro "só no teste" é como o hábito entra.

**O guardrail devolve posição, nunca valor.** `classificar()` entrega tipo,
início, fim e score. Assim a regra 2 vale por construção da estrutura de dados,
e não por disciplina de quem for escrever o log depois.

## O que ainda não existe

Motor de política, tokenização, trilha de auditoria, dashboard. Fases 1 a 5 do
[`docs/playbooks/construcao.md`](../docs/playbooks/construcao.md).

Este gateway ainda **não** intercepta tráfego real: o guardrail classifica e
anota, não transforma nem bloqueia. Bloquear sem motor de política seria
decidir sem base normativa, que é o oposto do produto.
