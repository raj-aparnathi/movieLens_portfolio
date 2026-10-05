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
    load_raw_data,
    get_kpi_summary,
    get_genre_analytics,
    get_genre_pairs_analysis,
    get_age_genre_analysis,
    inject_custom_css,
    get_plotly_layout
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("📊 Exploratory Data Mining Analysis")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Empirical exploratory analysis revealing rating distributions, volume by genre, quality benchmarks, 5-star concentrations, and co-occurring genre pair dynamics."
    "</p>",
    unsafe_allow_html=True
)

with st.spinner("Compiling EDA metrics from DMT pipeline..."):
    movies, ratings, users = load_raw_data()
    kpis = get_kpi_summary()
    genre_data = get_genre_analytics()
    genre_pairs_count, pair_ratings_df, reliable_pairs = get_genre_pairs_analysis()
    age_data = get_age_genre_analysis()

# SECTION 1: Rating Distribution
st.subheader("1. Global Rating Distribution & Skewness")

col_r1, col_r2 = st.columns([2, 1])

with col_r1:
    rating_counts = ratings["Rating"].value_counts().sort_index()
    rating_pcts = (rating_counts / len(ratings) * 100).round(2)
    
    fig_ratings = go.Figure(
        data=[
            go.Bar(
                x=[f"{r} Stars" for r in rating_counts.index],
                y=rating_counts.values,
                text=[f"{v:,} ({p}%)" for v, p in zip(rating_counts.values, rating_pcts.values)],
                textposition="outside",
                marker=dict(
                    color=["#EF4444", "#F97316", "#FBBF24", "#4F46E5", "#10B981"],
                    line=dict(color="rgba(0,0,0,0.1)", width=1)
                )
            )
        ]
    )
    fig_ratings.update_layout(
        get_plotly_layout(dark_mode, height=360),
        title="Distribution of 1,000,209 Movie Ratings",
        xaxis_title="Rating (Stars)",
        yaxis_title="Count of Ratings",
        yaxis=dict(range=[0, max(rating_counts.values) * 1.18])
    )
    st.plotly_chart(fig_ratings, use_container_width=True)

with col_r2:
    st.markdown(f"""
    <div class="takeaway-box" style="margin-top: 10px;">
        <div class="takeaway-header">Empirical Takeaway</div>
        <div class="takeaway-text">
            <b>Positive Skew:</b> Ratings display a clear left-skewed distribution towards favorable scores.<br><br>
            • <b>Mode:</b> 4 Stars represents <b>{rating_pcts[4]}%</b> of all logged ratings (348,971 entries).<br>
            • <b>Positive Sentiment:</b> 4 & 5 stars together account for <b>{(rating_pcts[4] + rating_pcts[5]):.1f}%</b> of the dataset.<br>
            • <b>Mean Rating:</b> Overall benchmark across all titles is <b>{kpis['mean_rating']:.2f} / 5.00</b>.<br>
            • <b>Lowest Frequency:</b> 1 Star represents only <b>{rating_pcts[1]}%</b> of user feedback.
        </div>
    </div>
    """, unsafe_allow_html=True)

# SECTION 2: Genre Volume vs Quality (Average Rating)
st.subheader("2. Genre Volume vs Quality Disparity")

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_volume = px.bar(
        x=genre_data["rating_count"].values[::-1],
        y=genre_data["rating_count"].index[::-1],
        orientation="h",
        labels={"x": "Total Ratings Count", "y": "Genre"},
        title="Most Rated Movie Genres (Market Volume)",
        color=genre_data["rating_count"].values[::-1],
        color_continuous_scale="Purples"
    )
    fig_volume.update_layout(get_plotly_layout(dark_mode, height=480))
    fig_volume.update_coloraxes(showscale=False)
    st.plotly_chart(fig_volume, use_container_width=True)

with col_g2:
    fig_quality = px.bar(
        x=genre_data["avg_rating"].values[::-1],
        y=genre_data["avg_rating"].index[::-1],
        orientation="h",
        labels={"x": "Average Rating (Stars)", "y": "Genre"},
        title="Highest Average Rated Genres (Viewer Acclaim)",
        color=genre_data["avg_rating"].values[::-1],
        color_continuous_scale="Teal"
    )
    fig_quality.update_layout(
        get_plotly_layout(dark_mode, height=480),
        xaxis=dict(range=[2.8, 4.3])
    )
    fig_quality.update_coloraxes(showscale=False)
    st.plotly_chart(fig_quality, use_container_width=True)

