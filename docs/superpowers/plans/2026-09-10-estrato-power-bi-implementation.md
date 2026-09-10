# Estrato for Power BI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add a reproducible public Gold-to-Power-BI consumption layer to Estrato, with an export contract, Desktop template instructions, responsible semantic model and validation evidence.

**Architecture:** A Python exporter reads the already-tested Gold facts from DuckDB and writes a local, untracked CSV extract plus manifest.json. Power BI Desktop consumes that folder through pasta_dados, creates two independent facts and conformed dimensions, and presents coverage and interpretation warnings.

**Tech Stack:** Python 3, DuckDB, Polars, pytest, dbt-duckdb, Power BI Desktop, Power Query (M), DAX, Markdown.

**Spec:** docs/superpowers/specs/2026-09-10-estrato-power-bi-design.md

## Global Constraints

- Use only public ANM RAL data and project-owned rules. Never include company data, identities, internal rules, credentials, local paths, tenant IDs or internal screens.
- Read only the existing Gold facts; do not rebuild Python/dbt rules in Power Query.
- Do not connect the facts directly or use bidirectional relationships. Comparison is through conformed dimensions and shows coverage.
- Preserve beneficiada mixed units. Never sum incompatible quantities or call a difference value added, processing gain or causal effect.
- Version the exporter and documentation, not a complete extract. Generated extracts stay ignored.
- Use these public entity names: Fato_Producao_Bruta, Fato_Producao_Beneficiada, Dim_Data, Dim_Substancia, Dim_Localidade, Dim_Unidade, Dim_Cobertura and parameter pasta_dados.
- Add .pbit, PNG screenshots and rendered model PNG only after real Power BI Desktop validation. Never fabricate binaries or images.

---

## File Structure

