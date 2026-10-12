#!/usr/bin/env bash
#
# Download Western Australia's three historic rabbit-proof fences and turn
# them into one small file for the fence map:
#
#   data/geo/rabbit-proof-fences.geojson   three lines, property: fence
#                                          ("No. 1", "No. 2", "No. 3")
#
# Source: DPIRD, Historic Number 1/2/3 Rabbit Proof Fence (DPIRD-046/047/048),
# CC BY 3.0 AU, via the WA Government's public SLIP map service.
#
# Usage (from the project folder; needs Node.js for mapshaper):
#   scripts/build_fences.sh

set -euo pipefail

RAW="data/raw/fences"
SERVICE="https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Buildings_and_Structures/MapServer"
mkdir -p "$RAW" data/geo

# Layers 1, 2 and 3 of the service are fences No. 1, 2 and 3
for n in 1 2 3; do
  curl -sf "$SERVICE/$n/query?where=1%3D1&outFields=*&outSR=4326&f=geojson" -o "$RAW/rpf$n.geojson"
done

# combine-files  read all three as separate layers
# -each          name each line after its file (rpf1 -> "No. 1")
# -merge-layers  one layer, three features
# -simplify      drop 90% of the points (still exact at page size)
cd "$RAW"
npx --yes mapshaper@0.7 -i rpf1.geojson rpf2.geojson rpf3.geojson combine-files \
  -each 'fence = this.layer_name.replace("rpf", "No. ")' \
  -merge-layers force \
  -filter-fields fence \
  -simplify 10% keep-shapes \
  -o ../../geo/rabbit-proof-fences.geojson precision=0.001
