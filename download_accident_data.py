#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "pandas",
#   "pyarrow",
#   "simpledbf",
#   "tqdm",
# ]
# ///
"""
Download work-related accident datasets for thesis research.

Datasets:
  1. CAT   - Comunicação de Acidente de Trabalho (INSS/Brazil) — individual accident records
  2. SINAN - Acidente de Trabalho Grave (DATASUS/Brazil) — covers informal workers too
  3. ILOSTAT - ILO global fatal + non-fatal occupational injury data

All outputs are saved as Parquet files in ./data/

SINAN note: DATASUS distributes files in .dbc format (blast-compressed DBF).
  Conversion requires the `dbc2dbf` CLI tool. Install it with:
    sudo dnf install dbc2dbf          # Fedora
    sudo apt install dbc2dbf          # Debian/Ubuntu
    brew install dbc2dbf              # macOS
  If unavailable, raw .dbc files are saved to ./data/sinan_raw/ with instructions.
"""

import io  # noqa: F401 — used by ILO CSV parsing
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# 1.  CAT — Comunicação de Acidente de Trabalho
# ─────────────────────────────────────────────
# INSS publishes one ZIP per month. Each ZIP contains a semicolon-delimited CSV.
# We download all available months for a given year and concatenate them.
#
# URL patterns (INSS changed the path in mid-2023):
#   Old (≤ 2022):  .../Plano+2016_2018_Grupos+de+dados/INSS+-+Comunicação+de+Acidente+de+Trabalho+-+CAT/...
#   New (≥ 2023):  .../PDA_{YEAR}/Grupos_de_dados/Comunicações+de+Acidente+de+Trabalho+–+CAT/...

CAT_OLD_BASE = (
    "https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com"
    "/Plano+2016_2018_Grupos+de+dados"
    "/INSS+-+Comunica%C3%A7%C3%A3o+de+Acidente+de+Trabalho+-+CAT"
    "/D.SDA.PDA.005.CAT.{yyyymm}.ZIP"
)

CAT_NEW_BASE = (
    "https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com"
    "/PDA_{year}/Grupos_de_dados"
    "/Comunica%C3%A7%C3%B5es+de+Acidente+de+Trabalho+%E2%80%93+CAT"
    "/D.SDA.PDA.005.CAT.{yyyymm}.ZIP"
)


def cat_urls(year: int, month: int) -> list[str]:
    """Return candidate URLs to try in order (old pattern first, then new)."""
    yyyymm = f"{year}{month:02d}"
    return [
        CAT_OLD_BASE.format(yyyymm=yyyymm),
        CAT_NEW_BASE.format(year=year, yyyymm=yyyymm),
    ]


def download_cat(years: list[int] = [2022, 2023]) -> None:
    """Download CAT monthly files for the given years and save as Parquet."""
    all_frames: list[pd.DataFrame] = []

    for year in years:
        for month in tqdm(range(1, 13), desc=f"CAT {year}", unit="month"):
            resp = None
            for url in cat_urls(year, month):
                try:
                    resp = requests.get(url, timeout=60)
                    if resp.status_code == 200:
                        break
                    resp = None
                except Exception:
                    resp = None

            if resp is None or resp.status_code != 200:
                tqdm.write(f"  skip {year}-{month:02d} (not found on either URL)")
                continue

            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                csv_name = zf.namelist()[0]
                df = pd.read_csv(
                    zf.open(csv_name),
                    sep=";",
                    encoding="latin-1",
                    low_memory=False,
                )
            df["source_year"] = year
            df["source_month"] = month
            all_frames.append(df)

    if not all_frames:
        print("CAT: no data downloaded — check URLs or network connection.")
        return

    cat = pd.concat(all_frames, ignore_index=True)
    # Normalize column names to lowercase snake_case
    cat.columns = [c.strip().lower().replace(" ", "_") for c in cat.columns]

    out = DATA_DIR / "cat_acidentes_trabalho.parquet"
    cat.to_parquet(out, index=False, engine="pyarrow")
    print(f"CAT saved → {out}  ({len(cat):,} rows)")


# ──────────────────────────────────────────────────────────────────────
# 2.  SINAN DRT — Acidente de Trabalho Grave (DATASUS direct download)
# ──────────────────────────────────────────────────────────────────────
# DATASUS distributes SINAN files in .dbc format (blast-compressed DBF).
# We download them directly via HTTPS and convert using the `dbc2dbf` CLI.
# File naming: WGACT = Acidente de Trabalho Grave, P22 = production year 2022
#
# HTTPS mirror: https://datasus.saude.gov.br (redirects to FTP content)
# FTP base:     ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/PROD/

