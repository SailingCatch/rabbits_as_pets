# Data

Every file the page loads lives in this folder. This guide says where each
one comes from, how to make it, and what its columns mean.

The two **core sources** required by the brief are the Atlas of Living
Australia (wild rabbit records) and RSPCA Australia (shelter statistics).
The ABS boundaries and the legal-status table are supporting data.

Large raw downloads go in `data/raw/`, which git ignores. Only the small,
ready-to-use files are committed (about 360 KB in total).

| File | Made by | Used in charts |
|---|---|---|
| `geo/australia-states.topojson` | `scripts/build_boundaries.sh` | 1, 2, 3, 6 |
| `geo/state-centroids.csv` | `scripts/build_boundaries.sh` | 2, 5, 6 |
| `ala/sightings-points.csv` | `scripts/prepare_ala.py` | 1 |
| `ala/sightings-grid-by-year.csv` | `scripts/prepare_ala.py` | 3 |
| `ala/sightings-by-month.csv` | `scripts/prepare_ala.py` | 4 |
| `ala/sightings-by-state-year.csv` | `scripts/prepare_ala.py` | 5 |
| `ala/sightings-hexbins.geojson` | `scripts/prepare_ala.py` | 3 (hexagon map) |
| `ala/sightings-by-state-month.csv` | `scripts/prepare_ala.py` | 6 (ridgeline) |
| `ala/source.json` | `scripts/prepare_ala.py` | (metadata) |
| `rspca/other-animals-by-state.csv` | `scripts/extract_rspca.py` | 6, 7, 9, 10 |
| `rspca/received-by-animal.csv` | `scripts/extract_rspca.py` | 8 |
| `legal/rabbit-legal-status.csv` | compiled by hand | 2 |
| `peng/lagovirus-samples.csv` | typed in from the paper | 9 |
| `ama/pets-in-australia-2025.csv` | typed in from the report | 1 |
| `history/timeline.csv` | typed in from CSIRO, PestSmart, DPIRD | 2 |
| `geo/rabbit-proof-fences.geojson` | `scripts/build_fences.sh` | 3 |
| `ramsey/rhdv2-site-abundance.csv` | typed in from the paper | 4 |
| `anrd/rhd-sites.csv` | `scripts/prepare_anrd.py` | 4a |

All files join on one column, **`state`**: the short codes `NSW`, `VIC`,
`QLD`, `SA`, `WA`, `TAS`, `NT`, `ACT`.

On NixOS the tools the scripts need can be borrowed for one command with
`nix shell nixpkgs#nodejs -c ...` (mapshaper) and
`nix shell nixpkgs#poppler-utils -c ...` (pdftotext).

---

## 1. State boundaries (ABS)

**Source:** Australian Bureau of Statistics, *Australian Statistical
Geography Standard (ASGS) Edition 3*, State and Territory (STE) 2021,
GDA2020. Licence: CC BY 4.0.

1. Download [STE_2021_AUST_SHP_GDA2020.zip](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/STE_2021_AUST_SHP_GDA2020.zip)
   and unzip it into `data/raw/abs/`.
2. From the project folder run:

   ```bash
   scripts/build_boundaries.sh data/raw/abs/STE_2021_AUST_GDA2020.shp
   ```

**Output columns**

- `australia-states.topojson`, object `states`: `state` (code), `name` (full name), `area_km2`
- `state-centroids.csv`: `state`, `name`, `area_km2`, `lon`, `lat` (a point inside each state)

---

## 2. Wild rabbit records (Atlas of Living Australia)

**Source:** Atlas of Living Australia occurrence download, *Oryctolagus
cuniculus* (European rabbit), 2010–2025, Australia, ALA default data
quality profile. Downloaded 12 October 2026, 118,526 records.
**DOI:** <https://doi.org/10.26197/ala.d8ea8887-feb6-468f-8fd6-2cf0ff66193f>
Licence: set per record, mostly CC BY 4.0 and CC BY-NC 4.0
(non-commercial; fine for coursework).

To redo it:

