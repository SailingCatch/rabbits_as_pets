#!/usr/bin/env bash
#
# Turn the ABS state and territory boundary file (about 20 MB) into two small
# files for the maps:
#
#   data/geo/australia-states.topojson   simplified outlines, about 100 KB
#                                        one object called "states", each
#                                        shape has properties: name, state,
#                                        area_km2
#   data/geo/state-centroids.csv         one point inside each state, for
#                                        labels and proportional circles,
#                                        plus the state's land area
#                                        columns: state, name, area_km2, lon, lat
#
# "state" is the short code (NSW, VIC, ...) used by every other data file,
# so all the maps join their data on that one column.
#
# Usage (from the project folder):
#   scripts/build_boundaries.sh data/raw/STE_2021_AUST_SHP_GDA2020/STE_2021_AUST_GDA2020.shp
#
# Needs Node.js. mapshaper is downloaded and run by npx, nothing to install.

set -euo pipefail

INPUT="${1:?Give the path to the ABS STE_2021 .shp (or .geojson) file}"
OUT_DIR="data/geo"
mkdir -p "$OUT_DIR"

# Lookup from the ABS full name to the short code used across the project.
# Rows that aren't one of these eight ("Other Territories",
# "Outside Australia") get no code and are dropped by the filter below.
CODES="({
  'New South Wales': 'NSW',
  'Victoria': 'VIC',
  'Queensland': 'QLD',
  'South Australia': 'SA',
  'Western Australia': 'WA',
  'Tasmania': 'TAS',
  'Northern Territory': 'NT',
  'Australian Capital Territory': 'ACT'
})"

# Step by step:
#   -each           add the short code, a plain "name" and the ABS area
#   -filter         keep the eight states and territories
#   -filter-fields  drop every other ABS column (keeps the file small)
#   -simplify       remove 99% of the outline detail (invisible at page size);
#                   keep-shapes stops small islands from vanishing entirely
#   -rename-layers  call the TopoJSON object "states" (the specs refer to it)
#   -o              write the TopoJSON; quantization rounds coordinates
#   -points inner   swap each shape for a point well inside it
#   -each           store that point's coordinates as lon / lat columns
#   -o              write the centroids as CSV
npx --yes mapshaper@0.7 "$INPUT" \
  -each "name = STE_NAME21, state = ${CODES}[STE_NAME21], area_km2 = Math.round(AREASQKM21)" \
  -filter "state !== undefined" \
  -filter-fields state,name,area_km2 \
  -simplify 1% keep-shapes \
  -rename-layers states \
  -o "$OUT_DIR/australia-states.topojson" format=topojson quantization=100000 \
  -points inner \
  -each "lon = +this.x.toFixed(3), lat = +this.y.toFixed(3)" \
  -o "$OUT_DIR/state-centroids.csv" format=csv

echo "Done:"
ls -lh "$OUT_DIR"
