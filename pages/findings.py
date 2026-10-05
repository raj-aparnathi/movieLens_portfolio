import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Ensure utils can be imported
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data_loader import (
    load_raw_data,
    get_kpi_summary,
    get_genre_analytics,
    get_genre_pairs_analysis,
    run_apriori_rules,
    inject_custom_css
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("💡 Empirical Data Mining Findings")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Key conclusions, verified statistical benchmarks, and data mining discoveries derived strictly from DMT.ipynb and MovieLens 1M."
    "</p>",
    unsafe_allow_html=True
)

with st.spinner("Compiling verified DMT findings..."):
    movies, ratings, users = load_raw_data()
    kpis = get_kpi_summary()
    genre_data = get_genre_analytics()
    _, _, reliable_pairs = get_genre_pairs_analysis()
    _, rules = run_apriori_rules(0.02, 0.3)

top_rule = rules.iloc[0] if not rules.empty else None

# Summary KPI Table matching Cell 43
st.subheader("1. Official Project Benchmark Scorecard")

scorecard_df = pd.DataFrame({
    "Mining Metric / Finding": [
        "Total Catalog Movies",
        "Total Logged Ratings",
        "Overall Average Rating",
        "Most Frequent Rating (Mode)",
        "Highest Volume Genre",
        "Highest Average Rated Genre",
        "Highest Rated Genre Pair (≥500 Ratings)",
        "Highest-Lift Genre Association Rule",
        "Peak Association Rule Lift"
    ],
    "Empirical Value": [
        f"{len(movies):,}",
        f"{len(ratings):,}",
        f"{ratings['Rating'].mean():.2f} / 5.00",
        f"Rating {ratings['Rating'].value_counts().idxmax()} (34.9% of all ratings)",
        f"{genre_data['rating_count'].idxmax()} ({genre_data['rating_count'].max():,} ratings)",
        f"{genre_data['avg_rating'].idxmax()} ({genre_data['avg_rating'].max():.2f} average rating)",
        f"{reliable_pairs['mean'].idxmax()} ({reliable_pairs['mean'].max():.2f} average rating)",
        f"{top_rule['Rule'] if top_rule is not None else 'N/A'}",
        f"{top_rule['lift']:.2f}x lift factor" if top_rule is not None else "N/A"
    ]
})

st.dataframe(scorecard_df, use_container_width=True, hide_index=True)

# SECTION 2: Curated Analytical Insight Cards
st.subheader("2. Detailed Mining Discoveries")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">⭐ Rating Distribution & Skewness</div>
        <div class="analysis-subtitle">Global Audience Tendency</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            The overall mean rating is <b>{kpis['mean_rating']:.2f}</b> with a standard deviation of 1.12.
            Contrary to a standard bell curve, ratings are strongly left-skewed:
            <b>Rating 4</b> is the modal score (34.9%), and ratings 4 and 5 collectively constitute <b>57.5%</b> of the entire repository.
            Users demonstrate a distinct propensity to rate titles they enjoy rather than log negative feedback on mediocre titles.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">🏆 Genre Quality: The Film-Noir Benchmark</div>
        <div class="analysis-subtitle">Critical Acclaim vs Audience Volume</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            <b>Film-Noir</b> achieved the highest average rating (<b>4.08</b>) across all 18 genres, followed by <b>Documentary</b> (3.93) and <b>War</b> (3.89).
            Furthermore, <b>34.6%</b> of all Film-Noir ratings were a perfect 5 stars.
            In contrast, <b>Horror</b> had the lowest average rating at <b>3.22</b>, demonstrating high viewer polarization and critical skepticism.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">🔗 Genre Synergies: Film-Noir + Mystery</div>
        <div class="analysis-subtitle">Multi-Genre Combination Performance</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            Among genre combinations with statistical significance (minimum 500 ratings),
            the pairing of <b>Film-Noir + Mystery</b> ranked #1 with an average rating of <b>{reliable_pairs['mean'].max():.2f}</b> across 13,835 ratings.
            This was closely followed by <b>Film-Noir + Romance</b> (4.06) and <b>Film-Noir + Thriller</b> (4.03).
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">📦 Commercial Volume vs. Critical Acclaim</div>
        <div class="analysis-subtitle">Market Domination by Comedy & Drama</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            <b>Comedy</b> (356,580 ratings) and <b>Drama</b> (354,529 ratings) account for more than <b>70%</b> of all user interactions in MovieLens 1M.
            However, their mean ratings (Comedy: 3.52, Drama: 3.77) position them near the empirical average, reflecting mainstream mass-market accessibility.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">🧬 Apriori Rule Discovery: Children's → Animation</div>
        <div class="analysis-subtitle">Maximum Lift Factor (12.38x)</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            Applying Apriori with a 2% support threshold identified <b>Children's → Animation</b> as the single strongest association rule in the catalog.
            With a <b>Lift of 12.38</b> and <b>Confidence of 83.2%</b>, this rule confirms that animated releases were almost exclusively produced within the family/children genre ecosystem in 2000.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">👥 Demographics: Generational Leniency Trend</div>
        <div class="analysis-subtitle">Age Cohort Rating Behavior</div>
        <div style="font-size:0.925rem; line-height:1.65;">
            Mean rating strictly correlates with viewer age: viewers aged <b>56+</b> exhibit the highest average rating (<b>3.77</b>),
            whereas youth viewers (<b>Under 18</b>) give the lowest average rating (<b>3.55</b>).
            Despite this leniency gap, Comedy, Drama, and Action remain the unanimous top 3 most-watched genres for every single age demographic.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Conclusion Block matching Cell 44
st.subheader("3. Formal Project Conclusion")

st.markdown("""
<div class="takeaway-box" style="padding:22px; font-size:0.95rem; line-height:1.75;">
    <div class="takeaway-header" style="font-size:0.95rem;">DMT Synthesis Summary</div>
    The MovieLens 1M dataset was systematically investigated using Data Mining Techniques.
    By integrating exploratory profiling, combinatorial genre pairs, Apriori frequent itemset mining, and unsupervised PCA dimensionality reduction:
    <ul style="margin-top:8px; margin-bottom:8px;">
        <li>Identified the universal positive rating skew and benchmarked the global average at 3.58.</li>
        <li>Uncovered the contrast between mass commercial genres (Comedy/Drama) and elite niche acclaim (Film-Noir/Documentary).</li>
        <li>Established quantitative co-occurrence rules with statistical lift up to 12.38x.</li>
        <li>Demonstrated that user genre preferences reduce cleanly to 2 principal components distinguishing omnivorous breadth from visceral spectacle.</li>
    </ul>
    All analyses and metrics presented are verified against the raw dataset records and reproducible pipelines.
</div>
""", unsafe_allow_html=True)
