import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

# CONFIG
ST_PAGE_TITLE = "PV Signal Mini-Lab"
DATA_DIR = Path(__file__).parent.parent / "data/processed"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"

st.set_page_config(page_title=ST_PAGE_TITLE, layout="wide")

# LOAD DATA
@st.cache_data
def load_data():
    try:
        clean_df = pd.read_csv(DATA_DIR / "clean_data.csv")
        signals_df = pd.read_csv(OUTPUT_DIR / "tables/signals.csv")
        
        if clean_df.empty or signals_df.empty:
            st.error("⚠️ Data files are empty. Regenerate data.")
            st.stop()
            
        return clean_df, signals_df
    except FileNotFoundError as e:
        st.error(f"❌ Data file not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

df_clean, df_signals = load_data()

# SESSION STATE
if 'selected_signal_idx' not in st.session_state:
    st.session_state.selected_signal_idx = None

# SIDEBAR
st.sidebar.title("PV Mini-Lab 🧪")
st.sidebar.info("**Note:** SIMULATED dataset. No real patient data.")

# PAGE SELECTOR
page = st.sidebar.radio(
    "📍 Navigate to:",
    ["Overview", "Signal Explorer", "Case Review"],
    index=0
)

# Show selection info in sidebar
if st.session_state.selected_signal_idx is not None:
    sig = df_signals.iloc[st.session_state.selected_signal_idx]
    st.sidebar.success(f"🔍 **Selected Signal:**")
    st.sidebar.markdown(f"**Drug:** {sig['drug_name']}")
    st.sidebar.markdown(f"**Event:** {sig['event_pt']}")
    st.sidebar.markdown(f"**Cases (a):** {sig['a']}")
    if st.sidebar.button("❌ Clear Selection"):
        st.session_state.selected_signal_idx = None
        st.rerun()

# ============ PAGE: OVERVIEW ============
if page == "Overview":
    st.title("🛡️ PV Signal Mini-Lab Overview")
    
    st.warning("⚠️ **DISCLAIMER:** Data is simulated. Does not imply clinical causality.")

    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Cases (N)", df_clean['case_id'].nunique())
    with kpi2:
        st.metric("Drug-Event Pairs", len(df_clean))
    with kpi3:
        methadone_cases = df_clean[df_clean['drug_name'] == 'Methadone']['case_id'].nunique()
        st.metric("Methadone Cases", methadone_cases)
    with kpi4:
        n_signals = len(df_signals[df_signals['signal_flag'] == True])
        st.metric("Potential Signals", n_signals)
        
    st.markdown("---")
    
    # FIGURES
    st.subheader("Dataset Demographics")
    
    def load_html_fig(filename):
        path = FIG_DIR / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    col1, col2 = st.columns(2)
    with col1:
        html_age = load_html_fig("fig_age_hist.html")
        if html_age:
            components.html(html_age, height=400)
        html_drugs = load_html_fig("fig_top_drugs.html")
        if html_drugs:
            components.html(html_drugs, height=400)
    with col2:
        html_sex = load_html_fig("fig_sex_dist.html")
        if html_sex:
            components.html(html_sex, height=400)
        html_events = load_html_fig("fig_top_events.html")
        if html_events:
            components.html(html_events, height=400)

    st.subheader("Co-occurrence Heatmap")
    html_heat = load_html_fig("fig_heatmap.html")
    if html_heat:
        components.html(html_heat, height=500)

# ============ PAGE: SIGNAL EXPLORER ============
elif page == "Signal Explorer":
    st.title("📡 Signal Detection Explorer")
    
    st.markdown("**Methodology:** PRR/ROR screening. Threshold: `PRR ≥ 2.0` AND `a ≥ 10`.")
    
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        min_a = st.slider("Min Cases (a)", 3, 50, 3)
    with col_f2:
        filter_drug = st.multiselect("Filter Drug", df_signals['drug_name'].unique())
    with col_f3:
        show_watchlist_only = st.checkbox("Show Watchlist Only", value=False)
        
    # Apply Filters
    filtered_signals = df_signals[df_signals['a'] >= min_a].copy()
    if filter_drug:
        filtered_signals = filtered_signals[filtered_signals['drug_name'].isin(filter_drug)]
    if show_watchlist_only:
        filtered_signals = filtered_signals[filtered_signals['is_watchlist'] == True]
    
    # Reset index
    filtered_signals = filtered_signals.reset_index(drop=True)
    
    if len(filtered_signals) > 0:
        # Create unified display table
        display_df = filtered_signals[['drug_name', 'event_pt', 'a', 'b', 'c', 'd', 'PRR', 'ROR', 'is_watchlist', 'signal_flag']].copy()
        display_df.columns = ['Drug', 'Event', 'a', 'b', 'c', 'd', 'PRR', 'ROR', 'Watchlist', 'Signal']
        display_df['PRR'] = display_df['PRR'].round(2)
        display_df['ROR'] = display_df['ROR'].round(2)
        display_df['Watchlist'] = display_df['Watchlist'].apply(lambda x: '✅' if x else '❌')
        display_df['Signal'] = display_df['Signal'].apply(lambda x: '🚩' if x else '➖')
        
        # Add selection column
        display_df.insert(0, 'Select', False)
        
        st.markdown("### Signal Detection Results")
        st.caption(f"Showing {len(display_df)} signals. Click checkbox to select for Case Review.")
        
        # Interactive table with selection
        edited_df = st.data_editor(
            display_df,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", default=False),
                "Drug": st.column_config.TextColumn("Drug"),
                "Event": st.column_config.TextColumn("Event"),
                "a": st.column_config.NumberColumn("a", help="Cases with Drug AND Event"),
                "b": st.column_config.NumberColumn("b", help="Cases with Drug but NOT Event"),
                "c": st.column_config.NumberColumn("c", help="Cases with Event but NOT Drug"),
                "d": st.column_config.NumberColumn("d", help="Cases with neither"),
                "PRR": st.column_config.NumberColumn("PRR", help="Proportional Reporting Ratio"),
                "ROR": st.column_config.NumberColumn("ROR", help="Reporting Odds Ratio"),
                "Watchlist": st.column_config.TextColumn("Watchlist", help="Event on priority watchlist?"),
                "Signal": st.column_config.TextColumn("Signal", help="Meets PRR≥2.0 AND a≥10?"),
            },
            disabled=['Drug', 'Event', 'a', 'b', 'c', 'd', 'PRR', 'ROR', 'Watchlist', 'Signal'],
            hide_index=True,
            use_container_width=True
        )
        
        # Handle selection
        selected_rows = edited_df[edited_df['Select'] == True]
        if len(selected_rows) > 0:
            selected_idx = selected_rows.index[0]
            selected_row = filtered_signals.iloc[selected_idx]
            
            st.session_state.selected_signal_idx = selected_idx
            
            st.success(f"✅ Selected: **{selected_row['drug_name']} + {selected_row['event_pt']}** | Go to 'Case Review' in sidebar.")
        
        st.markdown("---")
        
        # Legend
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1:
            st.caption("🚩 = Signal detected (PRR≥2.0 AND a≥10)")
            st.caption("➖ = Below threshold")
        with col_leg2:
            st.caption("✅ = On Watchlist (priority event)")
            st.caption("❌ = Not on Watchlist")
        
        # Download
        csv = filtered_signals.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "signals.csv", "text/csv")
    else:
        st.warning("No signals match filters. Adjust criteria.")

