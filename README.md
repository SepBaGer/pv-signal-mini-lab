# PV Signal Mini-Lab 🧪

A simulated Pharmacovigilance (PV) workbench for end-to-end signal detection (Screening -> Metrics -> Dashboard).

**⚠️ DISCLAIMER:**
> All data in this repository is **SIMULATED** text data generated for educational and technical demonstration purposes.
> It DOES NOT represent real patient data.
> The statistical signals (PRR/ROR) are based on injected patterns and **DO NOT imply clinical causality**.

---

## 🏗️ Project Architecture

This repo demonstrates a "Mini-Lab" workflow:

1. **Ingest:** Generates synthetic ICSRs (Individual Case Safety Reports).
2. **Clean:** Denormalizes data into a Case-Drug-Event long format.
3. **Metrics:** Calculates **PRR** (Proportional Reporting Ratio) and **ROR** (Reporting Odds Ratio) using a 2x2 contingency table.
4. **Visualize:** Streamlit Dashboard for signal triage and review.

### Directory Structure

```
pv-signal-mini-lab/
├── data/
│   ├── raw/             # Generated CSVs (cases, drugs, events)
│   └── processed/       # Denormalized analysis ready data
├── notebooks/           # Jupyter notebooks for prototyping
├── src/
│   ├── ingest.py        # Data generator (Seeds & Weights)
│   ├── clean.py         # ETL & De-duplication
│   ├── metrics.py       # Signal Statistics (a,b,c,d calculation)
│   └── viz.py           # Potly Figure generation
├── app/
│   └── app.py           # Streamlit Dashboard
├── docs/                # Safety Narratives
└── outputs/             # Tables, HTML Figures, Screenshots
```

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Run Pipeline (Reproduce Data)

```bash
# Generate Data (creates data/raw/)
python src/ingest.py

# Clean & Merge (creates data/processed/)
python src/clean.py

# Generate Visuals (creates outputs/figures/)
python src/viz.py

# Calculate Signals (creates outputs/tables/)
python src/metrics.py
```

### 3. Launch Dashboard

```bash
streamlit run app/app.py
```

## 📊 Methodology

### Signal Metrics

For each Drug-Event pair, we construct a 2x2 table:

|             | Event +           | Event -           |
|-------------|-------------------|-------------------|
| **Drug +**  | **a** (Cases)     | **b**             |
| **Drug -**  | **c**             | **d**             |

- **PRR:** `(a/(a+b)) / (c/(c+d))`
- **ROR:** `(a/b) / (c/d)`
- **Criteria:** We flag a signal if `a ≥ 10` AND `PRR ≥ 2.0`.

### Target Drugs

- **Methadone** (Target)
- Comparators: Buprenorphine, Morphine, Oxycodone

## 📝 Deliverables

- **Dashboard:** Interactive signal explorer.
- **Narratives:** See `docs/` for simulated medical reviews of Methadone signals.
- **Dataset:** `data/raw/` (N=2000 cases).
