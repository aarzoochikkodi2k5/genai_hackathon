
"""
app.py — AI Sports Commentary Generator (UPGRADED)
Run: python -m streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()

import json, io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Sports Command Center",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

:root {
  --red:#e8122c; --red-glow:rgba(232,18,44,0.35);
  --cyan:#00e5ff; --cyan-glow:rgba(0,229,255,0.3);
  --gold:#ffb300; --gold-glow:rgba(255,179,0,0.3);
  --green:#00e676; --purple:#ce93d8;
  --bg:#060a12; --surface:#0c1220; --surface2:#101828;
  --border:rgba(255,255,255,0.07); --border2:rgba(255,255,255,0.12);
  --text:#e8eaf0; --muted:#7a8599; --faint:#3a4455;
  --font-display:'Barlow Condensed',sans-serif;
  --font-body:'Barlow',sans-serif;
  --font-mono:'Space Mono',monospace;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #060a12 !important;
    color: #e8eaf0 !important;
    font-family: 'Barlow', sans-serif !important;
}

/* Animated grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(0,229,255,0.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.018) 1px, transparent 1px);
    background-size: 64px 64px;
    animation: gridDrift 30s linear infinite;
}
@keyframes gridDrift { 0%{background-position:0 0} 100%{background-position:64px 64px} }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #090e1a !important;
    border-right: 1px solid rgba(0,229,255,0.12) !important;
}
[data-testid="stSidebar"] * { color: #b0bcd0 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {
    color: #00e5ff !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: 1px;
}
[data-testid="stSidebar"] .stRadio label { color: #e8eaf0 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Header ── */
.cmd-header {
    background: linear-gradient(180deg, #080d1a 0%, rgba(6,10,18,0) 100%);
    padding: 3rem 2rem 2rem;
    text-align: center;
    border-bottom: 1px solid rgba(0,229,255,0.12);
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.cmd-header::before {
    content: '';
    position: absolute; top: -120px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse, rgba(0,229,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(232,18,44,0.12); border: 1px solid rgba(232,18,44,0.3);
    border-radius: 100px; padding: 4px 14px; margin-bottom: 16px;
    font-family: 'Space Mono', monospace; font-size: 10px; color: #e8122c;
    letter-spacing: 2px; text-transform: uppercase;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #e8122c; animation: blink 1.2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.cmd-title {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 4.5rem; font-weight: 900; line-height: 0.9;
    background: linear-gradient(135deg, #ffffff 0%, #00e5ff 45%, #e8122c 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -1px; margin-bottom: 0.5rem;
}
.cmd-sub {
    color: #7a8599; font-size: 0.95rem; font-weight: 300;
    letter-spacing: 1px; margin: 0;
}
.header-metrics {
    display: flex; justify-content: center; gap: 48px;
    margin-top: 2rem; padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.hm-val { font-family:'Barlow Condensed',sans-serif; font-size:1.9rem; font-weight:800; line-height:1; }
.hm-lbl { font-family:'Space Mono',monospace; font-size:0.65rem; color:#7a8599;
           text-transform:uppercase; letter-spacing:1.5px; margin-top:3px; }

/* ── Cards ── */
.cmd-card {
    background: #0c1220;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.5rem;
    position: relative; overflow: hidden;
    margin-bottom: 1rem;
}
.cmd-card::before {
    content:''; position:absolute; inset:0; border-radius:14px;
    background: linear-gradient(135deg, rgba(255,255,255,0.015) 0%, transparent 60%);
    pointer-events: none;
}
.card-glow-top-cyan::after {
    content:''; position:absolute; top:-1px; left:16px; right:16px; height:1px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
}
.card-glow-top-red::after {
    content:''; position:absolute; top:-1px; left:16px; right:16px; height:1px;
    background: linear-gradient(90deg, transparent, #e8122c, transparent);
}
.card-glow-top-gold::after {
    content:''; position:absolute; top:-1px; left:16px; right:16px; height:1px;
    background: linear-gradient(90deg, transparent, #ffb300, transparent);
}

/* ── Score Hero ── */
.score-hero {
    background: linear-gradient(135deg, #0a0f1e 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px; padding: 2.2rem 1.5rem;
    text-align: center; position: relative; overflow: hidden;
    margin: 0.75rem 0;
}
.score-hero::before {
    content:''; position:absolute; top:-80px; left:50%; transform:translateX(-50%);
    width:320px; height:320px;
    background: radial-gradient(circle, rgba(0,229,255,0.07) 0%, transparent 70%);
    pointer-events:none;
}
.sh-teams {
    font-family:'Space Mono',monospace; font-size:0.75rem;
    color:#7a8599; letter-spacing:2px; text-transform:uppercase; margin-bottom:0.6rem;
}
.sh-score {
    font-family:'Barlow Condensed',sans-serif; font-size:4rem;
    font-weight:900; letter-spacing:4px; line-height:1;
}
.sh-venue { font-family:'Space Mono',monospace; font-size:0.7rem; color:#7a8599; margin-top:0.6rem; }
.sh-winner {
    display:inline-block; margin-top:0.8rem;
    background:rgba(0,230,118,0.1); border:1px solid rgba(0,230,118,0.3);
    border-radius:100px; padding:4px 16px;
    font-family:'Space Mono',monospace; font-size:0.65rem;
    color:#00e676; letter-spacing:1.5px; text-transform:uppercase;
}

/* ── Section labels ── */
.sec-label {
    font-family:'Space Mono',monospace; font-size:0.65rem;
    letter-spacing:2px; text-transform:uppercase;
    color:#7a8599; margin-bottom:0.75rem;
    display:flex; align-items:center; gap:10px;
}
.sec-label::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.06); }

/* ── Stat boxes ── */
.stat-box {
    background: #0c1220; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 1.1rem 1.3rem;
    position: relative; overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.stat-box:hover { border-color: rgba(255,255,255,0.12); transform: translateY(-2px); }
.stat-box-accent { position:absolute; left:0; top:0; bottom:0; width:3px; border-radius:3px 0 0 3px; }
.stat-val {
    font-family:'Barlow Condensed',sans-serif; font-size:2rem;
    font-weight:800; line-height:1; margin-bottom:4px;
}
.stat-lbl {
    font-family:'Space Mono',monospace; font-size:0.6rem;
    color:#7a8599; text-transform:uppercase; letter-spacing:1.5px;
}
.stat-sub { font-size:0.75rem; color:#7a8599; margin-top:4px; }

/* ── Commentary boxes ── */
.commentary-en {
    background: linear-gradient(135deg, rgba(0,229,255,0.04), transparent);
    border-left: 3px solid #00e5ff; border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem; color: #c0f0f8;
    line-height: 1.9; font-size: 0.88rem; margin: 0.5rem 0;
}
.commentary-kn {
    background: linear-gradient(135deg, rgba(232,18,44,0.04), transparent);
    border-left: 3px solid #e8122c; border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem; color: #ffd0d0;
    line-height: 2.1; font-size: 0.95rem; margin: 0.5rem 0;
}
.commentary-label {
    font-family:'Barlow Condensed',sans-serif; font-weight:700;
    font-size:0.8rem; letter-spacing:1.5px; text-transform:uppercase;
    margin-bottom:6px;
}

/* ── Highlight cards ── */
.highlight-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 0.65rem 1rem;
    margin: 0.3rem 0; font-size:0.85rem;
    display:flex; align-items:center; gap:10px;
    transition: border-color 0.2s;
}
.highlight-card:hover { border-color: rgba(0,229,255,0.25); }

/* ── Player of Match ── */
.pom-card {
    background: linear-gradient(135deg, rgba(255,179,0,0.08), rgba(255,179,0,0.02));
    border: 1px solid rgba(255,179,0,0.3);
    border-radius: 14px; padding: 1.3rem 1.6rem;
    position: relative; overflow: hidden; margin: 0.8rem 0;
}
.pom-card::before {
    content:'★ PLAYER OF THE MATCH';
    position:absolute; top:-8px; left:16px;
    font-family:'Space Mono',monospace; font-size:0.6rem;
    letter-spacing:2px; color:#ffb300;
    background:#060a12; padding:2px 8px;
}
.pom-name { font-family:'Barlow Condensed',sans-serif; font-size:1.5rem; font-weight:700; color:#ffb300; margin:6px 0 3px; }
.pom-detail { font-size:0.82rem; color:rgba(255,179,0,0.65); }

/* ── Football score ── */
.fb-score-hero {
    background: linear-gradient(135deg, #0f0509 0%, #180c0c 100%);
    border: 1px solid rgba(232,18,44,0.2);
    border-radius: 18px; padding: 2.2rem 1.5rem;
    text-align:center; position:relative; overflow:hidden;
    margin: 0.75rem 0;
}
.fb-score-num {
    font-family:'Barlow Condensed',sans-serif;
    font-size:4.5rem; font-weight:900; letter-spacing:6px;
}
.goal-card {
    background: linear-gradient(135deg, rgba(0,230,118,0.05), transparent);
    border-left: 3px solid #00e676; border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem; margin: 0.3rem 0;
    color:#b0ffd8; font-size:0.85rem;
    display:flex; align-items:center; gap:10px;
}

/* ── Tournament stat metric ── */
.metric-card {
    background: linear-gradient(135deg, #101828, #0c1624);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.3rem;
    text-align:center; transition:transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform:translateY(-3px); border-color:rgba(0,229,255,0.2); }
.metric-val {
    font-family:'Barlow Condensed',sans-serif;
    font-size:2.2rem; font-weight:800; color:#60a5fa;
    line-height:1; margin-bottom:4px;
}
.metric-lbl {
    font-family:'Space Mono',monospace; font-size:0.6rem;
    color:#7a8599; text-transform:uppercase; letter-spacing:1.5px;
}
.metric-sub { font-size:0.8rem; color:#94a3b8; margin-top:4px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #090e1a !important;
    border-radius: 10px !important; padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #7a8599 !important;
    border-radius: 8px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important; letter-spacing: 1px !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,229,255,0.1) !important;
    color: #00e5ff !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00c4d8, #0070e0) !important;
    border: none !important; border-radius: 10px !important;
    color: #fff !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important; font-weight: 800 !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 6px 28px rgba(0,200,220,0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 40px rgba(0,200,220,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #e8122c, #ff5722) !important;
    box-shadow: 0 6px 28px rgba(232,18,44,0.35) !important;
}

/* ── Selectbox / inputs ── */
.stSelectbox > div > div {
    background: #101828 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: #e8eaf0 !important;
}
.stSelectbox label, .stRadio label, .stSlider label,
.stNumberInput label, .stTextInput label, .stTextArea label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important; color: #7a8599 !important;
    text-transform: uppercase !important; letter-spacing: 1.5px !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #101828 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important; color: #e8eaf0 !important;
}
.stTextArea textarea {
    background: #101828 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important; color: #e8eaf0 !important;
}
.stSlider > div > div > div { background: #00e5ff !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* ── Radio ── */
.stRadio > div { gap: 4px !important; }
.stRadio > div > label {
    background: #0c1220 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; padding: 8px 14px !important;
}
.stRadio > div > label:has(input:checked) {
    background: rgba(0,229,255,0.08) !important;
    border-color: rgba(0,229,255,0.3) !important;
    color: #00e5ff !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0c1220 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    font-family:'Barlow Condensed',sans-serif !important;
    font-weight:700 !important; letter-spacing:1px !important;
    text-transform:uppercase !important; color:#7a8599 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #7a8599 !important;
    font-family:'Space Mono',monospace !important; font-size:0.7rem !important;
    border-radius: 8px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0c1220 !important;
    border: 1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
}

/* ── Code block ── */
.stCodeBlock { border-radius: 10px !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060a12; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: #2a3f5f; }

/* ── Info / Error ── */
.info-strip {
    background: linear-gradient(135deg, #081e3a, #0a2545);
    border-left: 3px solid #00e5ff; border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.1rem; color: #a0d8ef; font-size:0.85rem; margin:0.5rem 0;
}
.error-strip {
    background: #1a0808; border-left: 3px solid #e8122c;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.1rem; color: #f88; font-size:0.85rem; margin:0.5rem 0;
}

/* ── Award card ── */
.award-card {
    background: #0c1220; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 1.1rem 1.3rem; position:relative; overflow:hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.award-card:hover { transform:translateY(-2px); border-color:rgba(255,179,0,0.3); }
.award-card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
    background: linear-gradient(180deg, #ffb300, rgba(255,179,0,0.1));
}
.award-title {
    font-family:'Space Mono',monospace; font-size:0.6rem;
    color:#ffb300; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;
}
.award-player {
    font-family:'Barlow Condensed',sans-serif; font-size:1.2rem;
    font-weight:700; color:#e8eaf0; margin-bottom:2px;
}
.award-team { font-size:0.78rem; color:#7a8599; }

/* ── NRR badge ── */
.nrr-pos { color:#00e5ff; font-family:'Space Mono',monospace; font-size:0.8rem; }
.nrr-neg { color:#e8122c; font-family:'Space Mono',monospace; font-size:0.8rem; }
.qualified-q {
    display:inline-block; padding:2px 8px; border-radius:100px;
    font-family:'Space Mono',monospace; font-size:0.55rem;
    background:rgba(0,230,118,0.12); color:#00e676;
    border:1px solid rgba(0,230,118,0.25); text-transform:uppercase;
}

/* ── Stagger animation ── */
@keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:none} }
.stagger-1{animation:fadeUp 0.4s 0.05s ease both}
.stagger-2{animation:fadeUp 0.4s 0.1s ease both}
.stagger-3{animation:fadeUp 0.4s 0.15s ease both}
.stagger-4{animation:fadeUp 0.4s 0.2s ease both}

/* ── Success alert ── */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
PLOTLY = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,16,30,0.85)",
    font=dict(color="#b0bcd0", family="Space Mono"),
    margin=dict(l=8, r=8, t=36, b=8),
    title_font=dict(color="#60c8f8", family="Barlow Condensed", size=16),
)
GRID = dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)")
TICK = dict(tickfont=dict(color="#7a8599", size=10, family="Space Mono"))

C_CYAN   = "#00e5ff"
C_RED    = "#e8122c"
C_GOLD   = "#ffb300"
C_GREEN  = "#00e676"
C_PURPLE = "#ce93d8"
C_ORANGE = "#ff6d00"

PALETTE = [C_CYAN, C_RED, C_GOLD, C_GREEN, C_PURPLE, C_ORANGE,
           "#7986cb", "#4db6ac", "#f06292", "#aed581"]


def px_bar(df, x, y, title, color=C_CYAN, horizontal=False, text_col=None):
    kw = dict(x=y, y=x, orientation="h") if horizontal else dict(x=x, y=y)
    fig = px.bar(df, **kw, title=title, color_discrete_sequence=[color],
                 text=text_col or y)
    fig.update_traces(textposition="outside",
                      marker=dict(color=color,
                                  line=dict(color="rgba(0,0,0,0)", width=0)),
                      textfont=dict(color="#7a8599", size=9))
    fig.update_layout(**PLOTLY, title_font_size=14)
    fig.update_xaxes(**GRID, **TICK)
    fig.update_yaxes(**GRID, **TICK)
    return fig


def plotly_color_alpha(color, alpha=0.06):
    if isinstance(color, str):
        if color.startswith("rgb"):
            return color.replace("rgb(", "rgba(").replace(")", f",{alpha})")
        if color.startswith("#"):
            if len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                return f"rgba({r},{g},{b},{alpha})"
            if len(color) == 9:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                a = int(color[7:9], 16) / 255
                return f"rgba({r},{g},{b},{a})"
    return color


def px_line_multi(labels, datasets, title):
    """datasets = list of {name, data, color, dash}"""
    fig = go.Figure()
    for ds in datasets:
        fig.add_trace(go.Scatter(
            x=labels, y=ds["data"], name=ds["name"],
            line=dict(color=ds["color"], width=2,
                      dash=ds.get("dash", "solid")),
            fill="tozeroy",
            fillcolor=plotly_color_alpha(ds["color"], 0.06),
            mode="lines", hovertemplate="%{y:.1f}<extra>%{fullData.name}</extra>",
        ))
    fig.update_layout(**PLOTLY, title=title)
    fig.update_xaxes(**GRID, **TICK)
    fig.update_yaxes(**GRID, **TICK)
    return fig


def px_donut(labels, values, title, colors=None):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors or PALETTE[:len(labels)],
                    line=dict(color="#060a12", width=2)),
        textfont=dict(color="#e8eaf0", size=10),
    ))
    fig.update_layout(**PLOTLY, title=title, showlegend=True,
                      legend=dict(font=dict(color="#7a8599", size=10)))
    return fig


def px_radar(cats, vals1, vals2, name1, name2, color1=C_CYAN, color2=C_RED):
    fig = go.Figure()
    for vals, name, col in [(vals1, name1, color1), (vals2, name2, color2)]:
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", name=name,
            line=dict(color=col, width=2),
            fillcolor=plotly_color_alpha(col, 0.1),
            marker=dict(size=5, color=col),
        ))
    fig.update_layout(
        **{k: v for k, v in PLOTLY.items()
           if k not in ("plot_bgcolor",)},
        polar=dict(
            bgcolor="rgba(10,16,30,0.7)",
            radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.06)",
                            color="#7a8599", tickfont=dict(size=8)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                             color="#7a8599",
                             tickfont=dict(color="#94a3b8", size=10)),
        ),
        showlegend=True,
        legend=dict(font=dict(color="#7a8599", size=10)),
    )
    return fig


def px_scatter_bubble(df, x, y, size_col, color_col, hover_cols, title):
    fig = px.scatter(df, x=x, y=y, size=size_col, color=color_col,
                     hover_data=hover_cols, title=title,
                     color_discrete_sequence=PALETTE, size_max=50)
    fig.update_traces(marker=dict(line=dict(width=1, color="#060a12")),
                      textfont=dict(color="#e8eaf0"))
    fig.update_layout(**PLOTLY)
    fig.update_xaxes(**GRID, **TICK)
    fig.update_yaxes(**GRID, **TICK)
    return fig


def px_gauge(value, title, max_val=100, color=C_CYAN):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#7a8599", "size": 12,
                                        "family": "Space Mono"}},
        number={"font": {"color": "#e8eaf0", "size": 26,
                         "family": "Barlow Condensed"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#7a8599",
                     "tickfont": {"size": 8}},
            "bar":  {"color": color, "thickness": 0.6},
            "bgcolor": "#101828",
            "bordercolor": "#1e2a3a",
            "steps": [
                {"range": [0, max_val * .33], "color": "#111a2e"},
                {"range": [max_val * .33, max_val * .66], "color": "#141f30"},
                {"range": [max_val * .66, max_val], "color": "#111a2e"},
            ],
            "threshold": {"line": {"color": color, "width": 2},
                          "thickness": 0.8, "value": value},
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#e8eaf0"),
                      height=180,
                      margin=dict(l=16, r=16, t=40, b=8))
    return fig


def goal_timeline(goals, home_team, away_team):
    fig = go.Figure()
    fig.add_shape(type="line", x0=0, x1=95, y0=0.5, y1=0.5,
                  line=dict(color="rgba(255,255,255,0.08)", width=2))
    fig.add_shape(type="line", x0=45, x1=45, y0=0.1, y1=0.9,
                  line=dict(color=C_GOLD, width=1, dash="dash"))
    fig.add_annotation(x=45, y=0.96, text="HT", showarrow=False,
                       font=dict(color=C_GOLD, size=10, family="Space Mono"))
    for g in goals:
        col = C_CYAN if g["team"] == home_team else C_RED
        y_pos = 0.72 if g["team"] == home_team else 0.28
        fig.add_trace(go.Scatter(
            x=[g["minute"]], y=[0.5],
            mode="markers+text",
            marker=dict(size=24, color=plotly_color_alpha(col, 0.14),
                        line=dict(color=col, width=2)),
            text=[f"⚽ {g['minute']}'"],
            textposition="top center" if g["team"] == home_team else "bottom center",
            textfont=dict(color=col, size=9, family="Space Mono"),
            hovertext=f"{g['minute']}' — {g['scorer']} ({g['team']})",
            hoverinfo="text", showlegend=False,
        ))
        fig.add_annotation(
            x=g["minute"], y=y_pos,
            text=f"<b>{g['scorer']}</b>",
            showarrow=False,
            font=dict(color=col, size=9, family="Barlow Condensed"),
            align="center",
        )
    fig.update_layout(
        **PLOTLY, title="⚽ Goal Timeline",
        xaxis=dict(range=[-2, 97], title="Minute", **GRID, **TICK),
        yaxis=dict(visible=False, range=[-0.1, 1.2]),
        height=200,
    )
    return fig


def normalize_innings(raw) -> dict:
    if isinstance(raw, list):
        raw = next((x for x in raw if isinstance(x, dict)), {})
    if isinstance(raw, dict):
        keys = list(raw.keys())
        if len(keys) == 1 and isinstance(raw[keys[0]], dict):
            return raw[keys[0]]
        return raw
    return {}


# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="cmd-header">
  <div class="live-badge"><div class="live-dot"></div>LIVE · AI POWERED</div>
  <div class="cmd-title">🏏⚽ SPORTS<br>COMMAND CENTER</div>
  <p class="cmd-sub">Broadcaster-grade commentary · ICC T20 WC 2026 · ISL · English & ಕನ್ನಡ</p>
</div>
""", unsafe_allow_html=True)


