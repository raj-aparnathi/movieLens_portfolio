/* ============================================================
   MovieLens 1M — DMT Analytics Portfolio
   Main Application JavaScript
   ============================================================ */

// ============================================================
// GLOBAL STATE
// ============================================================
let DATA = {};
const DATA_FILES = [
  'kpis', 'genre_analytics', 'genre_pairs',
  'association_rules', 'pca', 'age_genre', 'dataset_samples'
];

// ============================================================
// PLOTLY THEME UTILITIES
// ============================================================
function getPlotlyLayout(opts = {}) {
  const dark = document.documentElement.getAttribute('data-theme') === 'dark';
  const bg = dark ? '#111827' : '#FFFFFF';
  const text = dark ? '#F8FAFC' : '#0F172A';
  const grid = dark ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.06)';
  const muted = dark ? '#94A3B8' : '#64748B';

  return Object.assign({
    height: opts.height || 400,
    margin: { l: 50, r: 20, t: 44, b: 50 },
    paper_bgcolor: bg,
    plot_bgcolor: bg,
    font: { family: 'Plus Jakarta Sans, sans-serif', color: text, size: 12 },
    xaxis: Object.assign({ showgrid: true, gridcolor: grid, zeroline: false, color: text }, opts.xaxis || {}),
    yaxis: Object.assign({ showgrid: true, gridcolor: grid, zeroline: false, color: text }, opts.yaxis || {}),
    hoverlabel: {
      bgcolor: dark ? '#1E293B' : '#0F172A',
      font: { size: 12, family: 'Plus Jakarta Sans, sans-serif', color: '#FFFFFF' }
    },
    coloraxis: { showscale: false }
  }, opts.extra || {});
}

function getPlotlyConfig() {
  return { responsive: true, displayModeBar: false };
}

function fmt(n) {
  return n.toLocaleString('en-US');
}

// ============================================================
// DATA LOADING
// ============================================================
async function loadAllData() {
  if (window.DMT_DATA && Object.keys(window.DMT_DATA).length > 0) {
    DATA = window.DMT_DATA;
    return;
  }
  const promises = DATA_FILES.map(async (name) => {
    const resp = await fetch(`data/${name}.json`);
    DATA[name] = await resp.json();
  });
  await Promise.all(promises);
}

// ============================================================
// SIDEBAR STATS
// ============================================================
function updateSidebarStats() {
  const k = DATA.kpis;
  document.getElementById('sidebar-ratings').textContent = fmt(k.total_ratings);
  document.getElementById('sidebar-users').textContent = fmt(k.total_users);
  document.getElementById('sidebar-movies').textContent = fmt(k.total_movies);
  document.getElementById('sidebar-genres').textContent = k.distinct_genres_count;
}

// ============================================================
// NAVIGATION
// ============================================================
const pageRendered = {};

function navigateTo(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const page = document.getElementById('page-' + pageId);
  if (page) page.classList.add('active');

  const navBtn = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (navBtn) navBtn.classList.add('active');

  // Lazy render
  if (!pageRendered[pageId]) {
    pageRendered[pageId] = true;
    renderPage(pageId);
  } else {
    // Re-render charts for theme changes if needed
    replotCharts(pageId);
  }

  closeSidebar();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderPage(pageId) {
  switch (pageId) {
    case 'overview': renderOverview(); break;
    case 'dataset': renderDataset(); break;
    case 'exploration': renderExploration(); break;
    case 'association': renderAssociation(); break;
    case 'pca': renderPCA(); break;
    case 'age-genre': renderAgeGenre(); break;
    case 'findings': renderFindings(); break;
    case 'methodology': renderMethodology(); break;
    case 'about': break; // static content
  }
}

// Track which charts exist on which page for re-rendering on theme change
const pageCharts = {};

function replotCharts(pageId) {
  if (pageCharts[pageId]) {
    // Re-render entire page on theme change
    pageRendered[pageId] = false;
    pageRendered[pageId] = true;
    renderPage(pageId);
  }
}

// ============================================================
// SIDEBAR TOGGLE (mobile)
// ============================================================
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.querySelector('.sidebar-overlay').classList.toggle('active');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.querySelector('.sidebar-overlay').classList.remove('active');
}

// ============================================================
// THEME TOGGLE
// ============================================================
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);

  document.getElementById('theme-icon').textContent = next === 'dark' ? '☀️' : '🌙';
  document.getElementById('theme-label').textContent = next === 'dark' ? 'Light Mode' : 'Dark Mode';

  // Re-render all rendered pages for theme
  Object.keys(pageRendered).forEach(pid => {
    if (pageRendered[pid]) {
      pageRendered[pid] = false;
    }
  });
  // Re-render current page
  const activePage = document.querySelector('.page.active');
  if (activePage) {
    const pid = activePage.id.replace('page-', '');
    pageRendered[pid] = true;
    renderPage(pid);
  }
}

