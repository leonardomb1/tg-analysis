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
import sys
import time
from datetime import datetime
from ftplib import FTP, error_perm
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import py7zr
import requests
from tqdm import tqdm

# ── Windows UTF-8 fix ────────────────────────────────────────────────────────
# Windows CMD/PowerShell default to cp1252; Portuguese chars would UnicodeError.
# reconfigure() is available on Python 3.7+ when stdout is a real TTY or file.
if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")

_TQDM_ASCII = sys.platform == "win32"   # use plain ASCII bar on Windows CMD


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

# IBGE state code (first 2 digits of 6-digit municipality code) → UF abbreviation
# Used to derive state when RAIS regional files lack a sigla_uf column
# Maps IBGE state code (first 2 digits of 6-digit municipality code) → UF abbreviation
IBGE_STATE_CODE_TO_UF: dict[str, str] = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE",
    "27": "AL", "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}

# Maps UF abbreviation → full state name as used in CAT (INSS) dataset
UF_TO_NOME: dict[str, str] = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

RAIS_STATES = ["SP", "CE", "BA"]
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
            ascii=_TQDM_ASCII,
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
    col_munic: str | None = None
    use_derived_uf: bool = False

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
                col_uf    = _find_col(cols, "sigla_uf") or _find_col(cols, "_uf")
                col_munic = _find_col(cols, "município") or _find_col(cols, "municipio")
                use_derived_uf = col_uf is None and col_munic is not None
                if use_derived_uf:
                    _log("  → col sigla_uf não encontrada; UF será derivada de 'Município' (código IBGE)")
                _log(f"Columns detected — CBO: {col_cbo}, CNAE: {col_cnae}, "
                     f"wage: {col_wage}, UF: {col_uf or f'derivada de {col_munic}'}")
                if not col_cbo or not col_cnae:
                    _log(f"ERROR: could not find CBO/CNAE columns. Available: {cols[:20]}")
                    return None

            # Derive UF from municipality code when sigla_uf column is absent
            if use_derived_uf and col_munic in chunk.columns:
                chunk["_uf_derived"] = (
                    chunk[col_munic].astype(str).str.zfill(6).str[:2]
                    .map(IBGE_STATE_CODE_TO_UF)
                )
                col_uf_for_filter: str | None = "_uf_derived"
            else:
                col_uf_for_filter = col_uf

            # Filter by UF if needed (regional file)
            if uf_filter and col_uf_for_filter and col_uf_for_filter in chunk.columns:
                chunk = chunk[chunk[col_uf_for_filter].fillna("") == uf_filter]

            if chunk.empty:
                continue

            # Keep only the columns we need
            keep = [c for c in [col_cbo, col_cnae, col_wage, col_uf_for_filter] if c]
            chunk = chunk[[c for c in keep if c in chunk.columns]].copy()

            # Convert wage to numeric
            if col_wage and col_wage in chunk.columns:
                chunk[col_wage] = pd.to_numeric(chunk[col_wage], errors="coerce")

            # CNAE: take first 2 digits for sector-level aggregation
            chunk["cnae2"] = chunk[col_cnae].astype(str).str[:2]

            group_cols = [col_cbo, "cnae2"]
            if col_uf_for_filter and col_uf_for_filter in chunk.columns:
                chunk["uf"] = chunk[col_uf_for_filter].fillna("").str.strip()
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
    # Normalize UF abbreviation → full state name to match CAT column "uf_munic._empregador"
    if "uf" in result.columns:
        result["uf"] = result["uf"].map(UF_TO_NOME).fillna(result["uf"])
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
# 3.  Novo CAGED — Cadastro Geral de Empregados e Desempregados (MTE)
# ─────────────────────────────────────────────────────────────────────────
# Novo CAGED (from Jan/2020): monthly hirings & firings across all formal CLT workers.
# Unlike RAIS (end-of-year stock), CAGED records salary at the moment of hire/fire.
# Advantage over RAIS: one national FTP directory, no regional splitting needed.
#
# FTP structure:
#   /pdet/microdados/NOVO CAGED/{year}/{YYYYMM}/CAGEDMOV{YYYYMM}.7z
#
# Key columns in CAGEDMOV files (semicolon-delimited, latin-1):
#   cbo2002ocupação      — 6-digit CBO occupation code (already a string)
#   subclasse            — CNAE 2.0 subclass (7 chars, e.g. "4711302") → first 2 = division
#   uf                   — IBGE state numeric code (11–53, integer)
#   salário              — monthly salary (decimal comma)
#   saldomovimentação    — +1 = hire, -1 = fire (both have salary data)
#
# We aggregate all movements (hirings + firings) per CBO × CNAE-division × UF,
# computing the average salary. This gives a national salary proxy for all 27 states.

CAGED_FTP_BASE = "/pdet/microdados/NOVO CAGED"
CAGED_YEAR = 2022
CAGED_CHUNK_SIZE = 500_000


