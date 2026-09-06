"""Build a reviewed Markdown report from Recon's automatic profiling output.

    python -m etl.quality_report data/recon/recon_Producao_Bruta.json
"""

import json
import logging
import sys
from pathlib import Path

from etl.config import QUALITY_REPORT_MD, RECON_DIR

logger = logging.getLogger(__name__)

NUMERIC_COLUMNS = {
    "Quantidade Produção - Minério ROM (t)",
    "Quantidade Contido",
    "Quantidade Transformação / Consumo / Utilização (t)",
    "Valor Transformação / Consumo / Utilização nesta mina (R$)",
    "Quantidade Transferência para Transformação / Utilização / Consumo (t)",
    "Valor Transferência para Transformação / Utilização / Consumo (R$)",
}


def build_report(recon: dict) -> str:
    """Render Recon findings with the domain review applied by the pipeline."""
    meta = recon["metadados_execucao"]
    qualidade = meta["score_qualidade"]
    dup = meta["duplicatas"]
    n_rows = meta["linhas_originais"]

    lines = [
        f"# Perfilamento e triagem técnica: {meta['tabela']}",
        "",
        f"Este documento parte do perfilamento automático do §recon§ "
        f"(versão {meta['versao_profiler']}), executado em {meta['timestamp_utc']} "
        f"sobre {n_rows:,} linhas e {meta['total_colunas']} colunas. "
        "Os achados foram revisados à luz do dicionário da fonte e das regras "
        "implementadas no staging; o score automático não é apresentado como "
        "diagnóstico final.",
        "",
        "## Resultado da triagem",
        "",
        "| Achado automático | Decisão técnica | Tratamento na pipeline |",
        "|---|---|---|",
        "| §Ano base§ classificado como dado pessoal | Falso positivo. O próprio perfil indica a heurística §ano§ → §aluno§; a coluna é um ano inteiro com 16 valores. | Convertido para §smallint§. |",
        "| Seis campos numéricos classificados como mistura de tipos | Falso positivo. Os valores usam decimal brasileiro e foram preservados como texto no Bronze. | §parse_br_decimal§ converte vírgula decimal para §DOUBLE§ no staging. |",
        "| §Unidade de Medida - Contido§ com §-§ como ausência | Confirmado. | §nullif(..., '-')§ converte o sentinela para nulo no staging. |",
        "| §Quantidade Venda (t)§ com grafias divergentes | Falso positivo. §145§ e §14,5§ são valores numéricos distintos, não grafias do mesmo valor. | Conversão numérica preserva a diferença entre os valores. |",
        "| §Indicação Contido§ com 71,7% de nulos | Característica da fonte a monitorar; não impede a modelagem das métricas de produção e venda. | Campo é preservado na camada de staging. |",
        "",
        "## Sinais do perfilamento automático",
        "",
        f"O profiler atribuiu score {qualidade['score']}/100 (nota {qualidade['nota']}) e "
        f"marcou {qualidade['colunas_comprometidas']} colunas. Após a triagem, esse "
        "score deve ser lido como sensível ao formato da fonte, não como uma nota "
        "da qualidade analítica do dataset. Não foram encontradas linhas duplicadas "
        f"no perfilamento ({dup['qtd_linhas_duplicadas']} de {n_rows:,}).",
        "",
        "## Colunas sinalizadas",
        "",
        "| Coluna | Sinal do profiler | Leitura revisada |",
        "|---|---|---|",
    ]

    for column in qualidade.get("colunas_criticas", []):
        name = column["coluna"]
        reason = "; ".join(column.get("motivos", []))
        if name in NUMERIC_COLUMNS:
            reviewed = "Decimal brasileiro, tratado no staging."
        elif name == "Unidade de Medida - Contido":
            reviewed = "Sentinela §-§ convertida para nulo."
        elif name == "Quantidade Venda (t)":
            reviewed = "Valores distintos; não há normalização a aplicar."
        elif name == "Indicação Contido":
            reviewed = "Nulos preservados e monitorados."
        else:
            reviewed = "Revisar com o contexto da fonte."
        lines.append(f"| {name} | {reason} | {reviewed} |")

    lines.extend([
        "",
        "## Regras implementadas",
        "",
        "- O Bronze mantém as colunas da fonte como texto, evitando perda de informação na ingestão.",
        "- O staging converte os decimais brasileiros com a macro §parse_br_decimal§.",
        "- A unidade §-§ em §Unidade de Medida - Contido§ é convertida para nulo.",
        "- §Ano base§ é convertido para §smallint§; não há dado pessoal nessa coluna.",
        "",
        "## Sumário da fonte",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Linhas analisadas | {n_rows:,} |",
        f"| Colunas | {meta['total_colunas']} |",
        f"| Linhas duplicadas | {dup['qtd_linhas_duplicadas']} |",
        "| Período disponível | 2010 a 2025 |",
        "",
    ])
    return "\n".join(lines).replace("§", chr(96))


def main(recon_path: Path = None, out_path: Path = None) -> Path:
    recon_path = recon_path or (RECON_DIR / "recon_Producao_Bruta.json")
    out_path = out_path or QUALITY_REPORT_MD

    with open(recon_path, encoding="utf-8") as f:
        recon = json.load(f)

    report = build_report(recon)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    logger.info("Quality report: wrote %s", out_path)
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(recon_path=path)