1. Log in at [ala.org.au](https://www.ala.org.au/) and open
   [this search](https://biocache.ala.org.au/occurrences/search?q=lsid%3Ahttps%3A%2F%2Fbiodiversity.org.au%2Fafd%2Ftaxa%2F692effa3-b719-495f-a86f-ce89e2981652&fq=year%3A%5B2010%20TO%202025%5D&fq=country%3A%22Australia%22)
   (leave the default data quality profile on).
2. **Download → Occurrence records**, reason "Education". ALA emails a zip.
3. Save it in `data/raw/ala/` and run:

   ```bash
   python3 scripts/prepare_ala.py data/raw/ala/records-2026-10-12.zip
   ```

The script prints how many records it read, and how many had no
coordinates (5, left off the maps) or no month (1,461, left out of the
heatmap). Every record counts towards its state's total. The DOI and
download date are copied into `ala/source.json`.

**Output columns**

- `sightings-points.csv`: `year`, `state`, `lat`, `lon`, `count` (2024–2025; each row is a ~1 km spot and how many records were made there)
- `sightings-grid-by-year.csv`: `year`, `lon`, `lat`, `count` (records in each 1° square, 2010–2025; lon/lat are the square's centre)
- `sightings-by-month.csv`: `year`, `month`, `count` (2010–2025)
- `sightings-by-state-year.csv`: `year`, `state`, `count` (2010–2025; divide by `area_km2` for chart 5)

**Remember on the page**

- These are *reported sightings*, not a rabbit census. They're higher
  where more people live and look.
- A few spots hold hundreds of records (e.g. 473 at one spot in WA in
  2024): those are survey sites, not crowds of rabbits.
- The 1° grid includes a handful of island records (e.g. Macquarie
  Island, latitude −54) that fall outside a mainland map frame.

---

## 3. Shelter statistics (RSPCA Australia)

**Source:** RSPCA Australia, *Annual Statistics* 2010–11 to 2024–25,
Table 4 "Animals received by each RSPCA Society". No open licence is
stated, so cite every PDF (the CSV names the file and page for each row).

1. Download each year's PDF from the [RSPCA annual statistics](https://www.rspca.org.au/about/annual-statistics)
   page into `data/raw/rspca/`.
2. Run:

   ```bash
   python3 scripts/extract_rspca.py
   ```

The script copies the numbers exactly as printed, then checks that outcomes
add up to each state's total, that states add up to the national total,
and that each PDF's "last year's total" matches the previous PDF. It prints
every mismatch.

**Which "other animals"?** Use Table 4's *Other Animals* block (budgies,
ferrets, guinea pigs, mice, rabbits, rats, ...), about 6,000–8,000 a year.
The national "Total other animals" in Tables 1 and 2 (about 36,000) also
includes wildlife, livestock and horses, so don't use it.

**Columns**

- `other-animals-by-state.csv`: `financial_year` (e.g. `2024-25`), `state`,
  `received`, `reclaimed`, `returned`, `rehomed`, `in_care`,
  `transferred`, `euthanased`, `other`, `note`, `source_pdf`, `source_page`.
  `returned` is only printed from 2021–22 on; it's empty before that.
- `received-by-animal.csv`: `financial_year`, `state`, `dogs`, `cats`,
  `other_animals`, `source_pdf`, `source_page`.

**Problems in the PDFs (footnote these on the page; the `note` column has the wording)**

- **2024–25, NSW and NT swapped.** The PDF heads its columns ACT, NSW, NT
  but the numbers are in the order ACT, NT, NSW: its own "last year's
  total" rows only match the 2023–24 PDF that way round, for every kind
  of animal. The script swaps them back.
- **2024–25, "Reclaimed" row.** It repeats the 2023–24 row exactly, so no
  state's outcomes add up to its total. Totals and other outcomes are fine.
  Avoid charting 2024–25 "reclaimed".
- **2010–11, WA.** Printed as 0, but the 2011–12 PDF gives WA's 2010–11
  total as 38 (which is also the gap between the states and the national
  total).
- **2013–14, NT.** Outcomes add up to 34, one more than the printed 33.
- RSPCA ACT, NT and TAS don't include council pound animals; the other
  states do. NSW stopped including council animals after 2010–11, so NSW
  drops sharply between 2010–11 and 2011–12 for that reason.

---

## 4. Legal status of pet rabbits (compiled)

**Source:** each state and territory government's website, one URL per
row. This is supporting data compiled for this project, not one of the two
core sources.

**Columns:** `state`, `name`, `status` (`Allowed`, `Allowed with extra rules`
or `Banned`), `rule` (one plain-English sentence shown in the tooltip),
`source_url`, `verified` (`yes` once the government page has been read).

**Checklist** (verified 12 October 2026 unless ticked otherwise):

- [x] QLD, NT (Queensland and NT government pages)
- [x] SA (Landscape SA fact sheet: escape-proof cage required by law)
- [x] WA (DPIRD, importing animals to WA)
- [x] TAS (NRE Tasmania, rabbit biology)
- [x] ACT (Mandatory Code of Practice DI2024-231, legislation.act.gov.au)
- [ ] NSW: the DPI site blocks automated access, so check in a browser and add a URL
- [ ] VIC: check the Agriculture Victoria "Guidelines on keeping pet rabbits" page in a browser

---

## 5. Rabbit virus testing (Peng et al. 2023)

**Source:** Peng, N. Y. G., Hall, R. N., Huang, N., West, P., et al. (2023).
Utilizing molecular epidemiology and citizen science for the surveillance
of lagoviruses in Australia. *Viruses*, 15(12), 2348.
<https://doi.org/10.3390/v15122348> (open access, CC BY 4.0;
full text on PubMed Central, PMC10747141).

CSIRO tested 2,771 dead rabbits and hares sent in by the public between
January 2015 and December 2022. `peng/lagovirus-samples.csv` holds the
numbers stated in the paper's Results (sections 3.1 and 3.2), in long form:

**Columns:** `breakdown` (`source`, `state`, `result` or `variant`),
`category`, `samples`, `note`. Filter on `breakdown` in a spec.

- The paper's sample sources add to 2,777, six more than its total of 2,771.
- `variant` counts are positive samples only (1,640 of the 1,643 positives).
- Year-by-year splits are only shown in the paper's Figure 1, not as numbers.

---

## 6. Pet ownership (Animal Medicines Australia 2025)

**Source:** Animal Medicines Australia (2025). *Pets in Australia: A
national survey of pets and people.*
[PDF](https://animalmedicinesaustralia.org.au/wp-content/uploads/2025/09/SNR-2403006-Pet-Ownership-Study-2025-Designed_F3.pdf)

`ama/pets-in-australia-2025.csv` holds the headline figures: households with
pets (2016–2025), households by pet type, estimated pet numbers, which
small mammals people keep (rabbits 51%) and why. **Columns:** `breakdown`,
`category`, `value`, `unit`, `year`, `note`, `pdf_page`.

National figures only, from a survey of 2,450 people (65 of them
small-mammal owners), so use them for context and annotations rather than
for maps.

---

## 7. Timeline of rabbit control (compiled)

`history/timeline.csv`: one row per event, with the page it came from.
**Columns:** `year`, `label` (short, shown on the chart), `detail` (tooltip),
`theme` (`arrival`, `barrier`, `virus`, `resistance`), `source_url`.
Population figures (600 million in 1950, about 300 million in 1995) are the
sources' estimates, so the page says so. Sources disagree on two dates:
calicivirus got out in 1995 and was officially released in 1996, and RHDV2
is dated 2014 (PestSmart) or 2015 (CSIRO); the table uses CSIRO's.

---

## 8. Rabbit numbers before and after RHDV2 (Ramsey et al. 2023)

**Source:** Ramsey, D. S. L. et al. (2023). Sustained impact of RHDV2 on
wild rabbit populations across Australia eight years after its initial
detection. *Viruses*, 15(5), 1159. <https://doi.org/10.3390/v15051159>
(open access, CC BY 4.0).

`ramsey/rhdv2-site-abundance.csv` is the paper's Table 1: the estimated
typical (equilibrium) winter–spring rabbit abundance, in rabbits per km of
spotlight transect, before and after RHDV2 reached each site.
**Columns:** `site`, `state`, `before`, `after`, `change` (proportion,
e.g. −0.82). The paper's average across all sites is −0.64.

---

## 9. Rabbit-proof fences (DPIRD)

**Source:** WA Department of Primary Industries and Regional Development,
Historic Number 1, 2 and 3 Rabbit Proof Fence (DPIRD-046, 047, 048),
CC BY 3.0 AU. Run `scripts/build_fences.sh`; it downloads the three lines
from the WA Government's public map service (no login) and simplifies them
into `geo/rabbit-proof-fences.geojson` (about 10 KB, property `fence`).
The source describes the lines as indicative historic locations.

---

## 10. Long-term rabbit counts (Australian National Rabbit Database)

**Source:** Roy-Dufresne, E. et al. (2019). The Australian National Rabbit
Database: 50 yr of population monitoring of an invasive species. *Ecology*
100(7): e02750. <https://doi.org/10.1002/ecy.2750>. The paper states: "No
copyright or proprietary restrictions are associated with the use of this
data set other than citation of this Data Paper."

1. Download the paper's supporting file **ecy2750-sup-0001-DataS1.zip**
   (Wiley blocks scripts, so use a browser) into `data/raw/anrd/`.
2. Run:

   ```bash
   python3 scripts/prepare_anrd.py data/raw/anrd/ecy2750-sup-0001-datas1.zip
   ```

The abundance file has 51,241 night-time spotlight counts from 524 sites,
1965–2015. The script keeps the sites that meet a fixed rule, so the choice
can be explained and repeated: counted in at least 10 years, starting in or
before 1994 and running to 1997 or later, outside Tasmania (whose transects
are possum surveys that almost never record a rabbit). Twelve sites qualify.

**Columns:** `site`, `state`, `dataset`, `year`, `rabbits_per_km` (median of
that year's counts), `counts` (how many counts the median is from).

**Not used, but worth knowing:** the occurrence file holds about 100
historic release records (`AUS_HistRelease`, 1825–1925; locations only
accurate to about 15 km, and some state labels are wrong) and 994 dated
records of calicivirus spreading across Australia in 1995–1999
(`AUS_RHDV1Spread`). Don't use the occurrence file to extend the sightings
map back in time: before 1990 it is mostly museum specimens, and the 2000s
are dominated by one warren survey on Yorke Peninsula (about 500,000 records).

