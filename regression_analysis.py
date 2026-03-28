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

Hipótese: coeficiente negativo para log(salário) → setores de menor remuneração
têm maior taxa de óbito, controlando por setor e estado.

Execução: uv run regression_analysis.py
"""

import duckdb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA_DIR = "data"
OUT_CSV = f"{DATA_DIR}/regression_results.csv"


def load_data() -> pd.DataFrame:
    con = duckdb.connect()
    df = con.execute("""
        WITH rais AS (
            SELECT
                LPAD(CAST(cbo AS VARCHAR), 6, '0') AS cbo,
                cnae2                              AS cnae2_div,
                uf,
                AVG(salario_medio)                 AS salario_medio_setor
            FROM 'data/rais_salario_por_setor_ocupacao.parquet'
            WHERE salario_medio > 0
            GROUP BY 1, 2, 3
        )
        SELECT
            SPLIT_PART(c.cbo, '-', 1)                        AS cbo,
            CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]      AS cnae2_div,
            trim(c."uf_munic._empregador")                   AS uf,
            r.salario_medio_setor,
            COUNT(*)                                         AS n_acidentes,
            SUM(CASE WHEN trim(c.indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)::DOUBLE
                / NULLIF(COUNT(*), 0)                        AS taxa_obito
        FROM 'data/cat_acidentes_trabalho.parquet' c
        JOIN rais r
            ON  SPLIT_PART(c.cbo, '-', 1)                   = r.cbo
            AND CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]  = r.cnae2_div
            AND trim(c."uf_munic._empregador")               = r.uf
        GROUP BY 1, 2, 3, 4
        HAVING COUNT(*) >= 10
    """).df()
    con.close()
    return df


def main() -> None:
    print("Carregando dados CAT × RAIS ...")
    df = load_data()
    print(f"  {len(df):,} grupos CBO×CNAE×UF com ≥10 acidentes")
    print(f"  UFs cobertas: {sorted(df['uf'].unique())}")
    print(f"  Salário médio: R${df['salario_medio_setor'].mean():,.0f} "
          f"(range R${df['salario_medio_setor'].min():,.0f}–{df['salario_medio_setor'].max():,.0f})")
    print()

    # Variável dependente: taxa de óbito (proporção 0–1)
    # Variável independente: log do salário médio setorial
    # Efeitos fixos: CNAE 2 dígitos (setor) e UF (estado)
    df = df.dropna(subset=["salario_medio_setor", "taxa_obito"])
    df = df[df["salario_medio_setor"] > 0].copy()
    df["log_salario"] = np.log(df["salario_medio_setor"])

    # Modelo 1: simples — só log(salário)
    m1 = smf.ols("taxa_obito ~ log_salario", data=df).fit()

    # Modelo 2: com efeito fixo de setor (CNAE)
    m2 = smf.ols("taxa_obito ~ log_salario + C(cnae2_div)", data=df).fit()

    # Modelo 3: com efeitos fixos de setor + estado
    m3 = smf.ols("taxa_obito ~ log_salario + C(cnae2_div) + C(uf)", data=df).fit()

    for label, model in [("M1 (sem FE)", m1), ("M2 (FE setor)", m2), ("M3 (FE setor+UF)", m3)]:
        coef = model.params.get("log_salario", float("nan"))
        pval = model.pvalues.get("log_salario", float("nan"))
        r2   = model.rsquared
        n    = int(model.nobs)
        sig  = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        print(f"{label}: coef={coef:+.6f}  p={pval:.4f}{sig}  R²={r2:.4f}  N={n:,}")

    print()
    print("=== Sumário completo — Modelo 3 (efeitos fixos setor + UF) ===")
    # Print only the non-FE coefficients for readability
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

    # Save full results
    summary_df.reset_index(names="term").to_csv(OUT_CSV, index=False)
    print(f"\nResultados completos salvos → {OUT_CSV}")

    # Interpretation
    print("\n=== Interpretação ===")
    coef3 = m3.params.get("log_salario", float("nan"))
    pval3 = m3.pvalues.get("log_salario", float("nan"))
    if pval3 < 0.05:
        direction = "negativo" if coef3 < 0 else "positivo"
        print(f"Coeficiente {direction} e estatisticamente significante (p={pval3:.4f}).")
        if coef3 < 0:
            print("→ Confirma hipótese: setores com menor remuneração têm maior taxa de óbito.")
        else:
            print("→ Contradiz hipótese: pode refletir confundimento geográfico ou setorial.")
    else:
        print(f"Coeficiente não significante (p={pval3:.4f}) ao nível 5%.")
        print("→ O proxy salarial setorial (RAIS SP+CE+BA) não prediz significativamente")
        print("  a taxa de óbito neste subconjunto. Limitações: cobertura geográfica parcial,")
        print("  proxy ecológico em vez de renda individual, e possível confundimento por setor.")


if __name__ == "__main__":
    main()