// ============================================================
// PAGE: OVERVIEW
// ============================================================
function renderOverview() {
  const k = DATA.kpis;
  const ga = DATA.genre_analytics;
  pageCharts['overview'] = true;

  // KPI Cards
  const kpiContainer = document.getElementById('overview-kpis');
  kpiContainer.innerHTML = `
    <div class="kpi-card">
      <div class="kpi-label">Total Users</div>
      <div class="kpi-value">${fmt(k.total_users)}</div>
      <div class="kpi-subtext">Demographically profiled viewers</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Catalog Movies</div>
      <div class="kpi-value">${fmt(k.total_movies)}</div>
      <div class="kpi-subtext">Across ${k.distinct_genres_count} distinct genres</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Ratings</div>
      <div class="kpi-value">${fmt(k.total_ratings)}</div>
      <div class="kpi-subtext">5-star scale (Mode: ${k.mode_rating})</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Average Rating</div>
      <div class="kpi-value">${k.mean_rating.toFixed(2)}</div>
      <div class="kpi-subtext">Global benchmark score</div>
    </div>
  `;

  // Rating Distribution Chart
  const rd = k.rating_distribution;
  const rp = k.rating_pcts;
  const ratingKeys = Object.keys(rd).sort();
  const colors = ['#F87171', '#FB923C', '#FBBF24', '#6366F1', '#10B981'];

  Plotly.newPlot('chart-rating-dist', [{
    type: 'bar',
    x: ratingKeys.map(r => r + ' ★'),
    y: ratingKeys.map(r => rd[r]),
    text: ratingKeys.map(r => rp[r] + '%'),
    textposition: 'outside',
    marker: { color: colors }
  }], getPlotlyLayout({
    extra: { title: `Rating Distribution (${fmt(k.total_ratings)} Ratings)` },
    yaxis: { range: [0, Math.max(...ratingKeys.map(r => rd[r])) * 1.15], showgrid: true, gridcolor: undefined, zeroline: false }
  }), getPlotlyConfig());

  // Top 10 Most Rated Genres
  const gcEntries = Object.entries(ga.rating_count).sort((a, b) => b[1] - a[1]).slice(0, 10);
  Plotly.newPlot('chart-top-genres', [{
    type: 'bar',
    x: gcEntries.map(e => e[1]).reverse(),
    y: gcEntries.map(e => e[0]).reverse(),
    orientation: 'h',
    marker: { color: gcEntries.map((_, i) => `hsl(${260 - i * 10}, 60%, ${40 + i * 4}%)`).reverse() }
  }], getPlotlyLayout({
    extra: { title: 'Top 10 Most-Rated Genres (Audience Volume)' },
    xaxis: { title: 'Total Ratings Count' }
  }), getPlotlyConfig());

  // Discovery Cards
  const discoveries = document.getElementById('overview-discoveries');
  discoveries.innerHTML = `
    <div class="takeaway" style="margin:0;">
      <div class="takeaway-header">Positive Skew & Mode</div>
      <div class="takeaway-text"><b>Rating 4</b> is the most common score (34.9% of ratings). Together, 4 and 5 stars represent <b>57.5%</b> of all feedback, indicating strong positive viewer engagement.</div>
    </div>
    <div class="takeaway" style="margin:0;">
      <div class="takeaway-header">Commercial Volume vs. Quality</div>
      <div class="takeaway-text"><b>Comedy</b> (356K) and <b>Drama</b> (354K) dominate viewership. In contrast, <b>Film-Noir</b> holds the highest average rating at <b>4.08</b> (with 34.6% 5-star ratings).</div>
    </div>
    <div class="takeaway" style="margin:0;">
      <div class="takeaway-header">Apriori Genre Association</div>
      <div class="takeaway-text">Mining frequent itemsets identified <b>Children's → Animation</b> with a peak <b>Lift of 12.38</b> and <b>83.2% confidence</b>, reflecting heavy industrial co-tagging.</div>
    </div>
    <div class="takeaway" style="margin:0;">
      <div class="takeaway-header">Demographic Preferences & PCA</div>
      <div class="takeaway-text">Viewers aged <b>56+</b> exhibit the highest rating leniency (mean 3.77). 2D PCA reduces taste profiles into breadth of consumption vs spectacle vs narrative drama.</div>
    </div>
  `;
}

// ============================================================
// PAGE: DATASET
// ============================================================
function renderDataset() {
  const k = DATA.kpis;
  const ds = DATA.dataset_samples;
  pageCharts['dataset'] = true;

  // KPI cards
  document.getElementById('dataset-kpis').innerHTML = `
    <div class="kpi-card">
      <div class="kpi-label">Ratings Dataframe</div>
      <div class="kpi-value">${fmt(k.total_ratings)}</div>
      <div class="kpi-subtext">ratings.dat (25.6 MB)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Unique Users</div>
      <div class="kpi-value">${fmt(k.total_users)}</div>
      <div class="kpi-subtext">users.dat (140 KB)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Unique Movies</div>
      <div class="kpi-value">${fmt(k.total_movies)}</div>
      <div class="kpi-subtext">movies.dat (175 KB)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Distinct Genres</div>
      <div class="kpi-value">${k.distinct_genres_count}</div>
      <div class="kpi-subtext">Pipe-delimited multi-label</div>
    </div>
  `;

  // Show default tab
  showDataTab('ratings');

  // Demographic charts
  const ageOrder = ['Under 18', '18-24', '25-34', '35-44', '45-49', '50-55', '56+'];
  const ageCounts = ageOrder.map(a => ds.age_distribution[a] || 0);

  Plotly.newPlot('chart-age-dist', [{
    type: 'bar', x: ageOrder, y: ageCounts,
    marker: { color: ageCounts.map((_, i) => `hsl(210, 70%, ${35 + i * 8}%)`) }
  }], getPlotlyLayout({
    height: 350,
    extra: { title: 'User Distribution by Age Group' },
    xaxis: { title: 'Age Cohort' }, yaxis: { title: 'Number of Users' }
  }), getPlotlyConfig());

  Plotly.newPlot('chart-gender-dist', [{
    type: 'pie',
    labels: [`Male (${ds.gender_pcts.M}%)`, `Female (${ds.gender_pcts.F}%)`],
    values: [ds.gender_distribution.M, ds.gender_distribution.F],
    hole: 0.45,
    marker: { colors: ['#4F46E5', '#EC4899'] }
  }], getPlotlyLayout({
    height: 350,
    extra: { title: 'User Gender Breakdown' }
  }), getPlotlyConfig());
}

