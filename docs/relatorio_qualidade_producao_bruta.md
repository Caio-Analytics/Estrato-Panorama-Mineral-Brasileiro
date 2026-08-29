# Relatório de inconsistências — Producao_Bruta

Gerado a partir do perfilamento automático (`recon`, versão 3.0.0) rodado em 2026-08-29T01:39:09.206327+00:00, sobre 6,313 linhas / 14 colunas. Extração fiel do que o profiler sinalizou — pontos aqui **não foram corrigidos** nesta pipeline, ficam para o próximo passo.

**Score de qualidade:** 63.5/100 (nota C) · 9 coluna(s) comprometida(s) · 0 linha(s) duplicada(s)

## Colunas críticas

| Coluna | Dano | Motivo(s) |
|---|---|---|
| Indicação Contido | 0.72 | 72% de nulos |
| Quantidade Produção - Minério ROM (t) | 0.70 | mistura de tipos |
| Quantidade Contido | 0.70 | mistura de tipos |
| Quantidade Transformação / Consumo / Utilização (t) | 0.70 | mistura de tipos |
| Valor Transformação / Consumo / Utilização nesta mina (R$) | 0.70 | mistura de tipos |
| Quantidade Transferência para Transformação / Utilização / Consumo (t) | 0.70 | mistura de tipos |
| Valor Transferência para Transformação / Utilização / Consumo (R$) | 0.70 | mistura de tipos |
| Unidade de Medida - Contido | 0.60 | nulos disfarçados |
| Quantidade Venda (t) | 0.50 | grafias divergentes |

## Risco LGPD

Nível: 🔴 Alta (exposição 0.9)

| Coluna | Tipo sinalizado |
|---|---|
| Ano base | Nome de pessoa |

> 1 coluna(s) com dado pessoal. Mascarar ou hashear antes de compartilhar o arquivo, e restringir quem acessa a camada que guarda o valor original.

## Recomendações de ETL

| Prioridade | Coluna | Camada | Ação | Linhas afetadas | % impacto |
|---|---|---|---|---|---|
| 🔴 ALTA | Ano base | Silver | LGPD: Mascarar/Hashear 'Ano base' (Nome de pessoa). Protege 6,313 registros (100.0%). | 6,313 | 100.0% |
| 🔴 ALTA | Quantidade Produção - Minério ROM (t) | Bronze | 'Quantidade Produção - Minério ROM (t)' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🔴 ALTA | Quantidade Contido | Bronze | 'Quantidade Contido' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🔴 ALTA | Unidade de Medida - Contido | Bronze | 'Unidade de Medida - Contido' usa '-' como marcador de ausência em 4,041 registros (64.0%). Converter para NULL — hoje entram como valor válido e distorcem contagens e médias. | 4,041 | 64.0% |
| 🟡 MÉDIA | Quantidade Venda (t) | Silver | 'Quantidade Venda (t)' tem o mesmo valor escrito de formas diferentes (ex.: '145' / '14,5'). Padronizar reduz a cardinalidade de 3729 para 3727 — sem isso qualquer GROUP BY divide o mesmo grupo em vários. | 6,313 | 100.0% |
| 🟡 MÉDIA | Quantidade Transformação / Consumo / Utilização (t) | Bronze | 'Quantidade Transformação / Consumo / Utilização (t)' segue o formato ,999999 em 83% dos valores (ex.: ',000000'), mas 852 valor(es) fogem dele: '500,000000', '187,610000', '58661,000000'. Em código de cadastro isso costuma ser digitação manual, campo truncado ou registro de outro sistema — conferir antes de usar como chave. | 852 | — |
| 🔴 ALTA | Quantidade Transformação / Consumo / Utilização (t) | Bronze | 'Quantidade Transformação / Consumo / Utilização (t)' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🟡 MÉDIA | Valor Transformação / Consumo / Utilização nesta mina (R$) | Bronze | 'Valor Transformação / Consumo / Utilização nesta mina (R$)' segue o formato ,999999 em 83% dos valores (ex.: ',000000'), mas 838 valor(es) fogem dele: '22500,000000', '32000,000000', '9260950,810000'. Em código de cadastro isso costuma ser digitação manual, campo truncado ou registro de outro sistema — conferir antes de usar como chave. | 838 | — |
| 🔴 ALTA | Valor Transformação / Consumo / Utilização nesta mina (R$) | Bronze | 'Valor Transformação / Consumo / Utilização nesta mina (R$)' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🔴 ALTA | Quantidade Transferência para Transformação / Utilização / Consumo (t) | Bronze | 'Quantidade Transferência para Transformação / Utilização / Consumo (t)' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🔴 ALTA | Valor Transferência para Transformação / Utilização / Consumo (R$) | Bronze | 'Valor Transferência para Transformação / Utilização / Consumo (R$)' contém mistura de tipos: ['numerico', 'texto_puro']. Normalizar antes de qualquer transformação. | 6,313 | 100.0% |
| 🟢 BAIXA | (tabela) | Silver | Otimizar o dtype de 11 coluna(s) economiza 0.8 MB em memória: Ano base → int16, UF → category, Classe Substância → category, Substância Mineral → category (+7). O script de limpeza gerado já aplica todas. | 6,313 | — |

## Sumário por coluna

| Coluna | Tipo inferido | % nulos | Únicos | Observações |
|---|---|---|---|---|
| Ano base | Número Inteiro | 0.0% | 16 | — |
| UF | Texto | 0.0% | 27 | — |
| Classe Substância | Texto | 0.0% | 4 | — |
| Substância Mineral | Texto | 0.0% | 56 | — |
| Quantidade Produção - Minério ROM (t) | Texto | 0.0% | 5,423 | mistura de tipos |
| Quantidade Contido | Texto | 0.0% | 1,711 | mistura de tipos |
| Unidade de Medida - Contido | Texto | 0.0% | 4 | possui sentinela de nulo |
| Indicação Contido | Texto | 71.7% | 27 | — |
| Quantidade Venda (t) | Texto | 0.0% | 3,729 | inconsistência de normalização |
| Valor Venda (R$) | Texto | 0.0% | 3,760 | — |
| Quantidade Transformação / Consumo / Utilização (t) | Texto | 0.0% | 1,028 | mistura de tipos |
| Valor Transformação / Consumo / Utilização nesta mina (R$) | Texto | 0.0% | 1,019 | mistura de tipos |
| Quantidade Transferência para Transformação / Utilização / Consumo (t) | Texto | 0.0% | 1,971 | mistura de tipos |
| Valor Transferência para Transformação / Utilização / Consumo (R$) | Texto | 0.0% | 1,974 | mistura de tipos |
