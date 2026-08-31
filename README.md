# Bateia

Pipeline de dados sobre a mineração brasileira: extração, transformação em
dbt, cruzamento SQL e dashboard. Nome vem do instrumento usado para separar
mineral valioso do sedimento.

**[→ Dashboard](output/dashboard.html)** (HTML único, sem dependências,
abre offline). **[→ Documentação dbt](docs/dbt/index.html)** (linhagem dos
modelos, testes, descrições de coluna, gerada automaticamente).

![Visão geral do dashboard](docs/screenshots/bruta_dark.png)

## Sobre o projeto

Dados 100% reais e públicos, publicados pela ANM (Agência Nacional de
Mineração) a partir do Relatório Anual de Lavra (RAL). Duas bases, ~10.300
registros, 2010–2025: **Produção Bruta** (o que sai da lavra) e **Produção
Beneficiada** (o que sai da usina, já processado).

**Tecnologias:** Python · Polars · dbt (dbt-duckdb) · DuckDB · PyArrow ·
pytest · GitHub Actions · Playwright · HTML/CSS/JS vanilla.

## As bases

> **Produção Bruta** — "Dados de produção bruta e respectivas destinações
> (vendas, transferências, consumo e transformação) obtidos a partir do
> Relatório Anual de Lavra (RAL) [...] pode haver inconsistências nas
> informações disponibilizadas, por sua fonte ser dados declaratórios."

> **Produção Beneficiada** — mesma fonte, para o produto já processado.

6.313 registros de produção bruta + 3.982 de produção beneficiada, 56 e 52
substâncias. As duas compartilham UF/Classe/Substância como dimensões, mas
não compartilham unidade: Bruta é sempre em toneladas; Beneficiada varia
por linha (t, kg, ct — diamante em quilates, bauxita em toneladas). Ver
[`transform/models/staging/`](transform/models/staging/).

## O achado central: quanto o beneficiamento agrega

Cruzando as duas bases por substância
([`transform/models/marts/cruzamento/`](transform/models/marts/cruzamento/)),
comparando valor de venda bruto vs. beneficiado:

![Cruzamento Bruta x Beneficiada](docs/screenshots/beneficiamento_dark.png)

Metais mostram multiplicadores extremos ao serem processados (Ferro 132x,
Cobre ~4.250x, Níquel ~5.590x); granulados não-metálicos (areia, rocha
ornamental, saibro) mostram valor agregado negativo — mais valor é
capturado já na venda bruta. Nos totais nacionais o valor beneficiado é uma
ordem de grandeza acima do bruto: R$ 88,7 bi vs. R$ 2,39 tri em vendas
acumuladas.

## Arquitetura

```
data/raw/{Producao_Bruta,Producao_Beneficiada}.csv (cp1252, decimal BR)
        │
        ▼
┌────────────────┐  Polars lê o CSV cp1252, tipa como string, grava Parquet
│  BRONZE (EL)    │  com lineage. dbt não decodifica cp1252, por isso Python.
└───────┬─────────┘
        ▼
┌────────────────┐  dbt lendo o Parquet como fonte externa — parsing de
│  STAGING        │  decimal BR via macro, sentinela → nulo
└───────┬─────────┘
        ▼
┌────────────────┐  seed uf_regiao + colunas derivadas — fct_producao_bruta
│  MARTS: core    │  / beneficiada, uma linha por declaração
└───────┬─────────┘
        ▼
┌────────────────┐  GROUP BY + window functions (LAG p/ YoY) por ano, UF,
│  MARTS: agg     │  substância, classe, mix de destinação
└───────┬─────────┘
        ▼
┌────────────────┐  FULL OUTER JOIN Bruta × Beneficiada por substância
│  MARTS: cruz.   │
└───────┬─────────┘
        ▼
┌────────────────┐  Python lê os marts do DuckDB, monta o payload,
│  DASHBOARD      │  filtros 100% client-side, sem servidor
└────────────────┘
```

`python -m etl.pipeline` roda tudo em menos de 2s (Bronze → `dbt build` →
dashboard). STAGING → MARTS é `dbt build`: 18 modelos, 57 testes de schema
+ 1 teste singular.

## Analytics Engineering com dbt

A camada de transformação é um projeto dbt em [`transform/`](transform/):

- **Sources externas** — `models/staging/_sources.yml` aponta direto para
  o Parquet do Bronze via `external_location`, sem copiar nada pro
  warehouse antes.
- **Macro compartilhado** —
  [`macros/parse_br_decimal.sql`](transform/macros/parse_br_decimal.sql)
  centraliza o parsing de decimal brasileiro usado pelos dois modelos de
  staging.