# ============ PAGE: CASE REVIEW ============
elif page == "Case Review":
    st.title("🩺 Case Review")
    
    # Check if signal was selected
    if st.session_state.selected_signal_idx is not None:
        sig = df_signals.iloc[st.session_state.selected_signal_idx]
        st.info(f"📌 Reviewing cases for: **{sig['drug_name']} + {sig['event_pt']}**")
        
        # Get matching cases
        matching_cases = df_clean[
            (df_clean['drug_name'] == sig['drug_name']) &
            (df_clean['event_pt'] == sig['event_pt'])
        ]['case_id'].unique().tolist()
        
        st.markdown(f"**{len(matching_cases)} case(s)** with this drug-event combination")
        
        # Case selector from matching
        selected_case = st.selectbox("Select Case ID", matching_cases)
    else:
        st.markdown("*No signal selected. Choose a signal in 'Signal Explorer' first, or browse all cases below.*")
        all_cases = sorted(df_clean['case_id'].unique())
        selected_case = st.selectbox("Select Case ID", all_cases)
    
    if selected_case:
        case_data = df_clean[df_clean['case_id'] == selected_case]
        first_row = case_data.iloc[0]
        
        st.markdown("---")
        st.markdown("### Patient Demographics")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Age", first_row['age'])
        c2.metric("Sex", first_row['sex'])
        c3.metric("Reporter", first_row['reporter_type'])
        c4.metric("Serious?", first_row['serious'])
        
        st.markdown("### Drugs")
        unique_drugs = case_data[['drug_name', 'role_cod', 'indication']].drop_duplicates()
        st.table(unique_drugs)
        
        st.markdown("### Events")
        unique_events = case_data[['event_pt']].drop_duplicates()
        st.table(unique_events)
        
        st.info("**Medical Officer Comment:** [Placeholder for assessment]")
