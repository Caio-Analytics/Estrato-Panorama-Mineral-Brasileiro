"""Tests for the Python side of the pipeline: Bronze (extract+load) and the
dashboard build. The transform layer (cleaning, aggregation, the Bruta x
Beneficiada cross-reference) is dbt's job now, and its own test suite —
schema tests, the singular test, `dbt build` itself — is what validates it;
see transform/. Run both suites in CI (see .github/workflows/tests.yml):

    dbt build --project-dir transform --profiles-dir transform
    pytest tests/
"""

import json

import polars as pl
import pytest

from etl import bronze
from etl.config import BENEFICIADA, BRUTA, DUCKDB_PATH, DatasetSpec

SPECS = [BRUTA, BENEFICIADA]
SPEC_IDS = [s.key for s in SPECS]


@pytest.fixture(scope="module", params=SPECS, ids=SPEC_IDS)
def spec(request):
    return request.param


@pytest.fixture(scope="module")
def bronze_df(spec, tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp(f"{spec.key}_bronze")

    class _Patched(DatasetSpec):
        @property
        def bronze_parquet(self):
            return tmp_dir / f"{self.key}.parquet"

    patched = _Patched(key=spec.key, raw_csv=spec.raw_csv, raw_columns=spec.raw_columns)
    return bronze.run_bronze(patched)


class TestBronze:
    def test_columns_present(self, spec, bronze_df):
        for c in spec.raw_columns:
            assert c in bronze_df.columns

    def test_everything_is_string_typed(self, spec, bronze_df):
        for c in spec.raw_columns:
            assert bronze_df.schema[c] == pl.Utf8

    def test_row_count_matches_source_csv(self, spec, bronze_df):
        # header line included, minus 1
        with open(spec.raw_csv, encoding="windows-1252") as f:
            n_lines = sum(1 for _ in f)
        assert bronze_df.height == n_lines - 1


class TestDashboardBuild:
    """Integration smoke test over the real dbt-built warehouse — requires
    `dbt build` to have already run (see module docstring)."""

    @pytest.fixture(scope="class")
    def payload(self):
        if not DUCKDB_PATH.exists():
            pytest.skip(f"{DUCKDB_PATH} not found — run `dbt build` first")

        import duckdb

        from dashboard.build_dashboard import build_cruzamento_payload, build_dataset_payload

        con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
        try:
            return {
                "bruta": build_dataset_payload(con, "fct_producao_bruta", uniform_unit=True),
                "beneficiada": build_dataset_payload(con, "fct_producao_beneficiada", uniform_unit=False),
                "cruzamento": build_cruzamento_payload(con),
            }
        finally:
            con.close()

    def test_both_datasets_have_rows(self, payload):
        assert len(payload["bruta"]["rows"]) > 0
        assert len(payload["beneficiada"]["rows"]) > 0

    def test_cruzamento_has_comparable_substances(self, payload):
        assert len(payload["cruzamento"]["porSubstanciaComparavel"]) > 0

    def test_full_build_produces_valid_self_contained_html(self, tmp_path):
        from dashboard.build_dashboard import build_dashboard

        if not DUCKDB_PATH.exists():
            pytest.skip(f"{DUCKDB_PATH} not found — run `dbt build` first")

        out = build_dashboard(out_path=tmp_path / "dashboard.html")
        html = out.read_text(encoding="utf-8")

        assert "<title>Bateia</title>" in html
        assert "__DATA_JSON__" not in html  # placeholder must be substituted
        assert "__APP_JS__" not in html

        start = html.index("const DATA = ") + len("const DATA = ")
        end = html.index(";\n</script>")
        data = json.loads(html[start:end])
        assert data["bruta"]["anoMin"] == 2010
        assert data["beneficiada"]["anoMin"] == 2010
