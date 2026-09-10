# Estrato for Power BI: design

## Purpose

Add a public Power BI consumption layer to Estrato Panorama Mineral Brasileiro.
It demonstrates how a versioned analytical Gold layer can be modelled,
measured and communicated in Power BI Desktop without recreating the pipeline
there or representing any company process.

The report answers: **how have declared Brazilian raw and beneficiated mineral
production evolved, where is it concentrated, and which slices are genuinely
comparable?**

Only public ANM RAL data and project-owned analytical rules may be used. The
deliverable must not include corporate data, internal rules, company identity,
credentials, local paths, tenant identifiers or internal screenshots.

## Scope and boundaries

This is an extension of this repository, not a separate project or a Power BI
Service deployment. The first release includes a Power BI template (`.pbit`),
screenshots captured from Power BI Desktop, a reproducible public extract and
documentation. It does not include Power BI Service, an automated Desktop
pipeline, a custom theme or what-if parameters.

Estrato remains responsible for collection, Brazilian-decimal parsing,
transformation, tests, Gold facts and lineage. Power BI is responsible for
reading the exported Gold contract, semantic modelling, DAX, visualisation and
interpretation. No transformation rule already owned by Python or dbt will be
duplicated in Power Query.

## Architecture

```text
Public ANM RAL CSVs
        |
        v
Estrato: Bronze -> dbt staging -> tested Gold facts (DuckDB)
        |
        v
Versioned public export contract (CSV files + manifest)
        |
        v
Power Query parameter pasta_dados
        |
        v
Conformed dimensions + two independent facts + DAX
        |
        v
Power BI Desktop report and Estrato.pbit
```

The exporter will query the Gold facts created by `dbt build` from
`data/warehouse/bateia.duckdb`. It writes an untracked local extract under a
user-selected folder. The repository versions the exporter, contract and
instructions, rather than a second full data copy. A manifest records the
extract generation timestamp, source period, row counts and the source facts
used. This makes totals reproducible while avoiding a redundant snapshot.

## Export contract

The local extract contains a manifest plus one final file per entity:

```text
<pasta_dados>/
  manifest.json
  Fato_Producao_Bruta.csv
  Fato_Producao_Beneficiada.csv
  Dim_Data.csv
  Dim_Substancia.csv
  Dim_Localidade.csv
  Dim_Unidade.csv
  Dim_Cobertura.csv
```

Each fact retains declaration grain: one ANM declaration, identified with
`origem`, `_row_id` and a stable `chave_declaracao` scoped by its origin. Both
facts export `ano_base`, normalized `uf`, `regiao`, normalized
`substancia_mineral`, normalized `classe_substancia`, declared monetary fields
and `valor_total`. They also retain original numeric fields and their units.

`Fato_Producao_Bruta` exports the tonnage-specific columns already normalized
by the Gold fact, including `qtd_producao_rom_t`. `Fato_Producao_Beneficiada`
does **not** force mixed units into tonnes; each reported quantity retains its
corresponding unit. `Dim_Unidade` is used only where a quantity is being read
within a single declared unit. Monetary measures are the default cross-base
measure and are labelled as nominal declared values in BRL.

The dimension exports are derived from the same facts. Their business keys are
trimmed, upper-cased and accent-insensitive where appropriate, but their
display labels remain readable. Nulls are exported explicitly as blank keys or
`Não informado`, with the chosen treatment recorded in the data dictionary.

`Dim_Cobertura` is a bridge-free descriptive dimension at the comparable
substance/year/locality grain. It flags whether a slice is present on both
sides and whether it meets the documented minimum-record rule. It is not used
to join facts to one another.

## Semantic model

The model contains these relationships, each single-direction from dimension
to fact:

- `Dim_Data[ano_base]` to both facts.
- `Dim_Substancia[chave_substancia]` to both facts.
- `Dim_Localidade[chave_localidade]` to both facts.
- `Dim_Unidade[chave_unidade]` only to the corresponding quantity-specific
  fact fields when the unit is applicable.
- `Dim_Cobertura` remains a descriptive comparison table; it has no direct
  fact-to-fact relationship and does not create a bidirectional filter path.

The facts never relate directly. A report comparison uses conformed filters,
then shows its coverage alongside values. This avoids portraying the two ANM
declarations as paired operational events.

## Power Query design

`pasta_dados` is a required text parameter pointing to the extract directory.
Readable staging queries use it to load CSV and manifest files, assign explicit
date, whole-number, decimal and text types, normalize dimension keys and make
null handling visible. Intermediate staging queries have loading disabled;
only final dimensions, final facts and the coverage table load to the model.
No query fetches ANM data, calls a local absolute path or reconstructs dbt
business logic.

## Measures and language

The template provides measures for record count; total declared value or
production within a compatible unit; previous-year value; absolute and percent
year-over-year variation; substance share; substance rank; count of comparable
substances; comparable coverage percent; filtered minimum and maximum period;
and dynamic filter-context text.

Measure names, visual titles and tooltips state unit, period and active scope.
There is intentionally no measure called value added, processing gain,
beneficiation gain or equivalent. Differences between declared values are
shown only as descriptive differences with an adjacent warning.

## Report pages

1. **Leia antes / escopo**: public source, extract period, meanings of raw and
   beneficiated production, non-conclusions, and extract refresh date.
2. **Panorama**: declared value or compatible volume, annual evolution, leading
   substances, geographic concentration, and year/substance/locality filters.
3. **Produção bruta**: trend, substance ranking, locality distribution and a
   detail table.
4. **Produção beneficiada**: the same analytical grammar and filters as the
   raw-production page.
5. **Comparativo responsável**: substances present in both sources, coverage,
   comparable-slice evolution and the explicit non-causal interpretation
   warning.
6. **Qualidade e linhagem**: record counts by source, transparent null or
   discard indicators, ANM -> Estrato -> Power BI diagram, and links to tests
   and pipeline documentation.

Every visual has a useful title, tooltip and alt text. The report is checked in
full-screen reading mode for contrast, keyboard navigation and tab order.

## Repository artefacts

```text
powerbi/
  README.md
  Estrato.pbit
  data/
    README.md
  docs/
    modelo-de-dados.png
    dicionario-de-medidas.md
    limites-da-analise.md
    roteiro-de-validacao.md
  screenshots/
    01-escopo.png
    02-panorama.png
    03-extracao.png
    04-processamento.png
    05-comparativo.png
```

The repository also adds an export command and automated tests for the export
contract. The `.pbit` and screenshots are added only after they are produced
in Power BI Desktop from the documented extract. If Desktop is unavailable in
the execution environment, the implementation stops before claiming those
artefacts exist and records the precise manual steps required.

## Validation

The automated suite verifies the export schema, stable keys, row counts,
period range, required dimensions and that exported monetary totals reconcile
with the queried Gold facts. The manual Power BI validation checks the
manifest totals against measures, expected cross-filtering, absence of
ambiguous relationships, labels and tooltips, accessibility, full-screen
screenshots and the absence of sensitive material. The README must let another
person generate the extract, set `pasta_dados`, open the template and refresh
it without contacting the author.

## Non-goals and explicit limits

Raw and beneficiated declarations are not operationally paired. They can
differ in coverage, grain, time, substance composition and units. Nominal
declared values are not inflation adjusted. A comparison is therefore useful
for scope and coverage, but cannot prove value added, causality or economic
effect from processing.
