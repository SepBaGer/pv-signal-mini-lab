import pandas as pd
from pathlib import Path

# CONFIG
RAW_DIR = Path(__file__).parent.parent / "data/raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data/processed"

def clean_data():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. LOAD DATA
    print("Loading raw data...")
    cases = pd.read_csv(RAW_DIR / "cases.csv")
    drugs = pd.read_csv(RAW_DIR / "drugs.csv")
    events = pd.read_csv(RAW_DIR / "events.csv")
    
    print(f"Loaded: {len(cases)} cases, {len(drugs)} drugs, {len(events)} events.")
    
    # 2. QUALITY CHECKS (Basic)
    # Check for duplicate case_ids in cases
    n_unique_cases = cases['case_id'].nunique()
    if n_unique_cases != len(cases):
        print(f"WARNING: Found duplicate case_ids in cases.csv. Dropping duplicates.")
        cases = cases.drop_duplicates(subset=['case_id'])
        
    # Check linkage
    drug_case_ids = set(drugs['case_id'])
    event_case_ids = set(events['case_id'])
    valid_case_ids = set(cases['case_id'])
    
    orphan_drugs = drug_case_ids - valid_case_ids
    orphan_events = event_case_ids - valid_case_ids
    
    if orphan_drugs:
        print(f"WARNING: {len(orphan_drugs)} drug records have no matching case. Dropping.")
        drugs = drugs[drugs['case_id'].isin(valid_case_ids)]
        
    if orphan_events:
        print(f"WARNING: {len(orphan_events)} event records have no matching case. Dropping.")
        events = events[events['case_id'].isin(valid_case_ids)]
        
    # 3. MERGE (Long Format Generation)
    # Logic: Cartesian Product of Drugs x Events within each Case
    
    # Merge Cases + Drugs
    case_drugs = pd.merge(cases, drugs, on='case_id', how='inner')
    
    # Merge + Events
    # Inner join will multiply rows: For a case with D drugs and E events, we get D*E rows.
    # This represents all potential Drug-Event pairs for screening.
    full_data = pd.merge(case_drugs, events, on='case_id', how='inner')
    
    # 4. FINAL CLEANUP
    # Standardize columns
    final_cols = [
        'case_id', 'report_year', 'age', 'sex', 'reporter_type', 
        'serious', 'drug_name', 'role_cod', 'indication', 'event_pt'
    ]
    
    # Ensure all exist
    clean_df = full_data[final_cols].copy()
    
    # Deduplicate exact rows if any (shouldn't be if raw is clean, but safe practice)
    n_before = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    n_after = len(clean_df)
    
    if n_before != n_after:
        print(f"Dropped {n_before - n_after} duplicate rows during merge.")
        
    # 5. SAVE
    out_path = PROCESSED_DIR / "clean_data.csv"
    clean_df.to_csv(out_path, index=False)
    
    print("-" * 30)
    print("CLEANING COMPLETE")
    print(f"Output saved to: {out_path}")
    print(f"Total Analysis Rows (Pairs): {len(clean_df)}")
    print("-" * 30)
    print(clean_df.head())

if __name__ == "__main__":
    clean_data()