- **Seed como fonte de verdade** —
  [`seeds/uf_regiao.csv`](transform/seeds/uf_regiao.csv), testado como
  qualquer outro modelo.
- **staging → marts** — `stg_*` tipa 1:1 com a fonte; `marts/core` monta
  os fatos; `marts/bruta`, `marts/beneficiada` e `marts/cruzamento`
  agregam, cada camada via `ref()`.
- **57 testes de schema + 1 singular** — `not_null`, `unique`,
  `accepted_values`, um `relationships` validando UF contra o seed, e
  [`tests/assert_valor_agregado_matches_diferenca.sql`](transform/tests/assert_valor_agregado_matches_diferenca.sql).
- **Docs e linhagem gerados** — `dbt docs generate --static` produz
  [`docs/dbt/index.html`](docs/dbt/index.html):

![Grafo de linhagem dbt](docs/screenshots/dbt_lineage.png)

## Stack

| Camada | Ferramenta |
|---|---|
| Extração + carga | Polars (cp1252 → Parquet tipado) |
| Transformação | dbt (dbt-duckdb) |
| Execução SQL | DuckDB, embutido |
| Dashboard | HTML/CSS/JS vanilla, SVG, zero CDN |
| Testes Python | pytest (Bronze + build do dashboard) |
| CI | GitHub Actions — Bronze → `dbt build` → pytest → dashboard |
| Screenshots | Playwright (`scripts/capture_screenshots.py`) |
| Formato colunar | Parquet (PyArrow) |

## Qualidade de dados

A base de Produção Bruta veio com um perfilamento automático (`recon`).
Duas sinalizações "críticas" eram falsos positivos: uma coluna de ano
confundida com dado pessoal, e seis colunas numéricas sinalizadas como
"mistura de tipos" que na verdade são decimal brasileiro consistente (mais
uma, por "grafias divergentes", também não se sustenta — '145' e '14,5'
são números diferentes). Extração completa em
[`docs/relatorio_qualidade_producao_bruta.md`](docs/relatorio_qualidade_producao_bruta.md),
gerada por [`etl/quality_report.py`](etl/quality_report.py).

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m etl.pipeline   # Bronze -> dbt build -> output/dashboard.html
```

Depois abra `output/dashboard.html` no navegador — não precisa de servidor.

```bash
python -m pytest tests/ -v
dbt build --project-dir transform --profiles-dir transform
dbt docs generate --static --project-dir transform --profiles-dir transform
python -m etl.quality_report
python scripts/capture_screenshots.py
```

## Estrutura

```
etl/
  config.py             DatasetSpec (Bruta + Beneficiada), caminhos
  bronze.py              extração + carga: CSV cp1252 -> Parquet
  quality_report.py      recon JSON -> relatório Markdown
  pipeline.py             orquestrador
transform/               projeto dbt
  models/staging/         stg_* — tipagem, parsing decimal BR
  models/marts/core/       fct_producao_bruta / fct_producao_beneficiada
  models/marts/bruta/      (e beneficiada/) agregados
  models/marts/cruzamento/ cruzamento Bruta x Beneficiada
  macros/ seeds/ tests/
dashboard/
  template.html          shell HTML/CSS
  app.js                  filtros, agregação, chart builders (SVG)
  build_dashboard.py     lê os marts do DuckDB, injeta no template
scripts/
  capture_screenshots.py
data/
  raw/                    CSVs originais
  recon/                  perfilamento automático
  bronze/ warehouse/     gerados pela pipeline (não versionados)
docs/
  relatorio_qualidade_producao_bruta.md
  dbt/index.html          docs + linhagem dbt (gerada)
  screenshots/
output/
  dashboard.html
tests/
  test_etl.py
.github/workflows/
  tests.yml
```

## Dashboard

Três seções em uma página: **Produção Bruta** e **Produção Beneficiada**
(filtros de ano, região, classe e busca por substância) e
**Beneficiamento**, o cruzamento entre as duas. Tema claro/escuro segue o
sistema por padrão, com alternância manual persistida localmente.

## Screenshots

| | |
|---|---|
| ![Produção Bruta](docs/screenshots/bruta_dark.png) | ![Produção Beneficiada](docs/screenshots/beneficiada_dark.png) |
| ![Beneficiamento](docs/screenshots/beneficiamento_dark.png) | ![Tema claro](docs/screenshots/bruta_light.png) |
| ![Linhagem dbt](docs/screenshots/dbt_lineage.png) | |
