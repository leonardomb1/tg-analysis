#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb",
#   "pandas",
#   "pyarrow",
#   "statsmodels",
#   "numpy",
# ]
# ///
"""
Regressão OLS multivariada: taxa de óbito por acidente ~ log(salário médio setorial)
com efeitos fixos de setor (CNAE 2 dígitos) e estado (UF).

Duas análises paralelas:
  - RAIS (SP+CE+BA, ~30% cobertura CAT): proxy regional mais preciso
  - CAGED nacional (27 UFs, ~75% cobertura CAT): cobertura nacional

Hipótese: coeficiente negativo para log(salário) → setores de menor remuneração
têm maior taxa de óbito, controlando por setor e estado.

Execução: uv run regression_analysis.py
"""

import duckdb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA_DIR = "data"
OUT_CSV_RAIS   = f"{DATA_DIR}/regression_results_rais.csv"
OUT_CSV_CAGED  = f"{DATA_DIR}/regression_results_caged.csv"

CAT_QUERY = """
    SELECT
        SPLIT_PART(c.cbo, '-', 1)                        AS cbo,
        CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]      AS cnae2_div,
        trim(c."uf_munic._empregador")                   AS uf,
        proxy.salario_medio_setor,
        COUNT(*)                                         AS n_acidentes,
        SUM(CASE WHEN trim(c.indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)::DOUBLE
            / NULLIF(COUNT(*), 0)                        AS taxa_obito
    FROM 'data/cat_acidentes_trabalho.parquet' c
    JOIN {alias} proxy
        ON  SPLIT_PART(c.cbo, '-', 1)                   = proxy.cbo
        AND CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]  = proxy.cnae2_div
        AND trim(c."uf_munic._empregador")               = proxy.uf
    GROUP BY 1, 2, 3, 4
    HAVING COUNT(*) >= 10
"""


def load_data_rais() -> pd.DataFrame:
    con = duckdb.connect()
    df = con.execute(f"""
        WITH rais AS (
            SELECT
                LPAD(CAST(cbo AS VARCHAR), 6, '0')     AS cbo,
                cnae2                                  AS cnae2_div,
                uf,
                AVG(salario_medio)                     AS salario_medio_setor
            FROM 'data/rais_salario_por_setor_ocupacao.parquet'
            WHERE salario_medio > 0
            GROUP BY 1, 2, 3
        )
        {CAT_QUERY.format(alias='rais')}
    """).df()
    con.close()
    return df


def load_data_caged() -> pd.DataFrame:
    con = duckdb.connect()
    df = con.execute(f"""
        WITH caged AS (
            SELECT
                cbo,
                cnae2                              AS cnae2_div,
                uf,
                AVG(salario_medio)                 AS salario_medio_setor
            FROM 'data/caged_salario_por_setor_ocupacao.parquet'
            WHERE salario_medio > 0
            GROUP BY 1, 2, 3
        )
        {CAT_QUERY.format(alias='caged')}
    """).df()
    con.close()
    return df


def run_models(df: pd.DataFrame, fonte: str, out_csv: str) -> None:
    print(f"\n{'='*60}")
    print(f"FONTE: {fonte}")
    print(f"{'='*60}")
    print(f"  {len(df):,} grupos CBO×CNAE×UF com ≥10 acidentes")
    print(f"  UFs cobertas ({df['uf'].nunique()}): {sorted(df['uf'].unique())}")
    print(f"  Salário médio: R${df['salario_medio_setor'].mean():,.0f} "
          f"(range R${df['salario_medio_setor'].min():,.0f}–{df['salario_medio_setor'].max():,.0f})")

    df = df.dropna(subset=["salario_medio_setor", "taxa_obito"])
    df = df[df["salario_medio_setor"] > 0].copy()
    df["log_salario"] = np.log(df["salario_medio_setor"])

    m1 = smf.ols("taxa_obito ~ log_salario", data=df).fit()
    m2 = smf.ols("taxa_obito ~ log_salario + C(cnae2_div)", data=df).fit()
    m3 = smf.ols("taxa_obito ~ log_salario + C(cnae2_div) + C(uf)", data=df).fit()

    print()
    for label, model in [("M1 (sem FE)", m1), ("M2 (FE setor)", m2), ("M3 (FE setor+UF)", m3)]:
        coef = model.params.get("log_salario", float("nan"))
        pval = model.pvalues.get("log_salario", float("nan"))
        r2   = model.rsquared
        n    = int(model.nobs)
        sig  = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        print(f"{label}: coef={coef:+.6f}  p={pval:.4f}{sig}  R²={r2:.4f}  N={n:,}")

    print()
    print(f"--- Sumário M3 (efeitos fixos setor + UF) — {fonte} ---")
    summary_df = pd.DataFrame({
        "coef": m3.params,
        "std_err": m3.bse,
        "t": m3.tvalues,
        "p_value": m3.pvalues,
        "ci_lower": m3.conf_int()[0],
        "ci_upper": m3.conf_int()[1],
    })
    key_rows = summary_df[~summary_df.index.str.startswith("C(")]
    print(key_rows.round(6).to_string())

    summary_df.reset_index(names="term").to_csv(out_csv, index=False)
    print(f"Resultados completos salvos → {out_csv}")

    coef3 = m3.params.get("log_salario", float("nan"))
    pval3 = m3.pvalues.get("log_salario", float("nan"))
    print("\n--- Interpretação ---")
    if pval3 < 0.05:
        direction = "negativo" if coef3 < 0 else "positivo"
        print(f"Coeficiente {direction} e estatisticamente significante (p={pval3:.4f}).")
        if coef3 < 0:
            print("→ Confirma hipótese: setores com menor remuneração têm maior taxa de óbito.")
        else:
            print("→ Contradiz hipótese: pode refletir confundimento geográfico ou setorial.")
    else:
        print(f"Coeficiente não significante (p={pval3:.4f}) ao nível 5%.")
        print("→ Proxy salarial setorial não prediz significativamente a taxa de óbito.")
        print("  Limitação esperada: proxy ecológico em vez de renda individual.")


def main() -> None:
    print("=== Análise RAIS (SP+CE+BA — proxy regional) ===")
    try:
        df_rais = load_data_rais()
        run_models(df_rais, "RAIS SP+CE+BA", OUT_CSV_RAIS)
    except Exception as e:
        print(f"RAIS indisponível: {e}")

    print("\n=== Análise CAGED (nacional — proxy nacional) ===")
    try:
        df_caged = load_data_caged()
        run_models(df_caged, "CAGED Nacional", OUT_CSV_CAGED)
    except Exception as e:
        print(f"CAGED indisponível: {e}")


if __name__ == "__main__":
    main()