def _download_file_ftp_caged(remote_path: str, dest: Path, desc: str) -> bool:
    """Download a single file from MTE FTP using an already-open path convention."""
    from ftplib import FTP, error_perm
    host = "ftp.mtps.gov.br"
    try:
        ftp = FTP(host, timeout=60)
        ftp.login()
        ftp.set_pasv(True)
        ftp.encoding = "latin-1"
        try:
            file_size = ftp.size(remote_path)
        except Exception:
            file_size = None
        size_str = f"{file_size/1e6:.0f} MB" if file_size else "? MB"
        _log(f"  Baixando {dest.name} ({size_str}) ...")
        downloaded = 0
        with open(dest, "wb") as f, tqdm(
            total=file_size, unit="B", unit_scale=True, unit_divisor=1024,
            desc=desc, dynamic_ncols=True, miniters=1, ascii=_TQDM_ASCII,
        ) as pbar:
            def _write(data: bytes) -> None:
                nonlocal downloaded
                f.write(data)
                downloaded += len(data)
                pbar.update(len(data))
            ftp.retrbinary(f"RETR {remote_path}", _write, blocksize=262144)
        ftp.quit()
        if dest.stat().st_size > 10_000:
            return True
        dest.unlink(missing_ok=True)
        return False
    except Exception as exc:
        _log(f"  FTP error ({desc}): {exc}")
        dest.unlink(missing_ok=True)
        return False


def download_caged(year: int = CAGED_YEAR) -> None:
    """Download Novo CAGED monthly files for the given year and save aggregated Parquet.

    Downloads all 12 monthly CAGEDMOV files, aggregates salary by CBO × CNAE-division × UF,
    and saves to data/caged_salario_por_setor_ocupacao.parquet.
    Compressed .7z files are cached in data/caged_raw/ to allow re-runs without re-downloading.
    """
    raw_dir = DATA_DIR / "caged_raw"
    raw_dir.mkdir(exist_ok=True)

    all_monthly: list[pd.DataFrame] = []

    for month in range(1, 13):
        yyyymm = f"{year}{month:02d}"
        filename = f"CAGEDMOV{yyyymm}.7z"
        remote_path = f"{CAGED_FTP_BASE}/{year}/{yyyymm}/{filename}"
        archive_path = raw_dir / filename

        # Download if not cached
        if archive_path.exists() and archive_path.stat().st_size > 10_000:
            _log(f"CAGED {yyyymm}: já em cache ({archive_path.stat().st_size/1e6:.0f} MB)")
        else:
            if not _download_file_ftp_caged(remote_path, archive_path, yyyymm):
                _log(f"CAGED {yyyymm}: download falhou — pulando")
                continue

        # Extract to temp dir, aggregate, then delete CSV to save disk
        extract_dir = raw_dir / yyyymm
        extract_dir.mkdir(exist_ok=True)
        existing = list(extract_dir.glob("*.txt")) + list(extract_dir.glob("*.csv"))

        if existing and existing[0].stat().st_size > 10_000:
            csv_path = existing[0]
            _log(f"CAGED {yyyymm}: já extraído ({csv_path.stat().st_size/1e6:.0f} MB)")
        else:
            _log(f"CAGED {yyyymm}: extraindo {archive_path.stat().st_size/1e6:.0f} MB ...")
            t0 = time.monotonic()
            try:
                with py7zr.SevenZipFile(archive_path, mode="r") as z:
                    z.extractall(path=extract_dir)
            except Exception as exc:
                _log(f"CAGED {yyyymm}: extração falhou — {exc}")
                continue
            _log(f"CAGED {yyyymm}: extraído em {time.monotonic()-t0:.0f}s")
            existing = list(extract_dir.glob("*.txt")) + list(extract_dir.glob("*.csv"))
            if not existing:
                _log(f"CAGED {yyyymm}: nenhum arquivo encontrado após extração")
                continue
            csv_path = existing[0]

        # Aggregate in chunks
        _log(f"CAGED {yyyymm}: agregando {csv_path.stat().st_size/1e6:.0f} MB em chunks ...")
        t0 = time.monotonic()
        monthly_agg = _aggregate_caged_chunks(csv_path, yyyymm)
        if monthly_agg is not None:
            all_monthly.append(monthly_agg)
            _log(f"CAGED {yyyymm}: {len(monthly_agg):,} grupos CBO×CNAE×UF em {time.monotonic()-t0:.0f}s")

        # Delete extracted CSV to save disk (keep the .7z)
        csv_path.unlink(missing_ok=True)

    if not all_monthly:
        _log("CAGED: nenhum dado carregado.")
        return

    _log("CAGED: consolidando 12 meses ...")
    combined = pd.concat(all_monthly, ignore_index=True)
    result = (
        combined.groupby(["cbo", "cnae2", "uf"], observed=True)
        .agg(salario_sum=("salario_sum", "sum"), n_trabalhadores=("n", "sum"))
        .reset_index()
    )
    result["salario_medio"] = (
        result["salario_sum"] / result["n_trabalhadores"].replace(0, float("nan"))
    )
    result.drop(columns=["salario_sum"], inplace=True)

    out = DATA_DIR / "caged_salario_por_setor_ocupacao.parquet"
    result.to_parquet(out, index=False, engine="pyarrow")
    n_mov = int(result["n_trabalhadores"].sum())
    n_ufs = result["uf"].nunique()
    _log(f"CAGED salvo → {out}  ({len(result):,} grupos CBO×CNAE×UF, {n_mov:,} movimentações, {n_ufs} UFs)")


