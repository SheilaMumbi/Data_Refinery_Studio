import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Refinery Studio",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;600;700&family=Syne:wght=400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
code, pre, .stCode, .stDataFrame { font-family: 'JetBrains Mono', monospace !important; }

.stApp { background: #0b0f1a; color: #e2e8f0; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }

[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid #1e2d40; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stFileUploader label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important; font-size: 0.78rem;
    letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600;
}

.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2234 100%);
    border: 1px solid #1e3a5f; border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.6rem;
}
.metric-card h4 {
    color: #64748b; font-size: 0.7rem; letter-spacing: 0.12em;
    text-transform: uppercase; margin: 0 0 0.3rem 0;
    font-family: 'JetBrains Mono', monospace;
}
.metric-card .value {
    color: #38bdf8; font-size: 1.8rem; font-weight: 700;
    font-family: 'JetBrains Mono', monospace; line-height: 1;
}
.metric-card .label { color: #475569; font-size: 0.72rem; margin-top: 0.2rem; }

.section-header {
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.05rem;
    color: #e2e8f0; letter-spacing: 0.03em; padding: 0.6rem 0 0.4rem 0;
    border-bottom: 1px solid #1e2d40; margin-bottom: 1rem;
}

.clean-badge {
    display: inline-block; background: #052e16;
    border: 1px solid #16a34a; color: #4ade80;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    padding: 2px 10px; border-radius: 20px; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace; margin-left: 6px;
}
.warn-badge {
    display: inline-block; background: #431407;
    border: 1px solid #ea580c; color: #fb923c;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    padding: 2px 10px; border-radius: 20px; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace; margin-left: 6px;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2.2rem;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1; letter-spacing: -0.02em;
}
.hero-sub {
    color: #475569; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em; margin-top: 0.3rem;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: #111827; border-radius: 10px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 8px; color: #64748b;
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
    font-weight: 600; letter-spacing: 0.06em; padding: 8px 18px;
}
.stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #38bdf8 !important; }
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    color: white; border: none; border-radius: 8px;
    font-family: 'Syne', sans-serif; font-weight: 700;
    font-size: 0.9rem; letter-spacing: 0.04em;
    padding: 0.6rem 2rem; transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; border: none; }
