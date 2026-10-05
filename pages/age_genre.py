import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure utils can be imported
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data_loader import (
    get_age_genre_analysis,
    inject_custom_css,
    get_plotly_layout
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("👥 Age Cohort × Genre Interaction Patterns")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Cross-tabulated mining of demographic age cohorts against movie genre consumption volumes, rating leniency, and highest-rated preferences."
    "</p>",
    unsafe_allow_html=True
)

with st.spinner("Analyzing demographic genre intersections..."):
    age_data = get_age_genre_analysis()

# SECTION 1: Heatmap (Age Group x Genre Average Rating)
st.subheader("1. Age Group × Genre Rating Heatmap")

heatmap_df = age_data["genre_age_rating"].reindex([
    "Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"
])

col_h1, col_h2 = st.columns([2.2, 1])

with col_h1:
    fig_heatmap = px.imshow(
        heatmap_df,
        labels=dict(x="Movie Genre", y="Age Cohort", color="Average Rating"),
        x=heatmap_df.columns,
        y=heatmap_df.index,
        color_continuous_scale="Viridis",
        aspect="auto",
        text_auto=".2f",
        title="Average Movie Rating by Age Group and Genre"
    )
    fig_heatmap.update_layout(get_plotly_layout(dark_mode, height=440))
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col_h2:
    st.markdown("""
    <div class="takeaway-box" style="margin-top: 10px;">
        <div class="takeaway-header">Heatmap Observations</div>
        <div class="takeaway-text">
            <b>Universal Critical Consensus:</b><br>
            • <b>Film-Noir</b> achieves top ratings across almost every demographic cohort, peaking at <b>4.19</b> in the 56+ bracket.<br><br>
            • <b>Documentaries</b> show strong consistency (3.71 to 4.01), with older cohorts appreciating non-fiction more.<br><br>
            • <b>Horror</b> consistently receives the lowest average ratings across all generations (3.11 in Under 18 to 3.26 in 56+).<br><br>
            • <b>Animation</b> receives its highest average praise from viewers aged <b>Under 18 (3.70)</b> and <b>56+ (3.74)</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

# SECTION 2: Highest Rated Genre per Age Bracket
st.subheader("2. Highest-Rated Genre by Age Bracket")

max_genres = pd.DataFrame({
    "Age Cohort": heatmap_df.index,
    "Highest-Rated Genre": heatmap_df.idxmax(axis=1).values,
    "Peak Average Rating": heatmap_df.max(axis=1).round(2).values
})

col_m1, col_m2 = st.columns([1.2, 1.8])

with col_m1:
    st.dataframe(max_genres, use_container_width=True, hide_index=True)

with col_m2:
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">Consistent Peak Preference</div>
        <div class="analysis-subtitle">Direct verification from DMT.ipynb Cell 22</div>
        <div style="font-size:0.9rem; line-height:1.6;">
            Across virtually every generation—from young adults (18-24) to mature seniors (56+)—<b>Film-Noir</b> emerges as the undisputed highest-rated genre.
            This demonstrates that while viewership is small, viewer satisfaction and rating commitment in classic stylized crime drama is exceptionally durable across decades of age difference.
        </div>
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: Most Watched / Rated Genres per Age Bracket
st.subheader("3. Most Watched Genres by Demographic Cohort (Consumption Volume)")

view_mode = st.radio("Select View:", ["Top 3 Most Rated Genres", "Top 5 Most Rated Genres"], horizontal=True)

if view_mode == "Top 3 Most Rated Genres":
    top_data = age_data["top3_genres_by_age"]
    chart_title = "Top 3 Most Rated Movie Genres for Each Age Group"
else:
    top_data = age_data["top5_genres_by_age"]
    chart_title = "Top 5 Most Rated Movie Genres for Each Age Group"

# Create grouped/faceted visualization
fig_top_genres = px.bar(
    top_data,
    x="Genre",
    y="Movie_Count",
    color="Age_Group",
    barmode="group",
    labels={"Movie_Count": "Number of Ratings Given", "Genre": "Genre"},
    title=chart_title,
    color_discrete_sequence=px.colors.qualitative.Prism
)
fig_top_genres.update_layout(get_plotly_layout(dark_mode, height=440))
st.plotly_chart(fig_top_genres, use_container_width=True)

# Demographics Breakdown Table
st.subheader("4. Detailed Cross-Cohort Preferences Table")

pivot_counts = age_data["age_genre_count"].pivot(
    index="Age_Group", columns="Genre", values="Movie_Count"
).reindex(["Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"]).fillna(0).astype(int)

st.dataframe(pivot_counts, use_container_width=True)

st.markdown("""
<div class="takeaway-box">
    <div class="takeaway-header">Key Demographic Finding</div>
    <div class="takeaway-text">
        Regardless of age bracket, <b>Comedy</b>, <b>Drama</b>, and <b>Action</b> invariably capture the top 3 spots in volume across every single demographic cohort.
        The primary generational shifts occur in secondary genres: younger viewers (Under 18 and 18-24) exhibit elevated proportions of <b>Sci-Fi</b> and <b>Animation</b>,
        whereas older viewers (45-49, 50-55, 56+) display significantly higher engagement in <b>Thriller</b>, <b>Romance</b>, and <b>War</b>.
    </div>
</div>
""", unsafe_allow_html=True)
