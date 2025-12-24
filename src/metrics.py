
import pandas as pd
import numpy as np
from pathlib import Path

# CONFIG
PROCESSED_DATA_PATH = Path(__file__).parent.parent / "data/processed/clean_data.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs/tables"

WATCHLIST = [
    "Sedation", "Respiratory depression", "QT prolongation", "Arrhythmia", 
    "Syncope", "Drug interaction", "Confusion", "Nausea", "Constipation", 
    "Withdrawal symptoms"
]

def calculate_metrics():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. LOAD DATA
    print("Loading data for metrics...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # Total unique cases in the full dataset (N for denominator logic)
    # Note: In a 2x2 contingency for a specific drug-event pair:
    # N is usually the Total Number of Reports in the database.
    total_cases_N = df['case_id'].nunique()
    
    print(f"Total Database Cases (N): {total_cases_N}")
    
    # 2. AGGREGATE COUNTS (a)
    # Count cases per Drug-Event pair
    # We use 'case_id' nunique to be safe, though our cleaning shouldn't have dups
    pair_counts = df.groupby(['drug_name', 'event_pt'])['case_id'].nunique().reset_index(name='a')
    
    # 3. CALCULATE MARGINALS
    # Total cases per Drug (a + b)
    drug_counts = df.groupby('drug_name')['case_id'].nunique().reset_index(name='n_drug')
    
    # Total cases per Event (a + c)
    event_counts = df.groupby('event_pt')['case_id'].nunique().reset_index(name='n_event')
    
    # Merge marginals back to pairs
    metrics_df = pd.merge(pair_counts, drug_counts, on='drug_name')
    metrics_df = pd.merge(metrics_df, event_counts, on='event_pt')
    
    # 4. DERIVE a, b, c, d
    # a = count(Drug + Event)
    # b = count(Drug + ~Event) = n_drug - a
    # c = count(~Drug + Event) = n_event - a
    # d = count(~Drug + ~Event) = N - (a + b) - c  OR  N - n_drug - c
    
    metrics_df['b'] = metrics_df['n_drug'] - metrics_df['a']
    metrics_df['c'] = metrics_df['n_event'] - metrics_df['a']
    metrics_df['d'] = total_cases_N - metrics_df['n_drug'] - metrics_df['c']
    
    # 5. HALDANE CORRECTION (for ROR stability)
    # If any cell is 0, add 0.5 to all.
    # Vectorized approach: Check if a*b*c*d == 0 (actually check if any is 0 row-wise)
    # For simplicity in this non-vectorized reading, we'll make corrected columns
    # But let's apply it globally or row-wise.
    # To be precise: correction is applied per row if that row has a zero.
    
    def calc_prr_ror(row):
        a, b, c, d = row['a'], row['b'], row['c'], row['d']
        
        # Correction
        has_zero = (a==0 or b==0 or c==0 or d==0)
        
        ac, bc, cc, dc = a, b, c, d
        if has_zero:
            ac += 0.5
            bc += 0.5
            cc += 0.5
            dc += 0.5
            
        # PRR = (a / (a+b)) / (c / (c+d))
        # Denom 0 check (should rarely happen with drug counts > 0)
        try:
            r1 = ac / (ac + bc)
            r0 = cc / (cc + dc)
            prr = r1 / r0 if r0 > 0 else np.nan
        except:
            prr = np.nan
            
        # ROR = (a/b) / (c/d) = (ad) / (bc)
        try:
            ror = (ac * dc) / (bc * cc) if (bc * cc) > 0 else np.nan
        except:
            ror = np.nan
            
        return pd.Series([prr, ror, has_zero])
        
    print("Calculating PRR / ROR...")
    metrics_df[['PRR', 'ROR', 'Corrected']] = metrics_df.apply(calc_prr_ror, axis=1)
    
    # 6. FLAGS & FILTERING
    metrics_df['is_watchlist'] = metrics_df['event_pt'].isin(WATCHLIST)
    
    # Define "Signal" status
    # Rule: a >= 3 is visible. But project says a>=10 is quality threshold.
    # Let's flag anything with a>=3 and PRR>=2 as a potential 'signal_flag'
    metrics_df['signal_flag'] = (metrics_df['a'] >= 10) & (metrics_df['PRR'] >= 2.0)
    
    # Sort: Watchlist first, then by PRR desc
    metrics_df = metrics_df.sort_values(by=['is_watchlist', 'a', 'PRR'], ascending=[False, False, False])
    
    # 7. EXPORT
    # Select columns
    out_cols = [
        'drug_name', 'event_pt', 
        'a', 'b', 'c', 'd', 
        'PRR', 'ROR', 
        'is_watchlist', 'signal_flag'
    ]
    
    # Filter for output (Drop very low counts to keep CSV clean? 
    # Or keep all > 0? Plan said "filter for a>=3")
    final_df = metrics_df[metrics_df['a'] >= 3][out_cols]
    
    out_path = OUTPUT_DIR / "signals.csv"
    final_df.to_csv(out_path, index=False)
    
    print(f"Signals calculated. Saved {len(final_df)} pairs (with a>=3) to {out_path}.")
    
    # Validation Peek
    print("\nTop Signals (Watchlist):")
    print(final_df[final_df['is_watchlist'] == True].head(5))

if __name__ == "__main__":
    calculate_metrics()