.stAlert { border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
.stDataFrame { border-radius: 8px; border: 1px solid #1e2d40; }
hr { border-color: #1e2d40; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
for key, default in {
    "df_raw": None,
    "df_cleaned": None,
    "cleaning_log": [],
    "cleaning_done": False,
    "_last_file": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Plotly Theme ───────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono, monospace", color="#94a3b8", size=11),
    xaxis=dict(gridcolor="#1e2d40", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#1e2d40", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    margin=dict(l=40, r=20, t=40, b=40),
)

# ─── Data Loading Helpers ───────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> pd.DataFrame:
    import io
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    return pd.DataFrame({
        "Missing Count": missing,
        "Missing %": pct,
        "Dtype": df.dtypes,
    }).sort_values("Missing Count", ascending=False)


# ─── Data Cleaning Engine ───────────────────────────────────────────────────────
def clean_dataframe(
    df: pd.DataFrame,
    drop_duplicates: bool,
    drop_missing_thresh: float,
    num_fill: str,
    cat_fill: str,
    strip_whitespace: bool,
    fix_dtypes: bool,
) -> tuple[pd.DataFrame, list[str]]:
    log = []
    df = df.copy()
    original_shape = df.shape

    if strip_whitespace:
        str_cols = df.select_dtypes(include="object").columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace("nan", np.nan)
        log.append(f"✅ Stripped whitespace from {len(str_cols)} string column(s).")

    if drop_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        log.append(f"✅ Removed {removed:,} duplicate row(s). ({before:,} → {len(df):,} rows)")

    if drop_missing_thresh < 1.0:
        before_cols = df.shape[1]
        thresh = int((1 - drop_missing_thresh) * len(df))
        df = df.dropna(thresh=thresh, axis=1)
        dropped = before_cols - df.shape[1]
        if dropped:
            log.append(f"✅ Dropped {dropped} column(s) with >{drop_missing_thresh*100:.0f}% missing values.")

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        if num_fill == "Median":
            df[num_cols] = df[num_cols].fillna(df[num_cols].median())
        elif num_fill == "Mean":
            df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
        elif num_fill == "Zero":
            df[num_cols] = df[num_cols].fillna(0)
        elif num_fill == "Drop rows":
            before = len(df)
            df = df.dropna(subset=num_cols)
            log.append(f"✅ Dropped {before - len(df):,} row(s) with missing numerical values.")
        if num_fill != "Drop rows":
            log.append(f"✅ Filled missing numerical values using {num_fill} ({len(num_cols)} column(s)).")

    cat_cols = df.select_dtypes(include="object").columns.tolist()
    if cat_cols:
        if cat_fill == "Mode":
            for col in cat_cols:
                mode_val = df[col].mode()
                df[col] = df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")
        elif cat_fill == "Constant: 'Unknown'":
            df[cat_cols] = df[cat_cols].fillna("Unknown")
        elif cat_fill == "Drop rows":
            before = len(df)
            df = df.dropna(subset=cat_cols)
            log.append(f"✅ Dropped {before - len(df):,} row(s) with missing categorical values.")
        if cat_fill != "Drop rows":
            log.append(f"✅ Filled missing categorical values using {cat_fill} ({len(cat_cols)} column(s)).")

    if fix_dtypes:
        converted = []
        for col in df.select_dtypes(include="object").columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="raise")
                converted.append(col)
            except Exception:
                pass
        if converted:
            log.append(f"✅ Auto-converted {len(converted)} column(s) to numeric: {', '.join(converted)}.")

    final_shape = df.shape
    log.insert(0, f"📐 Shape Transformation: {original_shape[0]:,}×{original_shape[1]} → {final_shape[0]:,}×{final_shape[1]}")
    return df, log


# ─── Sidebar Panel ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title">🧼 Data Clean</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// processing & validation studio</div>', unsafe_allow_html=True)
    st.markdown("---")

    uploaded = st.file_uploader("Upload CSV Dataset", type=["csv"])
    df = None

    if uploaded:
        try:
            df = load_csv(uploaded.read())
            if (st.session_state["df_raw"] is None or
                    st.session_state["_last_file"] != uploaded.name):
                st.session_state["df_raw"] = df
                st.session_state["df_cleaned"] = None
                st.session_state["cleaning_done"] = False
                st.session_state["cleaning_log"] = []
                st.session_state["_last_file"] = uploaded.name
            st.success(f"Loaded · {df.shape[0]:,} rows × {df.shape[1]} cols")
        except Exception as e:
            st.error(f"Read error: {e}")

    if st.session_state["df_raw"] is not None and df is None:
        df = st.session_state["df_raw"]

    st.markdown("---")
    if df is not None:
        if st.session_state["cleaning_done"]:
            st.markdown('<span class="clean-badge">✔ Pipeline Executed</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="warn-badge">⚠ Untreated Raw Data</span>', unsafe_allow_html=True)
            st.caption("Apply treatment settings within the **Data Cleaning** workflow tab.")

# ─── Main Interface ─────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Data Clean Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// profile · clean · evaluate diagnostics · download</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if df is None:
    st.info("⬅  Upload a raw CSV target dataset from the sidebar utility to get started.")
    st.stop()

tab1, tab2 = st.tabs([
    "📊 Structural Analysis Summary",
    "🧹 Data Cleaning Engine",
])

# ── Tab 1: Data Overview ────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Dataset Profile</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f'<div class="metric-card"><h4>Rows</h4><div class="value">{df.shape[0]:,}</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="metric-card"><h4>Columns</h4><div class="value">{df.shape[1]}</div></div>', unsafe_allow_html=True)
    with col_c:
        total_missing = df.isnull().sum().sum()
        st.markdown(f'<div class="metric-card"><h4>Missing Records</h4><div class="value">{total_missing:,}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True, height=280)

    st.markdown('<div class="section-header">Null-Value Diagnostics Breakdown</div>', unsafe_allow_html=True)
    st.dataframe(get_missing_summary(df), use_container_width=True)

    st.markdown('<div class="section-header">Descriptive Features Statistics</div>', unsafe_allow_html=True)
    st.dataframe(df.describe(include="all").T, use_container_width=True)


# ── Tab 2: Data Cleaning ────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Processing Engine Parameters</div>', unsafe_allow_html=True)

    with st.expander("⚙️ Refine Imputation & Pruning Directives", expanded=True):
        cl1, cl2 = st.columns(2)
        with cl1:
            drop_duplicates  = st.checkbox("Prune duplicate records (rows)", value=True)
            strip_whitespace = st.checkbox("Trim trailing/leading string whitespace", value=True)
            fix_dtypes       = st.checkbox("Parse and convert text-encoded integers/floats", value=True)
        with cl2:
            drop_missing_thresh = st.slider(
                "Drop entire column structural indices missing over:",
                min_value=0.1, max_value=1.0, value=0.6, step=0.05, format="%.0f%%",
            )
            num_fill = st.selectbox(
                "Numerical Imputation Assignment Scheme",
                ["Median", "Mean", "Zero", "Drop rows"], index=0
            )
            cat_fill = st.selectbox(
                "Categorical Imputation Assignment Scheme",
                ["Mode", "Constant: 'Unknown'", "Drop rows"], index=0
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_run, col_reset = st.columns([1, 5])
    with col_run:
        run_clean = st.button("🧹 Execute Rules Matrix")
    with col_reset:
        if st.button("↺ Revert to Raw Structure"):
            st.session_state["df_cleaned"] = None
            st.session_state["cleaning_done"] = False
            st.session_state["cleaning_log"] = []
            st.rerun()

    if run_clean:
        with st.spinner("Executing rule transforms against target elements..."):
            try:
                cleaned_df, log = clean_dataframe(
                    df,
                    drop_duplicates=drop_duplicates,
                    drop_missing_thresh=drop_missing_thresh,
                    num_fill=num_fill,
                    cat_fill=cat_fill,
                    strip_whitespace=strip_whitespace,
                    fix_dtypes=fix_dtypes,
                )
                st.session_state["df_cleaned"] = cleaned_df
                st.session_state["cleaning_log"] = log
                st.session_state["cleaning_done"] = True
            except Exception as e:
                st.error(f"Execution Error Exception Encountered: {e}")

    if st.session_state["cleaning_done"] and st.session_state["df_cleaned"] is not None:
        cleaned_df = st.session_state["df_cleaned"]
        log        = st.session_state["cleaning_log"]

        st.markdown("---")
        st.markdown('<div class="section-header">System Operation Reports</div>', unsafe_allow_html=True)
        for entry in log:
            st.markdown(entry)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Variance Summary: Before vs. After</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><h4>Initial Rows</h4><div class="value">{df.shape[0]:,}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><h4>Processed Rows</h4><div class="value">{cleaned_df.shape[0]:,}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><h4>Initial Columns</h4><div class="value">{df.shape[1]}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><h4>Processed Columns</h4><div class="value">{cleaned_df.shape[1]}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        missing_before = df.isnull().sum().sum()
        missing_after  = cleaned_df.isnull().sum().sum()
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown(f'<div class="metric-card"><h4>Raw Missing Total Cells</h4><div class="value" style="color:#fb923c">{missing_before:,}</div></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="metric-card"><h4>Residual Missing Total Cells</h4><div class="value" style="color:#4ade80">{missing_after:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Heatmap Distribution Matrix (Post-Treatment)</div>', unsafe_allow_html=True)
        sample = cleaned_df.isnull().astype(int)
        if len(sample) > 300:
            sample = sample.sample(300, random_state=42)
        fig_heat = px.imshow(
            sample.T,
            color_continuous_scale=[[0, "#1e2d40"], [1, "#38bdf8"]],
            labels=dict(x="Sequential Index", y="Feature Vector", color="State Matrix"),
            title="Sparsity Mapping Summary (Blue Indicators Reflect Unresolved Fields)",
            aspect="auto",
        )
        fig_heat.update_layout(**PLOTLY_THEME, title_font_size=13, coloraxis_showscale=False, height=300)
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Processed Target Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(cleaned_df.head(50), use_container_width=True, height=280)

        # ─── Export Workspace Asset ──────────────────────────────────────────
        st.markdown('<div class="section-header">Export Workspace Asset</div>', unsafe_allow_html=True)
        
        @st.cache_data
        def convert_df_to_csv(target_dataframe):
            return target_dataframe.to_csv(index=False).encode('utf-8')

        csv_data = convert_df_to_csv(cleaned_df)
        
        st.download_button(
            label="💾 Download Processed Dataset (.CSV)",
            data=csv_data,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
        )

    elif not st.session_state["cleaning_done"]:
        st.info("Configure the parameters above and initialize via 'Execute Rules Matrix' to generate staging assets.")