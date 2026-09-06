# Estrato: direção de produto e design

O objetivo é um case de portfólio: tornar as habilidades de engenharia e análise
visíveis sem transformar detalhes de implementação em controles do dashboard.
A arquitetura remota com dbt e DuckDB foi preservada: Polars faz Bronze,
dbt transforma staging/marts e Python monta o dashboard a partir do warehouse.

## Direção visual

A skill UI/UX Pro Max recomendou o estilo Data-Dense Dashboard: indicadores,
filtros, tabelas e gráficos com hierarquia, contraste e foco visível. O padrão
comercial Enterprise Gateway retornado na mesma consulta não se aplica ao case
e foi descartado. A paleta verde mineral/cobre é uma adaptação autoral ao domínio.

- Marca Estrato com símbolo SVG de camadas; sem fontes ou imagens remotas.
- Tokens semânticos para superfícies, texto, séries e temas claro/escuro.
- Tipografia de sistema, números tabulares, espaçamento regular e cartões discretos.
- Navegação com URL por área e histórico do navegador, inclusive no celular.
- Alvos de 44 px, foco visível, filtros com estado pressionado, busca sem acentos.
- Gráficos com rolagem local em telas pequenas, evitando texto ilegível.
- Contexto metodológico e limite de escopo do comparativo dentro da interface.

## Correções de análise e entrega

Diferença entre valores declarados não comprova valor adicionado pelo beneficiamento.
O texto agora distingue comparação descritiva de causalidade. A razão no cartão
refere-se à substância com a maior diferença, não à maior razão de toda a base.
O crescimento YoY fica indefinido se faltar o ano anterior. Valores ausentes na
razão são exibidos como travessão. O build padrão sincroniza o HTML offline e o Pages.

## Validação reproduzível

`python -m pytest tests/ -v`, `python -m etl.pipeline` e
`python scripts/check_dashboard.py`. As capturas são geradas por
`python scripts/capture_screenshots.py`. Nenhum serviço externo é necessário
para executar o dashboard gerado.

## Integração com o repositório remoto

A cópia inicial local precedia a migração para dbt. A publicação usa o histórico
remoto como base, preserva modelos, macros, seeds, testes SQL e documentação de
linhagem. As melhorias visuais e de acessibilidade foram adaptadas a essa versão;
a transformação Python antiga não foi reintroduzida. Os testes Python adicionais
validam a fronteira de serialização do payload lido do DuckDB.
