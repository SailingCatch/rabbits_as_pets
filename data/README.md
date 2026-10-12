# Data

Every file the page loads lives in this folder. This guide says where each
one comes from, how to make it, and what its columns mean.

The two **core sources** required by the brief are the Atlas of Living
Australia (wild rabbit records) and RSPCA Australia (shelter statistics).
The ABS boundaries and the legal-status table are supporting data.

Large raw downloads go in `data/raw/`, which git ignores. Only the small,
ready-to-use files are committed.

| File | Made by | Used in charts |
|---|---|---|
| `geo/australia-states.topojson` | `scripts/build_boundaries.sh` | 1, 2, 3, 6 |
| `geo/state-centroids.csv` | `scripts/build_boundaries.sh` | 2, 6 |
| `ala/sightings-points.csv` | `scripts/prepare_ala.py` | 1 |
| `ala/sightings-grid-by-year.csv` | `scripts/prepare_ala.py` | 3 |
| `ala/sightings-by-month.csv` | `scripts/prepare_ala.py` | 4 |
| `rspca/other-animals-by-state.csv` | typed in by hand from the PDFs | 6–10 |
| `legal/rabbit-legal-status.csv` | compiled by hand | 2 |

All files join on one column, **`state`**: the short codes `NSW`, `VIC`,
`QLD`, `SA`, `WA`, `TAS`, `NT`, `ACT`.

---

## 1. State boundaries (ABS)

**Source:** Australian Bureau of Statistics, *Australian Statistical
Geography Standard (ASGS) Edition 3*, State and Territory (STE) 2021,
GDA2020. Licence: CC BY 4.0.

1. Go to the [ABS digital boundary files](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files)
   page and download **States and Territories – 2021 – Shapefile (GDA2020)**.
2. Unzip it into `data/raw/`.
3. From the project folder run:

   ```bash
   scripts/build_boundaries.sh data/raw/STE_2021_AUST_SHP_GDA2020/STE_2021_AUST_GDA2020.shp
   ```

   (The folder name inside the zip may differ slightly; point the script at the `.shp` file.)

**Output columns**

- `australia-states.topojson`, object `states`: `state` (code), `name` (full name)
- `state-centroids.csv`: `state`, `name`, `lon`, `lat` (a point inside each state)

---

## 2. Wild rabbit records (Atlas of Living Australia)

**Source:** Atlas of Living Australia (ALA), occurrence records for
*Oryctolagus cuniculus* (European rabbit). Licence: set per record, mostly
CC BY 4.0 and CC BY-NC 4.0 (non-commercial; fine for coursework). Cite the
download DOI ALA emails you.

1. Create a free account at [ala.org.au](https://www.ala.org.au/).
2. Search occurrence records for *Oryctolagus cuniculus*, then filter
   **Year: 2010 to 2025** (2026 is incomplete, so leave it out).
3. Choose **Download → Occurrence records → CSV**, reason "Education".
   ALA emails a zip link, usually within minutes.
4. Save the zip in `data/raw/` and run:

   ```bash
   python3 scripts/prepare_ala.py data/raw/<the-zip-name>.zip
   ```

5. Note the download date and DOI, and put both in the "About the data"
   section of `index.html`.

The script prints how many rows it wrote and skipped. Year ranges and grid
size are settings at the top of `scripts/prepare_ala.py`.

**Output columns**

- `sightings-points.csv`: `lat`, `lon`, `year`, `month`, `state` (2024–2025 only, coordinates rounded to about 1 km)
- `sightings-grid-by-year.csv`: `year`, `lon`, `lat`, `count` (records in each 1° square, 2019–2025; lon/lat are the square's centre)
- `sightings-by-month.csv`: `year`, `month`, `count` (2010–2025)

**Remember on the page:** these are *reported sightings*, not a rabbit
census. They're higher where more people live and look.

---

## 3. Shelter statistics (RSPCA Australia)

**Source:** RSPCA Australia, *Annual Statistics*, table for "Other
animals" by state and territory. Rabbits are counted in this group with
other small pets. No open licence is stated, so cite every PDF.

1. Download each year's PDF from the [RSPCA annual statistics](https://www.rspca.org.au/about/annual-statistics)
   page into `data/raw/rspca/`. Start with 2024–25, 2023–24 and 2010–11,
   then fill in the years between.
2. Open `rspca/other-animals-by-state.csv` and add **one row per state per
   year**, copying numbers exactly as printed.
3. Fill in `source_pdf` (file name) and `source_page` for every row.
4. Commit each year separately, e.g. `Transcribe RSPCA 2023–24 other-animals table`.

**Columns:** `financial_year` (e.g. `2024-25`), `state`, `received`,
then one column per outcome. The starting columns are `reclaimed`,
`rehomed`, `transferred`, `euthanased`, `in_care`, `other`. **Rename or
add columns so they match the rows printed in the PDF exactly.**

**Checks before you rely on it**

- [ ] The outcome columns for each state add up to `received`. If the PDF
      itself doesn't add up, keep the printed numbers and say so in a
      footnote. Never "fix" a printed number.
- [ ] 2024–25: the NSW and NT columns look swapped (NSW shows 0, NT 1,688,
      and the PDF's "last year" row disagrees with the 2023–24 PDF). Check
      the PDF; if it's a printing error, footnote it on the page.
- [ ] Note on the page which states' figures exclude council pound animals
      (the PDF's footnotes say).

---

## 4. Legal status of pet rabbits (compiled)

**Source:** each state and territory government's website, one URL per
row. This is supporting data compiled for this project, not one of the two
core sources.

**Columns:** `state`, `name`, `status` (`Allowed`, `Allowed with a code of
practice` or `Banned`), `rule` (one plain-English sentence shown in the
tooltip), `source_url`, `verified` (`yes` once you've read the government
page yourself).

**Checklist:** Queensland and the Northern Territory are confirmed. Before
publishing, find the official page for each row still marked `verified = no`,
correct the `status` and `rule` if needed, paste the URL and set `verified`
to `yes`.

- [ ] NSW (Department of Primary Industries)
- [ ] VIC (Agriculture Victoria)
- [ ] SA (Primary Industries and Regions SA)
- [ ] WA (Department of Primary Industries and Regional Development)
- [ ] TAS (Natural Resources and Environment Tasmania)
- [ ] ACT (City Services or legislation.act.gov.au: rabbit code of practice)
