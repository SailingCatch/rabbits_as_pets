"""
Download each state's and territory's population from the Australian Bureau
of Statistics and write one small file.

Source: ABS, National, state and territory population, Estimated Resident
Population (ERP), quarterly (dataflow ERP_Q), via the ABS Data API.
Licence: CC BY 4.0.

    data/abs/population-by-state.csv   columns: state, population, quarter
                                       (the latest quarter the ABS has published)
                                       -> chart 5a (Australians by rabbit rules)

Usage (from the project folder, needs internet, one request):
    python3 scripts/fetch_abs_population.py
"""

import csv
import io
import urllib.request
from pathlib import Path

# ABS region codes for the eight states and territories
REGIONS = {"1": "NSW", "2": "VIC", "3": "QLD", "4": "SA", "5": "WA", "6": "TAS", "7": "NT", "8": "ACT"}

# Measure 1 = estimated resident population, sex 3 = persons, age TOT = all ages
URL = ("https://data.api.abs.gov.au/rest/data/ABS,ERP_Q,1.0.0/"
       "1.3.TOT." + "+".join(REGIONS) + ".Q?startPeriod=2024-Q1")
OUTPUT = Path("data/abs/population-by-state.csv")


def main():
    request = urllib.request.Request(URL, headers={"Accept": "application/vnd.sdmx.data+csv"})
    with urllib.request.urlopen(request, timeout=60) as response:
        rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8"))))

    latest = max(row["TIME_PERIOD"] for row in rows)
    out = [[REGIONS[row["REGION"]], int(float(row["OBS_VALUE"])), latest]
           for row in rows if row["TIME_PERIOD"] == latest]
    out.sort(key=lambda r: list(REGIONS.values()).index(r[0]))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["state", "population", "quarter"])
        writer.writerows(out)
    total = sum(r[1] for r in out)
    print(f"Wrote {OUTPUT}: {len(out)} states and territories, {total:,} people, {latest}")


if __name__ == "__main__":
    main()
