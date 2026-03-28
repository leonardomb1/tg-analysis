#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "pandas",
#   "pyarrow",
#   "py7zr",
#   "tqdm",
# ]
# ///
"""
Download socioeconomic context datasets for thesis research.

Datasets:
  1. RAIS  - Relação Anual de Informações Sociais (MTE/Brazil)
             Salário médio por ocupação (CBO) e setor (CNAE) — estados SP e CE
             Saída: data/rais_salario_por_setor_ocupacao.parquet

  2. IBGE SIDRA — Tabela 6579
             Rendimento médio mensal domiciliar per capita por município (2022)
             Saída: data/ibge_renda_municipal.parquet

Usage:
    uv run download_socioeconomic_data.py
    uv run download_socioeconomic_data.py --skip-rais
    uv run download_socioeconomic_data.py --skip-ibge
"""

import io
import time
from datetime import datetime
from ftplib import FTP, error_perm
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import py7zr
import requests
from tqdm import tqdm


def _log(msg: str) -> None:
    """Print a timestamped log line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────
# 1.  RAIS — Relação Anual de Informações Sociais (MTE FTP)
# ─────────────────────────────────────────────────────────────────────────
# MTE distributes RAIS microdata as .7z archives via FTP (passive mode required).
# Files are organized by region/state (not per state as in prior years):
#
#   RAIS_VINC_PUB_SP.7z           ~948 MB  São Paulo only
#   RAIS_VINC_PUB_NORDESTE.7z     ~462 MB  AL,BA,CE,MA,PB,PE,PI,RN,SE
#   RAIS_VINC_PUB_MG_ES_RJ.7z    ~628 MB  MG, ES, RJ
#   RAIS_VINC_PUB_CENTRO_OESTE.7z ~279 MB  DF,GO,MS,MT
#   RAIS_VINC_PUB_NORTE.7z        ~156 MB  AC,AM,AP,PA,RO,RR,TO
#   RAIS_VINC_PUB_SUL.7z          ~599 MB  PR,RS,SC
#
# Uncompressed CSVs are much larger (~5–10× the .7z size).
# We aggregate on-the-fly in chunks to avoid running out of memory.
#
# Key columns in RAIS 2022 public files (after normalization to lowercase_underscore):
#   cbo_ocupação_2002   — CBO 2002 occupation code (6 digits)
#   cnae_2.0_subclasse  — CNAE 2.0 subclass code
#   vl_remun_média_nom  — average nominal monthly wage (decimal comma)
#   qtd_hora_contr      — contracted weekly hours
#   sigla_uf            — state abbreviation (needed to filter regional files)

RAIS_FTP_BASE = "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS"

# Map each target UF to (archive filename, uf_filter_value or None)
# uf_filter_value is the value in the sigla_uf column to keep; None = keep all rows
RAIS_STATE_TO_FILE: dict[str, tuple[str, str | None]] = {
    "SP": ("RAIS_VINC_PUB_SP.7z", None),
    "CE": ("RAIS_VINC_PUB_NORDESTE.7z", "CE"),
    "BA": ("RAIS_VINC_PUB_NORDESTE.7z", "BA"),
    "PE": ("RAIS_VINC_PUB_NORDESTE.7z", "PE"),
    "MG": ("RAIS_VINC_PUB_MG_ES_RJ.7z", "MG"),
    "RJ": ("RAIS_VINC_PUB_MG_ES_RJ.7z", "RJ"),
    "ES": ("RAIS_VINC_PUB_MG_ES_RJ.7z", "ES"),
    "RS": ("RAIS_VINC_PUB_SUL.7z", "RS"),
    "PR": ("RAIS_VINC_PUB_SUL.7z", "PR"),
    "SC": ("RAIS_VINC_PUB_SUL.7z", "SC"),
    "GO": ("RAIS_VINC_PUB_CENTRO_OESTE.7z", "GO"),
    "DF": ("RAIS_VINC_PUB_CENTRO_OESTE.7z", "DF"),
    "PA": ("RAIS_VINC_PUB_NORTE.7z", "PA"),
    "AM": ("RAIS_VINC_PUB_NORTE.7z", "AM"),
}

RAIS_STATES = ["SP", "CE"]
RAIS_YEAR = 2022

# Chunk size for reading large CSVs (rows per chunk — keeps memory manageable)
RAIS_CHUNK_SIZE = 500_000


def _download_file_ftp(ftp_url: str, dest: Path, desc: str) -> bool:
    """
    Download a file via FTP using ftplib (passive mode, Python built-in).
    Shows a live tqdm progress bar with bytes/s and ETA.
    Returns True on success.
    """
    parsed = urlparse(ftp_url)
    host = parsed.hostname or ""
    remote_path = parsed.path

    _log(f"Connecting to FTP: {host} ...")
    try:
        ftp = FTP(host, timeout=60)
        ftp.login()          # anonymous login
        ftp.set_pasv(True)   # passive mode (required for this server)

        try:
            file_size = ftp.size(remote_path)
        except Exception:
            file_size = None  # server may not support SIZE command

        size_str = f"{file_size/1e6:.0f} MB" if file_size else "? MB"
        _log(f"Starting download: {dest.name} ({size_str})")

        t0 = time.monotonic()
        downloaded = 0

        with open(dest, "wb") as f, tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=desc,
            dynamic_ncols=True,
            miniters=1,
        ) as pbar:
            def _write(data: bytes) -> None:
                nonlocal downloaded
                f.write(data)
                n = len(data)
                downloaded += n
                pbar.update(n)

            ftp.retrbinary(f"RETR {remote_path}", _write, blocksize=262144)

        elapsed = time.monotonic() - t0
        speed = downloaded / elapsed / 1e6
        _log(f"Download complete: {downloaded/1e6:.1f} MB in {elapsed:.0f}s ({speed:.1f} MB/s)")
        ftp.quit()

        if dest.stat().st_size > 10_000:
            return True
        dest.unlink(missing_ok=True)
        return False

    except error_perm as exc:
        _log(f"FTP permission error for {remote_path}: {exc}")
        dest.unlink(missing_ok=True)
        return False
    except Exception as exc:
        _log(f"FTP download failed ({desc}): {exc}")
        dest.unlink(missing_ok=True)
        return False


def _find_col(columns: list[str], *keywords: str) -> str | None:
    """Return first column name that contains all keywords (case-insensitive)."""
    for col in columns:
        if all(kw.lower() in col.lower() for kw in keywords):
            return col
    return None


def _aggregate_chunks(csv_path: Path, uf_filter: str | None, desc: str) -> pd.DataFrame | None:
    """
    Read a large RAIS CSV in chunks, optionally filter by UF, and aggregate
    sum of wages and count per CBO × CNAE2 group.
    Returns a DataFrame with columns: cbo, cnae2, uf, salario_sum, n_trabalhadores.
    """
    col_cbo: str | None = None
    col_cnae: str | None = None
    col_wage: str | None = None
    col_uf: str | None = None

    agg_frames: list[pd.DataFrame] = []
    total_rows = 0
    chunk_n = 0

    try:
        reader = pd.read_csv(
            csv_path, sep=";", encoding="latin-1", low_memory=False,
            decimal=",", chunksize=RAIS_CHUNK_SIZE,
        )
        for chunk in reader:
            chunk_n += 1
            # Normalize column names on first chunk
            chunk.columns = [c.strip().lower().replace(" ", "_") for c in chunk.columns]

            if chunk_n == 1:
                cols = list(chunk.columns)
                col_cbo  = _find_col(cols, "cbo")
                col_cnae = _find_col(cols, "cnae_2.0_subclasse") or _find_col(cols, "cnae2_subclasse") or _find_col(cols, "cnae")
                # Prefer "vl_remun_m*_nom" (média nominal) over faixa/SM columns
                col_wage = (
                    _find_col(cols, "vl_remun_m", "nom") or   # vl_remun_média_nom
                    _find_col(cols, "vl_remun", "nom") or      # vl_remun_dezembro_nom fallback
                    _find_col(cols, "vl_remun")                # last resort
                )
                col_uf   = _find_col(cols, "sigla_uf") or _find_col(cols, "_uf")
                _log(f"Columns detected — CBO: {col_cbo}, CNAE: {col_cnae}, "
                     f"wage: {col_wage}, UF: {col_uf}")
                if not col_cbo or not col_cnae:
                    _log(f"ERROR: could not find CBO/CNAE columns. Available: {cols[:20]}")
                    return None

            # Filter by UF if needed (regional file)
            if uf_filter and col_uf and col_uf in chunk.columns:
                chunk = chunk[chunk[col_uf].str.strip() == uf_filter]

            if chunk.empty:
                continue

            # Keep only the columns we need
            keep = [c for c in [col_cbo, col_cnae, col_wage, col_uf] if c]
            chunk = chunk[keep].copy()

            # Convert wage to numeric
            if col_wage and col_wage in chunk.columns:
                chunk[col_wage] = pd.to_numeric(chunk[col_wage], errors="coerce")

            # CNAE: take first 2 digits for sector-level aggregation
            chunk["cnae2"] = chunk[col_cnae].astype(str).str[:2]

            group_cols = [col_cbo, "cnae2"]
            if col_uf and col_uf in chunk.columns:
                chunk["uf"] = chunk[col_uf].str.strip()
                group_cols.append("uf")

            if col_wage and col_wage in chunk.columns:
                grp = (
                    chunk.groupby(group_cols, observed=True)
                    .agg(salario_sum=(col_wage, "sum"), n=(col_wage, "count"))
                    .reset_index()
                )
            else:
                grp = (
                    chunk.groupby(group_cols, observed=True)
                    .size()
                    .reset_index(name="n")
                )
                grp["salario_sum"] = float("nan")

            grp.rename(columns={col_cbo: "cbo"}, inplace=True)
            agg_frames.append(grp)
            total_rows += len(chunk)

            if chunk_n % 5 == 0:
                _log(f"  ... {total_rows:,} rows processed ({chunk_n} chunks)")

    except Exception as exc:
        _log(f"  {desc}: read/aggregate error — {exc}")
        return None

    if not agg_frames:
        return None

    _log(f"{desc}: {total_rows:,} vínculos processados em {chunk_n} chunks")
    combined = pd.concat(agg_frames, ignore_index=True)
    group_cols_final = ["cbo", "cnae2"] + (["uf"] if "uf" in combined.columns else [])
    result = (
        combined.groupby(group_cols_final, observed=True)
        .agg(salario_sum=("salario_sum", "sum"), n_trabalhadores=("n", "sum"))
        .reset_index()
    )
    result["salario_medio"] = result["salario_sum"] / result["n_trabalhadores"].replace(0, float("nan"))
    result.drop(columns=["salario_sum"], inplace=True)
    return result


def download_rais(year: int = RAIS_YEAR, states: list[str] = RAIS_STATES) -> None:
    """Download RAIS microdata for given states/year and save aggregated Parquet."""
    raw_dir = DATA_DIR / "rais_raw"
    raw_dir.mkdir(exist_ok=True)

    # Group states by archive so each archive is downloaded only once
    archives: dict[str, list[tuple[str, str | None]]] = {}
    for uf in states:
        if uf not in RAIS_STATE_TO_FILE:
            print(f"  UF {uf} not in RAIS_STATE_TO_FILE mapping — skipping")
            continue
        fname, uf_filter = RAIS_STATE_TO_FILE[uf]
        archives.setdefault(fname, []).append((uf, uf_filter))

    all_frames: list[pd.DataFrame] = []

    for filename, uf_list in archives.items():
        url = f"{RAIS_FTP_BASE}/{year}/{filename}"
        archive_path = raw_dir / filename
        uf_labels = ", ".join(uf for uf, _ in uf_list)

        if archive_path.exists() and archive_path.stat().st_size > 10_000:
            _log(f"{filename} already cached ({archive_path.stat().st_size/1e6:.0f} MB) — skipping download")
        else:
            size_mb = {
                "RAIS_VINC_PUB_SP.7z": 948,
                "RAIS_VINC_PUB_NORDESTE.7z": 462,
                "RAIS_VINC_PUB_MG_ES_RJ.7z": 628,
                "RAIS_VINC_PUB_SUL.7z": 599,
                "RAIS_VINC_PUB_CENTRO_OESTE.7z": 279,
                "RAIS_VINC_PUB_NORTE.7z": 156,
            }.get(filename, "?")
            _log(f"Downloading {filename} (~{size_mb} MB compressed) for UF(s): {uf_labels}")
            if not _download_file_ftp(url, archive_path, filename):
                _log(f"ERROR: {filename} download failed — skipping")
                continue

        extract_dir = raw_dir / filename.replace(".7z", "")
        extract_dir.mkdir(exist_ok=True)
        existing_csvs = list(extract_dir.glob("*.txt")) + list(extract_dir.glob("*.csv"))
        if existing_csvs and existing_csvs[0].stat().st_size > 10_000:
            _log(f"Already extracted: {existing_csvs[0].name} ({existing_csvs[0].stat().st_size/1e9:.2f} GB) — skipping")
        else:
            _log(f"Extracting {filename} ({archive_path.stat().st_size/1e6:.0f} MB) ...")
            t0 = time.monotonic()
            try:
                with py7zr.SevenZipFile(archive_path, mode="r") as z:
                    z.extractall(path=extract_dir)
            except Exception as exc:
                _log(f"ERROR: {filename} extraction failed — {exc}")
                continue
            _log(f"Extraction done in {time.monotonic()-t0:.0f}s")

        csvs = list(extract_dir.glob("*.txt")) + list(extract_dir.glob("*.csv"))
        if not csvs:
            _log(f"ERROR: no CSV/TXT found in {extract_dir}")
            continue

        csv_path = csvs[0]
        _log(f"Extracted file: {csv_path.name} ({csv_path.stat().st_size/1e9:.2f} GB)")

        for uf, uf_filter in uf_list:
            _log(f"Aggregating RAIS {uf} (UF filter={uf_filter!r}) in chunks of {RAIS_CHUNK_SIZE:,} rows ...")
            t0 = time.monotonic()
            df = _aggregate_chunks(csv_path, uf_filter, f"RAIS {uf}")
            if df is not None:
                if "uf" not in df.columns:
                    df["uf"] = uf
                all_frames.append(df)
                _log(f"RAIS {uf}: {len(df):,} grupos CBO×CNAE agregados em {time.monotonic()-t0:.0f}s")

    if not all_frames:
        _log("RAIS: no data loaded.")
        return

    rais = pd.concat(all_frames, ignore_index=True)
    out = DATA_DIR / "rais_salario_por_setor_ocupacao.parquet"
    rais.to_parquet(out, index=False, engine="pyarrow")
    n_vinculos = int(rais["n_trabalhadores"].sum())
    _log(f"RAIS saved → {out}  ({len(rais):,} grupos CBO×CNAE, {n_vinculos:,} vínculos originais)")


# ─────────────────────────────────────────────────────────────────────────
# 2.  IBGE SIDRA — Renda domiciliar per capita por município
# ─────────────────────────────────────────────────────────────────────────
# Tabela 3170 (Censo Demográfico 2010):
#   Pessoas de 10 anos ou mais de idade, com rendimento — por município
# Variável 842: Valor do rendimento nominal médio mensal (R$)
# Nível geográfico: Municípios (N6)
# Período: 2010 (Censo 2010 — dados de renda municipal mais completos disponíveis no SIDRA)
#
# Nota: os resultados do Censo 2022 com renda municipal ainda não estão publicados
# no SIDRA. O Censo 2010 continua sendo a referência padrão para rankings municipais
# de renda, usada em análises como Atlas Brasil/PNUD. A classificação relativa dos
# municípios é estável o suficiente para testar a hipótese socioeconômica.
#
# API doc: https://servicodados.ibge.gov.br/api/docs/agregados

IBGE_SIDRA_URL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/3170"
    "/periodos/2010/variaveis/842"
    "?localidades=N6[all]"
)


def download_ibge_renda() -> None:
    """Download IBGE SIDRA municipal income data (Tabela 3170) and save as Parquet."""
    _log("Requesting IBGE SIDRA tabela 3170 (Censo 2010, renda municipal) ...")
    try:
        resp = requests.get(IBGE_SIDRA_URL, timeout=120)
        resp.raise_for_status()
    except Exception as exc:
        _log(f"IBGE SIDRA error: {exc}")
        return

    data = resp.json()
    # Response structure: list of variable objects, each with resultados
    # resultados[].series[].localidade + series[].serie{period: value}
    rows = []
    for var_obj in data:
        for resultado in var_obj.get("resultados", []):
            # Keep only the "Total" classification (all dimensions = Total)
            categorias = resultado.get("classificacoes", [])
            if not all(
                list(c.get("categoria", {}).values())[0] == "Total"
                for c in categorias
                if c.get("categoria")
            ):
                continue

            for series_item in resultado.get("series", []):
                loc = series_item["localidade"]
                cod_municipio = loc["id"]
                nome_municipio = loc["nome"]
                serie = series_item["serie"]
                for periodo, valor in serie.items():
                    try:
                        renda = float(str(valor).replace(",", "."))
                    except (ValueError, TypeError):
                        renda = None
                    rows.append({
                        "cod_municipio": cod_municipio,
                        "municipio": nome_municipio,
                        "periodo": int(periodo),
                        "renda_media_mensal": renda,
                    })

    if not rows:
        _log("IBGE SIDRA: no data parsed from response.")
        return

    df = pd.DataFrame(rows)
    out = DATA_DIR / "ibge_renda_municipal.parquet"
    df.to_parquet(out, index=False, engine="pyarrow")
    _log(
        f"IBGE SIDRA saved → {out}  "
        f"({df['cod_municipio'].nunique():,} municípios, {len(df):,} rows)"
    )


# ─────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download socioeconomic datasets for thesis research."
    )
    parser.add_argument("--skip-rais", action="store_true", help="Skip RAIS download")
    parser.add_argument("--skip-ibge", action="store_true", help="Skip IBGE SIDRA download")
    parser.add_argument(
        "--rais-states",
        nargs="+",
        default=RAIS_STATES,
        metavar="UF",
        help=f"States for RAIS download (default: {' '.join(RAIS_STATES)})",
    )
    parser.add_argument(
        "--rais-year",
        type=int,
        default=RAIS_YEAR,
        help=f"Year for RAIS download (default: {RAIS_YEAR})",
    )
    args = parser.parse_args()

    _log("=" * 52)
    _log("Socioeconomic Dataset Downloader")
    _log(f"Output directory: {DATA_DIR.resolve()}")
    _log("=" * 52)

    if not args.skip_rais:
        _log(f"[1/2] RAIS {args.rais_year} — UFs: {', '.join(args.rais_states)}")
        download_rais(year=args.rais_year, states=args.rais_states)

    if not args.skip_ibge:
        _log("[2/2] IBGE SIDRA renda municipal")
        download_ibge_renda()

    _log("Done. Arquivos em ./data/:")
    for f in sorted(DATA_DIR.glob("*.parquet")):
        size_mb = f.stat().st_size / 1_048_576
        print(f"  {f.name:<60} {size_mb:>7.1f} MB")