# ── BOOT ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def boot():
    from src.data_parser import CricketMatchContext, FootballMatchContext, load_match_data
    from src.llm_engine import (
        generate_cricket_commentary,
        generate_cricket_post_match,
        generate_football_commentary,
    )
    from src.translator import initialize_translator, translate_to_kannada
    from src.t_loader import (
        load_tournament_data, get_match_list, build_context_from_match,
        get_tournament_summary, get_standings, get_top_batters,
        get_top_bowlers, get_awards,
    )
    initialize_translator()
    dfs = load_tournament_data("data")
    return dict(
        CricketMatchContext=CricketMatchContext,
        FootballMatchContext=FootballMatchContext,
        load_match_data=load_match_data,
        gen_cricket_commentary=generate_cricket_commentary,
        gen_cricket_post_match=generate_cricket_post_match,
        gen_football_commentary=generate_football_commentary,
        translate_to_kannada=translate_to_kannada,
        dfs=dfs,
        get_match_list=get_match_list,
        build_context_from_match=build_context_from_match,
        get_tournament_summary=get_tournament_summary,
        get_standings=get_standings,
        get_top_batters=get_top_batters,
        get_top_bowlers=get_top_bowlers,
        get_awards=get_awards,
    )


e = boot()
(dfs, CricketMatchContext, FootballMatchContext, load_match_data,
 gen_cricket_commentary, gen_cricket_post_match, gen_football_commentary,
 translate_to_kannada, get_match_list, build_context_from_match,
 get_tournament_summary, get_standings, get_top_batters,
 get_top_bowlers, get_awards) = (
    e["dfs"], e["CricketMatchContext"], e["FootballMatchContext"], e["load_match_data"],
    e["gen_cricket_commentary"], e["gen_cricket_post_match"], e["gen_football_commentary"],
    e["translate_to_kannada"], e["get_match_list"], e["build_context_from_match"],
    e["get_tournament_summary"], e["get_standings"], e["get_top_batters"],
    e["get_top_bowlers"], e["get_awards"],
)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    mode = st.radio("Mode", [
        "🏏 Cricket Commentary",
        "⚽ Football Commentary",
        "📊 Tournament Stats",
    ])

    st.markdown("---")
    st.markdown("### 🌐 Language")
    lang_mode = st.radio("Commentary Language", [
        "🇬🇧 English Only",
        "🇮🇳 Kannada Only",
        "🇬🇧🇮🇳 Both Languages",
    ], index=2)
    enable_kn = lang_mode != "🇬🇧 English Only"

    st.markdown("---")
    summary = get_tournament_summary(dfs)
    st.markdown("### 🏆 Tournament")
    key_labels = {
        "tournament_name": "Tournament", "edition": "Edition",
        "format": "Format", "hosts": "Hosts",
        "start_date": "Start", "end_date": "End",
    }
    for k, v in list(summary.items())[:6]:
        lbl = key_labels.get(k, k.replace("_", " ").title())
        st.markdown(f"**{lbl}:** {v}")

    st.markdown("---")
    st.markdown("### 📦 Stack")
    st.markdown("""
    🤖 **LLM:** Groq · LLaMA 3.3 70B  
    🌐 **NMT:** IndicTrans2  
    📊 **Data:** Kaggle ICC CSVs  
    🎨 **UI:** Streamlit + Plotly  
    """)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def show_dual(label: str, text: str, accent: str = C_CYAN):
    if not text or not isinstance(text, str):
        return
    st.markdown(f'<div class="commentary-label" style="color:{accent}">📢 {label}</div>',
                unsafe_allow_html=True)
    if lang_mode == "🇬🇧 English Only":
        st.markdown(f'<div class="commentary-en">{text}</div>', unsafe_allow_html=True)
    elif lang_mode == "🇮🇳 Kannada Only":
        kn = translate_to_kannada(text)
        st.markdown(f'<div class="commentary-kn">{kn}</div>', unsafe_allow_html=True)
    else:
        col_en, col_kn = st.columns(2)
        with col_en:
            st.markdown(f'<small style="font-family:Space Mono;color:#7a8599;font-size:0.6rem;letter-spacing:2px">🇬🇧 ENGLISH</small>', unsafe_allow_html=True)
            st.markdown(f'<div class="commentary-en">{text}</div>', unsafe_allow_html=True)
        with col_kn:
            st.markdown(f'<small style="font-family:Space Mono;color:#7a8599;font-size:0.6rem;letter-spacing:2px">🇮🇳 ಕನ್ನಡ</small>', unsafe_allow_html=True)
            kn = translate_to_kannada(text)
            st.markdown(f'<div class="commentary-kn">{kn}</div>', unsafe_allow_html=True)