SINAN_FTP_BASE = "ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/PROD"

# DATASUS uses two file-prefix conventions for Acidente de Trabalho Grave.
# We try both (P=final, R=preliminary) until one downloads successfully.
SINAN_FILENAME_CANDIDATES = ["WGACTP{yy}.dbc", "ACGRP{yy}.dbc", "WGACTR{yy}.dbc", "ACGRR{yy}.dbc"]


def download_sinan(years: list[int] = [2021, 2022]) -> None:
    """Download SINAN Acidente de Trabalho Grave and save as Parquet."""
    has_dbc2dbf = shutil.which("dbc2dbf") is not None
    has_wget = shutil.which("wget") is not None

    if not has_dbc2dbf:
        print(
            "WARNING: `dbc2dbf` not found in PATH. Raw .dbc files will be saved to "
            "./data/sinan_raw/ but cannot be converted to Parquet automatically.\n"
            "Install with:  sudo dnf install dbc2dbf  (Fedora)\n"
            "               sudo apt install dbc2dbf  (Debian/Ubuntu)\n"
        )

    try:
        from simpledbf import Dbf5
    except ImportError:
        Dbf5 = None

    raw_dir = DATA_DIR / "sinan_raw"
    raw_dir.mkdir(exist_ok=True)
    all_frames: list[pd.DataFrame] = []

    for year in tqdm(years, desc="SINAN ACGR", unit="year"):
        yy = str(year)[-2:]
        raw_path = None

        # DATASUS FTP is not reachable over HTTPS — use wget which handles FTP.
        # Try multiple filename patterns until one succeeds.
        if not has_wget:
            tqdm.write(f"  wget not found — install wget and run manually for SINAN {year}")
            continue

        for pattern in SINAN_FILENAME_CANDIDATES:
            filename = pattern.format(yy=yy)
            ftp_url = f"{SINAN_FTP_BASE}/{filename}"
            candidate_path = raw_dir / filename
            try:
                result = subprocess.run(
                    ["wget", "-q", "-O", str(candidate_path), ftp_url],
                    check=True,
                    capture_output=True,
                    timeout=180,
                )
                # wget exits 0 even for FTP 550 "file not found" — check file size
                if candidate_path.exists() and candidate_path.stat().st_size > 1024:
                    raw_path = candidate_path
                    tqdm.write(f"  downloaded {filename} ({candidate_path.stat().st_size / 1024:.0f} KB)")
                    break
                else:
                    candidate_path.unlink(missing_ok=True)  # remove empty/tiny file
            except subprocess.CalledProcessError:
                candidate_path.unlink(missing_ok=True)
            except Exception as exc:
                tqdm.write(f"  SINAN {year} wget error ({filename}): {exc}")
                candidate_path.unlink(missing_ok=True)

        if raw_path is None:
            tqdm.write(
                f"  SINAN {year}: no file found on DATASUS FTP.\n"
                f"  Check available files with: wget -q -O- "
                f"'ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/PROD/' | grep -i acgr"
            )
            continue

        if not has_dbc2dbf or Dbf5 is None:
            continue

        # Convert DBC → DBF → DataFrame
        dbf_path = raw_path.with_suffix(".dbf")
        try:
            subprocess.run(
                ["dbc2dbf", str(raw_path), str(dbf_path)],
                check=True,
                capture_output=True,
            )
            df = Dbf5(str(dbf_path)).to_dataframe()
            df["source_year"] = year
            all_frames.append(df)
            tqdm.write(f"  SINAN {year}: {len(df):,} rows")
            dbf_path.unlink(missing_ok=True)
        except subprocess.CalledProcessError as exc:
            tqdm.write(f"  dbc2dbf failed for {year}: {exc.stderr.decode()[:200]}")
        except Exception as exc:
            tqdm.write(f"  SINAN {year} parse error: {exc}")

    if all_frames:
        sinan_df = pd.concat(all_frames, ignore_index=True)
        sinan_df.columns = [c.strip().lower() for c in sinan_df.columns]
        out = DATA_DIR / "sinan_acidente_trabalho_grave.parquet"
        sinan_df.to_parquet(out, index=False, engine="pyarrow")
        print(f"SINAN saved → {out}  ({len(sinan_df):,} rows)")
    elif not has_dbc2dbf:
        print(f"SINAN raw .dbc files saved to {raw_dir} — install dbc2dbf to convert them.")


