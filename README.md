# Lavra

Pipeline de dados e dashboard analítico sobre a mineração brasileira, a
partir de duas bases públicas e reais da ANM (Agência Nacional de
Mineração): **Produção Bruta** e **Produção Beneficiada**, ambas extraídas
do Relatório Anual de Lavra (RAL), 2010–2025.

**[→ Ver o dashboard](output/dashboard.html)** (arquivo HTML único, sem
dependências externas — abre offline, direto do disco).

![Visão geral do dashboard](docs/screenshots/bruta_dark.png)

## As bases

> **Produção Bruta** — "Dados de produção bruta e respectivas destinações
> (vendas, transferências, consumo e transformação) obtidos a partir do
> Relatório Anual de Lavra (RAL) [...] pode haver inconsistências nas
> informações disponibilizadas, por sua fonte ser dados declaratórios."

> **Produção Beneficiada** — mesma metodologia e fonte (RAL/ANM), mas para
> o produto já processado/beneficiado — o que sai da usina, não da lavra.

6.313 registros de produção bruta + 3.982 de produção beneficiada, 16 anos,
56 e 52 substâncias minerais respectivamente. As duas bases compartilham
UF, Classe e Substância como dimensões, mas **não** compartilham grão nem
unidade: Bruta reporta tudo em toneladas; Beneficiada reporta cada
quantidade na unidade real do produto (t, kg ou ct, variando linha a
linha — um diamante em quilates ao lado de bauxita em toneladas). Essa
diferença é o motivo pelo qual `Silver` e `Gold` tratam as duas bases de
forma explicitamente diferente — ver `etl/config.py` e o docstring de
`etl/silver.py`.

## O achado central: quanto o beneficiamento agrega

Cruzando as duas bases por substância (SQL via DuckDB, `etl/cross_reference.py`),
comparando valor de venda declarado bruto vs. beneficiado:

![Cruzamento Bruta x Beneficiada](docs/screenshots/beneficiamento_dark.png)

Minérios metálicos mostram multiplicadores de valor extremos ao serem
processados — **Ferro 132x, Cobre ~4.250x, Níquel ~5.590x** — enquanto
granulados não-metálicos (areia, rocha ornamental, saibro) mostram valor
agregado **negativo**: mais valor é capturado já na venda bruta do que no
que é formalmente declarado como "beneficiado" para essas substâncias. Nos
totais nacionais, o valor declarado como beneficiado é uma ordem de
grandeza acima do bruto em todo o período — R$ 88,7 bi (bruta) vs.
R$ 2,39 tri (beneficiada) em vendas acumuladas, 2010–2025.

## Arquitetura

```
data/raw/{Producao_Bruta,Producao_Beneficiada}.csv (cp1252, decimal BR)
        │
        ▼
┌───────────────┐   Polars · leitura tipada como string, zero interpretação,
│   BRONZE      │   generic sobre DatasetSpec (etl/config.py)
└───────┬───────┘
        ▼
┌───────────────┐   Polars (lazy expressions) · parsing de decimal BR,
│   SILVER      │   sentinelas → nulo, categorias, Região, flags de qualidade
└───────┬───────┘   — soma quantidade só quando a unidade é uniforme (Bruta)
        ▼
┌───────────────┐   pandas · groupby+agg, pivot_table, groupby().transform()
│   GOLD        │   para participação %, .pct_change() para YoY — por base
└───────┬───────┘
        ▼
┌───────────────┐   DuckDB (SQL) · join Bruta × Beneficiada por substância,
│  CRUZAMENTO   │   valor agregado e fator de agregação — só por R$, nunca
└───────┬───────┘   por quantidade (unidades não são comparáveis entre bases)
        ▼
┌───────────────┐   Python → HTML/CSS/JS vanilla · payload compacto embutido,
│  DASHBOARD    │   agregação e filtros 100% client-side, sem servidor
└───────────────┘
```

`python -m etl.pipeline` roda as cinco etapas de ponta a ponta em
**~200ms** para as ~10.300 linhas combinadas.

## Stack e por que cada peça está aqui

