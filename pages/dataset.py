import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Ensure utils can be imported
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data_loader import (
    load_raw_data,
    get_kpi_summary,
    inject_custom_css,
    get_plotly_layout
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("🗃️ Dataset Architecture & Schema")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Comprehensive inspection of the raw GroupLens MovieLens 1M benchmark dataset, its relational schemas, demographic encodings, and preprocessing pipelines."
    "</p>",
    unsafe_allow_html=True
)

# Load data
with st.spinner("Accessing verified MovieLens data files..."):
    movies, ratings, users = load_raw_data()
    kpis = get_kpi_summary()

# High-level Dataset Stats in KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Ratings Dataframe</div>
        <div class="kpi-value">{kpis['total_ratings']:,}</div>
        <div class="kpi-subtext">ratings.dat (25.6 MB)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Unique Users</div>
        <div class="kpi-value">{kpis['total_users']:,}</div>
        <div class="kpi-subtext">users.dat (140 KB)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Unique Movies</div>
        <div class="kpi-value">{kpis['total_movies']:,}</div>
        <div class="kpi-subtext">movies.dat (175 KB)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Distinct Genres</div>
        <div class="kpi-value">{kpis['distinct_genres_count']}</div>
        <div class="kpi-subtext">Pipe-delimited multi-label</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Relational Structure & File Explanation
st.subheader("1. Relational Entities & Parsing Specifications")

