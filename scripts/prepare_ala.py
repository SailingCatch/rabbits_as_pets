"""
Turn the Atlas of Living Australia (ALA) rabbit download into small files
the charts can load quickly.

The raw download has one row per record and 192 columns (about 140 MB
unzipped). The charts only need counts, so this script writes:

    data/ala/sightings-points.csv        records per ~1 km spot, recent years
                                         columns: year, state, lat, lon, count
                                         -> (spare: dot map version of chart 3)

    data/ala/sightings-hexbins.geojson   records per hexagon (~80 km across),
                                         2021-2025; property: count
                                         -> chart 3 (hexagon map with fences)

    data/ala/sightings-grid-by-year.csv  records per 1° square (~100 km), per year
                                         columns: year, lon, lat, count
                                         -> chart 5 (map with a year picker)

    data/ala/sightings-by-month.csv      records per month
                                         columns: year, month, count
                                         -> (spare: heatmap version of chart 6)

    data/ala/sightings-by-state-month.csv records per state per month, 2010-2025
                                         columns: state, month, count
                                         -> chart 6 (ridgeline of the seasons)

    data/ala/sightings-by-state-year.csv records per state per year
                                         columns: year, state, count
                                         -> chart 7 (sightings per 1,000 km²)

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
import math
import sys
import zipfile
from collections import Counter
from pathlib import Path

# ---- Settings you might change ------------------------------------------

POINT_YEARS = {2024, 2025}          # years drawn as individual dots (chart 1)
GRID_YEARS = range(2010, 2026)      # years you can pick on the map (chart 3)
COUNT_YEARS = range(2010, 2026)     # years in the heatmap and state chart (charts 4, 5)
COORD_DECIMALS = 2                  # 2 decimals ≈ 1 km, plenty for a national map
HEX_YEARS = range(2021, 2026)       # years counted into the hexagon map (chart 3)
HEX_RADIUS_KM = 40                  # centre-to-corner size of each hexagon

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


# ---- Hexagons ----------------------------------------------------------------
# The page draws Australia with an Albers equal-area conic projection
# (parallels -18° and -36°, centred on 132°E). Binning in that same flat
# plane means every hexagon covers the same area and draws as a true,
# regular hexagon on the page. These are the projection formulas d3 and
# Vega use (conicEqualArea), on a unit sphere, so 1 unit = 6,371 km.

EARTH_RADIUS_KM = 6371
PHI1, PHI2 = math.radians(-18), math.radians(-36)
LON0 = 132
N = (math.sin(PHI1) + math.sin(PHI2)) / 2
C = 1 + math.sin(PHI1) * (2 * N - math.sin(PHI1))
R0 = math.sqrt(C) / N


def project(lon, lat):
    lam = math.radians(lon - LON0) * N
    r = math.sqrt(C - 2 * N * math.sin(math.radians(lat))) / N
    return r * math.sin(lam), R0 - r * math.cos(lam)


def unproject(x, y):
    r0y = R0 - y
    lam = math.atan2(x, abs(r0y)) * math.copysign(1, r0y)
    if r0y * N < 0:
        lam -= math.pi * math.copysign(1, x) * math.copysign(1, r0y)
    lat = math.asin((C - (x * x + r0y * r0y) * N * N) / (2 * N))
    return math.degrees(lam / N) + LON0, math.degrees(lat)


HEX_R = HEX_RADIUS_KM / EARTH_RADIUS_KM


def hex_cell(lon, lat):
    """Which hexagon (pointy-top, axial q/r numbering) a point falls in."""
    x, y = project(lon, lat)
    q = (math.sqrt(3) / 3 * x - y / 3) / HEX_R
    r = (2 / 3 * y) / HEX_R
    # round to the nearest hexagon using cube coordinates
    cx, cz = q, r
    cy = -cx - cz
    rx, ry, rz = round(cx), round(cy), round(cz)
    dx, dy, dz = abs(rx - cx), abs(ry - cy), abs(rz - cz)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy <= dz:
        rz = -rx - ry
    return rx, rz


def hex_polygon(q, r):
    """The hexagon's six corners as [lon, lat] pairs (closed ring).
    Corners go clockwise, which map libraries (d3, Vega) read as "the inside
    of this shape"; anticlockwise would mean "everything except it"."""
    cx = HEX_R * math.sqrt(3) * (q + r / 2)
    cy = HEX_R * 1.5 * r
    ring = []
    for i in range(7):
        angle = math.radians(-60 * i - 30)
        lon, lat = unproject(cx + HEX_R * math.cos(angle), cy + HEX_R * math.sin(angle))
        ring.append([round(lon, 3), round(lat, 3)])
    return ring


def write_hexbins(path, counts):
    features = [
        {"type": "Feature",
         "properties": {"count": n},
         "geometry": {"type": "Polygon", "coordinates": [hex_polygon(q, r)]}}
        for (q, r), n in sorted(counts.items())
    ]
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features},
                               separators=(",", ":")))
    size_kb = path.stat().st_size / 1024
    print(f"  {path}  ({len(features):,} hexagons, {sum(counts.values()):,} records, {size_kb:,.0f} KB)")


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
    hexes, state_months = Counter(), Counter()
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
            if state:
                state_months[(state, month)] += 1
        else:
            no_month += 1
        if lat is None or lon is None:
            no_coords += 1
            continue
        if year in POINT_YEARS:
            points[(year, state, round(lat, COORD_DECIMALS), round(lon, COORD_DECIMALS))] += 1
        if year in HEX_YEARS:
            hexes[hex_cell(lon, lat)] += 1
        if year in GRID_YEARS:
            # Snap to the nearest whole degree: the centre of a 1° square
            grid[(year, float(round(lon)), float(round(lat)))] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Read {total:,} records from {zip_path.name}. Wrote:")
    write_csv(OUTPUT_DIR / "sightings-points.csv", ["year", "state", "lat", "lon", "count"], points)
    write_csv(OUTPUT_DIR / "sightings-grid-by-year.csv", ["year", "lon", "lat", "count"], grid)
    write_csv(OUTPUT_DIR / "sightings-by-month.csv", ["year", "month", "count"], months)
    write_csv(OUTPUT_DIR / "sightings-by-state-month.csv", ["state", "month", "count"], state_months)
    write_csv(OUTPUT_DIR / "sightings-by-state-year.csv", ["year", "state", "count"], states)
    write_hexbins(OUTPUT_DIR / "sightings-hexbins.geojson", hexes)
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
