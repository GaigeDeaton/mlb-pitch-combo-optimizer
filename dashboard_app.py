# Streamlit dashboard for the MLB Pitch Combo Optimizer.
# Run this file with: streamlit run dashboard_app.py
import streamlit as st
import pandas as pd

# Set the browser tab title and page layout
st.set_page_config(page_title="MLB Pitch Combo Optimizer", layout="wide")

# Load the same clean, name-mapped CSV we built for Tableau -- it works
# just as well here, no changes needed
df = pd.read_csv("dashboard_combo_data.csv")

st.title("MLB Pitch Combo Optimizer")
st.caption("Find each pitcher's optimal 3-pitch combination by batter type and handedness.")

# Sidebar dropdown to pick a pitcher -- sorted alphabetically for easy searching
pitcher_list = sorted(df['pitcher_name'].unique())
selected_pitcher = st.sidebar.selectbox("Select a pitcher", pitcher_list)

# Filter the data down to just that pitcher's 12 rows (6 archetypes x 2 handedness)
pitcher_data = df[df['pitcher_name'] == selected_pitcher]

st.subheader(f"{selected_pitcher}'s optimal combos")
st.dataframe(
    pitcher_data[['batter_side', 'archetype_name', 'combo_display', 'run_value_score']],
    hide_index=True,
    use_container_width=True
)