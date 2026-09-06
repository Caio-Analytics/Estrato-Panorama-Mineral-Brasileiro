# Estrato: decisões de produto e design

Estrato é um case de portfólio que torna visíveis as decisões de engenharia e
análise sem transformar detalhes de implementação em controles do dashboard. A
arquitetura usa Polars na ingestão, dbt e DuckDB na transformação e Python para
montar um artefato estático a partir do warehouse.

[Abrir dashboard](https://caio-analytics.github.io/Estrato-Panorama-Mineral-Brasileiro/) ·
[Ver validação](../scripts/check_dashboard.py) ·
[Explorar screenshots](screenshots/)

## Decisões de interface

| Decisão | Problema que resolve | Evidência no produto |
|---|---|---|
| Hierarquia orientada a tarefas | Produção, processamento e comparativo respondem a perguntas distintas | Três áreas navegáveis com URL própria e histórico do navegador |
| Densidade controlada | A análise tem muitos indicadores sem exigir leitura de uma parede de dados | Indicadores, filtros, tabelas e gráficos usam hierarquia e espaçamento regulares |
| Paleta mineral e tema claro/escuro | O tema precisa apoiar leitura contínua sem competir com os dados | Tokens semânticos para superfícies, texto e séries em ambos os temas |
| Interação acessível | Filtros e gráficos não podem depender só do ponteiro | Alvos de 44 px, foco visível, estado pressionado e detalhes no foco ou ponteiro |
| Leitura em telas pequenas | Gráficos largos não devem reduzir texto até ficar ilegível | Rolagem horizontal é limitada à área do gráfico |
| Contexto metodológico no ponto de uso | Razões entre bases podem sugerir uma causalidade que os dados não sustentam | O comparativo descreve cobertura, unidades e limites de interpretação |

## Decisões de análise

O comparativo é descritivo. Diferenças entre os valores declarados nas bases não
demonstram valor adicionado pelo beneficiamento: as bases não pareiam operações,
empresas ou volumes. A razão destacada no cartão se refere à substância com a
maior diferença, não à maior razão de toda a base. O crescimento ano a ano fica
indefinido quando o ano anterior não existe, e valores ausentes de razão são
apresentados como indisponíveis.

## Validação reproduzível

O projeto valida a fronteira Python com `python -m pytest tests/ -v`, executa a
pipeline com `python -m etl.pipeline` e verifica o dashboard gerado com
`python scripts/check_dashboard.py`. As capturas são feitas por
`python scripts/capture_screenshots.py`. O dashboard final não requer serviço
externo para funcionar.

## Escopo técnico

A cópia local inicial precedia a migração para dbt. A versão atual preserva os
modelos, macros, seeds, testes SQL e documentação de linhagem do repositório
remoto. As melhorias de interface foram adaptadas a essa arquitetura; a
transformação Python anterior não foi reintroduzida. Os testes Python adicionais
cobrem a serialização do payload lido do DuckDB.