function showDataTab(tab) {
  const ds = DATA.dataset_samples;
  const k = DATA.kpis;
  const container = document.getElementById('data-tab-content');

  // Highlight active tab
  ['ratings', 'movies', 'users', 'preprocessing'].forEach(t => {
    const el = document.getElementById('tab-' + t);
    if (el) el.style.fontWeight = (t === tab) ? '800' : '600';
  });

  if (tab === 'ratings') {
    container.innerHTML = `
      <p style="font-size:0.825rem; color:var(--text-muted); margin-bottom:8px;">Showing 15 rows from ratings.dat:</p>
      ${buildTable(ds.ratings_sample, ['UserID', 'MovieID', 'Rating', 'Timestamp'])}
      <div class="takeaway mt-2">
        <div class="takeaway-header">Ratings Breakdown</div>
        <div class="takeaway-text"><b>Mean Rating:</b> ${k.mean_rating.toFixed(2)} | <b>Scale:</b> ${k.min_rating} to ${k.max_rating} | <b>Most Frequent:</b> ${k.mode_rating} Stars | <b>Total:</b> ${fmt(k.total_ratings)}</div>
      </div>`;
  } else if (tab === 'movies') {
    container.innerHTML = `
      <p style="font-size:0.825rem; color:var(--text-muted); margin-bottom:8px;">Showing 15 rows from movies.dat:</p>
      ${buildTable(ds.movies_sample, ['MovieID', 'Title', 'Genres'])}
      <div class="takeaway mt-2">
        <div class="takeaway-header">Genre Encoding</div>
        <div class="takeaway-text">Movies contain multi-label genres separated by pipes (<code>|</code>). During preprocessing, <code>.explode()</code> and binary dummy matrices are used to compute genre associations.</div>
      </div>`;
  } else if (tab === 'users') {
    container.innerHTML = `
      <p style="font-size:0.825rem; color:var(--text-muted); margin-bottom:8px;">Showing 15 rows from users.dat with demographic decoded labels:</p>
      ${buildTable(ds.users_sample, ['UserID', 'Gender', 'Age', 'Age_Group', 'Occupation', 'Occupation_Name', 'Zip-code'])}
      <div class="takeaway mt-2">
        <div class="takeaway-header">Demographic Mappings</div>
        <div class="takeaway-text">Integer age codes mapped to standard ranges: <b>Under 18</b>, <b>18-24</b>, <b>25-34</b>, <b>35-44</b>, <b>45-49</b>, <b>50-55</b>, <b>56+</b>.</div>
      </div>`;
  } else if (tab === 'preprocessing') {
    container.innerHTML = `
      <div class="card-title">Exact Transformations Implemented in DMT.ipynb</div>
      <div class="card-subtitle">Step-by-step reproducible data preparation</div>
      <ol style="line-height:1.9; font-size:0.925rem; padding-left:20px;">
        <li><b>Custom Delimiter Parsing:</b> Used <code>sep="::"</code> with Python engine and <code>encoding="latin-1"</code> to handle non-UTF-8 European movie titles.</li>
        <li><b>Demographic Range Mapping:</b> Transformed user age keys (1, 18, 25, 35, 45, 50, 56) into discrete cohorts (e.g. <code>Under 18</code>, <code>25-34</code>, <code>56+</code>).</li>
        <li><b>Relational Joins:</b> Joined <code>ratings</code> with <code>movies</code> on <code>MovieID</code>, then enriched with <code>users</code> on <code>UserID</code>.</li>
        <li><b>Multi-Label Genre Explosion:</b> Applied <code>df['Genres'].str.split('|')</code> and <code>.explode('Genre')</code> for atomic genre aggregations.</li>
        <li><b>Binary Dummy Transformation:</b> Constructed <code>str.get_dummies(sep='|')</code> for itemset mining and Apriori analysis.</li>
      </ol>`;
  }
}

