# Streamlit dashboard for the MLB Pitch Combo Optimizer.
# Run this file with: streamlit run dashboard_app.py
import streamlit as st
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="MLB Pitch Combo Optimizer", layout="wide")

# Small custom CSS for red/white accent styling beyond what the
# .streamlit/config.toml theme alone covers (title color, section dividers)
st.markdown("""
    <style>
    h1 { color: #C8102E; }
    hr { border-top: 2px solid #C8102E; }
    </style>
""", unsafe_allow_html=True)

# --- Load data ---
df = pd.read_csv("dashboard_combo_data.csv")

ARCHETYPE_INFO = {
    "Pure Slap Hitter": "Puts nearly every pitch in play, almost never strikes out (~14% K rate), but hits weakly (~85 mph avg exit velo, ~3% barrel rate).",
    "All-or-Nothing Power Hitter": "Elite power (highest barrel rate in the group) paired with heavy swing-and-miss (~31% K rate, ~35% whiff rate).",
    "Disciplined All-Rounder": "Most selective hitter of the group (lowest chase rate), with above-average power and contact quality.",
    "Free-Swinging Slugger": "Chases pitches out of the zone often (highest chase rate) and whiffs a lot, but still hits the ball hard when he connects.",
    "Complete Power Hitter": "The best blend of power and plate discipline -- highest exit velocity and hard-hit rate in the group.",
    "Contact-Over-Power Hitter": "Reliable bat-to-ball skills but limited power -- below-average exit velocity and barrel rate.",
}

PITCH_INFO = {
    "FF": "Four-Seam Fastball", "SI": "Sinker", "SL": "Slider",
    "CH": "Changeup", "ST": "Sweeper", "FC": "Cutter",
    "CU": "Curveball", "FS": "Splitter", "KC": "Knuckle Curve", "SV": "Slurve",
}

METHODOLOGY_INFO = [
    "**Data source:** 2026 season Statcast pitch-level data (Baseball Savant), refreshed via a daily automated pull.",
    "**Success metric:** Average run value per pitch (Statcast's delta_run_exp). Lower/more negative scores are better for the pitcher.",
    "**Batter archetypes:** 6 groups built via Gaussian Mixture Model clustering (soft/probabilistic, not hard-assigned) across 20 batter performance features.",
    "**Batter qualification:** Minimum 100 plate appearances required to be included in archetype clustering.",
    "**Pitcher arsenal qualification:** A pitch type must be thrown 100+ times this season to count as part of a pitcher's arsenal.",
    "**Combo scoring:** Weighted by each pitch's actual usage rate (not a simple average), so a pitcher's most-thrown pitch counts more than a rarely-used one.",
    "**Small-sample correction:** Empirical Bayes shrinkage applied at multiple levels (batter-by-pitch-category, pitcher-by-handedness, pitcher-by-archetype) to prevent thin samples from producing misleadingly extreme scores.",
]

# --- Title ---
st.title("MLB Pitch Combo Optimizer")
st.caption("Find the optimal 3-pitch combination by batter type and handedness.")
st.markdown("<hr>", unsafe_allow_html=True)

# --- Dynamic featured finding ---
# Background AND text color are both hardcoded here (rather than relying
# on the page theme) so this stays readable regardless of light/dark theme.
best_row = df.loc[df['run_value_score'].idxmin()]

st.markdown(f"""
    <div style="background-color:#C8102E; color:#FFFFFF;
                padding: 14px 18px; border-radius: 6px; margin-bottom: 16px;">
        <strong>🏆 Best matchup in the dataset:</strong>
        {best_row['pitcher_name']} vs. {best_row['batter_side']}
        {best_row['archetype_name']}s — {best_row['combo_display']}
        (Run Value Score: {best_row['run_value_score']:.4f})
    </div>
""", unsafe_allow_html=True)

# --- Layout ---
# Pitcher lookup now lives INSIDE main_col so it doesn't wait for the
# taller legend_col to finish -- this removes the blank-space gap.
main_col, legend_col = st.columns([3, 1])

with main_col:
    st.subheader("League-Wide Comparison")

    handedness_choice = st.radio(
        "Batter handedness",
        options=["Left-Handed Batter", "Right-Handed Batter"],
        horizontal=True,
    )

    archetype_choice = st.radio(
        "Batter archetype",
        options=sorted(df['archetype_name'].unique()),
        horizontal=True,
    )

    league_view = df[
        (df['batter_side'] == handedness_choice) &
        (df['archetype_name'] == archetype_choice)
    ].copy()

    league_view = league_view.sort_values('run_value_score', ascending=True)

    league_display = league_view[['pitcher_name', 'combo_display', 'run_value_score']].rename(columns={
        'pitcher_name': 'Pitcher Name',
        'combo_display': 'Combo Display',
        'run_value_score': 'Run Value Score',
    })

    st.dataframe(league_display, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Look Up a Specific Pitcher")

    # label_visibility="collapsed" hides the redundant text label while
    # keeping it for screen-reader accessibility
    pitcher_list = sorted(df['pitcher_name'].unique())
    selected_pitcher = st.selectbox(
        "Search for a pitcher",
        options=pitcher_list,
        index=None,
        placeholder="Start typing a name...",
        label_visibility="collapsed",
    )

    if selected_pitcher:
        pitcher_data = df[df['pitcher_name'] == selected_pitcher].copy()
        pitcher_data = pitcher_data.sort_values('run_value_score', ascending=True)

        pitcher_display = pitcher_data[['batter_side', 'archetype_name', 'combo_display', 'run_value_score']].rename(columns={
            'batter_side': 'Batter Side',
            'archetype_name': 'Archetype Name',
            'combo_display': 'Combo Display',
            'run_value_score': 'Run Value Score',
        })

        st.markdown(f"### {selected_pitcher}'s optimal combos")
        st.dataframe(pitcher_display, hide_index=True, use_container_width=True)
    else:
        st.info("Select a pitcher above to see their full combo breakdown.")

with legend_col:
    st.subheader("Archetype Key")
    for name, description in ARCHETYPE_INFO.items():
        st.markdown(f"**{name}**")
        st.caption(description)

    st.subheader("Pitch Type Key")
    for code, name in PITCH_INFO.items():
        st.markdown(f"**{code}** — {name}")

    st.subheader("Methodology & Parameters")
    st.caption(f"📅 Data current as of {df['data_as_of'].iloc[0]}")
    with st.expander("How these results were calculated"):
        for line in METHODOLOGY_INFO:
            st.markdown(f"- {line}")