
import pandas as pd
import plotly.express as px
from pathlib import Path

# CONFIG
PROCESSED_DATA_PATH = Path(__file__).parent.parent / "data/processed/clean_data.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs/figures"

def generate_visuals():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. LOAD DATA
    print("Loading processed data for viz...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # Unique cases for demographic plots
    df_cases = df.drop_duplicates(subset=['case_id'])
    
    print(f"Generating figures for {len(df_cases)} unique cases...")
    
    # --- FIG 1: Age Distribution ---
    fig_age = px.histogram(
        df_cases, x="age", nbins=20, 
        title="Distribution of Patient Age",
        color_discrete_sequence=['#636EFA']
    )
    fig_age.write_html(OUTPUT_DIR / "fig_age_hist.html")
    
    # --- FIG 2: Sex Distribution ---
    fig_sex = px.pie(
        df_cases, names="sex", 
        title="Case Distribution by Sex",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_sex.write_html(OUTPUT_DIR / "fig_sex_dist.html")
    
    # --- FIG 3: Top 10 Drugs ---
    # Count by Case-Drug unique pairs
    df_drug_cases = df[['case_id', 'drug_name']].drop_duplicates()
    top_drugs = df_drug_cases['drug_name'].value_counts().head(10).reset_index()
    top_drugs.columns = ['Drug', 'Count']
    
    fig_drugs = px.bar(
        top_drugs, x="Count", y="Drug", orientation='h',
        title="Top Reported Drugs (Case Count)",
        color="Count", color_continuous_scale='Viridis'
    )
    fig_drugs.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_drugs.write_html(OUTPUT_DIR / "fig_top_drugs.html")
    
    # --- FIG 4: Top 10 Events ---
    # Count by Case-Event unique pairs
    df_event_cases = df[['case_id', 'event_pt']].drop_duplicates()
    top_events = df_event_cases['event_pt'].value_counts().head(10).reset_index()
    top_events.columns = ['Event', 'Count']
    
    fig_events = px.bar(
        top_events, x="Count", y="Event", orientation='h',
        title="Top Reported Events (Case Count)",
        color="Count", color_continuous_scale='Magma'
    )
    fig_events.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_events.write_html(OUTPUT_DIR / "fig_top_events.html")
    
    # --- FIG 5: Serious vs Non-Serious by Drug ---
    # % Serious per drug
    df_serious = df[['case_id', 'drug_name', 'serious']].drop_duplicates()
    # Group by Drug + Serious
    serious_counts = df_serious.groupby(['drug_name', 'serious']).size().reset_index(name='Count')
    
    fig_serious = px.bar(
        serious_counts, x="Count", y="drug_name", color="serious",
        title="Seriousness Profile by Drug",
        barmode='stack'
    )
    fig_serious.write_html(OUTPUT_DIR / "fig_serious_drug.html")
    
    # --- FIG 6: Heatmap (Drug vs Event) ---
    # Filter top 5 drugs and top 10 events to avoid clutter
    top_5_drugs = top_drugs['Drug'].head(5).tolist()
    top_10_events_list = top_events['Event'].head(10).tolist()
    
    df_heat = df[
        (df['drug_name'].isin(top_5_drugs)) & 
        (df['event_pt'].isin(top_10_events_list))
    ]
    
    heatmap_data = df_heat.groupby(['drug_name', 'event_pt']).size().reset_index(name='Count')
    heatmap_matrix = heatmap_data.pivot(index='drug_name', columns='event_pt', values='Count').fillna(0)
    
    fig_heat = px.imshow(
        heatmap_matrix, 
        title="Drug-Event Co-occurrence Heatmap",
        aspect="auto",
        color_continuous_scale='RdBu_r'
    )
    fig_heat.write_html(OUTPUT_DIR / "fig_heatmap.html")
    
    print("Visualizations generated in outputs/figures/")

if __name__ == "__main__":
    generate_visuals()
