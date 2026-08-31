"""Paths and dataset specs for the Extract+Load boundary. Cleaning,
typing, and aggregation live in dbt (see transform/)."""

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RECON_DIR = DATA_DIR / "recon"
BRONZE_DIR = DATA_DIR / "bronze"

TRANSFORM_DIR = PROJECT_ROOT / "transform"
DUCKDB_PATH = DATA_DIR / "warehouse" / "bateia.duckdb"

OUTPUT_DIR = PROJECT_ROOT / "output"
DASHBOARD_HTML = OUTPUT_DIR / "dashboard.html"

DOCS_DIR = PROJECT_ROOT / "docs"
QUALITY_REPORT_MD = DOCS_DIR / "relatorio_qualidade_producao_bruta.md"

SOURCE_ENCODING = "windows-1252"
SOURCE_SEPARATOR = ","


@dataclass(frozen=True)
class DatasetSpec:
    key: str  # filename slug: "producao_bruta" — also the dbt source table name
    raw_csv: Path
    raw_columns: tuple = field(default_factory=tuple)

    @property
    def bronze_parquet(self) -> Path:
        return BRONZE_DIR / f"{self.key}.parquet"


BRUTA = DatasetSpec(
    key="producao_bruta",
    raw_csv=RAW_DIR / "Producao_Bruta.csv",
    raw_columns=(
        "Ano base", "UF", "Classe Substância", "Substância Mineral",
        "Quantidade Produção - Minério ROM (t)", "Quantidade Contido",
        "Unidade de Medida - Contido", "Indicação Contido",
        "Quantidade Venda (t)", "Valor Venda (R$)",
        "Quantidade Transformação / Consumo / Utilização (t)",
        "Valor Transformação / Consumo / Utilização nesta mina (R$)",
        "Quantidade Transferência para Transformação / Utilização / Consumo (t)",
        "Valor Transferência para Transformação / Utilização / Consumo (R$)",
    ),
)

BENEFICIADA = DatasetSpec(
    key="producao_beneficiada",
    raw_csv=RAW_DIR / "Producao_Beneficiada.csv",
    raw_columns=(
        "Ano base", "UF", "Classe Substância", "Substância Mineral",
        "Quantidade Produção", "Unidade de Medida - Produção",
        "Quantidade Contido", "Unidade de Medida - Contido", "Indicação Contido",
        "Quantidade Venda", "Unidade de Medida - Venda", "Valor Venda (R$)",
        "Quantidade Consumo/Utilização na Usina", "Unidade de Medida - Consumo/Utilização na Usina",
        "Valor Consumo / Utilização na Usina (R$)",
        "Quantidade Transferência para Transformação / Utilização / Consumo",
        "Unidade de Medida - Transferência para Transformação / Utilização / Consumo",
        "Valor Transferência para Transformação / Utilização / Consumo (R$)",
    ),
)

DATASETS = {"bruta": BRUTA, "beneficiada": BENEFICIADA}
