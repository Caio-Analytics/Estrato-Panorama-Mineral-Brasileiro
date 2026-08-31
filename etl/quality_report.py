"""Turns a recon profiler JSON into a standalone Markdown findings report.

    python -m etl.quality_report data/recon/recon_Producao_Bruta.json
"""

import json
import logging
import sys
from pathlib import Path

from etl.config import QUALITY_REPORT_MD, RECON_DIR

logger = logging.getLogger(__name__)


def build_report(recon: dict) -> str:
    meta = recon["metadados_execucao"]
    qualidade = meta["score_qualidade"]
    lgpd = meta["risco_lgpd"]
    dup = meta["duplicatas"]

    lines = []
    lines.append(f"# Relatório de inconsistências — {meta['tabela']}")
    lines.append("")
    lines.append(
        f"Gerado a partir do perfilamento automático (`recon`, versão "
        f"{meta['versao_profiler']}) rodado em {meta['timestamp_utc']}, "
        f"sobre {meta['linhas_originais']:,} linhas / {meta['total_colunas']} colunas. "
        f"Extração fiel do que o profiler sinalizou — pontos aqui **não foram "
        f"corrigidos** nesta pipeline, ficam para o próximo passo."
    )
    lines.append("")
    lines.append(
        f"**Score de qualidade:** {qualidade['score']}/100 (nota {qualidade['nota']}) · "
        f"{qualidade['colunas_comprometidas']} coluna(s) comprometida(s) · "
        f"{dup['qtd_linhas_duplicadas']} linha(s) duplicada(s)"
    )
    lines.append("")

    lines.append("## Colunas críticas")
    lines.append("")
    lines.append("| Coluna | Dano | Motivo(s) |")
    lines.append("|---|---|---|")
    for c in qualidade.get("colunas_criticas", []):
        motivos = "; ".join(c.get("motivos", []))
        lines.append(f"| {c['coluna']} | {c['dano']:.2f} | {motivos} |")
    lines.append("")

    if lgpd.get("colunas_sensiveis"):
        lines.append("## Risco LGPD")
        lines.append("")
        lines.append(f"Nível: {lgpd['nivel']} (exposição {lgpd['exposicao']})")
        lines.append("")
        lines.append("| Coluna | Tipo sinalizado |")
        lines.append("|---|---|")
        for c in lgpd["colunas_sensiveis"]:
            lines.append(f"| {c['coluna']} | {c['tipo']} |")
        lines.append("")
        lines.append(f"> {lgpd.get('recomendacao', '')}")
        lines.append("")

    lines.append("## Recomendações de ETL")
    lines.append("")
    lines.append("| Prioridade | Coluna | Camada | Ação | Linhas afetadas | % impacto |")
    lines.append("|---|---|---|---|---|---|")
    for r in recon.get("recomendacoes_etl", []):
        pct = r.get("Pct_Impacto", "—")
        lines.append(
            f"| {r['Prioridade']} | {r['Coluna']} | {r['Camada']} | {r['Acao']} | "
            f"{r['Linhas_Afetadas']:,} | {pct} |"
        )
    lines.append("")

    lines.append("## Sumário por coluna")
    lines.append("")
    lines.append("| Coluna | Tipo inferido | % nulos | Únicos | Observações |")
    lines.append("|---|---|---|---|---|")
    for col in recon.get("colunas", []):
        obs = []
        alertas = col.get("Alertas", {})
        if alertas.get("mistura_tipos", {}).get("tem_mistura"):
            obs.append("mistura de tipos")
        qualidade_col = col.get("Qualidade", {})
        if qualidade_col.get("sentinelas", {}).get("tem_sentinela"):
            obs.append("possui sentinela de nulo")
        if qualidade_col.get("inconsistencia_normalizacao", {}).get("tem_inconsistencia"):
            obs.append("inconsistência de normalização")
        obs_str = "; ".join(obs) if obs else "—"
        # Pct_Nulos in the recon schema is already 0-100, not a 0-1 fraction.
        lines.append(
            f"| {col['Coluna']} | {col['Tipo_Inferred']} | {col['Pct_Nulos']:.1f}% | "
            f"{col['Qtd_Unicos']:,} | {obs_str} |"
        )
    lines.append("")

    return "\n".join(lines)


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
