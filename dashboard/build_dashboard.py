"""Assembles the single-file dashboard from dbt's mart tables."""

import json
import logging
from pathlib import Path

import duckdb
import polars as pl

from etl.config import DASHBOARD_HTML, DUCKDB_PATH

logger = logging.getLogger(__name__)

DASHBOARD_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = DASHBOARD_DIR / "template.html"
APP_JS_PATH = DASHBOARD_DIR / "app.js"


def build_dataset_payload(con: duckdb.DuckDBPyConnection, table: str, uniform_unit: bool) -> dict:
    df = con.execute(f"select * from main_marts.{table}").pl()

    ufs = sorted(df["uf"].unique().drop_nulls().to_list())
    classes = sorted(df["classe_substancia"].unique().drop_nulls().to_list())
    substancias = sorted(df["substancia_mineral"].unique().drop_nulls().to_list())

    uf_idx = {u: i for i, u in enumerate(ufs)}
    cl_idx = {c: i for i, c in enumerate(classes)}
    sb_idx = {s: i for i, s in enumerate(substancias)}

    regiao_by_uf = dict(df.select(["uf", "regiao"]).unique().sort("uf").iter_rows())

    select_exprs = [
        pl.col("ano_base"),
        pl.col("uf").replace_strict(uf_idx).alias("uf_i"),
        pl.col("classe_substancia").replace_strict(cl_idx).alias("cl_i"),
        pl.col("substancia_mineral").replace_strict(sb_idx).alias("sb_i"),
    ]
    if uniform_unit:
        select_exprs += [pl.col("qtd_producao_rom_t").round(1), pl.col("qtd_venda_t").round(1)]
    select_exprs.append(pl.col("valor_venda").round(2))
    if uniform_unit:
        select_exprs.append(pl.col("qtd_transformacao_t").round(1))
    select_exprs.append(pl.col("valor_transformacao").round(2))
    if uniform_unit:
        select_exprs.append(pl.col("qtd_transferencia_t").round(1))
    select_exprs.append(pl.col("valor_transferencia").round(2))

    rows = df.select(select_exprs).rows()
    regioes_presentes = sorted(set(regiao_by_uf.values()))

    return {
        "ufs": ufs,
        "classes": classes,
        "substancias": substancias,
        "regiaoByUf": regiao_by_uf,
        "regioesSet": {r: True for r in regioes_presentes},
        "anoMin": int(df["ano_base"].min()),
        "anoMax": int(df["ano_base"].max()),
        "rows": rows,
    }


def build_cruzamento_payload(con: duckdb.DuckDBPyConnection) -> dict:
    por_sub = con.execute("select * from main_marts.cruzamento_por_substancia_comparavel").pl()
    por_ano = con.execute("select * from main_marts.cruzamento_por_ano").pl()
    resumo = con.execute("select * from main_marts.cruzamento_resumo").pl().row(0, named=True)

    return {
        "porSubstanciaComparavel": [
            {"substancia": r["substancia"], "valorAgregado": r["valor_agregado"], "fatorAgregacao": r["fator_agregacao"]}
            for r in por_sub.iter_rows(named=True)
        ],
        "porAno": [
            {"ano": r["ano"], "valorVendaBruta": r["valor_venda_bruta"], "valorVendaBeneficiada": r["valor_venda_beneficiada"]}
            for r in por_ano.iter_rows(named=True)
        ],
        "resumo": {
            "nSubstanciasAmbas": resumo["n_substancias_ambas"],
            "nSubstanciasComparaveis": resumo["n_substancias_comparaveis"],
        },
    }


def build_dashboard(out_path: Path = DASHBOARD_HTML, duckdb_path: Path = DUCKDB_PATH) -> Path:
    con = duckdb.connect(str(duckdb_path), read_only=True)
    try:
        payload = {
            "bruta": build_dataset_payload(con, "fct_producao_bruta", uniform_unit=True),
            "beneficiada": build_dataset_payload(con, "fct_producao_beneficiada", uniform_unit=False),
            "cruzamento": build_cruzamento_payload(con),
        }
    finally:
        con.close()

    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # avoid a stray "</script" in the data closing the inline <script> tag early
    data_json = data_json.replace("</script", "<\\/script")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    app_js = APP_JS_PATH.read_text(encoding="utf-8")

    html = template.replace("__DATA_JSON__", data_json).replace("__APP_JS__", app_js)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    size_kb = out_path.stat().st_size / 1024
    n_rows = len(payload["bruta"]["rows"]) + len(payload["beneficiada"]["rows"])
    logger.info("Dashboard: wrote %s (%.0f KB, %s rows embedded)", out_path, size_kb, n_rows)
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    build_dashboard()
