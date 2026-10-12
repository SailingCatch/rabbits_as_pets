"""
Turn an Atlas of Living Australia (ALA) rabbit download into three small
files the charts can load quickly.

The raw ALA download has one row per sighting and dozens of columns
(tens of MB). The page only needs a few columns, and two of the charts only
need counts, so this script writes:

    data/ala/sightings-points.csv        one row per sighting, recent years only
                                         columns: lat, lon, year, month, state
                                         -> chart 1 (dot map)

    data/ala/sightings-grid-by-year.csv  sightings counted in 1° x 1° squares
                                         columns: year, lon, lat, count
                                         -> chart 3 (small-multiple maps)

    data/ala/sightings-by-month.csv      sightings counted per month
                                         columns: year, month, count
                                         -> chart 4 (heatmap)

Nothing is invented or altered: rows without coordinates or a date are
skipped, every other row is kept and only counted or trimmed.

Usage (from the project folder):
    python3 scripts/prepare_ala.py data/raw/ala-rabbit-records.csv

The input can be the CSV inside the ALA zip, or the zip itself.
"""

import csv
import io
import sys
import zipfile
from collections import Counter
from pathlib import Path

# ---- Settings you might change ------------------------------------------

POINT_YEARS = {2024, 2025}          # years drawn as individual dots (chart 1)
GRID_YEARS = range(2019, 2026)      # years shown as small multiples (chart 3)
MONTH_YEARS = range(2010, 2026)     # years in the heatmap (chart 4)
GRID_SIZE = 1.0                     # grid square size in degrees (~100 km)
COORD_DECIMALS = 2                  # 2 decimals ≈ 1 km, plenty for a national map

OUTPUT_DIR = Path("data/ala")

# ALA has used slightly different column names over the years.
# For each value we need, these are the names we accept, in order.
COLUMN_NAMES = {
    "lat":   ["decimalLatitude", "Latitude - original", "latitude"],
    "lon":   ["decimalLongitude", "Longitude - original", "longitude"],
    "year":  ["year", "Year"],
    "month": ["month", "Month"],
    "state": ["stateProvince", "State/Territory", "cl22", "state"],
}

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

def open_rows(path):
    """Yield each record as a dict, from a .csv file or a .zip containing one."""
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_names = [n for n in archive.namelist() if n.endswith(".csv")]
            # ALA zips also hold citation/licence CSVs; the records file is the largest
            records_file = max(csv_names, key=lambda n: archive.getinfo(n).file_size)
            with archive.open(records_file) as raw:
                yield from csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"))
    else:
        with open(path, newline="", encoding="utf-8") as file:
            yield from csv.DictReader(file)


def find_columns(header):
    """Map our short names (lat, lon, ...) to the actual column names in this file."""
    found = {}
    for short_name, candidates in COLUMN_NAMES.items():
        match = next((name for name in candidates if name in header), None)
        if match is None:
            sys.exit(f"Could not find a '{short_name}' column. Columns in file: {header}")
        found[short_name] = match
    return found


def clean_record(row, columns):
    """Return (lat, lon, year, month, state) or None if the row can't be used."""
    try:
        lat = round(float(row[columns["lat"]]), COORD_DECIMALS)
        lon = round(float(row[columns["lon"]]), COORD_DECIMALS)
        year = int(float(row[columns["year"]]))
        month = int(float(row[columns["month"]]))
    except (ValueError, TypeError):
        return None                     # missing or non-numeric value
    if not 1 <= month <= 12:
        return None
    state_name = row[columns["state"]].strip()
    state = STATE_ABBREVIATIONS.get(state_name, state_name)
    return lat, lon, year, month, state


# ---- Grid helper -----------------------------------------------------------

def grid_centre(value):
    """Snap a coordinate to the centre of its grid square, e.g. 144.96 -> 144.5."""
    return (value // GRID_SIZE) * GRID_SIZE + GRID_SIZE / 2


# ---- Writing ---------------------------------------------------------------

def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
    size_kb = path.stat().st_size / 1024
    print(f"  {path}  ({len(rows):,} rows, {size_kb:,.0f} KB)")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    rows = open_rows(sys.argv[1])
    first = next(rows)
    columns = find_columns(list(first.keys()))

    points = []
    grid_counts = Counter()
    month_counts = Counter()
    skipped = 0

    for row in [first, *rows]:
        record = clean_record(row, columns)
        if record is None:
            skipped += 1
            continue
        lat, lon, year, month, state = record

        if year in POINT_YEARS:
            points.append((lat, lon, year, month, state))
        if year in GRID_YEARS:
            grid_counts[(year, grid_centre(lon), grid_centre(lat))] += 1
        if year in MONTH_YEARS:
            month_counts[(year, month)] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Wrote:")
    write_csv(OUTPUT_DIR / "sightings-points.csv",
              ["lat", "lon", "year", "month", "state"], points)
    write_csv(OUTPUT_DIR / "sightings-grid-by-year.csv",
              ["year", "lon", "lat", "count"],
              [(y, x, la, n) for (y, x, la), n in sorted(grid_counts.items())])
    write_csv(OUTPUT_DIR / "sightings-by-month.csv",
              ["year", "month", "count"],
              [(y, m, n) for (y, m), n in sorted(month_counts.items())])
    print(f"Skipped {skipped:,} rows without usable coordinates or date.")


if __name__ == "__main__":
    main()