| Camada | Ferramenta | Por quê |
|---|---|---|
| Ingestão + limpeza | **Polars** (lazy expressions) | Engine Rust multi-thread — o gargalo em Bronze/Silver é parsing de string em massa, exatamente onde Polars ganha de pandas |
| Agregação analítica | **pandas** | `pivot_table`, `groupby().transform()` para participação %, `.pct_change()` para YoY — API mais direta para esse tipo de exploração |
| Cruzamento entre bases | **DuckDB (SQL)** | Lê os Parquet de Silver diretamente; um `FULL OUTER JOIN` é o jeito mais direto de comparar duas tabelas por chave |
| Dashboard | **HTML/CSS/JS vanilla** | Zero dependência de CDN — gráficos (linha, barra, coluna 100%, barra divergente) em SVG puro; filtros recalculam tudo no navegador |
| Testes | **pytest** (parametrizado sobre as duas bases) | Bronze→Silver→Gold→Cruzamento cobertos pelas mesmas asserções |
| CI | **GitHub Actions** | roda os testes + o pipeline completo a cada push |
| Screenshots | **Playwright** | `scripts/capture_screenshots.py` gera as imagens deste README a partir do dashboard real |
| Formato colunar | **Parquet** (via PyArrow) | Bronze e Silver persistidos como Parquet entre etapas |

## Qualidade de dados

A base de Produção Bruta veio acompanhada de um perfilamento automático
(`recon`). Duas das sinalizações "críticas" eram falsos positivos (uma
coluna de ano confundida com dado pessoal; oito colunas numéricas
sinalizadas como "mistura de tipos" que na verdade são decimal brasileiro
consistente) — a investigação de cada uma está documentada inline em
[`etl/silver.py`](etl/silver.py). A extração completa do que o profiler
sinalizou, para acompanhamento à parte, está em
[`docs/relatorio_qualidade_producao_bruta.md`](docs/relatorio_qualidade_producao_bruta.md)
(gerado por [`etl/quality_report.py`](etl/quality_report.py), reutilizável
para qualquer `recon_<Tabela>.json` no mesmo formato).

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m etl.pipeline   # Bronze -> Silver -> Gold -> Cruzamento -> dashboard/output/dashboard.html
```

Depois, abra `output/dashboard.html` direto no navegador — não precisa de
servidor.

```bash
python -m pytest tests/ -v                    # 29 testes, Bronze->Silver->Gold->Cruzamento
python -m etl.quality_report                  # regera o relatório de inconsistências
python scripts/capture_screenshots.py         # regera as imagens deste README (requer playwright)
```

## Estrutura

```
etl/
  config.py             DatasetSpec (Bruta + Beneficiada), UF→Região, caminhos
  bronze.py               ingestão crua, genérica sobre DatasetSpec (Polars)
  silver.py                 limpeza, tipagem, flags de qualidade (Polars)
  gold.py                    agregados analíticos por base (pandas)
  cross_reference.py           cruzamento Bruta × Beneficiada (DuckDB/SQL)
  quality_report.py              recon JSON -> relatório Markdown de inconsistências
  pipeline.py                      orquestrador + timing de cada estágio
dashboard/
  template.html          shell HTML/CSS (3 seções, tema claro/escuro)
  app.js                  filtros, agregação e os 4 chart builders (SVG)
  build_dashboard.py     monta os 3 payloads e injeta no template
scripts/
  capture_screenshots.py  screenshots do dashboard via Playwright
data/
  raw/                    CSVs originais (não modificados)
  recon/                  perfilamento automático (entrada de quality_report.py)
  bronze/ silver/ gold/  gerados por `etl.pipeline` (não versionados)
docs/
  relatorio_qualidade_producao_bruta.md   inconsistências extraídas do recon
  screenshots/                             imagens deste README
output/
  dashboard.html          entregável final
tests/
  test_etl.py             parametrizado sobre as duas bases + cruzamento
.github/workflows/
  tests.yml                CI: pytest + pipeline completo a cada push
```

## Dashboard

Três seções em uma página: **Produção Bruta** e **Produção Beneficiada**
(cada uma com filtros de ano, região, classe e busca por substância,
recalculando todos os KPIs e gráficos no navegador) e **Beneficiamento**,
o resumo executivo do cruzamento entre as duas. Todo gráfico tem tooltip ao
passar o mouse; tema claro/escuro segue a preferência do sistema por
padrão, com alternância manual persistida localmente.

## Screenshots

| | |
|---|---|
| ![Produção Bruta](docs/screenshots/bruta_dark.png) | ![Produção Beneficiada](docs/screenshots/beneficiada_dark.png) |
| ![Beneficiamento](docs/screenshots/beneficiamento_dark.png) | ![Tema claro](docs/screenshots/bruta_light.png) |