# ────────────────────────────────────────────────────────────────────
# 3.  ILOSTAT — Global occupational injury data (ILO SDMX REST API)
# ────────────────────────────────────────────────────────────────────
# Indicators:
#   INJ_FATL_ECO_NB_A  — Fatal occupational injuries by economic activity
#   INJ_NFTL_ECO_NB_A  — Non-fatal occupational injuries by economic activity
#
# SDMX REST endpoint returns CSV directly.
# Using "all" for ref_area fetches every available country.
# We filter client-side if needed.

# ILO SDMX REST API — the bulk-download CDN (webapps.ilo.org) is Cloudflare-protected.
# The SDMX API at sdmx.ilo.org is accessible and returns CSV directly.
# Correct dataflow IDs do NOT include the _A (annual) suffix — frequency is a dimension.
ILO_SDMX_BASE = "https://sdmx.ilo.org/rest/data/ILO,{dataflow}?format=csv&startPeriod=2000"

ILO_INDICATORS = {
    "DF_INJ_FATL_ECO_NB": "fatal_injuries_by_economic_activity",
    "DF_INJ_NFTL_ECO_NB": "nonfatal_injuries_by_economic_activity",
    # Rates per 100,000 workers — comparable across countries regardless of workforce size
    "DF_INJ_FATL_ECO_RT": "fatal_injury_rate_by_economic_activity",
    "DF_INJ_NFTL_ECO_RT": "nonfatal_injury_rate_by_economic_activity",
    # Hours worked and wages — direct context for overwork/income hypothesis
    "DF_HOW_XEES_SEX_ECO_NB": "mean_weekly_hours_by_sex_economic_activity",
    "DF_EAR_EHRA_SEX_ECO_NB": "mean_hourly_earnings_by_sex_economic_activity",
}


def download_ilostat() -> None:
    """Download ILO occupational injury + labour context indicators via SDMX API."""
    for dataflow, label in tqdm(ILO_INDICATORS.items(), desc="ILOSTAT", unit="indicator"):
        url = ILO_SDMX_BASE.format(dataflow=dataflow)
        try:
            resp = requests.get(url, timeout=180)
            resp.raise_for_status()
        except Exception as exc:
            print(f"ILOSTAT {dataflow} error: {exc}")
            continue

        df = pd.read_csv(io.StringIO(resp.text), low_memory=False)
        df.columns = [c.strip().lower().replace(" ", "_").replace(".", "_") for c in df.columns]
        out = DATA_DIR / f"ilostat_{label}.parquet"
        df.to_parquet(out, index=False, engine="pyarrow")
        n_countries = df["ref_area"].nunique() if "ref_area" in df.columns else "?"
        print(f"ILOSTAT {dataflow} saved → {out}  ({len(df):,} rows, {n_countries} countries)")


# ────────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download work-accident datasets for thesis research."
    )
    parser.add_argument(
        "--skip-cat",
        action="store_true",
        help="Skip CAT download (large: ~12 files/year)",
    )
    parser.add_argument(
        "--skip-sinan",
        action="store_true",
        help="Skip SINAN download",
    )
    parser.add_argument(
        "--skip-ilo",
        action="store_true",
        help="Skip ILOSTAT download",
    )
    parser.add_argument(
        "--cat-years",
        nargs="+",
        type=int,
        default=[2022, 2023],
        metavar="YEAR",
        help="Years to download from CAT (default: 2022 2023)",
    )
    parser.add_argument(
        "--sinan-years",
        nargs="+",
        type=int,
        default=[2021, 2022],
        metavar="YEAR",
        help="Years to download from SINAN (default: 2021 2022)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Work Accident Dataset Downloader")
    print(f"Output directory: {DATA_DIR.resolve()}")
    print("=" * 60)

    if not args.skip_cat:
        print(f"\n[1/3] Downloading CAT (years={args.cat_years}) ...")
        download_cat(years=args.cat_years)

    if not args.skip_sinan:
        print(f"\n[2/3] Downloading SINAN DRT Acidente de Trabalho Grave (years={args.sinan_years}) ...")
        download_sinan(years=args.sinan_years)

    if not args.skip_ilo:
        print("\n[3/4] Downloading ILOSTAT indicators (injuries + hours worked + wages) ...")
        download_ilostat()

    print("\nDone. Files in ./data/:")
    for f in sorted(DATA_DIR.glob("*.parquet")):
        size_mb = f.stat().st_size / 1_048_576
        print(f"  {f.name:<60} {size_mb:>7.1f} MB")