function buildTable(data, cols) {
  let html = '<div class="data-table-wrapper"><table class="data-table"><thead><tr>';
  cols.forEach(c => { html += `<th>${c}</th>`; });
  html += '</tr></thead><tbody>';
  data.forEach(row => {
    html += '<tr>';
    cols.forEach(c => { html += `<td>${row[c] !== undefined ? row[c] : ''}</td>`; });
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  return html;
}

// ============================================================
// PAGE: EXPLORATION (EDA)
// ============================================================
function renderExploration() {
  const k = DATA.kpis;
  const ga = DATA.genre_analytics;
  const gp = DATA.genre_pairs;
  const ag = DATA.age_genre;
  pageCharts['exploration'] = true;

  const rd = k.rating_distribution;
  const rp = k.rating_pcts;
  const ratingKeys = Object.keys(rd).sort();
  const colors = ['#EF4444', '#F97316', '#FBBF24', '#4F46E5', '#10B981'];

  // Rating Distribution
  Plotly.newPlot('chart-eda-rating-dist', [{
    type: 'bar',
    x: ratingKeys.map(r => r + ' Stars'),
    y: ratingKeys.map(r => rd[r]),
    text: ratingKeys.map(r => `${fmt(rd[r])} (${rp[r]}%)`),
    textposition: 'outside',
    marker: { color: colors, line: { color: 'rgba(0,0,0,0.1)', width: 1 } }
  }], getPlotlyLayout({
    height: 360,
    extra: { title: `Distribution of ${fmt(k.total_ratings)} Movie Ratings` },
    xaxis: { title: 'Rating (Stars)' },
    yaxis: { title: 'Count of Ratings', range: [0, Math.max(...ratingKeys.map(r => rd[r])) * 1.18] }
  }), getPlotlyConfig());

  // Rating Takeaway
  document.getElementById('eda-rating-takeaway').innerHTML = `
    <div class="takeaway-header">Empirical Takeaway</div>
    <div class="takeaway-text">
      <b>Positive Skew:</b> Ratings display a clear left-skewed distribution towards favorable scores.<br><br>
      • <b>Mode:</b> 4 Stars represents <b>${rp['4']}%</b> of all logged ratings.<br>
      • <b>Positive Sentiment:</b> 4 & 5 stars together account for <b>${(parseFloat(rp['4']) + parseFloat(rp['5'])).toFixed(1)}%</b> of the dataset.<br>
      • <b>Mean Rating:</b> Overall benchmark is <b>${k.mean_rating.toFixed(2)} / 5.00</b>.<br>
      • <b>Lowest Frequency:</b> 1 Star represents only <b>${rp['1']}%</b> of feedback.
    </div>`;

  // Genre Volume
  const gcEntries = Object.entries(ga.rating_count).sort((a, b) => b[1] - a[1]);
  Plotly.newPlot('chart-genre-volume', [{
    type: 'bar',
    x: gcEntries.map(e => e[1]).reverse(),
    y: gcEntries.map(e => e[0]).reverse(),
    orientation: 'h',
    marker: { color: gcEntries.map((_, i) => `hsl(${270 - i * 4}, 55%, ${35 + i * 2}%)`).reverse() }
  }], getPlotlyLayout({
    height: 480,
    extra: { title: 'Most Rated Movie Genres (Market Volume)' },
    xaxis: { title: 'Total Ratings Count' }
  }), getPlotlyConfig());

  // Genre Quality
  const qaEntries = Object.entries(ga.avg_rating).sort((a, b) => b[1] - a[1]);
  Plotly.newPlot('chart-genre-quality', [{
    type: 'bar',
    x: qaEntries.map(e => e[1]).reverse(),
    y: qaEntries.map(e => e[0]).reverse(),
    orientation: 'h',
    marker: { color: qaEntries.map((_, i) => `hsl(${170 + i * 3}, 50%, ${30 + i * 2}%)`).reverse() }
  }], getPlotlyLayout({
    height: 480,
    extra: { title: 'Highest Average Rated Genres (Viewer Acclaim)' },
    xaxis: { title: 'Average Rating (Stars)', range: [2.8, 4.3] }
  }), getPlotlyConfig());

  // Volume vs Quality Card
  document.getElementById('eda-volume-vs-quality-card').innerHTML = `
    <div class="card-title">Critical Data Mining Insight: The Volume vs. Acclaim Paradox</div>
    <div class="card-subtitle">Comparing mass audience engagement against critical rating consensus</div>
    <div style="font-size:0.925rem; line-height:1.65;">
      While <b>Comedy</b> (${fmt(ga.rating_count['Comedy'])} ratings) and <b>Drama</b> (${fmt(ga.rating_count['Drama'])} ratings) dominate over 70% of total engagement,
      their average ratings remain centered around <b>${ga.avg_rating['Comedy']}</b> and <b>${ga.avg_rating['Drama']}</b>.
      In contrast, niche genres such as <b>Film-Noir</b> (mean <b>${ga.avg_rating['Film-Noir']}</b>) and <b>Documentary</b> (mean <b>${ga.avg_rating['Documentary']}</b>)
      command dramatically higher critical scores despite having less than 5% of the total rating volume.
    </div>`;

  // 5-Star Rating %
  const fsEntries = Object.entries(ga.five_star_pct).sort((a, b) => a[1] - b[1]);
  Plotly.newPlot('chart-five-star', [{
    type: 'bar',
    x: fsEntries.map(e => e[1]),
    y: fsEntries.map(e => e[0]),
    orientation: 'h',
    marker: { color: fsEntries.map((_, i) => `hsl(${60 + i * 15}, 70%, ${30 + i * 2}%)`) }
  }], getPlotlyLayout({
    height: 440,
    extra: { title: '5-Star Rating Proportion by Genre' },
    xaxis: { title: '% of Ratings That Are 5 Stars' }
  }), getPlotlyConfig());

  // Age Average Rating
  const ageOrder = ['Under 18', '18-24', '25-34', '35-44', '45-49', '50-55', '56+'];
  const ageAvg = ageOrder.map(a => ag.age_avg_rating[a]);
  Plotly.newPlot('chart-age-avg-rating', [{
    type: 'bar',
    x: ageOrder,
    y: ageAvg,
    text: ageAvg.map(v => v.toFixed(2)),
    textposition: 'outside',
    marker: { color: ageAvg.map((_, i) => `hsl(${30 + i * 15}, 80%, ${35 + i * 4}%)`) }
  }], getPlotlyLayout({
    height: 440,
    extra: { title: 'Generational Rating Leniency (Mean Rating by Age)' },
    xaxis: { title: 'Demographic Cohort' },
    yaxis: { title: 'Average Rating Given', range: [3.4, 3.9] }
  }), getPlotlyConfig());

  // Common Genre Pairs
  const cp = gp.top_common_pairs;
  Plotly.newPlot('chart-common-pairs', [{
    type: 'bar',
    x: cp.map(e => e.count).reverse(),
    y: cp.map(e => e.pair).reverse(),
    orientation: 'h',
    marker: { color: cp.map((_, i) => `hsl(210, 60%, ${35 + i * 4}%)`).reverse() }
  }], getPlotlyLayout({
    height: 420,
    extra: { title: 'Top 12 Most Common Movie Genre Combinations' },
    xaxis: { title: 'Number of Movies Produced' }
  }), getPlotlyConfig());

  // Reliable Pairs
  const rp2 = gp.reliable_pairs;
  Plotly.newPlot('chart-reliable-pairs', [{
    type: 'bar',
    x: rp2.map(e => e.mean).reverse(),
    y: rp2.map(e => e.pair).reverse(),
    orientation: 'h',
    marker: { color: rp2.map((_, i) => `hsl(${170 + i * 5}, 50%, ${30 + i * 3}%)`).reverse() }
  }], getPlotlyLayout({
    height: 420,
    extra: { title: 'Top Rated Genre Pairs (Filtered: ≥ 500 Ratings)' },
    xaxis: { title: 'Average Rating (Stars)', range: [3.8, 4.25] }
  }), getPlotlyConfig());

  // Pairs Takeaway
  const topReliable = rp2[0];
  document.getElementById('eda-pairs-takeaway').innerHTML = `
    <div class="takeaway-header">Genre Pair Synergy Finding</div>
    <div class="takeaway-text">
      While <b>Drama + Romance</b> and <b>Comedy + Romance</b> are the most commercially produced multi-genre combinations,
      the critically highest-rated pair among statistically reliable combinations (≥500 ratings) is <b>${topReliable.pair}</b>
      with an average rating of <b>${topReliable.mean.toFixed(2)}</b>,
      followed by <b>${rp2[1].pair}</b> (${rp2[1].mean.toFixed(2)}) and <b>${rp2[2].pair}</b> (${rp2[2].mean.toFixed(2)}).
    </div>`;
}

// ============================================================
// PAGE: ASSOCIATION RULES
// ============================================================
function renderAssociation() {
  const ar = DATA.association_rules;
  pageCharts['association'] = true;

  // KPIs
  document.getElementById('rules-kpis').innerHTML = `
    <div class="kpi-card">
      <div class="kpi-label">Frequent Itemsets</div>
      <div class="kpi-value">${ar.num_frequent_itemsets}</div>
      <div class="kpi-subtext">Support ≥ 2.0%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Generated Rules</div>
      <div class="kpi-value">${ar.num_rules}</div>
      <div class="kpi-subtext">Confidence ≥ 30%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Maximum Lift</div>
      <div class="kpi-value">${ar.max_lift.toFixed(2)}x</div>
      <div class="kpi-subtext">${ar.top_rule}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Peak Confidence</div>
      <div class="kpi-value">${ar.max_confidence.toFixed(1)}%</div>
      <div class="kpi-subtext">Predictive strength</div>
    </div>`;

  // Scatter Plot
  Plotly.newPlot('chart-rules-scatter', [{
    type: 'scatter',
    mode: 'markers',
    x: ar.rules.map(r => r.support),
    y: ar.rules.map(r => r.confidence),
    text: ar.rules.map(r => r.rule),
    marker: {
      size: ar.rules.map(r => Math.max(8, r.lift * 3)),
      color: ar.rules.map(r => r.lift),
      colorscale: 'Turbo',
      showscale: true,
      colorbar: { title: 'Lift', thickness: 12 }
    },
    hovertemplate: '<b>%{text}</b><br>Support: %{x:.2f}%<br>Confidence: %{y:.2f}%<br>Lift: %{marker.color:.2f}<extra></extra>'
  }], getPlotlyLayout({
    height: 440,
    extra: { title: 'Association Rules: Support vs Confidence (Size = Lift)' },
    xaxis: { title: 'Support (%)' },
    yaxis: { title: 'Confidence (%)' }
  }), getPlotlyConfig());

  // Top 10 Rules Bar
  const top10 = ar.rules.slice(0, 10);
  Plotly.newPlot('chart-rules-bar', [{
    type: 'bar',
    x: top10.map(r => r.lift),
    y: top10.map(r => r.rule),
    orientation: 'h',
    marker: { color: top10.map((_, i) => `hsl(${260 - i * 8}, 55%, ${35 + i * 3}%)`) }
  }], getPlotlyLayout({
    height: 440,
    extra: { title: 'Top 10 Association Rules Ranked by Lift' },
    xaxis: { title: 'Lift Value' },
    yaxis: { autorange: 'reversed' }
  }), getPlotlyConfig());

  // Rules Table
  let tableHtml = '<table class="data-table"><thead><tr><th>Association Rule</th><th>Antecedent(s)</th><th>Consequent(s)</th><th>Support (%)</th><th>Confidence (%)</th><th>Lift</th></tr></thead><tbody>';
  ar.rules.forEach(r => {
    tableHtml += `<tr><td>${r.rule}</td><td>${r.antecedents}</td><td>${r.consequents}</td><td>${r.support}%</td><td>${r.confidence}%</td><td>${r.lift.toFixed(2)}</td></tr>`;
  });
  tableHtml += '</tbody></table>';
  document.getElementById('rules-table-wrapper').innerHTML = tableHtml;
}

// ============================================================
// PAGE: PCA
// ============================================================
function renderPCA() {
  const pca = DATA.pca;
  pageCharts['pca'] = true;

  // KPIs
  document.getElementById('pca-kpis').innerHTML = `
    <div class="kpi-card">
      <div class="kpi-label">Analyzed Users</div>
      <div class="kpi-value">${fmt(pca.num_users)}</div>
      <div class="kpi-subtext">Demographic cohort mapped</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PC1 Variance</div>
      <div class="kpi-value">${pca.pc1_variance}%</div>
      <div class="kpi-subtext">Primary preference axis</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PC2 Variance</div>
      <div class="kpi-value">${pca.pc2_variance}%</div>
      <div class="kpi-subtext">Secondary preference axis</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Cumulative 2D</div>
      <div class="kpi-value">${pca.total_variance}%</div>
      <div class="kpi-subtext">Total variance retained</div>
    </div>`;

  // Interpretation
  document.getElementById('pca-interpretation').innerHTML = `
    <div class="takeaway-header">Component Interpretation</div>
    <div class="takeaway-text">
      <b>PC1 (${pca.pc1_variance}%): Broad Consumption & Leniency</b><br>
      Users with positive PC1 scores tend to be omnivorous viewers with high average engagement across multiple standard genres.<br><br>
      <b>PC2 (${pca.pc2_variance}%): Genre Polarization Axis</b><br>
      Differentiates high-octane spectacle viewers (Action, Sci-Fi, Adventure) from character-driven narrative audiences (Drama, Romance, Documentary).<br><br>
      <b>Age Group Dispersion:</b><br>
      Demographic cohorts overlap significantly in latent space, proving that genre taste transcends simple age silos.
    </div>`;

  // Group points by age group
  const ageGroups = {};
  const ageColors = {
    'Under 18': '#E11D48', '18-24': '#F97316', '25-34': '#FBBF24',
    '35-44': '#10B981', '45-49': '#0EA5E9', '50-55': '#6366F1', '56+': '#A855F7'
  };

  pca.points.forEach(p => {
    if (!ageGroups[p.age]) ageGroups[p.age] = { x: [], y: [] };
    ageGroups[p.age].x.push(p.pc1);
    ageGroups[p.age].y.push(p.pc2);
  });

  const traces = Object.entries(ageGroups).map(([name, pts]) => ({
    type: 'scatter', mode: 'markers', name,
    x: pts.x, y: pts.y,
    marker: { size: 4, color: ageColors[name] || '#888', opacity: 0.55 }
  }));

  Plotly.newPlot('chart-pca-scatter', traces, getPlotlyLayout({
    height: 500,
    extra: { title: `User Preference Projection (${fmt(pca.num_users)} Users)` },
    xaxis: { title: `Principal Component 1 (${pca.pc1_variance}% Variance)` },
    yaxis: { title: `Principal Component 2 (${pca.pc2_variance}% Variance)` }
  }), getPlotlyConfig());

  // Loadings
  const loadings = pca.loadings;
  const genresSorted1 = Object.keys(loadings).sort((a, b) => loadings[a].pc1 - loadings[b].pc1);
  const genresSorted2 = Object.keys(loadings).sort((a, b) => loadings[a].pc2 - loadings[b].pc2);

  Plotly.newPlot('chart-pc1-loadings', [{
    type: 'bar',
    x: genresSorted1.map(g => loadings[g].pc1),
    y: genresSorted1,
    orientation: 'h',
    marker: { color: genresSorted1.map(g => loadings[g].pc1 > 0 ? '#6366F1' : '#94A3B8') }
  }], getPlotlyLayout({
    height: 450,
    extra: { title: 'Genre Contributions to PC1 (Breadth)' },
    xaxis: { title: 'Loading Weight on PC1' }
  }), getPlotlyConfig());

  Plotly.newPlot('chart-pc2-loadings', [{
    type: 'bar',
    x: genresSorted2.map(g => loadings[g].pc2),
    y: genresSorted2,
    orientation: 'h',
    marker: { color: genresSorted2.map(g => loadings[g].pc2 > 0 ? '#0EA5E9' : '#F97316') }
  }], getPlotlyLayout({
    height: 450,
    extra: { title: 'Genre Contributions to PC2 (Spectacle vs. Narrative)' },
    xaxis: { title: 'Loading Weight on PC2' }
  }), getPlotlyConfig());
}

// ============================================================
// PAGE: AGE & GENRE
// ============================================================
function renderAgeGenre() {
  const ag = DATA.age_genre;
  pageCharts['age-genre'] = true;

  const ageOrder = ['Under 18', '18-24', '25-34', '35-44', '45-49', '50-55', '56+'];
  const genres = ag.genres;

  // Heatmap
  const zData = ageOrder.map(a => genres.map(g => ag.heatmap[a][g]));
  Plotly.newPlot('chart-age-genre-heatmap', [{
    type: 'heatmap',
    z: zData,
    x: genres,
    y: ageOrder,
    colorscale: 'Viridis',
    text: zData.map(row => row.map(v => v.toFixed(2))),
    texttemplate: '%{text}',
    hovertemplate: 'Age: %{y}<br>Genre: %{x}<br>Rating: %{z:.2f}<extra></extra>'
  }], getPlotlyLayout({
    height: 440,
    extra: { title: 'Average Movie Rating by Age Group and Genre' },
    xaxis: { title: 'Movie Genre' },
    yaxis: { title: 'Age Cohort' }
  }), getPlotlyConfig());

  // Max Genre Table
  let maxHtml = '<table class="data-table"><thead><tr><th>Age Cohort</th><th>Highest-Rated Genre</th><th>Peak Rating</th></tr></thead><tbody>';
  ag.max_genres.forEach(r => {
    maxHtml += `<tr><td>${r.age_group}</td><td><b>${r.genre}</b></td><td>${r.rating.toFixed(2)}</td></tr>`;
  });
  maxHtml += '</tbody></table>';
  document.getElementById('age-max-genre-table').innerHTML = maxHtml;

  // Top 5 Genres by Age - Grouped Bar
  const traces = [];
  ageOrder.forEach((age, i) => {
    const top5 = ag.top5_by_age[age];
    traces.push({
      type: 'bar',
      name: age,
      x: top5.map(t => t.genre),
      y: top5.map(t => t.count),
      marker: { color: `hsl(${i * 45}, 65%, 50%)` }
    });
  });

  Plotly.newPlot('chart-top-genres-by-age', traces, getPlotlyLayout({
    height: 440,
    extra: { title: 'Top 5 Most Rated Movie Genres for Each Age Group', barmode: 'group' },
    xaxis: { title: 'Genre' },
    yaxis: { title: 'Number of Ratings Given' }
  }), getPlotlyConfig());
}

// ============================================================
// PAGE: KEY FINDINGS
// ============================================================
function renderFindings() {
  const k = DATA.kpis;
  const ga = DATA.genre_analytics;
  const gp = DATA.genre_pairs;
  const ar = DATA.association_rules;

  const topGenreVol = Object.entries(ga.rating_count).sort((a, b) => b[1] - a[1])[0];
  const topGenreAvg = Object.entries(ga.avg_rating).sort((a, b) => b[1] - a[1])[0];
  const topPair = gp.reliable_pairs[0];
  const topRule = ar.rules[0];

  // Scorecard Table
  const scorecard = [
    ['Total Catalog Movies', fmt(k.total_movies)],
    ['Total Logged Ratings', fmt(k.total_ratings)],
    ['Overall Average Rating', `${k.mean_rating.toFixed(2)} / 5.00`],
    ['Most Frequent Rating (Mode)', `Rating ${k.mode_rating} (34.9% of all ratings)`],
    ['Highest Volume Genre', `${topGenreVol[0]} (${fmt(topGenreVol[1])} ratings)`],
    ['Highest Average Rated Genre', `${topGenreAvg[0]} (${topGenreAvg[1]} average rating)`],
    ['Highest Rated Genre Pair (≥500)', `${topPair.pair} (${topPair.mean.toFixed(2)} average rating)`],
    ['Highest-Lift Association Rule', topRule.rule],
    ['Peak Association Rule Lift', `${topRule.lift.toFixed(2)}x lift factor`],
  ];

  let html = '<table class="data-table"><thead><tr><th>Mining Metric / Finding</th><th>Empirical Value</th></tr></thead><tbody>';
  scorecard.forEach(([metric, value]) => {
    html += `<tr><td><b>${metric}</b></td><td>${value}</td></tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('scorecard-table').innerHTML = html;

  // Finding Cards
  document.getElementById('findings-cards').innerHTML = `
    <div>
      <div class="card">
        <div class="card-title">⭐ Rating Distribution & Skewness</div>
        <div class="card-subtitle">Global Audience Tendency</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          The overall mean rating is <b>${k.mean_rating.toFixed(2)}</b> with a standard deviation of 1.12.
          <b>Rating 4</b> is the modal score (34.9%), and ratings 4 and 5 collectively constitute <b>57.5%</b> of the entire repository.
          Users demonstrate a distinct propensity to rate titles they enjoy rather than log negative feedback.
        </div>
      </div>
      <div class="card">
        <div class="card-title">🏆 Genre Quality: The Film-Noir Benchmark</div>
        <div class="card-subtitle">Critical Acclaim vs Audience Volume</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          <b>Film-Noir</b> achieved the highest average rating (<b>${ga.avg_rating['Film-Noir']}</b>) across all 18 genres.
          Furthermore, <b>${ga.five_star_pct['Film-Noir']}%</b> of all Film-Noir ratings were a perfect 5 stars.
          In contrast, <b>Horror</b> had the lowest average rating at <b>${ga.avg_rating['Horror']}</b>.
        </div>
      </div>
      <div class="card">
        <div class="card-title">🔗 Genre Synergies: ${topPair.pair}</div>
        <div class="card-subtitle">Multi-Genre Combination Performance</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          Among genre combinations with statistical significance (minimum 500 ratings),
          the pairing of <b>${topPair.pair}</b> ranked #1 with an average rating of <b>${topPair.mean.toFixed(2)}</b>.
        </div>
      </div>
    </div>
    <div>
      <div class="card">
        <div class="card-title">📦 Commercial Volume vs. Critical Acclaim</div>
        <div class="card-subtitle">Market Domination by Comedy & Drama</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          <b>Comedy</b> (${fmt(ga.rating_count['Comedy'])} ratings) and <b>Drama</b> (${fmt(ga.rating_count['Drama'])} ratings) account for more than <b>70%</b> of all user interactions.
          However, their mean ratings (Comedy: ${ga.avg_rating['Comedy']}, Drama: ${ga.avg_rating['Drama']}) position them near the average.
        </div>
      </div>
      <div class="card">
        <div class="card-title">🧬 Apriori Rule Discovery: ${topRule.rule}</div>
        <div class="card-subtitle">Maximum Lift Factor (${topRule.lift.toFixed(2)}x)</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          Applying Apriori with a 2% support threshold identified <b>${topRule.rule}</b> as the strongest association.
          With a <b>Lift of ${topRule.lift.toFixed(2)}</b> and <b>Confidence of ${topRule.confidence.toFixed(1)}%</b>.
        </div>
      </div>
      <div class="card">
        <div class="card-title">👥 Demographics: Generational Leniency Trend</div>
        <div class="card-subtitle">Age Cohort Rating Behavior</div>
        <div style="font-size:0.925rem; line-height:1.65;">
          Mean rating correlates with viewer age: viewers aged <b>56+</b> exhibit the highest average rating (<b>${DATA.age_genre.age_avg_rating['56+']}</b>),
          whereas youth viewers (<b>Under 18</b>) give the lowest average rating (<b>${DATA.age_genre.age_avg_rating['Under 18']}</b>).
        </div>
      </div>
    </div>`;
}

// ============================================================
// PAGE: METHODOLOGY
// ============================================================
function renderMethodology() {
  const steps = [
    { step: 'Step 1', title: 'Raw Data Ingestion', desc: 'Loaded 1,000,209 ratings, 3,883 movies, and 6,040 users from plain-text .dat files using double-colon separators (::) and latin-1 encoding.', badge: 'Pandas / I/O' },
    { step: 'Step 2', title: 'Demographic & Relational Preprocessing', desc: 'Mapped numeric age codes to 7 cohorts (Under 18 to 56+), decoded 21 occupational codes, and performed relational joins on UserID and MovieID.', badge: 'Feature Engineering' },
    { step: 'Step 3', title: 'Exploratory Profiling & Multi-Label Explosion', desc: 'Exploded pipe-separated genre strings into 18 atomic genres. Computed rating distributions, skewness, 5-star ratios, and pairwise genre co-occurrences.', badge: 'EDA & Aggregation' },
    { step: 'Step 4', title: 'Frequent Itemset & Association Rule Mining', desc: 'Constructed binary incidence matrix across 18 genres. Applied the Apriori algorithm with min_support=0.02 and min_confidence=0.30 to discover high-lift genre rules.', badge: 'Apriori / MLxtend' },
    { step: 'Step 5', title: 'Unsupervised Dimensionality Reduction (PCA)', desc: 'Built a 6,040 × 18 User-Genre mean rating matrix. Applied Z-score standardization (StandardScaler) followed by 2-component PCA to map user preference segments.', badge: 'PCA / Scikit-learn' },
    { step: 'Step 6', title: 'Demographic Cross-Tabulation & Synthesis', desc: 'Cross-analyzed user age brackets against genre popularity, average ratings, and preference clusters to generate empirical conclusions.', badge: 'Empirical Synthesis' },
  ];

  let html = '';
  steps.forEach((item, i) => {
    const isLast = i === steps.length - 1;
    html += `
      <div class="pipeline-step">
        <div class="pipeline-connector">
          <div class="pipeline-dot"></div>
          ${!isLast ? '<div class="pipeline-line"></div>' : ''}
        </div>
        <div class="pipeline-content">
          <div class="card" style="margin-bottom:0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;">
              <div style="font-weight:800; font-size:1.05rem; color:var(--brand-primary);">${item.step}: ${item.title}</div>
              <span class="badge">${item.badge}</span>
            </div>
            <div style="font-size:0.9rem; line-height:1.6;">${item.desc}</div>
          </div>
        </div>
      </div>`;
  });

  document.getElementById('methodology-pipeline').innerHTML = html;
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
  // Restore theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';
  document.getElementById('theme-label').textContent = savedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';

  // Load data
  try {
    await loadAllData();
    updateSidebarStats();
    renderOverview();
    pageRendered['overview'] = true;
  } catch (err) {
    document.getElementById('main-content').innerHTML = `
      <div class="card" style="text-align:center; padding:40px;">
        <h2>Error Loading Data</h2>
        <p style="margin-top:10px;">Could not load JSON data files. Make sure to serve the site from a local HTTP server:</p>
        <code style="display:block; margin-top:10px; padding:10px;">python -m http.server 5500</code>
        <p style="margin-top:10px; color:var(--text-muted); font-size:0.85rem;">Error: ${err.message}</p>
      </div>`;
  }

  // Navigation
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      navigateTo(btn.getAttribute('data-page'));
    });
  });
});