| File | Responsibility |
|---|---|
| etl/powerbi_export.py | Query Gold facts, normalize public keys, write local CSV contract and manifest. |
| etl/config.py | Provide default ignored extract directory. |
| etl/pipeline.py | Invoke export after successful dbt build. |
| tests/test_powerbi_export.py | Test schema, keys, coverage, reconciliation and failure paths. |
| .gitignore | Exclude generated Power BI extract. |
| powerbi/README.md | Public run, Desktop, refresh and validation guide. |
| powerbi/data/README.md | Data contract and privacy boundary. |
| powerbi/docs/ | DAX, limits, validation route and source model diagram. |
| powerbi/Estrato.pbit, powerbi/screenshots/*.png | Real Desktop evidence only. |

### Task 1: Build the reproducible Gold export contract

**Files:**
- Create: etl/powerbi_export.py
- Modify: etl/config.py
- Modify: .gitignore
- Test: tests/test_powerbi_export.py

**Interfaces:**
- Consumes: source_path: Path, output_dir: Path, and Gold tables fct_producao_bruta / fct_producao_beneficiada.
- Produces: export_powerbi(source_path: Path = DUCKDB_PATH, output_dir: Path = POWERBI_EXPORT_DIR) -> Path; writes manifest.json plus seven CSV entities.
- Error: PowerBIExportError(RuntimeError) for unavailable warehouse or Gold facts, directing the user to run python -m etl.pipeline.

- [ ] **Step 1: Write failing contract tests**

Create a temporary DuckDB fixture with two rows per Gold fact and write:

~~~python
def test_export_writes_contract_and_reconciles_gold(tmp_path, gold_db):
    from etl.powerbi_export import export_powerbi

    extract = export_powerbi(source_path=gold_db, output_dir=tmp_path / "extract")

    assert {path.name for path in extract.iterdir()} == {
        "manifest.json", "Fato_Producao_Bruta.csv", "Fato_Producao_Beneficiada.csv",
        "Dim_Data.csv", "Dim_Substancia.csv", "Dim_Localidade.csv",
        "Dim_Unidade.csv", "Dim_Cobertura.csv",
    }
    manifest = json.loads((extract / "manifest.json").read_text())
    assert manifest["facts"]["Fato_Producao_Bruta"]["rows"] == 2
    assert manifest["periodo"] == {"min_ano_base": 2020, "max_ano_base": 2021}

    bruta = pl.read_csv(extract / "Fato_Producao_Bruta.csv")
    assert bruta["chave_declaracao"].to_list() == ["BRUTA:1", "BRUTA:2"]
    assert bruta["valor_total"].sum() == pytest.approx(300.0)
~~~

Add tests for missing database error and a substance present on only one fact with presente_em_ambas=False.

- [ ] **Step 2: Run the new tests and confirm the missing module failure**

Run: .venv/bin/python -m pytest tests/test_powerbi_export.py -v

Expected: collection fails with ModuleNotFoundError: No module named etl.powerbi_export.

- [ ] **Step 3: Define the output path and ignore it**

Add to etl/config.py:

~~~python
POWERBI_DIR = PROJECT_ROOT / "powerbi"
POWERBI_EXPORT_DIR = POWERBI_DIR / "data" / "extract"
~~~

Add to .gitignore:

~~~gitignore
# local Gold export consumed by the Power BI template
powerbi/data/extract/
~~~

- [ ] **Step 4: Implement the exporter**

Implement these focused functions:

~~~python
class PowerBIExportError(RuntimeError):
    pass

def normalize_key(value: object) -> str: ...
def read_gold_fact(con: duckdb.DuckDBPyConnection, table_name: str, origin: str) -> pl.DataFrame: ...
def build_dimensions(bruta: pl.DataFrame, beneficiada: pl.DataFrame) -> dict[str, pl.DataFrame]: ...
def build_coverage(bruta: pl.DataFrame, beneficiada: pl.DataFrame) -> pl.DataFrame: ...
def export_powerbi(source_path: Path = DUCKDB_PATH, output_dir: Path = POWERBI_EXPORT_DIR) -> Path: ...
~~~

read_gold_fact selects _row_id, ano_base, uf, regiao, classe_substancia, substancia_mineral, available quantity/unit pairs, valor_venda, valor_transformacao, valor_transferencia and valor_total. It adds origem, chave_declaracao=<ORIGEM>:<row_id>, chave_substancia and chave_localidade.

normalize_key applies trim, Unicode NFD accent removal and uppercase. Null dimension keys become NAO_INFORMADO; display labels remain readable. Build:
- Dim_Data: one row per year with data_inicio and data_fim.
- Dim_Substancia: distinct substance/class key and display fields.
- Dim_Localidade: UF/region.
- Dim_Unidade: every non-null declared unit.
- Dim_Cobertura: year + substance + locality, record counts per fact, presente_em_ambas, and comparavel_minimo_registros true only when both counts are at least five.

Write UTF-8 CSVs. Write version-1 manifest with gerado_em_utc, global period and each fact's row count plus valor_total_declarado.

- [ ] **Step 5: Run focused tests**

Run: .venv/bin/python -m pytest tests/test_powerbi_export.py -v

Expected: all contract, coverage and reconciliation tests pass.

- [ ] **Step 6: Commit**

~~~bash
git add etl/powerbi_export.py etl/config.py .gitignore tests/test_powerbi_export.py
git commit -m "feat: export Gold data for Power BI"
~~~

### Task 2: Integrate the export after dbt and verify the real snapshot

**Files:**
- Modify: etl/pipeline.py
- Modify: tests/test_etl.py
- Test: tests/test_powerbi_export.py

**Interfaces:**
- Consumes: powerbi_export.export_powerbi() from Task 1 after run_dbt_build().
- Produces: the full pipeline logs a Power BI export timed stage and reports the local extract.

- [ ] **Step 1: Write the failing orchestration test**

~~~python
def test_pipeline_exports_powerbi_after_successful_dbt(monkeypatch):
    from etl import pipeline

    calls = []
    monkeypatch.setattr(pipeline.bronze, "run_bronze", lambda spec: calls.append(spec.key))
    monkeypatch.setattr(pipeline, "run_dbt_build", lambda: calls.append("dbt"))
    monkeypatch.setattr(pipeline.build_dashboard, "build_dashboard", lambda: calls.append("dashboard"))
    monkeypatch.setattr(pipeline.powerbi_export, "export_powerbi", lambda: calls.append("powerbi"))

    pipeline.main()
    assert calls == ["producao_bruta", "producao_beneficiada", "dbt", "dashboard", "powerbi"]
~~~

- [ ] **Step 2: Run it and observe failure**

Run: .venv/bin/python -m pytest tests/test_etl.py::test_pipeline_exports_powerbi_after_successful_dbt -v

Expected: FAIL because etl.pipeline has no powerbi_export.

- [ ] **Step 3: Add the final pipeline stage**

Import powerbi_export beside bronze. After dashboard build, add:

~~~python
with timed("Power BI export"):
    extract = powerbi_export.export_powerbi()

logger.info("Pipeline complete -> dashboard: %s | Power BI extract: %s", out, extract)
~~~

The export must not run when dbt fails.

- [ ] **Step 4: Verify unit orchestration and the real Gold output**

~~~bash
.venv/bin/python -m pytest tests/test_etl.py::test_pipeline_exports_powerbi_after_successful_dbt tests/test_powerbi_export.py -v
.venv/bin/python -m etl.pipeline
.venv/bin/python -c "import json; from pathlib import Path; print(json.dumps(json.loads((Path('powerbi/data/extract') / 'manifest.json').read_text()), indent=2))"
~~~

Expected: unit tests pass; pipeline completes; manifest reports actual rows and 2010–2025 for current source. If dbt is unavailable, report that blocker and do not invent a manifest.

- [ ] **Step 5: Run full Python verification**

~~~bash
.venv/bin/python -m pytest tests/ -v
git diff --check
~~~

Expected: no test failures and no whitespace errors.

- [ ] **Step 6: Commit**

~~~bash
git add etl/pipeline.py tests/test_etl.py
git commit -m "feat: generate Power BI extract with pipeline"
~~~

### Task 3: Document the semantic model, DAX and public workflow

**Files:**
- Create: powerbi/README.md
- Create: powerbi/data/README.md
- Create: powerbi/docs/dicionario-de-medidas.md
- Create: powerbi/docs/limites-da-analise.md
- Create: powerbi/docs/roteiro-de-validacao.md
- Create: powerbi/docs/modelo-de-dados.mmd
- Modify: README.md
- Test: tests/test_powerbi_export.py

**Interfaces:**
- Consumes: names and manifest from Task 1.
- Produces: another user can generate the extract, set pasta_dados, open and refresh the template, reconcile totals and understand limits without contacting the author.

- [ ] **Step 1: Write the failing README acceptance test**

~~~python
def test_powerbi_readme_has_reproducible_public_workflow():
    text = Path("powerbi/README.md").read_text(encoding="utf-8")
    for term in [
        "pasta_dados", "Estrato.pbit", "python -m etl.pipeline",
        "ANM", "Power BI Desktop",
        "não usa dados, regras, identidade visual ou ambiente da empresa",
    ]:
        assert term in text
~~~

- [ ] **Step 2: Run it and observe absence**

Run: .venv/bin/python -m pytest tests/test_powerbi_export.py::test_powerbi_readme_has_reproducible_public_workflow -v

Expected: FAIL with FileNotFoundError.

- [ ] **Step 3: Write the extract contract guide**

In powerbi/data/README.md, document all seven CSV files plus manifest, declaration grain, key columns, UTF-8, manifest fields, privacy boundary and:

~~~bash
python -m etl.pipeline
# or, after dbt build:
python -m etl.powerbi_export
~~~

State that powerbi/data/extract/ is generated, ignored and selected by pasta_dados.

- [ ] **Step 4: Write the DAX dictionary with exact base measures**

~~~DAX
Registros Bruta = COUNTROWS ( Fato_Producao_Bruta )
Valor Declarado Bruta = SUM ( Fato_Producao_Bruta[valor_total] )
Valor Declarado Bruta AA = CALCULATE ( [Valor Declarado Bruta], DATEADD ( Dim_Data[data_inicio], -1, YEAR ) )
Variação Anual Bruta = [Valor Declarado Bruta] - [Valor Declarado Bruta AA]
Variação Anual Bruta % = DIVIDE ( [Variação Anual Bruta], [Valor Declarado Bruta AA] )
Participação da Substância Bruta = DIVIDE ( [Valor Declarado Bruta], CALCULATE ( [Valor Declarado Bruta], ALLSELECTED ( Dim_Substancia ) ) )
Ranking de Substâncias Bruta = RANKX ( ALLSELECTED ( Dim_Substancia[substancia_mineral] ), [Valor Declarado Bruta], , DESC, DENSE )
Substâncias Comparáveis = CALCULATE ( DISTINCTCOUNT ( Dim_Cobertura[chave_substancia] ), Dim_Cobertura[comparavel_minimo_registros] = TRUE () )
Cobertura Comparável % = DIVIDE ( [Substâncias Comparáveis], DISTINCTCOUNT ( Dim_Cobertura[chave_substancia] ) )
Período Inicial Filtrado = MIN ( Dim_Data[ano_base] )
Período Final Filtrado = MAX ( Dim_Data[ano_base] )
Contexto do Filtro = "Período: " & [Período Inicial Filtrado] & "–" & [Período Final Filtrado] & " | Valores declarados, nominais (R$)."
~~~

Add equivalent beneficiada measures and explicitly prohibit Valor Agregado, Ganho de Processamento, Fator de Agregação or equivalent.

- [ ] **Step 5: Write limits, model and validation artefacts**

In limites-da-analise.md, state non-pairing, different coverage/grain/composition/units, nominal values and no causality. Create this Mermaid source:

~~~mermaid
erDiagram
  Dim_Data ||--o{ Fato_Producao_Bruta : filtra
  Dim_Data ||--o{ Fato_Producao_Beneficiada : filtra
  Dim_Substancia ||--o{ Fato_Producao_Bruta : filtra
  Dim_Substancia ||--o{ Fato_Producao_Beneficiada : filtra
  Dim_Localidade ||--o{ Fato_Producao_Bruta : filtra
  Dim_Localidade ||--o{ Fato_Producao_Beneficiada : filtra
  Dim_Cobertura {
    string chave_substancia
    boolean presente_em_ambas
    boolean comparavel_minimo_registros
  }
~~~

Dim_Cobertura is deliberately shown with no relationship edge: it is a
descriptive comparison table, not a filter bridge.

The validation route must cover manifest reconciliation, filter scope, ambiguous-relationship inspection, tooltips, accessibility, reading-mode screenshots and sensitive-data inspection.

- [ ] **Step 6: Write the user README and link it from root README**

Explain problem, source, extract command, opening Estrato.pbit, setting pasta_dados, explicit M types, staging-query load disabled, final entities loaded, refresh, measures/dimensions, limits and validation. Include exactly:

> Este projeto não usa dados, regras, identidade visual ou ambiente da empresa.

Add a concise Power BI link in root README.md.

- [ ] **Step 7: Verify documentation**

~~~bash
.venv/bin/python -m pytest tests/test_powerbi_export.py -v
.venv/bin/python -m pytest tests/ -v
git diff --check
~~~

Expected: all tests and whitespace check pass.

- [ ] **Step 8: Commit**

~~~bash
git add README.md powerbi tests/test_powerbi_export.py
git commit -m "docs: document Power BI consumption layer"
~~~

### Task 4: Build and validate the actual Desktop template

**Files:**
- Create manually: powerbi/Estrato.pbit
- Create manually: powerbi/screenshots/{01-escopo,02-panorama,03-extracao,04-processamento,05-comparativo,06-qualidade-linhagem}.png
- Create after render and review: powerbi/docs/modelo-de-dados.png
- Modify: powerbi/README.md

**Interfaces:**
- Consumes: Task 2 extract and manifest; Task 3 query/model/measure definitions.
- Produces: validated six-page .pbit with no embedded data and no hard-coded local path.

- [ ] **Step 1: Generate and record a fresh extract**

~~~bash
.venv/bin/python -m etl.pipeline
.venv/bin/python -c "import json; from pathlib import Path; print(json.dumps(json.loads((Path('powerbi/data/extract') / 'manifest.json').read_text()), indent=2))"
~~~

Record date, period, rows and fact totals in the validation log. Do not hand-copy data into the template.

- [ ] **Step 2: Create Power Query entities**

Create text parameter pasta_dados. Load CSV staging queries from it, set explicit types and documented keys/null display handling, disable staging load and load only final entities. Read manifest only as refresh metadata.

- [ ] **Step 3: Create the model and measures**

Create single-direction dimension-to-fact relationships. Keep Dim_Cobertura disconnected from facts. Add Task 3 measures and reconcile totals to the manifest in a table visual. Confirm neither fact relates to the other.

- [ ] **Step 4: Build the six pages**

Create: Leia antes / escopo; Panorama; Produção bruta; Produção beneficiada; Comparativo responsável; Qualidade e linhagem. Keep fact pages visually parallel. Put non-causal warning and coverage beside comparison values.

- [ ] **Step 5: Validate in reading mode and capture evidence**

Check filters, coverage response, absence of ambiguous paths, titles/tooltips, contrast, alt text and keyboard order. Review full-screen screenshots for paths, credentials, tenants and company material before saving them.

- [ ] **Step 6: Export and clean-open the PBIT**

Export powerbi/Estrato.pbit; close Desktop, re-open it, set pasta_dados, refresh and re-reconcile against manifest. Confirm no data or absolute path is embedded.

- [ ] **Step 7: Commit only genuine Desktop artefacts**

~~~bash
git status --short
git diff --check
git add powerbi
git commit -m "feat: add Power BI report template"
~~~

If Desktop is unavailable, stop after Task 3 and report that Task 4 needs a Windows Power BI Desktop session; do not create fake files.

### Task 5: Verify repository outcome and update portfolio only with evidence

**Files:**
- Modify only after Task 4: files in /home/sung/Programacao/Portfolio-Caio-Leao/
- Test: tests/, scripts/check_dashboard.py, Desktop validation route

**Interfaces:**
- Consumes: validated PBIT, screenshots and manifest reconciliation.
- Produces: factual portfolio evidence about public ANM consumption modelling.

- [ ] **Step 1: Run final local verification**

~~~bash
.venv/bin/python -m pytest tests/ -v
.venv/bin/python scripts/check_dashboard.py
git diff --check
git status --short
~~~

Expected: all available automated checks pass. If Chromium is unavailable, report the exact blocker.

- [ ] **Step 2: Audit acceptance criteria against actual evidence**

Re-read spec and mark evidence for export/manifest, Gold responsibility, no fact relation, coverage, no causal measure, pages, docs, accessibility/full-screen review and sensitive-data inspection.

- [ ] **Step 3: Update portfolio only after evidence exists**

Add a restrained Estrato Power BI line naming public ANM data, Power Query, semantic model and DAX. Do not claim Service publication or enterprise use. Regenerate English, run portfolio tests and inspect PT/EN views before committing there.

- [ ] **Step 4: Report exact state**

State commits, commands and output. Distinguish local commits, verified remote publication and unperformed Desktop work. Do not push, publish to Power BI Service or change GitHub metadata without explicit authorization.

## Plan Self-Review

- **Spec coverage:** Tasks 1–2 deliver and validate Gold export; Task 3 documents contract, DAX, model, limits and validation; Task 4 covers Desktop template, pages and screenshots; Task 5 checks all criteria and keeps portfolio claims evidence-based.
- **Placeholder scan:** No unfinished markers are present. Desktop-only work is explicitly conditional on actual access and evidence.
- **Type consistency:** Task 1 defines export_powerbi(Path, Path) -> Path; Task 2 calls that exact function; later tasks use the same entity, manifest and parameter names.
