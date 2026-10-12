"""
Pick the long-running rabbit monitoring sites from the Australian National
Rabbit Database and write one small file for the calicivirus chart.

Source: Roy-Dufresne, E. et al. (2019). The Australian National Rabbit
Database: 50 yr of population monitoring of an invasive species. Ecology
100(7): e02750. https://doi.org/10.1002/ecy.2750 . "No copyright or
proprietary restrictions are associated with the use of this data set
other than citation of this Data Paper."

The abundance file has 51,241 night-time spotlight counts (rabbits seen per
km of transect) from 524 sites, 1965-2015. To show what calicivirus (RHD,
arrived 1995) did, the chart needs sites counted for many years both before
and after it arrived. Sites are chosen by a fixed rule, not by hand, so no
site is left out because it tells a different story:

    1. counted in at least MIN_YEARS different years
    2. first counted in or before LAST_START (before calicivirus arrived)
    3. last counted in or after FIRST_END (after it spread)
    4. not in Tasmania: those transects are possum surveys that almost
       never see a rabbit, so every count is zero

    data/anrd/rhd-sites.csv     one row per site per year
                                columns: site, state, dataset, year,
                                rabbits_per_km (median of that year's counts),
                                counts (how many counts that median is from)
                                -> chart 4a (small multiples)

Usage (from the project folder, after saving the paper's DataS1 zip in
data/raw/anrd/):
    python3 scripts/prepare_anrd.py data/raw/anrd/ecy2750-sup-0001-datas1.zip
"""

import csv
import io
import statistics
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

# ---- The site rule ---------------------------------------------------------

MIN_YEARS = 10
LAST_START = 1994
FIRST_END = 1997
EXCLUDE_STATES = {"TAS"}

ABUNDANCE_FILE = "DataS1/SI2_DataAbundance.csv"
OUTPUT = Path("data/anrd/rhd-sites.csv")


# Some site names only make sense next to their dataset's name
DISPLAY_NAMES = {
    ("SA_RoxbyDowns_Spot", "Mine"): "Roxby Downs mine",
    ("SA_RoxbyDowns_Spot", "Town_Inside"): "Roxby Downs town",
    ("SA_RoxbyDowns_Spot", "Town_Outside"): "Roxby Downs outskirts",
    ("SA_FlindersRanges_PIRSA", "GumCreek"): "Gum Creek",
    ("VIC_ParksVictoria", "Millewa_North_Murray_Sunset"): "Millewa (Murray-Sunset)",
}


def tidy_name(dataset, name):
    """'Millewa_North_Murray_Sunset' -> 'Millewa North Murray Sunset'"""
    return DISPLAY_NAMES.get((dataset, name), name.replace("_", " "))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    with zipfile.ZipFile(sys.argv[1]) as archive:
        with archive.open(ABUNDANCE_FILE) as raw:
            rows = list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")))

    # Every count, grouped by site and year. Rows with no year or no count
    # can't be placed on a time line, so they're skipped.
    counts = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["Year"] == "NA" or row["RabbitsPerKm"] in ("NA", ""):
            continue
        site = (row["AustraliaState"], row["DataSourceName"], row["DataSourceSiteSectionName"])
        counts[site][int(row["Year"])].append(float(row["RabbitsPerKm"]))

    chosen = []
    for site, years in counts.items():
        span = sorted(years)
        if (site[0] not in EXCLUDE_STATES and len(span) >= MIN_YEARS
                and span[0] <= LAST_START and span[-1] >= FIRST_END):
            chosen.append(site)

    out = []
    for state, dataset, name in sorted(chosen):
        for year, values in sorted(counts[(state, dataset, name)].items()):
            out.append([tidy_name(dataset, name), state, dataset, year,
                        round(statistics.median(values), 2), len(values)])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["site", "state", "dataset", "year", "rabbits_per_km", "counts"])
        writer.writerows(out)
    print(f"{len(counts)} sites in the database; {len(chosen)} meet the rule.")
    print(f"Wrote {OUTPUT} ({len(out)} rows, {OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
