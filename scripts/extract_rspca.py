"""
Read the RSPCA Australia annual statistics PDFs and write two small CSVs.

Each PDF has a "Table 4: Animals received by each RSPCA Society", with one
block per kind of animal and one column per state. This script copies the
numbers exactly as printed, then checks them three ways and prints any
problem it finds (it never "fixes" a printed number):

  1. each state's outcomes add up to its "Total other animals"
  2. the states add up to the printed national "Total" column
  3. "Last year's total" matches the previous year's PDF

    data/rspca/other-animals-by-state.csv
        the "Other Animals" block (budgies, ferrets, guinea pigs, mice,
        rabbits, rats, ...): one row per state per year
        columns: financial_year, state, received, reclaimed, returned,
                 rehomed, in_care, transferred, euthanased, other,
                 note, source_pdf, source_page
        "returned" is only printed from 2021-22 on; it's empty before that.
        -> charts 6, 7, 9, 10

    data/rspca/received-by-animal.csv
        totals for dogs, cats and other animals: one row per state per year
        columns: financial_year, state, dogs, cats, other_animals,
                 source_pdf, source_page
        -> chart 8

Usage (from the project folder, after downloading the PDFs into
data/raw/rspca/; needs pdftotext from poppler-utils):
    python3 scripts/extract_rspca.py
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

PDF_DIR = Path("data/raw/rspca")
OUTPUT_DIR = Path("data/rspca")

STATES = ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"]

# Row labels as printed -> our column names
OUTCOMES = {
    "Reclaimed": "reclaimed",
    "Returned": "returned",
    "Rehomed": "rehomed",
    "Currently in Care": "in_care",
    "Transferred": "transferred",
    "Euthanased": "euthanased",
    "Other": "other",
}

# Problems in the PDFs themselves, found by the checks below. Each one is
# shown on the page as a footnote, so the reader knows.
SWAPPED_COLUMNS = {
    # The 2024-25 PDF heads its columns ACT, NSW, NT, ... but the numbers are
    # in the order ACT, NT, NSW: its own "Last year's total" rows only match
    # the 2023-24 PDF with NSW and NT swapped, for every kind of animal.
    "2024-25": ("NSW", "NT"),
}
# (year, state or None for every state, note)
NOTES = [
    ("2024-25", None, "The PDF labels the NSW and NT columns the wrong way round; "
                      "they are swapped back here."),
    ("2024-25", None, "The PDF's 'Reclaimed' row repeats the 2023-24 figures "
                      "exactly, so outcomes don't add up to the total."),
    ("2010-11", "WA", "The PDF prints 0 for WA, but the 2011-12 PDF gives 38 as "
                      "WA's 2010-11 total."),
    ("2013-14", "NT", "The PDF's outcomes add up to 34, one more than its total of 33."),
]

NUMBER = re.compile(r"^-?[\d,]+(\.\d+)?%?$")


# ---- Reading the PDF text ------------------------------------------------

def pdf_lines(pdf):
    """The PDF as text lines, each tagged with its page number."""
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    return [(page + 1, line)
            for page, page_text in enumerate(text.split("\f"))
            for line in page_text.splitlines()]


def split_row(line):
    """'Rehomed   191  0  646 ...' -> ('Rehomed', ['191', '0', '646', ...]).
    Footnote markers stuck to the label ('Transferred3') are removed."""
    tokens = line.split()
    numbers = []
    while tokens and NUMBER.match(tokens[-1]):
        numbers.insert(0, tokens.pop().replace(",", ""))
    label = re.sub(r"(?<=[a-z])\d+$", "", " ".join(tokens)).strip()
    return label, numbers


def is_state_header(line):
    return re.search(r"\bACT\b", line) and re.search(r"\bWA\b", line)


def table4_rows(lines):
    """Yield (block, label, {state: number, 'Total': number}, page) for every
    row of Table 4 that has a number for each state plus the total.

    pdftotext sometimes puts a label on one line and its numbers on the next
    ('Currently in Care  2' then '8  0  117 ...'), so a label without a full
    set of numbers is held until the numbers turn up."""
    # The real Table 4 heading, not its entry in the contents page, is the
    # one with a row of state names just below it.
    start = next(i for i, (_, line) in enumerate(lines)
                 if re.search(r"\bTable 4\b", line)
                 and any(is_state_header(l) for _, l in lines[i + 1:i + 15]))
    columns, block, pending = None, None, None
    for page, line in lines[start:]:
        if re.search(r"\bTable 5\b", line):
            break
        if is_state_header(line):
            columns = [re.sub(r"\W|\d", "", t).replace("Darwin", "NT") for t in line.split()]
            continue
        if columns is None:
            continue
        label, numbers = split_row(line)
        if label in ("Dogs", "Cats", "Horses", "Livestock", "Wildlife", "Other Animals", "Other animals"):
            block, pending = label.lower(), None
            continue
        if label.startswith("Total other"):  # pdftotext sometimes cuts it short
            label = "Total other animals"
        if label.startswith("Total animals"):
            block = "all animals"           # so its "Last year" row isn't mistaken
        if len(numbers) == len(columns) + 1:
            label = label or pending
            pending = None
            if label:
                values = dict(zip(columns + ["Total"], (float(n.rstrip("%")) for n in numbers)))
                yield block, label, values, page
        elif label and not label.startswith(("Page", "Table", "State/Territory")):
            pending = label


def financial_year(pdf):
    first, second = re.search(r"(20\d\d)-(20\d\d)", pdf.name).groups()
    return f"{first}-{second[2:]}"


# ---- Checks --------------------------------------------------------------

def check(year, other, totals, last_year_printed, previous_totals):
    problems = []
    for state in STATES:
        row = other[state]
        outcome_sum = sum(row[c] or 0 for c in OUTCOMES.values())
        if outcome_sum != row["received"]:
            problems.append(f"{state}: outcomes add to {outcome_sum:g}, total printed {row['received']:g}")
    for block, values in totals.items():
        state_sum = sum(values[s] for s in STATES)
        if state_sum != values["Total"]:
            problems.append(f"{block}: states add to {state_sum:g}, national total printed {values['Total']:g}")
    if previous_totals:
        for state in STATES:
            if last_year_printed.get(state) != previous_totals[state]:
                problems.append(f"{state}: 'last year' printed as {last_year_printed.get(state):g}, "
                                f"previous PDF says {previous_totals[state]:g}")
    for problem in problems:
        print(f"  CHECK {year}  {problem}")


# ---- Main ----------------------------------------------------------------

def main():
    pdfs = sorted(PDF_DIR.glob("*.pdf"), key=financial_year)
    if not pdfs:
        sys.exit(f"No PDFs in {PDF_DIR}. See data/README.md.\n\n{__doc__}")

    other_rows, animal_rows = [], []
    previous_totals = None
    for pdf in pdfs:
        year = financial_year(pdf)
        swap = SWAPPED_COLUMNS.get(year)
        other = {s: {c: None for c in OUTCOMES.values()} for s in STATES}
        totals, last_year, pages = {}, {}, {}

        for block, label, values, page in table4_rows(pdf_lines(pdf)):
            if swap:
                values[swap[0]], values[swap[1]] = values[swap[1]], values[swap[0]]
            if label in ("Total dogs", "Total cats", "Total other animals"):
                totals[label] = values
                pages[label] = page
            if block != "other animals":
                continue
            if label in OUTCOMES:
                for state in STATES:
                    other[state][OUTCOMES[label]] = values[state]
            elif label == "Total other animals":
                for state in STATES:
                    other[state]["received"] = values[state]
            elif label.startswith("Last year"):
                last_year = values

        missing = {"Total dogs", "Total cats", "Total other animals"} - totals.keys()
        if missing:
            sys.exit(f"{pdf.name}: could not find {', '.join(sorted(missing))}")

        check(year, other, totals, last_year, previous_totals)
        previous_totals = totals["Total other animals"]

        for state in STATES:
            notes = [text for y, s, text in NOTES if y == year and s in (None, state)]
            row = other[state]
            other_rows.append([year, state, row["received"],
                               *(row[c] for c in OUTCOMES.values()),
                               " ".join(notes), pdf.name, pages["Total other animals"]])
            animal_rows.append([year, state,
                                totals["Total dogs"][state], totals["Total cats"][state],
                                totals["Total other animals"][state], pdf.name, min(pages.values())])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "other-animals-by-state.csv",
              ["financial_year", "state", "received", *OUTCOMES.values(),
               "note", "source_pdf", "source_page"], other_rows)
    write_csv(OUTPUT_DIR / "received-by-animal.csv",
              ["financial_year", "state", "dogs", "cats", "other_animals",
               "source_pdf", "source_page"], animal_rows)


def write_csv(path, header, rows):
    def tidy(value):                      # 12.0 -> 12, None -> empty cell
        if value is None:
            return ""
        return int(value) if isinstance(value, float) and value.is_integer() else value

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([tidy(v) for v in row] for row in rows)
    print(f"Wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
