# PV Mini-Lab Data Dictionary

## 1. Data Schema (Simulated ICSR)

### `cases.csv`

- `case_id` (str): Unique identifier (e.g., "CASE-0001").
- `age` (int): Patient age in years.
- `sex` (str): "M", "F", or "Unknown".
- `weight_kg` (float): Patient weight.
- `reporter_type` (str): "Physician", "Pharmacist", "Consumer", "Other".
- `report_date` (date): Date of report (YYYY-MM-DD).
- `serious` (str): "Yes", "No", "Unknown" (Derived per case).

### `drugs.csv`

- `case_id` (str): Foreign key to cases.
- `drug_name` (str): Standardized drug name (Methadone, Buprenorphine, Morphine, Oxycodone).
- `role_cod` (str): "PS" (Primary Suspect), "SS" (Secondary Suspect), "C" (Concomitant).
- `indication` (str): Indication for use (e.g., "Pain management", "Opioid dependence").

### `events.csv`

- `case_id` (str): Foreign key to cases.
- `event_pt` (str): MedDRA Preferred Term (simulated).
- `outcome` (str): NOT INCLUDED (per rules).

## 2. Signal Metrics (2x2 Contingency Table)

For a specific Drug-Event pair:

|             | Event Present (E) | Event Absent (~E) | Total |
|-------------|-------------------|-------------------|-------|
| **Drug (D)**    | a                 | b                 | a+b   |
| **Not Drug (~D)**| c                 | d                 | c+d   |
| **Total**   | a+c               | b+d               | N     |

- **a**: Cases with Drug D and Event E.
- **b**: Cases with Drug D but NOT Event E.
- **c**: Cases with Comparators but Event E.
- **d**: Cases with Comparators and NOT Event E.

### Formulas

- **PRR (Proportional Reporting Ratio)**: `(a / (a + b)) / (c / (c + d))`
- **ROR (Reporting Odds Ratio)**: `(a / b) / (c / d)`
  - *Correction:* If any cell is 0, add 0.5 to all cells.

### Interpretation

- **Screening Threshold:** `a ≥ 3` (Project rule: `a ≥ 10` for high confidence).
- **Disclaimer:** Exploratory screening only. Does not establish causality.
