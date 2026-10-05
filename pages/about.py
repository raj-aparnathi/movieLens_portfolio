import streamlit as st
import sys
from pathlib import Path

# Ensure utils can be imported
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data_loader import inject_custom_css

dark_mode = st.session_state.get("dark_mode", False)
inject_custom_css(dark_mode)

st.title("ℹ️ About the Project & Academic Scope")
st.markdown(
    "<p style='font-size:1.05rem; margin-top:-10px; margin-bottom:24px;'>"
    "Project documentation, dataset provenance, technology stack, and formal demarcation between implemented techniques and future research scope."
    "</p>",
    unsafe_allow_html=True
)

# SECTION 1: Project Metadata Cards
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("""
    <div class="analysis-card" style="height:100%;">
        <div class="analysis-title">Academic Context</div>
        <div class="analysis-subtitle">Coursework & Research Scope</div>
        <table style="width:100%; font-size:0.875rem; border-collapse:collapse; line-height:2.0;">
            <tr><td style="color:#64748B; width:35%;"><b>Project Title:</b></td><td>MovieLens 1M — Mining Movie Genre & Rating Patterns</td></tr>
            <tr><td style="color:#64748B;"><b>Course / Subject:</b></td><td>Data Mining Techniques (DMT)</td></tr>
            <tr><td style="color:#64748B;"><b>Source Dataset:</b></td><td>GroupLens Research, University of Minnesota</td></tr>
            <tr><td style="color:#64748B;"><b>Collection Year:</b></td><td>2000 (1,000,209 ratings across 6,040 users)</td></tr>
            <tr><td style="color:#64748B;"><b>Execution Engine:</b></td><td>Python 3.13 / Streamlit Analytical Dashboard</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div class="analysis-card" style="height:100%;">
        <div class="analysis-title">Technology Stack</div>
        <div class="analysis-subtitle">Libraries & Computing Frameworks</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;">
            <span class="badge">Python 3.13</span>
            <span class="badge">Streamlit 1.65</span>
            <span class="badge">Pandas 3.0</span>
            <span class="badge">NumPy 2.5</span>
            <span class="badge">Plotly 7.0</span>
            <span class="badge">Scikit-learn 1.9</span>
            <span class="badge">MLxtend 0.25 (Apriori)</span>
            <span class="badge">StandardScaler</span>
            <span class="badge">PCA Decomposition</span>
        </div>
        <div style="font-size:0.85rem; line-height:1.6; margin-top:16px; color:#475569;">
            Leverages Streamlit native caching (<code>@st.cache_data</code>) to deliver sub-second data slicing and interactive filtering over one million records in memory.
        </div>
    </div>
    """, unsafe_allow_html=True)

# SECTION 2: Implemented Techniques vs Future Scope (Strict Separation)
st.subheader("2. Formal Scope Boundary")

col_s1, col_s2 = st.columns(2)

with col_s1:
    st.markdown("""
    <div class="analysis-card" style="border-top:4px solid #10B981; height:100%;">
        <div style="font-weight:700; color:#10B981; font-size:1.1rem; margin-bottom:4px;">
            ✅ Implemented Techniques (Active in DMT.ipynb)
        </div>
        <div class="analysis-subtitle">Verified empirical implementations with reproducible code</div>
        <ul style="font-size:0.875rem; line-height:1.8; margin-top:10px;">
            <li><b>Data Loading & Parsing:</b> Custom parsing of <code>::</code> delimited files with Latin-1 character set handling.</li>
            <li><b>Demographic Feature Mapping:</b> Discretization of age keys into 7 analytical cohorts and occupation code mapping.</li>
            <li><b>Multi-Label Genre Explosion:</b> Vectorized parsing of pipe-separated multi-genre labels into atomic entities.</li>
            <li><b>Univariate & Bivariate EDA:</b> Rating frequency distributions, skewness analysis, 5-star ratio analysis, and genre performance benchmarks.</li>
            <li><b>Combinatorial Genre Pair Mining:</b> Pairwise co-occurrence counting and rating performance under statistical volume constraints (≥500 ratings).</li>
            <li><b>Association Rule Mining:</b> Apriori algorithm on movie genre incidence matrix with Support, Confidence, and Lift metrics.</li>
            <li><b>Dimensionality Reduction:</b> Construction of 6,040 × 18 User-Genre rating matrix, Z-score standardization, and 2-component PCA projection.</li>
            <li><b>Demographic Cross-Tabulation:</b> Heatmap generation and top-K genre volume ranking across age groups.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div class="analysis-card" style="border-top:4px solid #6366F1; height:100%;">
        <div style="font-weight:700; color:#6366F1; font-size:1.1rem; margin-bottom:4px;">
            🚀 Future Scope (Unimplemented Research Ideas)
        </div>
        <div class="analysis-subtitle">Prospective extensions for advanced recommendation systems</div>
        <ul style="font-size:0.875rem; line-height:1.8; margin-top:10px;">
            <li><b>User-User & Item-Item Collaborative Filtering:</b> Calculating cosine/Pearson similarities across users to predict missing individual ratings.</li>
            <li><b>Matrix Factorization (SVD / NMF):</b> Latent factor modeling using truncated Singular Value Decomposition to uncover hidden movie and user vectors.</li>
            <li><b>Neural Collaborative Filtering (NCF):</b> Deep learning architectures combining linear embeddings with multi-layer perceptrons (MLP).</li>
            <li><b>Sequential & Temporal Modeling:</b> Incorporating timestamp dynamics to capture how user genre tastes evolve over time.</li>
            <li><b>Content-Based Vector Embeddings:</b> Integrating movie plot summaries and cast metadata via natural language transformers (e.g. BERT/Sentence-Transformers).</li>
            <li><b>Hybrid Recommender System:</b> Blending collaborative collaborative matrix factorization with genre-association rules to address cold-start challenges.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: Dataset Limitations & Ethical Considerations
st.subheader("3. Dataset Limitations & Academic Citation")

col_l1, col_l2 = st.columns([1.5, 1])

with col_l1:
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">Dataset Limitations</div>
        <div class="analysis-subtitle">Important contextual factors for interpreting findings</div>
        <ul style="font-size:0.875rem; line-height:1.7;">
            <li><b>Historical Snapshot:</b> Data was collected in the year 2000 and reflects late-1990s viewing habits, cinema formats, and demographic internet access patterns of that era.</li>
            <li><b>Self-Selection Bias:</b> Viewers voluntarily choose which movies to watch and rate, creating positive skewness toward favorable ratings (mean 3.58).</li>
            <li><b>Self-Reported Demographics:</b> Demographic attributes (Age, Gender, Occupation, Zip-code) were provided voluntarily without external verification.</li>
            <li><b>Discrete Scale:</b> Ratings are whole stars from 1 to 5, without half-star increments or textual review sentiment.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_l2:
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">Academic Citation</div>
        <div class="analysis-subtitle">Official GroupLens reference</div>
        <div style="font-size:0.825rem; line-height:1.6; background:rgba(0,0,0,0.03); padding:12px; border-radius:8px; font-family:'JetBrains Mono', monospace;">
            F. Maxwell Harper and Joseph A. Konstan. 2015.<br>
            <i>The MovieLens Datasets: History and Context.</i><br>
            ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4, Article 19.<br>
            DOI: 10.1145/2827872
        </div>
    </div>
    """, unsafe_allow_html=True)
