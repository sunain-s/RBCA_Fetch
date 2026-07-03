# RBCA Register Tracker

A Python utility script that retrieves the latest Register of Registered Building Control Approvers (RBCAs) for England from the UK Government register, stores dated snapshots, and automatically identifies additions and removals between runs.

---

## Overview

This project automates the process of monitoring the public [Register of Registered Building Control Approvers (RBCAs)](https://www.find-a-building-control-approver.service.gov.uk/public-register-england/results?building-control-approver=&browse-all=true) published by the UK Government.

Instead of scraping HTML pages, the script retrieves data from the JSON API used by the public register, making the process faster, more reliable, and less susceptible to website layout changes.

Each execution produces:

- A complete snapshot of the current register
- A comparison against the previous snapshot
- CSV and Excel outputs for further analysis

---

## Features

- Retrieves the latest RBCA register directly from the Government API
- Stores dated snapshots for historical reference
- Detects:
  - New registrations (`[n]`)
  - Removed registrations (`[r]`)
- Exports both CSV and Excel formats
- Automatic retry handling for temporary HTTP failures
- Deduplicates registrations using the official registration number (RBCPxxxxxxxx)
- Organised output folders for snapshots and change (diff) reports

---

## Project Structure

```
RBCA_Fetch/
│
├── rbca_tracker.py
├── README.md
│
├── snapshots/
│   ├── RBCA_Register_YYYY-MM-DD.xlsx
│   └── RBCA_Register_YYYY-MM-DD.csv
│
└── diffs/
    ├── RBCA_Diff_YYYY-MM-DD.xlsx
    └── RBCA_Diff_YYYY-MM-DD.csv
```

---

## Requirements

- Python 3.10+
- pandas
- requests
- openpyxl

Install the required packages using:

```bash
pip install pandas requests openpyxl
```

or

```bash
python -m pip install pandas requests openpyxl
```

---

## Usage

Run the script:

```bash
python rbca_tracker.py
```

The script will:

1. Download the latest RBCA register
2. Create a dated snapshot
3. Compare against the previous snapshot (if one exists)
4. Generate a diff report

---

## Output

Each snapshot and diff report is exported as:

- Excel (.xlsx)
- CSV (.csv)

### Snapshot

Contains every currently registered RBCA.

Example:

| Registration Number | Company |
|---------------------|---------|
| RBCPxxxxxxxx | BUILDING CONTROL 1 LTD |
| RBCPyyyyyyyy | CONTROL BUILDINGS 2 LTD |

---

### Diff Report

Contains the current register together with any removed registrations.

The **Note** column indicates changes:

| Note | Meaning |
|------|---------|
| `[n]` | Newly registered since the previous snapshot |
| `[r]` | Registration no longer present in the latest register |

---

## Data Source

The register is obtained from the public Government API used by the Building Control Approver Register.

The script retrieves only publicly available information:

- Official company name
- Registration number

---

## Compliance

This project accesses publicly available Government data via the register's JSON API and identifies itself using a custom `User-Agent` header.

No rate-limiting bypass techniques, authentication, or protected content are used.

Users should ensure their use of Government information complies with the [GOV.UK guidance on reusing government content](https://www.gov.uk/help/reuse-govuk-content).

---

## Future Improvements

Potential enhancements include:
- Scheduled automated execution (quarterly)
- More targeted filtering, by registration type (only those who work on new builds)
- Company name change detection

---

## Notes

`RBCA_Register_2026-07-02.xlsx` is included solely as a test snapshot to demonstrate the diff functionality. It may be removed without affecting the operation of the script.

---

## Author

- [Sunain Syed](https://github.com/sunain-s/)