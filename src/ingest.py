
import pandas as pd
import numpy as np
import random
from pathlib import Path

# CONFIG
N_CASES = 2000
SEED = 42
OUTPUT_DIR = Path(__file__).parent.parent / "data/raw"

# TARGETS
DRUGS = ["Methadone", "Buprenorphine", "Morphine", "Oxycodone"]
WATCHLIST = [
    "Sedation", "Respiratory depression", "QT prolongation", "Arrhythmia", 
    "Syncope", "Drug interaction", "Confusion", "Nausea", "Constipation", 
    "Withdrawal symptoms"
]
NOISE_EVENTS = [
    "Headache", "Dizziness", "Rash", "Vomiting", "Insomnia", "Anxiety", 
    "Fatigue", "Diarrhea", "Pruritus", "Tremor"
]

def generate_data():
    np.random.seed(SEED)
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {N_CASES} cases...")

    # --- 1. CASES ---
    cases = []
    for i in range(1, N_CASES + 1):
        case_id = f"CASE-{i:04d}"
        age = int(np.random.normal(55, 15))
        age = max(0, min(100, age))
        sex = np.random.choice(["M", "F", "Unknown"], p=[0.48, 0.48, 0.04])
        reporter = np.random.choice(["Physician", "Pharmacist", "Consumer"], p=[0.6, 0.3, 0.1])
        serious = np.random.choice(["Yes", "No", "Unknown"], p=[0.4, 0.5, 0.1])
        
        cases.append({
            "case_id": case_id,
            "age": age,
            "sex": sex,
            "reporter_type": reporter,
            "serious": serious,
            "report_year": 2024
        })
    
    df_cases = pd.DataFrame(cases)
    
    # --- 2. DRUGS ---
    drug_records = []
    
    for case in cases:
        case_id = case["case_id"]
        # Assign primary suspect (skewed towards Methadone for volume if needed, or equal)
        # Let's do equal prob to start, or slight bias
        primary_drug = np.random.choice(DRUGS, p=[0.3, 0.2, 0.2, 0.3]) 
        
        drug_records.append({
            "case_id": case_id,
            "drug_name": primary_drug,
            "role_cod": "PS",
            "indication": "Pain management" if primary_drug != "Methadone" else "Opioid dependence"
        })
        
        # Chance of concomitants
        if random.random() < 0.3:
            concom = np.random.choice([d for d in DRUGS if d != primary_drug])
            drug_records.append({
                "case_id": case_id,
                "drug_name": concom,
                "role_cod": "SS",
                "indication": "Pain management"
            })
            
    df_drugs = pd.DataFrame(drug_records)
    
    # --- 3. EVENTS (With Signal Injection) ---
    event_records = []
    
    for case in cases:
        case_id = case["case_id"]
        
        # Check what drugs the patient has
        patient_drugs = df_drugs[df_drugs["case_id"] == case_id]["drug_name"].tolist()
        has_methadone = "Methadone" in patient_drugs
        
        # Determine events
        n_events = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
        
        # Probabilities
        events_pool = WATCHLIST + NOISE_EVENTS
        weights = np.ones(len(events_pool))
        
        # INJECTION LOGIC: Boost QT and Resp Dep for Methadone
        if has_methadone:
            # Indices for QT and Resp Dep
            idx_qt = events_pool.index("QT prolongation")
            idx_rd = events_pool.index("Respiratory depression")
            
            # Boost weights
            weights[idx_qt] = 8.0  # High boost
            weights[idx_rd] = 6.0
            
        # Normalize weights
        probs = weights / weights.sum()
        
        selected_events = np.random.choice(events_pool, size=n_events, replace=False, p=probs)
        
        for ev in selected_events:
            event_records.append({
                "case_id": case_id,
                "event_pt": ev
            })
            
    df_events = pd.DataFrame(event_records)
    
    # SAVE
    df_cases.to_csv(OUTPUT_DIR / "cases.csv", index=False)
    df_drugs.to_csv(OUTPUT_DIR / "drugs.csv", index=False)
    df_events.to_csv(OUTPUT_DIR / "events.csv", index=False)
    
    print("Data generation complete.")
    print(f"Cases: {len(df_cases)}")
    print(f"Drugs: {len(df_drugs)}")
    print(f"Events: {len(df_events)}")
    
    # Verify Signal Count for Methadone + QT
    # Simple check
    meth_cases = df_drugs[df_drugs["drug_name"] == "Methadone"]["case_id"].unique()
    qt_cases = df_events[df_events["event_pt"] == "QT prolongation"]["case_id"].unique()
    intersection = set(meth_cases).intersection(qt_cases)
    print(f"Methadone + QT Prolongation Cases (a): {len(intersection)}")

if __name__ == "__main__":
    generate_data()