def show_highlights(highlights: list, color: str = C_CYAN):
    for m in highlights:
        if not isinstance(m, str):
            continue
        if lang_mode == "🇮🇳 Kannada Only":
            kn = translate_to_kannada(m)
            st.markdown(f'<div class="highlight-card" style="border-left:3px solid {color};color:#ffd0d0">🏏 {kn}</div>', unsafe_allow_html=True)
        elif lang_mode == "🇬🇧🇮🇳 Both Languages":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="highlight-card">🏏 {m}</div>', unsafe_allow_html=True)
            with c2:
                kn = translate_to_kannada(m)
                st.markdown(f'<div class="highlight-card" style="border-left:3px solid {color};color:#ffd0d0">🏏 {kn}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="highlight-card">🏏 {m}</div>', unsafe_allow_html=True)


def show_pom(pom: dict, is_football: bool = False):
    if not pom or not isinstance(pom, dict):
        return
    en_pom = f"{pom.get('name','')} ({pom.get('team','')}) — {pom.get('reason','')}"
    if lang_mode == "🇬🇧 English Only":
        st.markdown(f'<div class="pom-card"><div class="pom-name">⭐ {pom.get("name","")}</div><div class="pom-detail">{pom.get("team","")} · {pom.get("reason","")}</div></div>', unsafe_allow_html=True)
    elif lang_mode == "🇮🇳 Kannada Only":
        kn = translate_to_kannada(en_pom)
        st.markdown(f'<div class="pom-card"><div class="pom-name">⭐ ಪಂದ್ಯದ ಶ್ರೇಷ್ಠ ಆಟಗಾರ</div><div class="pom-detail">{kn}</div></div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="pom-card"><div class="pom-name">⭐ {pom.get("name","")}</div><div class="pom-detail">{pom.get("team","")} · {pom.get("reason","")}</div></div>', unsafe_allow_html=True)
        with c2:
            kn = translate_to_kannada(en_pom)
            st.markdown(f'<div class="pom-card" style="border-color:rgba(232,18,44,0.3)"><div class="pom-name" style="color:#e8122c">⭐ ಪಂದ್ಯದ ಶ್ರೇಷ್ಠ ಆಟಗಾರ</div><div class="pom-detail" style="color:rgba(232,18,44,0.6)">{kn}</div></div>', unsafe_allow_html=True)