# Analytical Callout for Genre Disparity
st.markdown("""
<div class="analysis-card">
    <div class="analysis-title">Critical Data Mining Insight: The Volume vs. Acclaim Paradox</div>
    <div class="analysis-subtitle">Comparing mass audience engagement against critical rating consensus</div>
    <div style="font-size:0.925rem; line-height:1.65;">
        While <b>Comedy</b> (356,580 ratings) and <b>Drama</b> (354,529 ratings) dominate over 70% of total engagement, their average ratings remain centered around <b>3.52</b> and <b>3.77</b>.
        In contrast, niche genres such as <b>Film-Noir</b> (mean <b>4.08</b>) and <b>Documentary</b> (mean <b>3.93</b>) command dramatically higher critical scores despite having less than 5% of the total rating volume.
        This illustrates standard self-selection bias: viewers who deliberately seek out Film-Noir and Documentaries exhibit higher baseline appreciation and selectivity.
    </div>
</div>
""", unsafe_allow_html=True)

# SECTION 3: 5-Star Rating Ratio & Age Group Averages
st.subheader("3. 5-Star Rating Concentration & Generational Leniency")

col_s1, col_s2 = st.columns([1, 1])

with col_s1:
    five_star_series = genre_data["five_star_pct"].sort_values(ascending=True)
    fig_5star = px.bar(
        x=five_star_series.values,
        y=five_star_series.index,
        orientation="h",
        labels={"x": "% of Ratings That Are 5 Stars", "y": "Genre"},
        title="5-Star Rating Proportion by Genre",
        color=five_star_series.values,
        color_continuous_scale="Viridis"
    )
    fig_5star.update_layout(get_plotly_layout(dark_mode, height=440))
    fig_5star.update_coloraxes(showscale=False)
    st.plotly_chart(fig_5star, use_container_width=True)

with col_s2:
    age_means = age_data["age_avg_rating"].reindex([
        "Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"
    ])
    fig_age_avg = px.bar(
        x=age_means.index,
        y=age_means.values,
        labels={"x": "Demographic Cohort", "y": "Average Rating Given"},
        title="Generational Rating Leniency (Mean Rating by Age)",
        color=age_means.values,
        color_continuous_scale="Inferno",
        text=[f"{v:.2f}" for v in age_means.values]
    )
    fig_age_avg.update_layout(
        get_plotly_layout(dark_mode, height=440),
        yaxis=dict(range=[3.4, 3.9])
    )
    fig_age_avg.update_coloraxes(showscale=False)
    fig_age_avg.update_traces(textposition="outside")
    st.plotly_chart(fig_age_avg, use_container_width=True)

# SECTION 4: Co-occurring Genre Combinations & Reliable Pairs
st.subheader("4. Co-occurring Genre Pairs & Synergies")

col_p1, col_p2 = st.columns(2)

with col_p1:
    top_common_pairs = genre_pairs_count.head(12)
    labels_common = [f"{p[0]} + {p[1]}" for p in top_common_pairs.index]
    fig_pairs = px.bar(
        x=top_common_pairs.values[::-1],
        y=labels_common[::-1],
        orientation="h",
        labels={"x": "Number of Movies Produced", "y": "Genre Pair"},
        title="Top 12 Most Common Movie Genre Combinations",
        color=top_common_pairs.values[::-1],
        color_continuous_scale="Blues"
    )
    fig_pairs.update_layout(get_plotly_layout(dark_mode, height=420))
    fig_pairs.update_coloraxes(showscale=False)
    st.plotly_chart(fig_pairs, use_container_width=True)

with col_p2:
    top_reliable = reliable_pairs.head(12)
    fig_rel = px.bar(
        x=top_reliable["mean"].values[::-1],
        y=top_reliable.index[::-1],
        orientation="h",
        labels={"x": "Average Rating (Stars)", "y": "Genre Combination"},
        title="Top Rated Genre Pairs (Filtered: ≥ 500 Ratings)",
        color=top_reliable["mean"].values[::-1],
        color_continuous_scale="Teal"
    )
    fig_rel.update_layout(
        get_plotly_layout(dark_mode, height=420),
        xaxis=dict(range=[3.8, 4.25])
    )
    fig_rel.update_coloraxes(showscale=False)
    st.plotly_chart(fig_rel, use_container_width=True)

st.markdown(f"""
<div class="takeaway-box">
    <div class="takeaway-header">Genre Pair Synergy Finding</div>
    <div class="takeaway-text">
        While <b>Drama + Romance</b> (231 movies) and <b>Comedy + Romance</b> (150 movies) are the most commercially produced multi-genre combinations in the dataset,
        the critically highest-rated pair among statistically reliable combinations (≥500 ratings) is <b>Film-Noir + Mystery</b> with an average rating of <b>{top_reliable['mean'].iloc[0]:.2f}</b>, followed by <b>Film-Noir + Romance</b> ({top_reliable['mean'].iloc[1]:.2f}) and <b>Film-Noir + Thriller</b> ({top_reliable['mean'].iloc[2]:.2f}).
    </div>
</div>
""", unsafe_allow_html=True)