st.markdown("""
<div class="analysis-card">
    <div class="analysis-title">Original MovieLens 1M File Specifications</div>
    <div class="analysis-subtitle">Extracted directly from README and DMT.ipynb preprocessing pipeline</div>
    <p>The raw dataset utilizes double-colon delimiters (<code>::</code>) and <code>latin-1</code> character encoding to support international movie titles.</p>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("""
    <div class="analysis-card" style="height: 100%;">
        <div style="font-weight:700; color:#4F46E5; margin-bottom:8px;">🎬 movies.dat</div>
        <div style="font-size:0.85rem; line-height:1.6;">
            <b>Format:</b> <code>MovieID::Title::Genres</code><br>
            <b>Records:</b> 3,883 movies<br>
            <b>Title:</b> Movie title with year of release in parentheses (e.g. <i>Toy Story (1995)</i>)<br>
            <b>Genres:</b> Pipe-delimited multi-label string (e.g. <code>Animation|Children's|Comedy</code>)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div class="analysis-card" style="height: 100%;">
        <div style="font-weight:700; color:#0284C7; margin-bottom:8px;">⭐ ratings.dat</div>
        <div style="font-size:0.85rem; line-height:1.6;">
            <b>Format:</b> <code>UserID::MovieID::Rating::Timestamp</code><br>
            <b>Records:</b> 1,000,209 ratings<br>
            <b>Scale:</b> 1 to 5 whole stars<br>
            <b>User Density:</b> Every user has contributed at least 20 ratings<br>
            <b>Timestamp:</b> Epoch seconds from Unix time(2)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
    <div class="analysis-card" style="height: 100%;">
        <div style="font-weight:700; color:#059669; margin-bottom:8px;">👤 users.dat</div>
        <div style="font-size:0.85rem; line-height:1.6;">
            <b>Format:</b> <code>UserID::Gender::Age::Occupation::Zip-code</code><br>
            <b>Records:</b> 6,040 demographic profiles<br>
            <b>Gender:</b> 'M' (Male) or 'F' (Female)<br>
            <b>Age:</b> Categorical integers mapped to 7 demographic brackets<br>
            <b>Occupation:</b> 21 standard occupational codes (0 to 20)
        </div>
    </div>
    """, unsafe_allow_html=True)

# Interactive Data Exploration Tabs
st.subheader("2. Interactive Table Explorer & Schema Inspection")

tabs = st.tabs(["⭐ Ratings Data (1M)", "🎬 Movies Data (3.8K)", "👤 Users Data (6K)", "🔄 Preprocessing Logic"])

with tabs[0]:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption("Showing 15 rows from `ratings.dat`:")
        st.dataframe(ratings.head(15), use_container_width=True)
    with c2:
        st.markdown(f"""
        <div class="takeaway-box">
            <div class="takeaway-header">Ratings Breakdown</div>
            <div class="takeaway-text">
                <b>Mean Rating:</b> {kpis['mean_rating']:.2f}<br>
                <b>Rating Scale:</b> {kpis['min_rating']} to {kpis['max_rating']}<br>
                <b>Most Frequent:</b> {kpis['mode_rating']} Stars<br>
                <b>Total Tuples:</b> {len(ratings):,}
            </div>
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption("Showing 15 rows from `movies.dat`:")
        st.dataframe(movies.head(15), use_container_width=True)
    with c2:
        st.markdown("""
        <div class="takeaway-box">
            <div class="takeaway-header">Genre Encoding</div>
            <div class="takeaway-text">
                Movies contain multi-label genres separated by pipes (<code>|</code>). During preprocessing in DMT, <code>.explode()</code> and binary dummy matrices are used to compute genre associations.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tabs[2]:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption("Showing 15 rows from `users.dat` with demographic decoded labels:")
        st.dataframe(users[["UserID", "Gender", "Age", "Age_Group", "Occupation", "Occupation_Name", "Zip-code"]].head(15), use_container_width=True)
    with c2:
        st.markdown("""
        <div class="takeaway-box">
            <div class="takeaway-header">Demographic Mappings</div>
            <div class="takeaway-text">
                Integer age codes mapped to standard human-readable ranges: <b>Under 18</b>, <b>18-24</b>, <b>25-34</b>, <b>35-44</b>, <b>45-49</b>, <b>50-55</b>, <b>56+</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tabs[3]:
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">Exact Transformations Implemented in DMT.ipynb</div>
        <div class="analysis-subtitle">Step-by-step reproducible data preparation</div>
        <ol style="line-height:1.8; font-size:0.95rem;">
            <li><b>Custom Delimiter Parsing:</b> Used <code>sep="::"</code> with Python engine and <code>encoding="latin-1"</code> to handle non-UTF-8 European movie titles.</li>
            <li><b>Demographic Range Mapping:</b> Transformed user age keys (1, 18, 25, 35, 45, 50, 56) into discrete demographic cohorts (e.g. <code>Under 18</code>, <code>25-34</code>, <code>56+</code>).</li>
            <li><b>Relational Joins:</b> Joined <code>ratings</code> with <code>movies</code> on <code>MovieID</code>, followed by demographic enrichment with <code>users</code> on <code>UserID</code>.</li>
            <li><b>Multi-Label Genre Explosion:</b> Applied <code>df['Genres'].str.split('|')</code> and <code>.explode('Genre')</code> to enable atomic genre aggregations.</li>
            <li><b>Binary Dummy Transformation:</b> Constructed <code>str.get_dummies(sep='|')</code> for itemset mining and Apriori association analysis.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Demographic Visual Distribution
st.subheader("3. Demographic Distribution Overview")

d_col1, d_col2 = st.columns(2)

with d_col1:
    age_counts = users["Age_Group"].value_counts().reindex([
        "Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"
    ])
    fig_age = px.bar(
        x=age_counts.index,
        y=age_counts.values,
        labels={"x": "Age Cohort", "y": "Number of Users"},
        title="User Distribution by Age Group",
        color=age_counts.values,
        color_continuous_scale="Blues"
    )
    fig_age.update_layout(get_plotly_layout(dark_mode, height=350))
    fig_age.update_coloraxes(showscale=False)
    st.plotly_chart(fig_age, use_container_width=True)

with d_col2:
    gender_counts = users["Gender"].map({"M": "Male (71.7%)", "F": "Female (28.3%)"}).value_counts()
    fig_gender = px.pie(
        names=gender_counts.index,
        values=gender_counts.values,
        title="User Gender Breakdown",
        color_discrete_sequence=["#4F46E5", "#EC4899"],
        hole=0.45
    )
    fig_gender.update_layout(get_plotly_layout(dark_mode, height=350))
    st.plotly_chart(fig_gender, use_container_width=True)