# ── CRICKET COMMENTARY DISPLAY ────────────────────────────────────────────────
def display_cricket_commentary(data: dict, match_ctx=None):
    st.markdown("---")
    st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">🎙️ LIVE COMMENTARY</div>', unsafe_allow_html=True)

    for inn_key, inn_raw in data.items():
        if not inn_key.startswith("innings_"):
            continue
        inn_data = normalize_innings(inn_raw)
        if not inn_data or "error" in inn_data:
            st.markdown(f'<div class="error-strip">⚠️ {inn_data.get("error","Empty response")}</div>', unsafe_allow_html=True)
            continue

        inn_num = inn_key.split("_")[1]
        st.markdown(f'<div class="sec-label">🏏 INNINGS {inn_num}</div>', unsafe_allow_html=True)

        if "innings_opener" in inn_data:
            show_dual("Opening", inn_data["innings_opener"])

        for phase in inn_data.get("over_narratives", []):
            if isinstance(phase, dict):
                show_dual(f"Overs {phase.get('over_range','')}", phase.get("commentary",""))

        highlights = inn_data.get("key_moment_highlights", [])
        if highlights:
            st.markdown('<div class="sec-label" style="margin-top:12px">⚡ KEY MOMENTS</div>', unsafe_allow_html=True)
            show_highlights(highlights)

        if "innings_closer" in inn_data:
            show_dual("Innings Wrap", inn_data["innings_closer"])

    pm = normalize_innings(data.get("post_match", {}))
    if not pm or "error" in pm:
        return

    st.markdown("---")
    st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">📊 POST-MATCH ANALYSIS</div>', unsafe_allow_html=True)

    if "match_headline" in pm:
        st.markdown(f'<h3 style="font-family:Barlow Condensed;font-size:1.8rem;letter-spacing:1px;color:#e8eaf0">📰 {pm["match_headline"]}</h3>', unsafe_allow_html=True)
    if "match_summary" in pm:
        show_dual("Match Summary", pm["match_summary"])

    show_pom(pm.get("player_of_match", {}))

    if "turning_point" in pm:
        show_dual("Turning Point", pm["turning_point"])

    perfs = pm.get("top_performances", [])
    if perfs:
        st.markdown('<div class="sec-label">⭐ TOP PERFORMANCES</div>', unsafe_allow_html=True)
        for perf in perfs:
            if not isinstance(perf, dict):
                continue
            txt = f"**{perf.get('player','')}** — {perf.get('stat','')}. {perf.get('comment','')}"
            st.markdown(f'<div class="highlight-card">{txt}</div>', unsafe_allow_html=True)
            if lang_mode != "🇬🇧 English Only":
                kn = translate_to_kannada(f"{perf.get('player','')} — {perf.get('stat','')}. {perf.get('comment','')}")
                st.markdown(f'<div class="highlight-card" style="border-left:3px solid {C_RED};color:#ffd0d0">{kn}</div>', unsafe_allow_html=True)

    if "closing_thought" in pm:
        show_dual("Closing", pm["closing_thought"])

    # ── Performance charts ──
    if match_ctx and match_ctx.innings_summaries:
        st.markdown("---")
        st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">📈 PERFORMANCE CHARTS</div>', unsafe_allow_html=True)

        all_bat, all_bowl = [], []
        for inn in match_ctx.innings_summaries:
            for b in inn.get("top_batsmen", []):
                all_bat.append({**b, "innings": inn["batting_team"]})
            for bw in inn.get("top_bowlers", []):
                all_bowl.append({**bw, "innings": inn["bowling_team"]})

        col1, col2 = st.columns(2)
        if all_bat:
            bat_df = pd.DataFrame(all_bat)
            with col1:
                st.markdown('<div class="cmd-card card-glow-top-cyan">', unsafe_allow_html=True)
                fig = px_bar(bat_df, "player", "runs", "🏏 Top Batsmen — Runs", C_CYAN)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if all_bowl:
            bowl_df = pd.DataFrame(all_bowl)
            with col2:
                st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
                fig = px_bar(bowl_df, "player", "wickets", "🎯 Top Bowlers — Wickets", C_RED)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if all_bat and "strike_rate" in all_bat[0]:
            bat_df = pd.DataFrame(all_bat)
            fig = px_scatter_bubble(bat_df, "runs", "strike_rate", "sixes", "innings",
                                    ["player","fours","sixes"],
                                    "💥 Runs vs Strike Rate · Bubble = Sixes")
            st.plotly_chart(fig, use_container_width=True)


# ── FOOTBALL COMMENTARY DISPLAY ───────────────────────────────────────────────
def display_football_commentary(data: dict):
    if isinstance(data, list):
        data = next((x for x in data if isinstance(x, dict)), {})
    if not data or "error" in data:
        st.markdown(f'<div class="error-strip">⚠️ {data.get("error","Empty")}</div>', unsafe_allow_html=True)
        return

    st.markdown("---")
    st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">🎙️ MATCH COMMENTARY</div>', unsafe_allow_html=True)

    if "match_intro" in data:
        show_dual("Match Atmosphere", data["match_intro"], C_RED)
    if "first_half_commentary" in data:
        show_dual("First Half", data["first_half_commentary"], C_RED)

    goals = data.get("goal_highlights", [])
    if goals:
        st.markdown('<div class="sec-label">⚽ GOAL HIGHLIGHTS</div>', unsafe_allow_html=True)
        for g in goals:
            if not isinstance(g, dict):
                continue
            desc = g.get("description", "")
            minute = g.get("minute", "")
            if lang_mode == "🇬🇧 English Only":
                st.markdown(f'<div class="goal-card">⚽ <strong style="font-family:Space Mono;color:{C_GOLD}">{minute}\'</strong> &nbsp; {desc}</div>', unsafe_allow_html=True)
            elif lang_mode == "🇮🇳 Kannada Only":
                kn = translate_to_kannada(desc)
                st.markdown(f'<div class="goal-card">⚽ <strong style="font-family:Space Mono;color:{C_GOLD}">{minute}\'</strong> &nbsp; {kn}</div>', unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="goal-card">⚽ <strong style="font-family:Space Mono;color:{C_GOLD}">{minute}\'</strong> &nbsp; {desc}</div>', unsafe_allow_html=True)
                with c2:
                    kn = translate_to_kannada(desc)
                    st.markdown(f'<div class="commentary-kn">⚽ <strong>{minute}\'</strong> — {kn}</div>', unsafe_allow_html=True)

    if "second_half_commentary" in data:
        show_dual("Second Half", data["second_half_commentary"], C_RED)

    pm = data.get("post_match_analysis", {})
    if isinstance(pm, list):
        pm = next((x for x in pm if isinstance(x, dict)), {})
    if not pm:
        return

    st.markdown("---")
    st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">📊 POST-MATCH ANALYSIS</div>', unsafe_allow_html=True)

    if "match_headline" in pm:
        st.markdown(f'<h3 style="font-family:Barlow Condensed;font-size:1.8rem;color:#e8eaf0">📰 {pm["match_headline"]}</h3>', unsafe_allow_html=True)
    if "match_summary" in pm:
        show_dual("Match Summary", pm["match_summary"], C_RED)

    show_pom(pm.get("player_of_match", {}), is_football=True)

    if "tactical_breakdown" in pm:
        show_dual("Tactical Breakdown", pm["tactical_breakdown"], C_RED)
    if "turning_point" in pm:
        show_dual("Turning Point", pm["turning_point"], C_RED)

    perfs = pm.get("top_performances", [])
    if perfs:
        st.markdown('<div class="sec-label">⭐ TOP PERFORMANCES</div>', unsafe_allow_html=True)
        for perf in perfs:
            if not isinstance(perf, dict):
                continue
            txt = f"**{perf.get('player','')}** {perf.get('rating','')} — {perf.get('comment','')}"
            st.markdown(f'<div class="highlight-card" style="border-left:3px solid {C_RED}">{txt}</div>', unsafe_allow_html=True)
            if lang_mode != "🇬🇧 English Only":
                kn = translate_to_kannada(f"{perf.get('player','')} — {perf.get('comment','')}")
                st.markdown(f'<div class="highlight-card" style="border-left:3px solid {C_RED};color:#ffd0d0">{kn}</div>', unsafe_allow_html=True)

    if "closing_line" in data:
        show_dual("Closing", data["closing_line"], C_RED)