def _normalize_col_name(s: str) -> str:
    """Normalize a column name: strip accents, lowercase, spaces→underscores."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_str.strip().lower().replace(" ", "_")


def _aggregate_caged_chunks(csv_path: Path, desc: str) -> pd.DataFrame | None:
    """Read a CAGED monthly CSV in chunks and aggregate salary by CBO × CNAE-div × UF."""
    col_cbo: str | None = None
    col_cnae: str | None = None
    col_wage: str | None = None
    col_uf: str | None = None
    agg_frames: list[pd.DataFrame] = []
    total_rows = 0
    chunk_n = 0

    try:
        reader = pd.read_csv(
            csv_path, sep=";", encoding="utf-8", low_memory=False,
            decimal=",", chunksize=CAGED_CHUNK_SIZE, dtype=str,
        )
        for chunk in reader:
            chunk_n += 1
            chunk.columns = [_normalize_col_name(c) for c in chunk.columns]

            if chunk_n == 1:
                cols = list(chunk.columns)
                col_cbo  = _find_col(cols, "cbo")
                col_cnae = _find_col(cols, "subclasse") or _find_col(cols, "cnae")
                col_wage = _find_col(cols, "salario") or _find_col(cols, "salário")
                col_uf   = _find_col(cols, "uf")
                _log(f"  Colunas — CBO: {col_cbo}, CNAE: {col_cnae}, "
                     f"salário: {col_wage}, UF: {col_uf}")
                if not col_cbo or not col_cnae or not col_wage or not col_uf:
                    _log(f"  ERRO: coluna essencial não encontrada. Disponíveis: {cols[:20]}")
                    return None

            # Map UF numeric code → full state name (to match CAT)
            chunk["uf_nome"] = (
                chunk[col_uf].astype(str).str.strip().str.zfill(2)
                .map(IBGE_STATE_CODE_TO_UF)
                .map(UF_TO_NOME)
            )

            # Keep only rows with valid UF
            chunk = chunk[chunk["uf_nome"].notna()].copy()
            if chunk.empty:
                continue

            # CBO: already 6-char string in CAGED
            chunk["cbo"] = chunk[col_cbo].astype(str).str.strip().str.zfill(6)

            # CNAE division: first 2 chars of subclasse (e.g. "4711302" → "47")
            chunk["cnae2"] = chunk[col_cnae].astype(str).str.strip().str[:2]

            # Salary: convert from string with decimal comma
            chunk["salario_val"] = pd.to_numeric(
                chunk[col_wage].astype(str).str.replace(",", ".", regex=False),
                errors="coerce"
            )

            # Filter valid salary (> 0)
            chunk = chunk[chunk["salario_val"] > 0]
            if chunk.empty:
                continue

            grp = (
                chunk.groupby(["cbo", "cnae2", "uf_nome"], observed=True)
                .agg(salario_sum=("salario_val", "sum"), n=("salario_val", "count"))
                .reset_index()
                .rename(columns={"uf_nome": "uf"})
            )
            agg_frames.append(grp)
            total_rows += len(chunk)

            if chunk_n % 5 == 0:
                _log(f"  ... {total_rows:,} linhas processadas ({chunk_n} chunks)")

    except Exception as exc:
        _log(f"  {desc}: erro na leitura — {exc}")
        return None

    if not agg_frames:
        return None

    _log(f"  {desc}: {total_rows:,} movimentações válidas em {chunk_n} chunks")
    combined = pd.concat(agg_frames, ignore_index=True)
    result = (
        combined.groupby(["cbo", "cnae2", "uf"], observed=True)
        .agg(salario_sum=("salario_sum", "sum"), n=("n", "sum"))
        .reset_index()
    )
    return result


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
    parser.add_argument("--skip-caged", action="store_true", help="Skip Novo CAGED download")
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
    parser.add_argument(
        "--caged-year",
        type=int,
        default=CAGED_YEAR,
        help=f"Year for CAGED download (default: {CAGED_YEAR})",
    )
    args = parser.parse_args()

    _log("=" * 52)
    _log("Socioeconomic Dataset Downloader")
    _log(f"Output directory: {DATA_DIR.resolve()}")
    _log("=" * 52)

    if not args.skip_rais:
        _log(f"[1/3] RAIS {args.rais_year} — UFs: {', '.join(args.rais_states)}")
        download_rais(year=args.rais_year, states=args.rais_states)

    if not args.skip_ibge:
        _log("[2/3] IBGE SIDRA renda municipal")
        download_ibge_renda()

    if not args.skip_caged:
        _log(f"[3/3] Novo CAGED {args.caged_year} — nacional (27 UFs)")
        download_caged(year=args.caged_year)

    _log("Done. Arquivos em ./data/:")
    for f in sorted(DATA_DIR.glob("*.parquet")):
        size_mb = f.stat().st_size / 1_048_576
        print(f"  {f.name:<60} {size_mb:>7.1f} MB")
