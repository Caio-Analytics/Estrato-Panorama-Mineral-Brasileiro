# Perfilamento e triagem técnica: Producao_Bruta

Este documento parte do perfilamento automático do `recon` (versão 3.0.0), executado em 2026-08-29T01:39:09.206327+00:00 sobre 6,313 linhas e 14 colunas. Os achados foram revisados à luz do dicionário da fonte e das regras implementadas no staging; o score automático não é apresentado como diagnóstico final.

## Resultado da triagem

| Achado automático | Decisão técnica | Tratamento na pipeline |
|---|---|---|
| `Ano base` classificado como dado pessoal | Falso positivo. O próprio perfil indica a heurística `ano` → `aluno`; a coluna é um ano inteiro com 16 valores. | Convertido para `smallint`. |
| Seis campos numéricos classificados como mistura de tipos | Falso positivo. Os valores usam decimal brasileiro e foram preservados como texto no Bronze. | `parse_br_decimal` converte vírgula decimal para `DOUBLE` no staging. |
| `Unidade de Medida - Contido` com `-` como ausência | Confirmado. | `nullif(..., '-')` converte o sentinela para nulo no staging. |
| `Quantidade Venda (t)` com grafias divergentes | Falso positivo. `145` e `14,5` são valores numéricos distintos, não grafias do mesmo valor. | Conversão numérica preserva a diferença entre os valores. |
| `Indicação Contido` com 71,7% de nulos | Característica da fonte a monitorar; não impede a modelagem das métricas de produção e venda. | Campo é preservado na camada de staging. |

## Sinais do perfilamento automático

O profiler atribuiu score 63.5/100 (nota C) e marcou 9 colunas. Após a triagem, esse score deve ser lido como sensível ao formato da fonte, não como uma nota da qualidade analítica do dataset. Não foram encontradas linhas duplicadas no perfilamento (0 de 6,313).

## Colunas sinalizadas

| Coluna | Sinal do profiler | Leitura revisada |
|---|---|---|
| Indicação Contido | 72% de nulos | Nulos preservados e monitorados. |
| Quantidade Produção - Minério ROM (t) | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Quantidade Contido | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Quantidade Transformação / Consumo / Utilização (t) | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Valor Transformação / Consumo / Utilização nesta mina (R$) | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Quantidade Transferência para Transformação / Utilização / Consumo (t) | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Valor Transferência para Transformação / Utilização / Consumo (R$) | mistura de tipos | Decimal brasileiro, tratado no staging. |
| Unidade de Medida - Contido | nulos disfarçados | Sentinela `-` convertida para nulo. |
| Quantidade Venda (t) | grafias divergentes | Valores distintos; não há normalização a aplicar. |

## Regras implementadas

- O Bronze mantém as colunas da fonte como texto, evitando perda de informação na ingestão.
- O staging converte os decimais brasileiros com a macro `parse_br_decimal`.
- A unidade `-` em `Unidade de Medida - Contido` é convertida para nulo.
- `Ano base` é convertido para `smallint`; não há dado pessoal nessa coluna.

## Sumário da fonte

| Métrica | Valor |
|---|---|
| Linhas analisadas | 6,313 |
| Colunas | 14 |
| Linhas duplicadas | 0 |
| Período disponível | 2010 a 2025 |