# ══════════════════════════════════════════════════════════════════════════════
# MODE 1 — CRICKET
# ══════════════════════════════════════════════════════════════════════════════
if "Cricket" in mode:

    match_list   = get_match_list(dfs)
    match_labels = [m["label"] for m in match_list]
    chosen_label = st.selectbox("🏏 Select ICC T20 WC 2026 Match", match_labels)
    chosen_no    = match_list[match_labels.index(chosen_label)]["match_no"]

    st.markdown("---")
    st.markdown('<div class="sec-label">📂 OR UPLOAD YOUR OWN DATA</div>', unsafe_allow_html=True)

    with st.expander("📋 CSV Format Guide"):
        st.markdown("**Required columns:** `over · ball · batsman · bowler · runs · event · batting_team · bowling_team`")
        st.markdown("**Event values:** `boundary · six · wicket · dot · single · two · three`")
        st.code(
            "over,ball,batsman,bowler,runs,event,batting_team,bowling_team\n"
            "1,1,Rohit Sharma,Jasprit Bumrah,4,boundary,India,Australia",
            language="csv"
        )

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        uploaded_csv  = st.file_uploader("📊 Upload CSV", type=["csv"], key="ucsv")
    with col_u2:
        uploaded_json = st.file_uploader("📄 Upload JSON", type=["json"], key="ujson")

    match_ctx = None

    if uploaded_csv:
        try:
            csv_content = uploaded_csv.read().decode("utf-8")
            df_check    = pd.read_csv(io.StringIO(csv_content))
            required    = {"batting_team","bowling_team","over","ball","batsman","bowler","runs","event"}
            missing     = required - set(c.strip().lower() for c in df_check.columns)
            if missing:
                st.error(f"❌ Missing columns: {', '.join(sorted(missing))}")
            else:
                match_ctx = load_match_data(csv_content, sport="cricket")
                st.success(f"✅ CSV loaded — {match_ctx.team1} vs {match_ctx.team2}")

                with st.expander("📊 Preview Parsed Match Stats"):
                    inn = match_ctx.innings_summaries[0]
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    for col_obj, val, lbl in [
                        (mc1, inn["total"], "Score"),
                        (mc2, inn["overs"], "Overs"),
                        (mc3, inn["run_rate"], "Run Rate"),
                        (mc4, inn["top_batsmen"][0]["player"].split()[-1] if inn["top_batsmen"] else "N/A", "Top Bat"),
                    ]:
                        with col_obj:
                            st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

                    cb1, cb2 = st.columns(2)
                    with cb1:
                        st.markdown("**🏏 Top Batsmen**")
                        for b in inn["top_batsmen"]:
                            st.markdown(f"- **{b['player']}**: {b['runs']} runs | SR {b.get('strike_rate','')} | {b['fours']}×4 {b['sixes']}×6")
                    with cb2:
                        st.markdown("**🎯 Top Bowlers**")
                        for bw in inn["top_bowlers"]:
                            st.markdown(f"- **{bw['player']}**: {bw['wickets']}/{bw['runs']} | Econ {bw['economy']}")

                    bat_df = pd.DataFrame(inn["top_batsmen"])
                    if not bat_df.empty:
                        st.plotly_chart(px_bar(bat_df, "player", "runs", "Runs per Batsman", C_CYAN), use_container_width=True)
        except Exception as ex:
            st.error(f"❌ CSV error: {str(ex)[:200]}")

    elif uploaded_json:
        try:
            raw       = json.load(uploaded_json)
            match_ctx = load_match_data(raw)
            st.success(f"✅ JSON loaded — {match_ctx.team1} vs {match_ctx.team2}")
        except Exception as ex:
            st.error(f"❌ JSON error: {str(ex)[:120]}")
    else:
        try:
            match_ctx = build_context_from_match(chosen_no, dfs)
        except Exception as ex:
            st.error(f"Could not build match context: {ex}")

    if not match_ctx:
        st.stop()

    # ── Match overview ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="cmd-title" style="font-size:2rem;margin-bottom:1rem">📋 MATCH OVERVIEW</div>', unsafe_allow_html=True)

    # Score hero
    result = match_ctx.result
    stage  = result.get("stage", "T20")
    st.markdown(f"""
    <div class="score-hero">
      <div class="sh-teams">{match_ctx.team1.upper()} &nbsp;vs&nbsp; {match_ctx.team2.upper()}</div>
      <div class="sh-score">
        <span style="color:{C_CYAN}">{match_ctx.innings_summaries[0]["total"] if match_ctx.innings_summaries else "—"}</span>
        <span style="color:#3a4455;font-size:2.5rem;margin:0 1rem">|</span>
        <span style="color:{C_RED}">{match_ctx.innings_summaries[1]["total"] if len(match_ctx.innings_summaries)>1 else "—"}</span>
      </div>
      <div class="sh-venue">🏟️ {match_ctx.venue} &nbsp;·&nbsp; {stage} &nbsp;·&nbsp; {match_ctx.date}</div>
      <div><span class="sh-winner">🏆 {result.get("winner","TBD").upper()} — {result.get("margin","")}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Innings stat boxes
    cols_inn = st.columns(len(match_ctx.innings_summaries))
    for i, (col_obj, inn) in enumerate(zip(cols_inn, match_ctx.innings_summaries)):
        accent = C_CYAN if i == 0 else C_RED
        with col_obj:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-box-accent" style="background:{accent}"></div>
              <div class="stat-lbl" style="color:{C_GOLD}">INNINGS {inn["innings_number"]}</div>
              <div class="stat-val" style="color:{accent}">{inn["total"]}</div>
              <div class="stat-lbl">{inn["batting_team"]}</div>
              <div class="stat-sub">RR: {inn["run_rate"]} · {inn["overs"]} overs</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Per-innings expanders with charts ──────────────────────────────────────
    for inn in match_ctx.innings_summaries:
        accent = C_CYAN if inn["innings_number"] == 1 else C_RED
        with st.expander(f"Innings {inn['innings_number']}: {inn['batting_team']} — {inn['total']} ({inn['overs']} ov, RR {inn['run_rate']})"):
            col_b, col_w = st.columns(2)
            with col_b:
                st.markdown("**🏏 Top Batsmen**")
                for b in inn["top_batsmen"]:
                    st.markdown(f"- **{b['player']}**: {b['runs']} runs | Avg {b.get('average','')} | SR {b.get('strike_rate','')} | {b['fours']}×4 {b['sixes']}×6")
                if inn["top_batsmen"]:
                    bat_df = pd.DataFrame(inn["top_batsmen"])
                    fig_bat = px_bar(bat_df, "player", "runs", f"Innings {inn['innings_number']} — Runs", accent)
                    st.plotly_chart(fig_bat, use_container_width=True)
            with col_w:
                st.markdown("**🎯 Top Bowlers**")
                for bw in inn["top_bowlers"]:
                    st.markdown(f"- **{bw['player']}**: {bw['wickets']} wkts | Econ {bw['economy']} | Best: {bw.get('best','')}")
                if inn["top_bowlers"]:
                    bowl_df = pd.DataFrame(inn["top_bowlers"])
                    fig_bwl = px_bar(bowl_df, "player", "wickets", "Wickets", C_GOLD if inn["innings_number"] == 1 else C_PURPLE)
                    st.plotly_chart(fig_bwl, use_container_width=True)

    # ── Combined analytics ─────────────────────────────────────────────────────
    st.markdown('<div class="sec-label" style="margin-top:1.5rem">📈 COMBINED ANALYTICS</div>', unsafe_allow_html=True)
    all_bat, all_bowl = [], []
    for inn in match_ctx.innings_summaries:
        all_bat  += [{**b,  "team": inn["batting_team"]}  for b  in inn.get("top_batsmen", [])]
        all_bowl += [{**bw, "team": inn["bowling_team"]}  for bw in inn.get("top_bowlers", [])]

    if all_bat and all_bowl:
        ca1, ca2 = st.columns(2)
        bat_df  = pd.DataFrame(all_bat)
        bowl_df = pd.DataFrame(all_bowl)

        with ca1:
            st.markdown('<div class="cmd-card card-glow-top-cyan">', unsafe_allow_html=True)
            st.plotly_chart(px_bar(bat_df, "player", "runs", "🏏 All Batsmen — Runs", C_CYAN, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with ca2:
            st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
            st.plotly_chart(px_bar(bowl_df, "player", "wickets", "🎯 All Bowlers — Wickets", C_RED, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if "strike_rate" in all_bat[0]:
            st.markdown('<div class="cmd-card card-glow-top-gold">', unsafe_allow_html=True)
            st.plotly_chart(
                px_scatter_bubble(bat_df, "runs", "strike_rate", "sixes", "team",
                                  ["player","fours"], "💥 Runs vs Strike Rate · Bubble = Sixes"),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        if "economy" in all_bowl[0]:
            bdf = pd.DataFrame(all_bowl)
            radar_cats  = ["Wickets","Economy (inv)","Runs Conceded (inv)"]
            radar_vals1 = []
            radar_vals2 = []
            inn1_b = [b for b in all_bowl if b["team"] == match_ctx.innings_summaries[0].get("bowling_team","")]
            inn2_b = [b for b in all_bowl if b["team"] != match_ctx.innings_summaries[0].get("bowling_team","")]
            if inn1_b and inn2_b:
                def agg(lst):
                    wkts  = sum(b["wickets"] for b in lst)
                    econ  = sum(b["economy"] for b in lst) / len(lst)
                    runs  = sum(b["runs"]    for b in lst)
                    return [min(wkts*10,100), max(0,100-econ*8), max(0,100-runs/3)]
                fig_r = px_radar(
                    radar_cats, agg(inn1_b), agg(inn2_b),
                    inn1_b[0]["team"], inn2_b[0]["team"],
                )
                fig_r.update_layout(title="🕸️ Bowling Radar Comparison", **{k:v for k,v in PLOTLY.items() if k != "plot_bgcolor"})
                st.plotly_chart(fig_r, use_container_width=True)

    if match_ctx.key_moments:
        with st.expander("🏅 Awards & Context"):
            for km in match_ctx.key_moments:
                st.markdown(f"• {km}")

    # ── Generate button ────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🎙️ Generate Cricket Commentary", type="primary", use_container_width=True):
        with st.spinner("🤖 Generating with Groq AI · LLaMA 3.3 70B — ~20 seconds..."):
            try:
                commentary = {}
                for i in range(len(match_ctx.innings_summaries)):
                    commentary[f"innings_{i+1}"] = gen_cricket_commentary(match_ctx, i)
                commentary["post_match"] = gen_cricket_post_match(match_ctx)
                st.session_state["cricket_commentary"] = commentary
                st.session_state["cricket_ctx"]        = match_ctx
                st.session_state["sport"]              = "cricket"
                st.success("✅ Commentary ready! Scroll down.")
                st.rerun()
            except Exception as ex:
                st.error(f"Generation failed: {ex}")

    if st.session_state.get("sport") == "cricket" and "cricket_commentary" in st.session_state:
        display_cricket_commentary(
            st.session_state["cricket_commentary"],
            st.session_state.get("cricket_ctx")
        )
        st.markdown("---")
        st.download_button(
            "⬇️ Download Commentary (JSON)",
            data=json.dumps(st.session_state["cricket_commentary"], ensure_ascii=False, indent=2),
            file_name="cricket_commentary.json",
            mime="application/json",
        )


# ══════════════════════════════════════════════════════════════════════════════
# MODE 2 — FOOTBALL
# ══════════════════════════════════════════════════════════════════════════════
elif "Football" in mode:
    st.markdown('<div class="cmd-title" style="font-size:2.5rem;margin-bottom:1.5rem">⚽ FOOTBALL MATCH COMMENTARY</div>', unsafe_allow_html=True)

    FOOTBALL_MATCHES = [
        {
            "label": "Match 1 | Bengaluru FC vs Chennaiyin FC — ISL Final",
            "home_team": "Bengaluru FC", "away_team": "Chennaiyin FC",
            "home_score": 3, "away_score": 1,
            "competition": "Indian Super League", "venue": "Sree Kanteerava Stadium, Bengaluru",
            "date": "2024-03-15", "home_possession": 58,
            "home_shots": 14, "home_shots_on": 7,
            "away_shots": 8, "away_shots_on": 3,
            "goals": "18, Bengaluru FC, Sunil Chhetri\n34, Bengaluru FC, Alan Costa\n61, Chennaiyin FC, Nerijus Valskis\n78, Bengaluru FC, Cleiton Silva",
        },
        {
            "label": "Match 2 | Mumbai City FC vs ATK Mohun Bagan — ISL Semi",
            "home_team": "Mumbai City FC", "away_team": "ATK Mohun Bagan",
            "home_score": 2, "away_score": 2,
            "competition": "Indian Super League", "venue": "Mumbai Football Arena",
            "date": "2024-03-10", "home_possession": 52,
            "home_shots": 11, "home_shots_on": 5,
            "away_shots": 10, "away_shots_on": 4,
            "goals": "22, Mumbai City FC, Jorge Pereyra\n45, ATK Mohun Bagan, Hugo Boumous\n67, Mumbai City FC, Lallianzuala Chhangte\n88, ATK Mohun Bagan, Dimitri Petratos",
        },
        {
            "label": "Match 3 | Kerala Blasters vs FC Goa — ISL Group Stage",
            "home_team": "Kerala Blasters", "away_team": "FC Goa",
            "home_score": 1, "away_score": 2,
            "competition": "Indian Super League", "venue": "Jawaharlal Nehru Stadium, Kochi",
            "date": "2024-02-20", "home_possession": 44,
            "home_shots": 9, "home_shots_on": 3,
            "away_shots": 13, "away_shots_on": 6,
            "goals": "31, Kerala Blasters, Adrian Luna\n55, FC Goa, Noah Sadaoui\n82, FC Goa, Airam Cabrera",
        },
        {
            "label": "Match 4 | Hyderabad FC vs NorthEast United — ISL Group Stage",
            "home_team": "Hyderabad FC", "away_team": "NorthEast United",
            "home_score": 4, "away_score": 0,
            "competition": "Indian Super League", "venue": "GMC Balayogi Stadium, Hyderabad",
            "date": "2024-02-10", "home_possession": 65,
            "home_shots": 18, "home_shots_on": 10,
            "away_shots": 5, "away_shots_on": 1,
            "goals": "8, Hyderabad FC, Bartholomew Ogbeche\n29, Hyderabad FC, Halicharan Narzary\n54, Hyderabad FC, Bartholomew Ogbeche\n77, Hyderabad FC, Nikhil Poojary",
        },
        {
            "label": "Custom Match — Enter your own data",
            "home_team": "", "away_team": "", "home_score": 0, "away_score": 0,
            "competition": "", "venue": "", "date": "", "home_possession": 50,
            "home_shots": 10, "home_shots_on": 5,
            "away_shots": 10, "away_shots_on": 5, "goals": "",
        },
    ]

    labels_fb   = [m["label"] for m in FOOTBALL_MATCHES]
    chosen_fb_l = st.selectbox("⚽ Select Football Match", labels_fb)
    chosen_fb   = FOOTBALL_MATCHES[labels_fb.index(chosen_fb_l)]

    st.markdown("---")
    st.markdown('<div class="sec-label">📋 MATCH DETAILS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        home_team       = st.text_input("Home Team",       value=chosen_fb["home_team"])
        home_score      = st.number_input("Home Goals", 0, 20, chosen_fb["home_score"])
        home_possession = st.slider("Home Possession %", 0, 100, chosen_fb["home_possession"])
        home_shots      = st.number_input("Home Shots", 0, value=chosen_fb["home_shots"])
        home_shots_on   = st.number_input("Home Shots on Target", 0, value=chosen_fb["home_shots_on"])
    with col2:
        away_team       = st.text_input("Away Team",       value=chosen_fb["away_team"])
        away_score      = st.number_input("Away Goals", 0, 20, chosen_fb["away_score"])
        away_possession = 100 - home_possession
        st.markdown(f'<div class="info-strip">⚽ Away Possession: <strong>{away_possession}%</strong></div>', unsafe_allow_html=True)
        away_shots      = st.number_input("Away Shots", 0, value=chosen_fb["away_shots"])
        away_shots_on   = st.number_input("Away Shots on Target", 0, value=chosen_fb["away_shots_on"])

    competition = st.text_input("Competition", value=chosen_fb["competition"])
    venue       = st.text_input("Venue",       value=chosen_fb["venue"])
    match_date  = st.text_input("Date",        value=chosen_fb["date"])

    st.markdown('<div class="sec-label">⚽ GOALS</div>', unsafe_allow_html=True)
    goals_input = st.text_area("One goal per line: minute, team, scorer",
                               value=chosen_fb["goals"], height=120)

    goals = []
    for line in goals_input.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            goals.append({
                "minute": int(parts[0]) if parts[0].isdigit() else 0,
                "team":   parts[1],
                "scorer": parts[2],
                "assist": parts[3] if len(parts) > 3 else None,
                "type":   "open_play",
            })

    winner = home_team if home_score > away_score else (
             away_team if away_score > home_score else "Draw")
    margin = f"{max(home_score,away_score)}-{min(home_score,away_score)}"

    # ── Score hero ──────────────────────────────────────────────────────────────
    win_color = C_CYAN if home_score > away_score else (C_RED if away_score > home_score else C_GOLD)
    win_label = f"🏆 {winner.upper()} WIN" if winner != "Draw" else "⚖️ DRAW"
    st.markdown(f"""
    <div class="fb-score-hero">
      <div class="sh-teams">{home_team or "HOME"} &nbsp;&nbsp; vs &nbsp;&nbsp; {away_team or "AWAY"}</div>
      <div class="fb-score-num">
        <span style="color:{C_CYAN}">{home_score}</span>
        <span style="color:#3a4455;font-size:3rem;margin:0 1.5rem">—</span>
        <span style="color:{C_RED}">{away_score}</span>
      </div>
      <div class="sh-venue">{competition} · {venue}</div>
      <div><span class="sh-winner" style="background:rgba({','.join(['232,18,44' if win_color==C_RED else ('255,179,0' if win_color==C_GOLD else '0,229,255')])}, 0.1);border-color:rgba({','.join(['232,18,44' if win_color==C_RED else ('255,179,0' if win_color==C_GOLD else '0,229,255')])},0.3);color:{win_color}">{win_label}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Goal cards ──────────────────────────────────────────────────────────────
    if goals:
        st.markdown('<div class="sec-label">⚽ GOAL LOG</div>', unsafe_allow_html=True)
        gcols = st.columns(min(len(goals), 4))
        for gi, g in enumerate(goals):
            col_idx = gi % len(gcols)
            team_color = C_CYAN if g["team"] == home_team else C_RED
            with gcols[col_idx]:
                st.markdown(f"""
                <div class="goal-card" style="border-left-color:{team_color};background:linear-gradient(135deg,rgba({'0,229,255' if team_color==C_CYAN else '232,18,44'},0.05),transparent)">
                  ⚽ <strong style="font-family:Space Mono;color:{C_GOLD}">{g["minute"]}'</strong>
                  &nbsp; <strong style="color:{team_color}">{g["scorer"]}</strong>
                  <br><small style="color:#7a8599;font-size:0.72rem">{g["team"]}</small>
                </div>
                """, unsafe_allow_html=True)

    # ── Statistics charts ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec-label">📊 MATCH STATISTICS</div>', unsafe_allow_html=True)

    # Gauges row
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(px_gauge(home_possession, f"{home_team or 'Home'} Possession", 100, C_CYAN), use_container_width=True)
    with g2:
        st.plotly_chart(px_gauge(away_possession, f"{away_team or 'Away'} Possession", 100, C_RED), use_container_width=True)
    with g3:
        mx = max(home_shots, away_shots, 1)
        st.plotly_chart(px_gauge(home_shots_on, f"{home_team or 'Home'} Shots on Target", mx, C_GREEN), use_container_width=True)
    with g4:
        st.plotly_chart(px_gauge(away_shots_on, f"{away_team or 'Away'} Shots on Target", mx, C_GOLD), use_container_width=True)

    # Radar + head-to-head bar
    cr1, cr2 = st.columns(2)
    radar_cats = ["Possession", "Shots", "Shots on Target", "Goals"]
    with cr1:
        st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
        fig_r = px_radar(
            radar_cats,
            [home_possession, home_shots, home_shots_on, home_score * 15],
            [away_possession, away_shots, away_shots_on, away_score * 15],
            home_team or "Home", away_team or "Away",
        )
        fig_r.update_layout(title="🕸️ Team Performance Radar")
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr2:
        st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            "Stat":              ["Possession %", "Shots", "Shots on Tgt", "Goals"],
            home_team or "Home": [home_possession, home_shots, home_shots_on, home_score],
            away_team or "Away": [away_possession, away_shots, away_shots_on, away_score],
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name=home_team or "Home",
            x=stats_df["Stat"],
            y=stats_df[home_team or "Home"],
            marker_color=C_CYAN, marker_line_width=0,
        ))
        fig_bar.add_trace(go.Bar(
            name=away_team or "Away",
            x=stats_df["Stat"],
            y=stats_df[away_team or "Away"],
            marker_color=C_RED, marker_line_width=0,
        ))
        fig_bar.update_layout(**PLOTLY, barmode="group", title="📊 Head-to-Head Stats",
                              legend=dict(font=dict(color="#7a8599", size=10)))
        fig_bar.update_xaxes(**GRID, **TICK)
        fig_bar.update_yaxes(**GRID, **TICK)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Goal timeline
    if goals:
        st.markdown('<div class="cmd-card card-glow-top-gold">', unsafe_allow_html=True)
        st.plotly_chart(goal_timeline(goals, home_team, away_team), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3D scatter — possession / shots / goals
    st.markdown('<div class="sec-label">🌐 3D MATCH ANALYSIS</div>', unsafe_allow_html=True)
    m3d = pd.DataFrame({
        "Team":      [home_team or "Home", away_team or "Away"],
        "Possession":[home_possession, away_possession],
        "Shots":     [home_shots, away_shots],
        "Goals":     [home_score, away_score],
        "Accuracy":  [round(home_shots_on / max(home_shots,1)*100,1),
                      round(away_shots_on / max(away_shots,1)*100,1)],
    })
    fig_3d = px.scatter_3d(
        m3d, x="Possession", y="Shots", z="Goals",
        color="Team", size="Accuracy", text="Team",
        color_discrete_map={
            home_team or "Home": C_CYAN,
            away_team or "Away": C_RED,
        },
        title="🌐 3D — Possession · Shots · Goals (bubble = accuracy %)",
    )
    fig_3d.update_traces(textposition="top center",
                         textfont=dict(color="#e8eaf0"), marker_sizemin=18)
    fig_3d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(10,16,30,0.95)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599",
                       title="Possession %", backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599",
                       title="Total Shots", backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599",
                       title="Goals Scored", backgroundcolor="rgba(0,0,0,0)"),
        ),
        font=dict(color="#e8eaf0"),
        legend=dict(font=dict(color="#7a8599", size=10)),
        margin=dict(l=0, r=0, t=48, b=0),
        title_font=dict(color="#60c8f8", family="Barlow Condensed", size=16),
        height=520,
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    # ── Generate ────────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🎙️ Generate Football Commentary", type="secondary", use_container_width=True):
        with st.spinner("🤖 Generating football commentary with Groq AI..."):
            try:
                from src.data_parser import FootballMatchContext
                football_ctx = FootballMatchContext(
                    match_id="FB_MATCH", venue=venue,
                    home_team=home_team, away_team=away_team,
                    competition=competition, date=match_date,
                    score={"home": home_score, "away": away_score},
                    goals=goals, key_moments=[],
                    stats={
                        "home": {"possession": home_possession, "shots": home_shots,
                                 "shots_on_target": home_shots_on},
                        "away": {"possession": away_possession, "shots": away_shots,
                                 "shots_on_target": away_shots_on},
                    },
                    player_ratings=[], cards=[],
                    result={"winner": winner, "margin": margin},
                )
                result = gen_football_commentary(football_ctx)
                st.session_state["football_commentary"] = result
                st.session_state["sport"] = "football"
                st.success("✅ Commentary ready! Scroll down.")
                st.rerun()
            except Exception as ex:
                st.error(f"Generation failed: {ex}")

    if st.session_state.get("sport") == "football" and "football_commentary" in st.session_state:
        display_football_commentary(st.session_state["football_commentary"])
        st.markdown("---")
        st.download_button(
            "⬇️ Download Commentary (JSON)",
            data=json.dumps(st.session_state["football_commentary"], ensure_ascii=False, indent=2),
            file_name="football_commentary.json",
            mime="application/json",
        )


