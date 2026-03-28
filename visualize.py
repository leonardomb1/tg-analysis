#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb",
#   "pandas",
#   "pyarrow",
#   "matplotlib",
#   "numpy",
# ]
# ///
"""
Gera três figuras para a tese:
  1. quintis_renda_municipal.png   — quintil de renda IBGE × taxa de letalidade
  2. comparacao_global_ilo.png     — scatter países G20+LatAm, Brasil em destaque
  3. evolucao_temporal_br.png      — linhas: acidentes fatais BR por setor 2000–2023

Execução: uv run visualize.py
Saída: figures/
"""

from pathlib import Path

import duckdb
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

con = duckdb.connect()


# ─────────────────────────────────────────────────────────────────────────────
# Figura 1 — Quintis de renda municipal (IBGE) × taxa de letalidade
# ─────────────────────────────────────────────────────────────────────────────

def fig_quintis_ibge() -> None:
    df = con.execute("""
        WITH ibge AS (
            SELECT LEFT(cod_municipio, 6) AS cod_munic_6, renda_media_mensal
            FROM 'data/ibge_renda_municipal.parquet'
            WHERE renda_media_mensal IS NOT NULL AND renda_media_mensal > 0
        ),
        cat_com_renda AS (
            SELECT LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6) AS cod_munic_6,
                   trim(c.indica_óbito_acidente) AS obito,
                   i.renda_media_mensal
            FROM 'data/cat_acidentes_trabalho.parquet' c
            JOIN ibge i ON LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6) = i.cod_munic_6
            WHERE c.munic_empr NOT LIKE '000000%'
        ),
        quintis AS (
            SELECT *, NTILE(5) OVER (ORDER BY renda_media_mensal) AS quintil_renda
            FROM cat_com_renda
        )
        SELECT quintil_renda,
               MIN(renda_media_mensal) AS renda_min,
               MAX(renda_media_mensal) AS renda_max,
               COUNT(*) AS total_acidentes,
               SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END) AS obitos,
               ROUND(100.0 * SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END)
                   / NULLIF(COUNT(*), 0), 3) AS taxa_letalidade_pct
        FROM quintis GROUP BY 1 ORDER BY 1
    """).df()

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#d32f2f", "#e57373", "#ffb74d", "#81c784", "#388e3c"]
    bars = ax.bar(df["quintil_renda"], df["taxa_letalidade_pct"], color=colors, width=0.65, zorder=2)

    # Annotate bars with rate value
    for bar, val in zip(bars, df["taxa_letalidade_pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # X-tick labels with salary range
    labels = [
        f"Q{row['quintil_renda']}\n(R${row['renda_min']:,.0f}–\nR${row['renda_max']:,.0f})"
        for _, row in df.iterrows()
    ]
    ax.set_xticks(df["quintil_renda"])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_xlabel("Quintil de renda domiciliar per capita municipal (IBGE)", fontsize=11)
    ax.set_ylabel("Taxa de letalidade (%)", fontsize=11)
    ax.set_title("Renda municipal × Taxa de óbito por acidente de trabalho\n"
                 "CAT/INSS 2022–2023 — Brasil (n≈890k acidentes)", fontsize=12, fontweight="bold")
    ax.set_ylim(0, df["taxa_letalidade_pct"].max() * 1.25)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)

    ratio = df.loc[df["quintil_renda"] == 1, "taxa_letalidade_pct"].values[0] / \
            df.loc[df["quintil_renda"] == 5, "taxa_letalidade_pct"].values[0]
    ax.annotate(f"Q1/Q5 = {ratio:.1f}×",
                xy=(1, df.loc[df["quintil_renda"] == 1, "taxa_letalidade_pct"].values[0]),
                xytext=(2.5, df["taxa_letalidade_pct"].max() * 1.1),
                fontsize=10, color="#d32f2f",
                arrowprops=dict(arrowstyle="->", color="#d32f2f", lw=1.5))

    plt.tight_layout()
    out = FIGURES_DIR / "quintis_renda_municipal.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 2 — Comparação global ILO: taxa de lesão fatal
# ─────────────────────────────────────────────────────────────────────────────

def fig_comparacao_global() -> None:
    df = con.execute("""
        WITH latest AS (
            SELECT ref_area, obs_value,
                ROW_NUMBER() OVER (PARTITION BY ref_area ORDER BY time_period DESC) AS rn
            FROM 'data/ilostat_fatal_injury_rate_by_economic_activity.parquet'
            WHERE eco = 'ECO_AGGREGATE_TOTAL' AND obs_value IS NOT NULL
        )
        SELECT ref_area AS pais, ROUND(obs_value, 2) AS taxa_fatal,
               CASE
                   WHEN ref_area = 'BRA' THEN 'Brasil'
                   WHEN ref_area IN ('ARG','MEX','COL','CHL','PER','BOL','PRY','URY','ECU','VEN')
                       THEN 'América Latina'
                   WHEN ref_area IN ('USA','CAN','GBR','DEU','FRA','ITA','JPN','AUS','KOR',
                                     'IND','CHN','ZAF','SAU','TUR','IDN','RUS')
                       THEN 'G20'
                   ELSE 'Outros'
               END AS grupo
        FROM latest
        WHERE rn = 1 AND obs_value > 0
        ORDER BY taxa_fatal DESC
    """).df()

    color_map = {"Brasil": "#d32f2f", "América Latina": "#f57c00",
                 "G20": "#1976d2", "Outros": "#9e9e9e"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for grupo, grp_df in df.groupby("grupo"):
        x = range(len(grp_df))  # just for scatter positioning
        ax.scatter(grp_df["pais"], grp_df["taxa_fatal"],
                   color=color_map[grupo], label=grupo,
                   s=80, zorder=3, alpha=0.85)

    # Highlight Brazil
    br = df[df["pais"] == "BRA"]
    if not br.empty:
        ax.scatter(br["pais"], br["taxa_fatal"],
                   color="#d32f2f", s=200, zorder=5, marker="*")
        ax.annotate(f"Brasil\n{br['taxa_fatal'].values[0]:.1f}/100k",
                    xy=(br["pais"].values[0], br["taxa_fatal"].values[0]),
                    xytext=(5, br["taxa_fatal"].values[0] + 1.5),
                    fontsize=10, color="#d32f2f", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#d32f2f"))

    ax.set_xlabel("País (código ISO3)", fontsize=11)
    ax.set_ylabel("Taxa de lesão fatal (por 100k trabalhadores)", fontsize=11)
    ax.set_title("Taxa de lesão fatal no trabalho — comparação internacional\n"
                 "Fonte: ILOSTAT — ano mais recente disponível", fontsize=12, fontweight="bold")
    plt.xticks(rotation=75, fontsize=8)
    ax.legend(title="Grupo", fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    plt.tight_layout()

    out = FIGURES_DIR / "comparacao_global_ilo.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 3 — Evolução temporal: acidentes fatais no Brasil por setor
# ─────────────────────────────────────────────────────────────────────────────

def fig_evolucao_temporal() -> None:
    df = con.execute("""
        SELECT time_period AS ano, eco AS setor, obs_value AS fatais
        FROM 'data/ilostat_fatal_injuries_by_economic_activity.parquet'
        WHERE ref_area = 'BRA'
          AND eco IN ('ECO_AGGREGATE_TOTAL', 'ECO_AGGREGATE_AGR',
                      'ECO_AGGREGATE_CON', 'ECO_AGGREGATE_MAN', 'ECO_AGGREGATE_MEL')
          AND obs_value IS NOT NULL
        ORDER BY setor, ano
    """).df()

    setor_labels = {
        "ECO_AGGREGATE_TOTAL": "Total",
        "ECO_AGGREGATE_AGR":   "Agricultura",
        "ECO_AGGREGATE_CON":   "Construção",
        "ECO_AGGREGATE_MAN":   "Manufatura",
        "ECO_AGGREGATE_MEL":   "Mineração/Energia",
    }
    colors = {
        "ECO_AGGREGATE_TOTAL": "#212121",
        "ECO_AGGREGATE_AGR":   "#388e3c",
        "ECO_AGGREGATE_CON":   "#f57c00",
        "ECO_AGGREGATE_MAN":   "#1976d2",
        "ECO_AGGREGATE_MEL":   "#7b1fa2",
    }
    styles = {
        "ECO_AGGREGATE_TOTAL": "-",
        "ECO_AGGREGATE_AGR":   "--",
        "ECO_AGGREGATE_CON":   "--",
        "ECO_AGGREGATE_MAN":   "--",
        "ECO_AGGREGATE_MEL":   "--",
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    for setor, grp in df.groupby("setor"):
        label = setor_labels.get(setor, setor)
        ax.plot(grp["ano"], grp["fatais"],
                label=label,
                color=colors.get(setor, "#9e9e9e"),
                linestyle=styles.get(setor, "--"),
                linewidth=2.5 if setor == "ECO_AGGREGATE_TOTAL" else 1.8,
                marker="o", markersize=4)

    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Número de acidentes fatais", fontsize=11)
    ax.set_title("Evolução dos acidentes fatais no trabalho — Brasil, por setor\n"
                 "Fonte: ILOSTAT 2000–2023", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()

    out = FIGURES_DIR / "evolucao_temporal_br.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {out}")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Gerando figuras para a tese ...")
    fig_quintis_ibge()
    fig_comparacao_global()
    fig_evolucao_temporal()
    con.close()
    print(f"\nFiguras salvas em: {FIGURES_DIR.resolve()}/")
