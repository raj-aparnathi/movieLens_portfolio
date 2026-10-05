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
    get_pca_analysis,
    inject_custom_css,
    get_plotly_layout
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("🧬 Principal Component Analysis (PCA)")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Unsupervised dimensionality reduction projecting 6,040 user taste vectors across 18 genre dimensions into a 2D preference segment map."
    "</p>",
    unsafe_allow_html=True
)

with st.spinner("Computing user-genre rating matrix & PCA decomposition..."):
    pca_df, explained_var, loadings = get_pca_analysis()

pc1_pct = explained_var[0] * 100
pc2_pct = explained_var[1] * 100
total_var = pc1_pct + pc2_pct

# KPI Cards
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Analyzed Users</div>
        <div class="kpi-value">{len(pca_df):,}</div>
        <div class="kpi-subtext">Demographic cohort mapped</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">PC1 Variance</div>
        <div class="kpi-value">{pc1_pct:.1f}%</div>
        <div class="kpi-subtext">Primary preference axis</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">PC2 Variance</div>
        <div class="kpi-value">{pc2_pct:.1f}%</div>
        <div class="kpi-subtext">Secondary preference axis</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cumulative 2D</div>
        <div class="kpi-value">{total_var:.1f}%</div>
        <div class="kpi-subtext">Total variance retained</div>
    </div>
    """, unsafe_allow_html=True)

# Methodology Explanation Card
st.markdown("""
<div class="analysis-card">
    <div class="analysis-title">Mathematical Formulation of the User-Genre Preference Matrix</div>
    <div class="analysis-subtitle">How high-dimensional viewing behaviors were reduced into latent components</div>
    <div style="font-size:0.925rem; line-height:1.65;">
        1. <b>Feature Matrix Construction:</b> Aggregated 1,000,209 ratings into a <code>6,040 × 18</code> matrix where each cell represents user <i>u</i>'s average rating for genre <i>g</i> (unrated genres filled with 0).<br>
        2. <b>Z-Score Standardization:</b> Standardized using <code>StandardScaler()</code> (zero mean, unit variance) to prevent high-volume genres from artificially dominating covariance.<br>
        3. <b>Orthogonal Eigen-Decomposition:</b> Computed top 2 eigenvectors capturing maximum orthogonal variance across the user population.
    </div>
</div>
""", unsafe_allow_html=True)

# Interactive Controls & Scatter Visualization
st.subheader("1. Interactive 2D Movie Preference Segment Map")

# Demographic Filter
age_options = ["All Age Groups"] + sorted(list(pca_df["Age_Group"].dropna().unique()))
selected_age = st.selectbox("Filter Demographic Cohort:", age_options, index=0)

filtered_pca = pca_df if selected_age == "All Age Groups" else pca_df[pca_df["Age_Group"] == selected_age]

col_s1, col_s2 = st.columns([2.2, 1])

with col_s1:
    fig_pca = px.scatter(
        filtered_pca,
        x="PC1",
        y="PC2",
        color="Age_Group",
        hover_data={"PC1": ":.2f", "PC2": ":.2f", "Age_Group": True},
        opacity=0.65,
        title=f"User Preference Projection ({len(filtered_pca):,} Users)",
        labels={
            "PC1": f"Principal Component 1 ({pc1_pct:.1f}% Variance)",
            "PC2": f"Principal Component 2 ({pc2_pct:.1f}% Variance)"
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_pca.update_traces(marker=dict(size=6))
    fig_pca.update_layout(get_plotly_layout(dark_mode, height=500))
    st.plotly_chart(fig_pca, use_container_width=True)

with col_s2:
    st.markdown(f"""
    <div class="takeaway-box" style="margin-top: 10px;">
        <div class="takeaway-header">Component Interpretation</div>
        <div class="takeaway-text">
            <b>PC1 ({pc1_pct:.1f}%): Broad Consumption & Leniency</b><br>
            Users with positive PC1 scores tend to be omnivorous viewers with high average engagement across multiple standard genres.<br><br>
            <b>PC2 ({pc2_pct:.1f}%): Genre Polarization Axis</b><br>
            Differentiates high-octane spectacle viewers (Action, Sci-Fi, Adventure) from character-driven narrative audiences (Drama, Romance, Documentary).<br><br>
            <b>Age Group Dispersion:</b><br>
            Demographic cohorts overlap significantly in latent space, proving that genre taste in MovieLens 1M transcends simple age silos.
        </div>
    </div>
    """, unsafe_allow_html=True)

# SECTION 2: Component Loadings (Genre Weights)
st.subheader("2. Principal Component Loadings (Genre Dimensional Weights)")

col_l1, col_l2 = st.columns(2)

with col_l1:
    fig_pc1_loadings = px.bar(
        loadings.sort_values("PC1", ascending=True),
        x="PC1",
        y=loadings.sort_values("PC1", ascending=True).index,
        orientation="h",
        labels={"x": "Loading Weight on PC1", "index": "Genre"},
        title="Genre Contributions to PC1 (Breadth)",
        color="PC1",
        color_continuous_scale="Purples"
    )
    fig_pc1_loadings.update_layout(get_plotly_layout(dark_mode, height=450))
    fig_pc1_loadings.update_coloraxes(showscale=False)
    st.plotly_chart(fig_pc1_loadings, use_container_width=True)

with col_l2:
    fig_pc2_loadings = px.bar(
        loadings.sort_values("PC2", ascending=True),
        x="PC2",
        y=loadings.sort_values("PC2", ascending=True).index,
        orientation="h",
        labels={"x": "Loading Weight on PC2", "index": "Genre"},
        title="Genre Contributions to PC2 (Spectacle vs. Narrative)",
        color="PC2",
        color_continuous_scale="Tropic"
    )
    fig_pc2_loadings.update_layout(get_plotly_layout(dark_mode, height=450))
    fig_pc2_loadings.update_coloraxes(showscale=False)
    st.plotly_chart(fig_pc2_loadings, use_container_width=True)
