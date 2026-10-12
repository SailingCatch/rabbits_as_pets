"""
Turn the Atlas of Living Australia (ALA) rabbit download into four small
files the charts can load quickly.

The raw download has one row per record and 192 columns (about 140 MB
unzipped). The charts only need counts, so this script writes:

    data/ala/sightings-points.csv        records per ~1 km spot, recent years
                                         columns: year, state, lat, lon, count
                                         -> chart 1 (dot map)

    data/ala/sightings-grid-by-year.csv  records per 1° square (~100 km)
                                         columns: year, lon, lat, count
                                         -> chart 3 (small-multiple maps)

    data/ala/sightings-by-month.csv      records per month
                                         columns: year, month, count
                                         -> chart 4 (heatmap)

    data/ala/sightings-by-state-year.csv records per state per year
                                         columns: year, state, count
                                         -> chart 5 (sightings per 1,000 km²)

    data/ala/source.json                 DOI, citation and download date,
                                         for the "About the data" section

Nothing is invented or altered: every record is counted where it can be.
A record with no coordinates still counts towards its state's total, and
one with no month still appears on the maps.

Usage (from the project folder):
    python3 scripts/prepare_ala.py data/raw/ala/records-2026-10-12.zip
"""

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

# ---- Settings you might change ------------------------------------------

POINT_YEARS = {2024, 2025}          # years drawn as individual dots (chart 1)
GRID_YEARS = range(2019, 2026)      # years shown as small multiples (chart 3)
COUNT_YEARS = range(2010, 2026)     # years in the heatmap and state chart (charts 4, 5)
COORD_DECIMALS = 2                  # 2 decimals ≈ 1 km, plenty for a national map

OUTPUT_DIR = Path("data/ala")

STATE_ABBREVIATIONS = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Western Australia": "WA",
    "Tasmania": "TAS",
    "Northern Territory": "NT",
    "Australian Capital Territory": "ACT",
}


# ---- Reading -------------------------------------------------------------

def read_zip(path):
    """Return (records, doi) from the ALA zip. The records file is the
    largest CSV; the zip also holds citation and heading CSVs and doi.txt."""
    archive = zipfile.ZipFile(path)
    names = archive.namelist()
    records_file = max((n for n in names if n.endswith(".csv")),
                       key=lambda n: archive.getinfo(n).file_size)
    doi = archive.read("doi.txt").decode().strip() if "doi.txt" in names else None
    raw = archive.open(records_file)
    return csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")), doi


def number(text, kind=float):
    try:
        return kind(float(text))
    except (TypeError, ValueError):
        return None


# ---- Writing ---------------------------------------------------------------

def write_csv(path, header, counts):
    rows = [(*key, n) for key, n in sorted(counts.items())]
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
    size_kb = path.stat().st_size / 1024
    print(f"  {path}  ({len(rows):,} rows, {sum(counts.values()):,} records, {size_kb:,.0f} KB)")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    zip_path = Path(sys.argv[1])
    records, doi = read_zip(zip_path)

    points, grid, months, states = Counter(), Counter(), Counter(), Counter()
    total = no_coords = no_month = 0

    for row in records:
        total += 1
        year = number(row["year"], int)
        month = number(row["month"], int)
        lat = number(row["decimalLatitude"])
        lon = number(row["decimalLongitude"])
        state = STATE_ABBREVIATIONS.get(row["stateProvince"], "")
        if year not in COUNT_YEARS:
            continue

        if state:
            states[(year, state)] += 1
        if month in range(1, 13):
            months[(year, month)] += 1
        else:
            no_month += 1
        if lat is None or lon is None:
            no_coords += 1
            continue
        if year in POINT_YEARS:
            points[(year, state, round(lat, COORD_DECIMALS), round(lon, COORD_DECIMALS))] += 1
        if year in GRID_YEARS:
            # Snap to the nearest whole degree: the centre of a 1° square
            grid[(year, float(round(lon)), float(round(lat)))] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Read {total:,} records from {zip_path.name}. Wrote:")
    write_csv(OUTPUT_DIR / "sightings-points.csv", ["year", "state", "lat", "lon", "count"], points)
    write_csv(OUTPUT_DIR / "sightings-grid-by-year.csv", ["year", "lon", "lat", "count"], grid)
    write_csv(OUTPUT_DIR / "sightings-by-month.csv", ["year", "month", "count"], months)
    write_csv(OUTPUT_DIR / "sightings-by-state-year.csv", ["year", "state", "count"], states)
    print(f"{no_coords:,} records have no coordinates (left off the maps); "
          f"{no_month:,} have no month (left out of the heatmap).")

    source = {
        "source": "Atlas of Living Australia occurrence download",
        "species": "Oryctolagus cuniculus (European rabbit)",
        "filters": "Years 2010-2025, Australia, ALA default data quality profile",
        "doi": doi,
        "downloaded": zip_path.stem.removeprefix("records-"),
        "records": total,
    }
    (OUTPUT_DIR / "source.json").write_text(json.dumps(source, indent=2) + "\n")
    print(f"  {OUTPUT_DIR / 'source.json'}")


if __name__ == "__main__":
    main()
