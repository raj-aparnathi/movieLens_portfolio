import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure utils and pages can be imported regardless of execution path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.data_loader import (
    load_raw_data,
    get_kpi_summary,
    get_genre_analytics,
    inject_custom_css,
    get_plotly_layout
)

st.set_page_config(
    page_title="MovieLens 1M | Data Mining Portfolio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Branding and Global Settings
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-title">
        <span style="background: linear-gradient(135deg, #4F46E5, #06B6D4); color: white; padding: 4px 8px; border-radius: 8px; font-size: 0.85rem; font-weight: 800;">ML</span>
        MovieLens 1M
    </div>
    <div class="sidebar-subtitle">Mining Movie Genre & Rating Patterns</div>
</div>
""", unsafe_allow_html=True)

# Theme Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", False))
st.session_state["dark_mode"] = dark_mode

# Inject Theme CSS
inject_custom_css(dark_mode)

# Load cached data for sidebar live status
try:
    kpis = get_kpi_summary()
    st.sidebar.markdown(f"""
    <div style="background: {'#1E293B' if dark_mode else '#F1F5F9'}; padding: 12px; border-radius: 10px; margin-top: 10px; margin-bottom: 20px; font-size: 0.8rem; border: 1px solid {'rgba(255,255,255,0.06)' if dark_mode else 'rgba(0,0,0,0.05)'};">
        <div style="font-weight: 700; color: #4F46E5; margin-bottom: 6px; text-transform: uppercase; font-size: 0.725rem; letter-spacing: 0.05em;">Repository Status</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: {'#94A3B8' if dark_mode else '#64748B'};">Total Ratings:</span>
            <b>{kpis['total_ratings']:,}</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: {'#94A3B8' if dark_mode else '#64748B'};">Users:</span>
            <b>{kpis['total_users']:,}</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: {'#94A3B8' if dark_mode else '#64748B'};">Catalog Movies:</span>
            <b>{kpis['total_movies']:,}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: {'#94A3B8' if dark_mode else '#64748B'};">Distinct Genres:</span>
            <b>{kpis['distinct_genres_count']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
except Exception:
    kpis = None

# ====================================================================
# PAGE 1: OVERVIEW VIEW FUNCTION
# ====================================================================
def render_overview():
    # Hero Section
    st.markdown("""
    <div style="margin-bottom: 28px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="badge badge-emerald">DMT PORTFOLIO</span>
            <span class="badge">GROUPLENS 1M BENCHMARK</span>
            <span class="badge badge-amber">ACADEMIC RESEARCH</span>
        </div>
        <h1 style="font-size: 2.35rem; margin-bottom: 8px; line-height: 1.2;">
            MovieLens 1M — Mining Movie Genre & Rating Patterns
        </h1>
        <p style="font-size: 1.05rem; max-width: 950px; line-height: 1.6; margin-bottom: 16px;">
            An empirical data mining portfolio exploring audience behavior, commercial volume versus critical acclaim, 
            combinatorial genre pairs, Apriori frequent itemset rules, and unsupervised latent taste segments using PCA.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic KPI Cards (Computed directly from real dataset)
    if kpis:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Users</div>
                <div class="kpi-value">{kpis['total_users']:,}</div>
                <div class="kpi-subtext">Demographically profiled viewers</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Catalog Movies</div>
                <div class="kpi-value">{kpis['total_movies']:,}</div>
                <div class="kpi-subtext">Across {kpis['distinct_genres_count']} distinct genres</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Ratings</div>
                <div class="kpi-value">{kpis['total_ratings']:,}</div>
                <div class="kpi-subtext">5-star scale (Mode: {kpis['mode_rating']})</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Average Rating</div>
                <div class="kpi-value">{kpis['mean_rating']:.2f}</div>
                <div class="kpi-subtext">Global benchmark score</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Core Charts Section
    movies, ratings, users = load_raw_data()
    genre_data = get_genre_analytics()

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        # Rating Distribution
        rating_counts = ratings["Rating"].value_counts().sort_index()
        fig_r = go.Figure(
            data=[
                go.Bar(
                    x=[f"{r} ★" for r in rating_counts.index],
                    y=rating_counts.values,
                    text=[f"{v/len(ratings)*100:.1f}%" for v in rating_counts.values],
                    textposition="outside",
                    marker=dict(
                        color=["#F87171", "#FB923C", "#FBBF24", "#6366F1", "#10B981"]
                    )
                )
            ]
        )
        fig_r.update_layout(
            get_plotly_layout(dark_mode, height=360),
            title="Rating Distribution (1,000,209 Ratings)",
            xaxis_title="Rating (Stars)",
            yaxis_title="Count of Ratings",
            yaxis=dict(range=[0, max(rating_counts.values) * 1.15])
        )
        st.plotly_chart(fig_r, use_container_width=True)

    with col_c2:
        # Top 10 Most Rated Genres
        top10_genres = genre_data["rating_count"].head(10)
        fig_g = px.bar(
            x=top10_genres.values[::-1],
            y=top10_genres.index[::-1],
            orientation="h",
            labels={"x": "Total Ratings Count", "y": "Genre"},
            title="Top 10 Most-Rated Genres (Audience Volume)",
            color=top10_genres.values[::-1],
            color_continuous_scale="Purples"
        )
        fig_g.update_layout(get_plotly_layout(dark_mode, height=360))
        fig_g.update_coloraxes(showscale=False)
        st.plotly_chart(fig_g, use_container_width=True)

    # Executive Analytical Callouts
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">Core Empirical Discoveries at a Glance</div>
        <div class="analysis-subtitle">Verified findings extracted directly from DMT.ipynb data mining execution</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 14px;">
            <div class="takeaway-box" style="margin: 0;">
                <div class="takeaway-header">Positive Skew & Mode</div>
                <div class="takeaway-text">
                    <b>Rating 4</b> is the most common score (34.9% of ratings). Together, 4 and 5 stars represent <b>57.5%</b> of all feedback, indicating strong positive viewer engagement.
                </div>
            </div>
            <div class="takeaway-box" style="margin: 0;">
                <div class="takeaway-header">Commercial Volume vs. Quality</div>
                <div class="takeaway-text">
                    <b>Comedy</b> (356K) and <b>Drama</b> (354K) dominate viewership. In contrast, <b>Film-Noir</b> holds the highest average rating at <b>4.08</b> (with 34.6% 5-star ratings).
                </div>
            </div>
            <div class="takeaway-box" style="margin: 0;">
                <div class="takeaway-header">Apriori Genre Association</div>
                <div class="takeaway-text">
                    Mining frequent itemsets identified <b>Children's → Animation</b> with a peak <b>Lift of 12.38</b> and <b>83.2% confidence</b>, reflecting heavy industrial co-tagging.
                </div>
            </div>
            <div class="takeaway-box" style="margin: 0;">
                <div class="takeaway-header">Demographic Preferences & PCA</div>
                <div class="takeaway-text">
                    Viewers aged <b>56+</b> exhibit the highest rating leniency (mean 3.77). 2D PCA reduces taste profiles into breadth of consumption vs spectacle vs narrative drama.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Guide / Index
    st.markdown("""
    <div style="margin-top: 24px; padding: 20px; border-radius: 12px; background: rgba(79, 70, 229, 0.04); border: 1px dashed rgba(79, 70, 229, 0.3);">
        <h4 style="margin-bottom: 8px; color: #4F46E5 !important;">Explore the Analytical Portfolio</h4>
        <p style="font-size: 0.9rem; margin-bottom: 12px;">Use the modern sidebar navigation to inspect individual research modules:</p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <span class="badge">🗃️ Dataset & Schema</span>
            <span class="badge">📊 Exploratory Analysis</span>
            <span class="badge">🔗 Association Rules (Apriori)</span>
            <span class="badge">🧬 PCA Projection</span>
            <span class="badge">👥 Age & Genre Analysis</span>
            <span class="badge">💡 Key Findings</span>
            <span class="badge">⚙️ Methodology Pipeline</span>
            <span class="badge">ℹ️ About Project & Scope</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ====================================================================
# STREAMLIT MULTI-PAGE NAVIGATION SETUP
# ====================================================================
pages_dir = current_dir / "pages"

overview_p = st.Page(render_overview, title="Overview", icon=":material/dashboard:", default=True)
dataset_p = st.Page(str(pages_dir / "dataset.py"), title="Dataset & Schema", icon=":material/table_chart:")
eda_p = st.Page(str(pages_dir / "eda.py"), title="Exploration (EDA)", icon=":material/analytics:")
rules_p = st.Page(str(pages_dir / "association_rules.py"), title="Association Rules", icon=":material/hub:")
pca_p = st.Page(str(pages_dir / "pca.py"), title="PCA Projection", icon=":material/scatter_plot:")
age_genre_p = st.Page(str(pages_dir / "age_genre.py"), title="Age & Genre", icon=":material/groups:")
findings_p = st.Page(str(pages_dir / "findings.py"), title="Key Findings", icon=":material/lightbulb:")
methodology_p = st.Page(str(pages_dir / "methodology.py"), title="Methodology", icon=":material/account_tree:")
about_p = st.Page(str(pages_dir / "about.py"), title="About Project", icon=":material/info:")

nav = st.navigation({
    "Dashboard": [overview_p, dataset_p, eda_p],
    "Mining Models": [rules_p, pca_p, age_genre_p],
    "Synthesis & Docs": [findings_p, methodology_p, about_p]
})

nav.run()

# Unified Footer
st.sidebar.markdown("""
<div class="footer-bar">
    <div style="font-weight: 600; color: #4F46E5;">MovieLens 1M Analytics Suite</div>
    <div>Data Mining Techniques (DMT)</div>
    <div style="font-size: 0.725rem; margin-top: 4px;">GroupLens Research © 2000</div>
</div>
""", unsafe_allow_html=True)
