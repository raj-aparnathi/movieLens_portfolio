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
    run_apriori_rules,
    inject_custom_css,
    get_plotly_layout
)

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("🔗 Association Rule Mining (Apriori)")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Frequent itemset discovery and association rule mining on movie genre metadata using the classic Apriori algorithm."
    "</p>",
    unsafe_allow_html=True
)

# Mandatory Scientific Clarification
st.info(
    "📌 **Methodological Clarification**: The association rules shown below capture **genre co-occurrence within movie metadata** "
    "(i.e., when a movie is tagged with Genre A, what is the probability it is also tagged with Genre B). "
    "These rules represent **movie genre associations**, NOT a collaborative user recommendation system."
)

# Interactive Control Toolbar
st.subheader("1. Mining Parameter Configuration")

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 2])

with ctrl_col1:
    min_sup = st.slider(
        "Minimum Support Threshold",
        min_value=0.01,
        max_value=0.08,
        value=0.02,
        step=0.005,
        help="Fraction of all movies that must contain the genre set."
    )

with ctrl_col2:
    min_conf = st.slider(
        "Minimum Confidence Threshold",
        min_value=0.20,
        max_value=0.85,
        value=0.30,
        step=0.05,
        help="Conditional probability P(Consequent | Antecedent)."
    )

with ctrl_col3:
    st.markdown("""
    <div style="font-size:0.825rem; line-height:1.5; padding:8px 12px; border-left:3px solid #6366F1;">
        <b>Baseline DMT.ipynb Parameters:</b><br>
        <code>min_support = 0.02 (2.0%)</code><br>
        <code>min_confidence = 0.30 (30.0%)</code><br>
        <i>Top rule identified: Children's → Animation (Lift = 12.38)</i>
    </div>
    """, unsafe_allow_html=True)

# Run Apriori Mining
with st.spinner("Executing Apriori frequent itemset generation..."):
    frequent_itemsets, rules = run_apriori_rules(min_support=min_sup, min_confidence=min_conf)

if rules.empty:
    st.warning("No association rules found with the selected Support and Confidence thresholds. Try lowering the thresholds.")
else:
    # Metric KPI Overview
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Frequent Itemsets</div>
            <div class="kpi-value">{len(frequent_itemsets)}</div>
            <div class="kpi-subtext">Support ≥ {min_sup*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Generated Rules</div>
            <div class="kpi-value">{len(rules)}</div>
            <div class="kpi-subtext">Confidence ≥ {min_conf*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        max_lift = rules["lift"].max()
        top_rule_str = rules.iloc[0]["Rule"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Maximum Lift</div>
            <div class="kpi-value">{max_lift:.2f}x</div>
            <div class="kpi-subtext">{top_rule_str}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        max_conf = rules["confidence"].max()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Peak Confidence</div>
            <div class="kpi-value">{max_conf*100:.1f}%</div>
            <div class="kpi-subtext">Predictive strength</div>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 2: Rule Visualizations
    st.subheader("2. Rule Evaluation & Lift Landscape")
    
    vis_col1, vis_col2 = st.columns([1.1, 0.9])
    
    with vis_col1:
        # Scatter Plot: Support vs Confidence sized by Lift
        fig_scatter = px.scatter(
            rules,
            x="support",
            y="confidence",
            size="lift",
            color="lift",
            hover_name="Rule",
            hover_data={
                "support": ":.3f",
                "confidence": ":.3f",
                "lift": ":.2f"
            },
            labels={
                "support": "Support (Itemset Frequency)",
                "confidence": "Confidence (Rule Accuracy)",
                "lift": "Lift Factor"
            },
            title="Association Rules: Support vs Confidence (Size = Lift)",
            color_continuous_scale="Turbo"
        )
        fig_scatter.update_layout(get_plotly_layout(dark_mode, height=440))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with vis_col2:
        # Top 10 rules bar chart by Lift
        top_rules = rules.head(10).copy()
        fig_bar = px.bar(
            top_rules,
            x="lift",
            y="Rule",
            orientation="h",
            labels={"lift": "Lift Value", "Rule": "Association Rule"},
            title="Top 10 Association Rules Ranked by Lift",
            color="lift",
            color_continuous_scale="Purples"
        )
        fig_bar.update_layout(get_plotly_layout(dark_mode, height=440))
        fig_bar.update_yaxes(autorange="reversed")
        fig_bar.update_coloraxes(showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Mathematical Formula Explanations
    st.subheader("3. Formal Association Mining Metrics")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown("""
        <div class="analysis-card" style="height: 100%;">
            <div style="font-weight:700; color:#4F46E5; margin-bottom:8px;">1. Support (P(A ∩ B))</div>
            <div style="font-size:0.875rem; line-height:1.6;">
                Proportion of movies in the catalog containing both genre A and genre B.<br><br>
                <code>Support(A → B) = Count(A ∪ B) / Total Movies</code><br><br>
                Indicates the statistical significance and frequency of the co-occurrence.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown("""
        <div class="analysis-card" style="height: 100%;">
            <div style="font-weight:700; color:#0284C7; margin-bottom:8px;">2. Confidence (P(B | A))</div>
            <div style="font-size:0.875rem; line-height:1.6;">
                Conditional probability that a movie has genre B given that it is tagged with genre A.<br><br>
                <code>Confidence(A → B) = Support(A ∪ B) / Support(A)</code><br><br>
                Reflects directional predictive reliability.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown("""
        <div class="analysis-card" style="height: 100%;">
            <div style="font-weight:700; color:#059669; margin-bottom:8px;">3. Lift (Ratio of Dependence)</div>
            <div style="font-size:0.875rem; line-height:1.6;">
                Measures how much more often A and B occur together than if they were statistically independent.<br><br>
                <code>Lift(A → B) = Confidence(A → B) / Support(B)</code><br><br>
                <b>Lift > 1:</b> Positive association.<br>
                <b>Lift = 1:</b> Independent occurrence.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 4: Interactive Table
    st.subheader("4. Complete Mined Association Rules Table")
    
    display_rules = rules[[
        "Rule", "Antecedents_Str", "Consequents_Str", "support", "confidence", "lift"
    ]].copy()
    
    display_rules["support"] = (display_rules["support"] * 100).round(2).astype(str) + "%"
    display_rules["confidence"] = (display_rules["confidence"] * 100).round(2).astype(str) + "%"
    display_rules["lift"] = display_rules["lift"].round(2)
    
    display_rules.columns = [
        "Association Rule", "Antecedent(s)", "Consequent(s)", "Support (%)", "Confidence (%)", "Lift Ratio"
    ]
    
    st.dataframe(display_rules, use_container_width=True)

    st.markdown("""
    <div class="takeaway-box">
        <div class="takeaway-header">Key Mining Discovery</div>
        <div class="takeaway-text">
            The strongest mutual association in the entire dataset is between <b>Children's</b> and <b>Animation</b>:
            An antecedent of <i>Children's</i> yields <i>Animation</i> with a massive <b>Lift of 12.38</b> and <b>Confidence of 83.2%</b>.
            Conversely, <i>Animation</i> implies <i>Children's</i> with the exact same Lift of <b>12.38</b> and a Confidence of <b>64.4%</b>.
            This demonstrates near-complete industrial coupling of animated feature films with family and children's content during this era.
        </div>
    </div>
    """, unsafe_allow_html=True)