# ══════════════════════════════════════════════════════════════════════════════
# MODE 3 — TOURNAMENT STATS
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="cmd-title" style="font-size:2.5rem;margin-bottom:1.5rem">📊 ICC T20 WC 2026 — TOURNAMENT DASHBOARD</div>', unsafe_allow_html=True)

    batting_df = dfs["batting"]
    bowling_df = dfs["bowling"]
    matches_df = dfs["matches"]

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card stagger-1"><div class="metric-val" style="color:{C_CYAN}">{len(matches_df)}</div><div class="metric-lbl">Total Matches</div></div>', unsafe_allow_html=True)
    with m2:
        top_scorer = batting_df.loc[batting_df["runs"].idxmax()]
        st.markdown(f'<div class="metric-card stagger-2"><div class="metric-val" style="color:{C_RED}">{int(top_scorer["runs"])}</div><div class="metric-lbl">Most Runs</div><div class="metric-sub">{top_scorer["player"]}</div></div>', unsafe_allow_html=True)
    with m3:
        top_wkt = bowling_df.loc[bowling_df["wickets"].idxmax()]
        st.markdown(f'<div class="metric-card stagger-3"><div class="metric-val" style="color:{C_GOLD}">{int(top_wkt["wickets"])}</div><div class="metric-lbl">Most Wickets</div><div class="metric-sub">{top_wkt["player"]}</div></div>', unsafe_allow_html=True)
    with m4:
        top_sr = batting_df.loc[batting_df["strike_rate"].idxmax()]
        st.markdown(f'<div class="metric-card stagger-4"><div class="metric-val" style="color:{C_GREEN}">{top_sr["strike_rate"]}</div><div class="metric-lbl">Best Strike Rate</div><div class="metric-sub">{top_sr["player"]}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Points Table", "🏏 Top Batsmen", "🎯 Top Bowlers", "📈 Analytics", "🥇 Awards"
    ])

    with tab1:
        standings = get_standings(dfs)
        for grp, grp_df in standings.groupby("group"):
            st.markdown(f'<div class="sec-label">GROUP {grp}</div>', unsafe_allow_html=True)
            display = grp_df[["team","matches_played","won","lost","net_run_rate","points","qualified"]].copy()
            display.columns = ["Team","P","W","L","NRR","Pts","Q"]
            st.dataframe(display.reset_index(drop=True), use_container_width=True, hide_index=True)

        # NRR horizontal bar
        nrr_df = standings.sort_values("net_run_rate", ascending=True)
        fig_nrr = px.bar(
            nrr_df, x="net_run_rate", y="team", orientation="h",
            title="📊 Net Run Rate — All Teams",
            color="net_run_rate",
            color_continuous_scale=[[0,"#e8122c"],[0.45,"#ffb300"],[1,"#00e5ff"]],
        )
        fig_nrr.update_layout(**PLOTLY, coloraxis_showscale=False,
                              title_font_color="#60c8f8")
        fig_nrr.update_xaxes(**GRID, **TICK)
        fig_nrr.update_yaxes(**GRID, **TICK)
        st.plotly_chart(fig_nrr, use_container_width=True)

    with tab2:
        top10 = get_top_batters(dfs, 10)

        st.markdown('<div class="cmd-card card-glow-top-cyan">', unsafe_allow_html=True)
        st.plotly_chart(px_bar(top10, "player", "runs", "🏏 Top 10 Run Scorers", C_CYAN), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown('<div class="cmd-card card-glow-top-gold">', unsafe_allow_html=True)
            sr_df = top10.sort_values("strike_rate", ascending=False).head(8)
            st.plotly_chart(px_bar(sr_df, "player", "strike_rate", "💥 Strike Rate Leaders", C_GOLD, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cb2:
            st.markdown('<div class="cmd-card card-glow-top-green">' if False else '<div class="cmd-card card-glow-top-cyan">', unsafe_allow_html=True)
            avg_df = top10.sort_values("average", ascending=False).head(8)
            st.plotly_chart(px_bar(avg_df, "player", "average", "📈 Batting Averages", C_GREEN, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Bubble chart
        st.markdown('<div class="cmd-card card-glow-top-cyan">', unsafe_allow_html=True)
        st.plotly_chart(
            px_scatter_bubble(top10, "runs", "strike_rate", "average", "team",
                              ["player","average","fifties","hundreds"],
                              "💥 Runs vs Strike Rate · Bubble = Average"),
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label">BATTING TABLE</div>', unsafe_allow_html=True)
        disp = top10.copy()
        disp.columns = ["Player","Team","Matches","Runs","Avg","SR","50s","100s"]
        st.dataframe(disp.reset_index(drop=True), use_container_width=True, hide_index=True)

    with tab3:
        top10b = get_top_bowlers(dfs, 10)

        st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
        st.plotly_chart(px_bar(top10b, "player", "wickets", "🎯 Top 10 Wicket Takers", C_RED), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        bw1, bw2 = st.columns(2)
        with bw1:
            st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
            econ_df = top10b.sort_values("economy").head(8)
            st.plotly_chart(px_bar(econ_df, "player", "economy", "💰 Best Economy Rates", C_PURPLE, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with bw2:
            st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
            avg_b = top10b.sort_values("average").head(8)
            st.plotly_chart(px_bar(avg_b, "player", "average", "📉 Best Bowling Averages", C_ORANGE, horizontal=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Scatter: wickets vs economy
        st.markdown('<div class="cmd-card card-glow-top-red">', unsafe_allow_html=True)
        fig_ws = px.scatter(
            top10b, x="wickets", y="economy", color="team", size="average",
            hover_data=["player","average","best_figures"],
            title="🎯 Wickets vs Economy Rate · Bubble = Average",
            color_discrete_sequence=PALETTE, size_max=40,
        )
        fig_ws.update_layout(**PLOTLY)
        fig_ws.update_xaxes(**GRID, **TICK, title="Wickets")
        fig_ws.update_yaxes(**GRID, **TICK, title="Economy")
        st.plotly_chart(fig_ws, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label">BOWLING TABLE</div>', unsafe_allow_html=True)
        disp_b = top10b.copy()
        disp_b.columns = ["Player","Team","Matches","Wickets","Econ","Avg","Best"]
        st.dataframe(disp_b.reset_index(drop=True), use_container_width=True, hide_index=True)

    with tab4:
        st.markdown('<div class="sec-label">TOURNAMENT ANALYTICS</div>', unsafe_allow_html=True)

        aa1, aa2 = st.columns(2)
        with aa1:
            wins_df = matches_df.groupby("winner").size().reset_index(name="wins").sort_values("wins", ascending=False).head(8)
            st.plotly_chart(px_bar(wins_df, "winner", "wins", "🏆 Most Wins by Team", C_GOLD, horizontal=True), use_container_width=True)
        with aa2:
            toss_df = matches_df["toss_decision"].value_counts().reset_index()
            toss_df.columns = ["decision","count"]
            st.plotly_chart(px_donut(toss_df["decision"].tolist(), toss_df["count"].tolist(),
                                     "🎲 Toss Decision Split", [C_CYAN, C_RED]), use_container_width=True)

        # 3D batting scatter
        st.markdown('<div class="sec-label" style="margin-top:1.5rem">🌐 3D BATTING ANALYSIS</div>', unsafe_allow_html=True)
        bat_all = dfs["batting"].copy()
        fig_3db = px.scatter_3d(
            bat_all, x="runs", y="strike_rate", z="sixes",
            color="team", size="average",
            hover_data=["player","fifties","hundreds"],
            title="🌐 Runs · Strike Rate · Sixes (bubble = average)",
            color_discrete_sequence=PALETTE,
        )
        fig_3db.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(10,16,30,0.95)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Runs", backgroundcolor="rgba(0,0,0,0)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Strike Rate", backgroundcolor="rgba(0,0,0,0)"),
                zaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Sixes", backgroundcolor="rgba(0,0,0,0)"),
            ),
            font=dict(color="#e8eaf0"),
            legend=dict(font=dict(color="#7a8599", size=10)),
            margin=dict(l=0, r=0, t=48, b=0),
            title_font=dict(color="#60c8f8", family="Barlow Condensed", size=16),
            height=560,
        )
        st.plotly_chart(fig_3db, use_container_width=True)

        # 3D bowling scatter
        st.markdown('<div class="sec-label">🌐 3D BOWLING ANALYSIS</div>', unsafe_allow_html=True)
        bowl_all = dfs["bowling"].copy()
        fig_3dbw = px.scatter_3d(
            bowl_all, x="wickets", y="economy", z="average",
            color="team", size="overs",
            hover_data=["player","best_figures"],
            title="🌐 Wickets · Economy · Average (bubble = overs)",
            color_discrete_sequence=PALETTE,
        )
        fig_3dbw.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(10,16,30,0.95)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Wickets", backgroundcolor="rgba(0,0,0,0)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Economy", backgroundcolor="rgba(0,0,0,0)"),
                zaxis=dict(gridcolor="rgba(255,255,255,0.05)", color="#7a8599", title="Average", backgroundcolor="rgba(0,0,0,0)"),
            ),
            font=dict(color="#e8eaf0"),
            legend=dict(font=dict(color="#7a8599", size=10)),
            margin=dict(l=0, r=0, t=48, b=0),
            title_font=dict(color="#60c8f8", family="Barlow Condensed", size=16),
            height=560,
        )
        st.plotly_chart(fig_3dbw, use_container_width=True)

        # 2D Runs vs SR scatter (full dataset)
        fig_2d = px.scatter(
            bat_all, x="runs", y="strike_rate",
            color="team", size="sixes",
            hover_data=["player","average","fifties","hundreds"],
            title="💥 All Batsmen — Runs vs Strike Rate",
            color_discrete_sequence=PALETTE,
        )
        fig_2d.update_layout(**PLOTLY)
        fig_2d.update_xaxes(**GRID, **TICK, title="Runs")
        fig_2d.update_yaxes(**GRID, **TICK, title="Strike Rate")
        st.plotly_chart(fig_2d, use_container_width=True)

    with tab5:
        st.markdown(f'<div class="cmd-title" style="font-size:2.2rem;text-align:center;margin-bottom:2rem;background:linear-gradient(135deg,{C_GOLD},#fff 50%,{C_GOLD});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">ICC T20 WC 2026<br>TOURNAMENT AWARDS</div>', unsafe_allow_html=True)
        awards_df = get_awards(dfs)
        award_cols = st.columns(3)
        for i, (_, r) in enumerate(awards_df.iterrows()):
            with award_cols[i % 3]:
                st.markdown(f"""
                <div class="award-card">
                  <div class="award-title">{r["award"]}</div>
                  <div class="award-player">{r["player_or_detail"]}</div>
                  <div class="award-team">{r.get("team","")}</div>
                </div>
                """, unsafe_allow_html=True)
