"""
app.py — AI Sports Commentary Generator
Uses real ICC T20 World Cup 2026 Kaggle data
Run: streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()

import json
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Sports Commentary Generator",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem;
}
.main-header h1 { color: #e94560; margin: 0; font-size: 2rem; }
.main-header p  { color: #a8b2d8; margin: 0.4rem 0 0; }

.commentary-box-en {
    background: #0d1b2a; border-left: 4px solid #00b4d8;
    border-radius: 8px; padding: 1.1rem 1.3rem;
    color: #caf0f8; line-height: 1.75; margin: 0.5rem 0;
}
.commentary-box-kn {
    background: #1a0a2e; border-left: 4px solid #ff6b6b;
    border-radius: 8px; padding: 1.1rem 1.3rem;
    color: #ffd6e0; line-height: 1.9; margin: 0.5rem 0; font-size: 1.05rem;
}
.section-header {
    background: #1e2a3a; padding: 0.5rem 1rem; border-radius: 6px;
    margin: 1rem 0 0.4rem; color: #00b4d8; font-weight: 600;
}
.highlight-card {
    background: #162032; border: 1px solid #2a3f5f;
    border-radius: 8px; padding: 0.7rem 1rem;
    margin: 0.35rem 0; color: #e2e8f0;
}
.player-of-match {
    background: linear-gradient(135deg, #2d1b00, #4a2c00);
    border: 2px solid #f59e0b; border-radius: 10px;
    padding: 1rem 1.4rem; margin: 1rem 0;
}
.player-of-match h3 { color: #fbbf24; margin: 0 0 0.3rem; }
.player-of-match p  { color: #fde68a; margin: 0; }
.stat-box {
    background: #1a2744; border-radius: 8px; padding: 0.8rem; text-align: center;
}
.stat-box .v { font-size: 1.5rem; font-weight: 700; color: #60a5fa; }
.stat-box .l { font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem; }
.error-box {
    background: #2d1515; border-left: 4px solid #ef4444;
    border-radius: 6px; padding: 1rem; color: #fca5a5;
}
.info-box {
    background: #0a2340; border-left: 4px solid #38bdf8;
    border-radius: 6px; padding: 0.8rem 1rem; color: #bae6fd;
    margin: 0.5rem 0; font-size: 0.9rem;
}
.football-score {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1rem 0;
}
.football-score .score { font-size: 3rem; font-weight: 900; color: #fbbf24; }
.football-score .teams { font-size: 1.1rem; color: #a8b2d8; margin-top: 0.3rem; }
.goal-card {
    background: #0d2b1a; border-left: 4px solid #22c55e;
    border-radius: 8px; padding: 0.7rem 1rem; margin: 0.35rem 0; color: #bbf7d0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏏⚽ AI Sports Commentary Generator</h1>
    <p>ICC T20 World Cup 2026 · Broadcaster-style narration in English & ಕನ್ನಡ</p>
</div>
""", unsafe_allow_html=True)


# ── Boot: load all engines and data once ────────────────────────────────────────
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
        load_tournament_data,
        get_match_list,
        build_context_from_match,
        get_tournament_summary,
        get_standings,
        get_top_batters,
        get_top_bowlers,
        get_awards,
    )

    initialize_translator()
    dfs = load_tournament_data("data")

    return {
        "CricketMatchContext":      CricketMatchContext,
        "FootballMatchContext":     FootballMatchContext,
        "load_match_data":          load_match_data,
        "gen_cricket_commentary":   generate_cricket_commentary,
        "gen_cricket_post_match":   generate_cricket_post_match,
        "gen_football_commentary":  generate_football_commentary,
        "translate_to_kannada":     translate_to_kannada,
        "dfs":                      dfs,
        "get_match_list":           get_match_list,
        "build_context_from_match": build_context_from_match,
        "get_tournament_summary":   get_tournament_summary,
        "get_standings":            get_standings,
        "get_top_batters":          get_top_batters,
        "get_top_bowlers":          get_top_bowlers,
        "get_awards":               get_awards,
    }


e                        = boot()
dfs                      = e["dfs"]
CricketMatchContext       = e["CricketMatchContext"]
FootballMatchContext      = e["FootballMatchContext"]
load_match_data           = e["load_match_data"]
gen_cricket_commentary    = e["gen_cricket_commentary"]
gen_cricket_post_match    = e["gen_cricket_post_match"]
gen_football_commentary   = e["gen_football_commentary"]
translate_to_kannada      = e["translate_to_kannada"]
get_match_list            = e["get_match_list"]
build_context_from_match  = e["build_context_from_match"]
get_tournament_summary    = e["get_tournament_summary"]
get_standings             = e["get_standings"]
get_top_batters           = e["get_top_batters"]
get_top_bowlers           = e["get_top_bowlers"]
get_awards                = e["get_awards"]


# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    mode = st.radio("Mode", ["🏏 Cricket Commentary", "⚽ Football Commentary", "📊 Tournament Stats"])
    enable_kn = st.checkbox("Kannada Translation", value=True)

    st.markdown("---")
    summary = get_tournament_summary(dfs)
    st.markdown("### 🏆 Tournament")
    for k, v in list(summary.items())[:6]:
        st.markdown(f"**{k}:** {v}")


# ── Shared helper ────────────────────────────────────────────────────────────────
def show_dual(label: str, text: str):
    """Show text in English + Kannada side by side."""
    if not text or not isinstance(text, str):
        return
    st.markdown(f'<div class="section-header">📢 {label}</div>', unsafe_allow_html=True)
    if enable_kn:
        col_en, col_kn = st.columns(2)
        with col_en:
            st.markdown("🇬🇧 **English**")
            st.markdown(f'<div class="commentary-box-en">{text}</div>', unsafe_allow_html=True)
        with col_kn:
            st.markdown("🇮🇳 **ಕನ್ನಡ**")
            kn = translate_to_kannada(text)
            st.markdown(f'<div class="commentary-box-kn">{kn}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="commentary-box-en">{text}</div>', unsafe_allow_html=True)


def normalize_innings(raw) -> dict:
    """
    Groq sometimes wraps innings in a list or a single-key dict.
    This unwraps it to always return a plain dict.
    """
    if isinstance(raw, list):
        raw = next((x for x in raw if isinstance(x, dict)), {})
    if isinstance(raw, dict):
        keys = list(raw.keys())
        # unwrap {"innings": {...}} or {"result": {...}}
        if len(keys) == 1 and isinstance(raw[keys[0]], dict):
            return raw[keys[0]]
        return raw
    return {}


def display_cricket_commentary(data: dict):
    """Render full cricket commentary + post-match."""
    st.markdown("---")
    st.markdown("## 🎙️ Live Commentary")

    for inn_key, inn_raw in data.items():
        if not inn_key.startswith("innings_"):
            continue

        inn_data = normalize_innings(inn_raw)

        if not inn_data:
            st.markdown(f'<div class="error-box">⚠️ {inn_key}: empty response from AI</div>', unsafe_allow_html=True)
            continue

        if "error" in inn_data:
            st.markdown(f'<div class="error-box">⚠️ Innings error: {inn_data["error"]}</div>', unsafe_allow_html=True)
            continue

        inn_num = inn_key.split("_")[1]
        st.markdown(f"### 🏏 Innings {inn_num}")

        if "innings_opener" in inn_data:
            show_dual("Opening", inn_data["innings_opener"])

        for phase in inn_data.get("over_narratives", []):
            if isinstance(phase, dict):
                show_dual(
                    f"Overs {phase.get('over_range', '')}",
                    phase.get("commentary", "")
                )

        highlights = inn_data.get("key_moment_highlights", [])
        if highlights:
            st.markdown('<div class="section-header">⚡ Key Moments</div>', unsafe_allow_html=True)
            for moment in highlights:
                if not isinstance(moment, str):
                    continue
                if enable_kn:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="highlight-card">🏏 {moment}</div>', unsafe_allow_html=True)
                    with c2:
                        kn = translate_to_kannada(moment)
                        st.markdown(f'<div class="highlight-card" style="color:#ffd6e0">🏏 {kn}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="highlight-card">🏏 {moment}</div>', unsafe_allow_html=True)

        if "innings_closer" in inn_data:
            show_dual("Innings Wrap", inn_data["innings_closer"])

    # ── Post-match ──────────────────────────────────────────────────────────────
    pm = normalize_innings(data.get("post_match", {}))
    if not pm or "error" in pm:
        if pm and "error" in pm:
            st.markdown(f'<div class="error-box">⚠️ Post-match error: {pm["error"]}</div>', unsafe_allow_html=True)
        return

    st.markdown("---")
    st.markdown("## 📊 Post-Match Analysis")

    if "match_headline" in pm:
        st.markdown(f"### 📰 {pm['match_headline']}")

    if "match_summary" in pm:
        show_dual("Match Summary", pm["match_summary"])

    pom = pm.get("player_of_match", {})
    if pom and isinstance(pom, dict):
        en_pom = f"{pom.get('name','')} ({pom.get('team','')}) — {pom.get('reason','')}"
        if enable_kn:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="player-of-match"><h3>🏆 Player of the Match</h3><p>{en_pom}</p></div>', unsafe_allow_html=True)
            with c2:
                kn_pom = translate_to_kannada(en_pom)
                st.markdown(f'<div class="player-of-match"><h3>🏆 ಪಂದ್ಯದ ಶ್ರೇಷ್ಠ ಆಟಗಾರ</h3><p>{kn_pom}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="player-of-match"><h3>🏆 Player of the Match</h3><p>{en_pom}</p></div>', unsafe_allow_html=True)

    if "turning_point" in pm:
        show_dual("Turning Point", pm["turning_point"])

    perfs = pm.get("top_performances", [])
    if perfs:
        st.markdown('<div class="section-header">⭐ Top Performances</div>', unsafe_allow_html=True)
        for perf in perfs:
            if not isinstance(perf, dict):
                continue
            txt = f"**{perf.get('player','')}** — {perf.get('stat','')}. {perf.get('comment','')}"
            st.markdown(f'<div class="highlight-card">{txt}</div>', unsafe_allow_html=True)
            if enable_kn:
                kn_txt = translate_to_kannada(f"{perf.get('player','')} — {perf.get('stat','')}. {perf.get('comment','')}")
                st.markdown(f'<div class="highlight-card" style="color:#ffd6e0">{kn_txt}</div>', unsafe_allow_html=True)

    if "closing_thought" in pm:
        show_dual("Closing", pm["closing_thought"])


def display_football_commentary(data: dict):
    """Render full football commentary + post-match."""
    # Normalize top level
    if isinstance(data, list):
        data = next((x for x in data if isinstance(x, dict)), {})
    if not data or "error" in data:
        st.markdown(f'<div class="error-box">⚠️ {data.get("error","Empty response")}</div>', unsafe_allow_html=True)
        return

    st.markdown("---")
    st.markdown("## 🎙️ Match Commentary")

    if "match_intro" in data:
        show_dual("Match Atmosphere", data["match_intro"])

    if "first_half_commentary" in data:
        show_dual("First Half", data["first_half_commentary"])

    goals = data.get("goal_highlights", [])
    if goals:
        st.markdown('<div class="section-header">⚽ Goal Highlights</div>', unsafe_allow_html=True)
        for g in goals:
            if not isinstance(g, dict):
                continue
            desc = g.get("description", "")
            minute = g.get("minute", "")
            en_txt = f"**{minute}'** — {desc}"
            if enable_kn:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="goal-card">{en_txt}</div>', unsafe_allow_html=True)
                with c2:
                    kn_desc = translate_to_kannada(desc)
                    st.markdown(f'<div class="commentary-box-kn">**{minute}\'** — {kn_desc}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="goal-card">{en_txt}</div>', unsafe_allow_html=True)

    if "second_half_commentary" in data:
        show_dual("Second Half", data["second_half_commentary"])

    # Post-match
    pm = data.get("post_match_analysis", {})
    if isinstance(pm, list):
        pm = next((x for x in pm if isinstance(x, dict)), {})
    if not pm:
        return

    st.markdown("---")
    st.markdown("## 📊 Post-Match Analysis")

    if "match_headline" in pm:
        st.markdown(f"### 📰 {pm['match_headline']}")

    if "match_summary" in pm:
        show_dual("Match Summary", pm["match_summary"])

    pom = pm.get("player_of_match", {})
    if pom and isinstance(pom, dict):
        en_pom = f"{pom.get('name','')} ({pom.get('team','')}) — {pom.get('reason','')}"
        if enable_kn:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="player-of-match"><h3>🏆 Player of the Match</h3><p>{en_pom}</p></div>', unsafe_allow_html=True)
            with c2:
                kn_pom = translate_to_kannada(en_pom)
                st.markdown(f'<div class="player-of-match"><h3>🏆 ಪಂದ್ಯದ ಶ್ರೇಷ್ಠ ಆಟಗಾರ</h3><p>{kn_pom}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="player-of-match"><h3>🏆 Player of the Match</h3><p>{en_pom}</p></div>', unsafe_allow_html=True)

    if "tactical_breakdown" in pm:
        show_dual("Tactical Breakdown", pm["tactical_breakdown"])

    if "turning_point" in pm:
        show_dual("Turning Point", pm["turning_point"])

    perfs = pm.get("top_performances", [])
    if perfs:
        st.markdown('<div class="section-header">⭐ Top Performances</div>', unsafe_allow_html=True)
        for perf in perfs:
            if not isinstance(perf, dict):
                continue
            txt = f"**{perf.get('player','')}** {perf.get('rating','')} — {perf.get('comment','')}"
            st.markdown(f'<div class="highlight-card">{txt}</div>', unsafe_allow_html=True)
            if enable_kn:
                kn_txt = translate_to_kannada(f"{perf.get('player','')} — {perf.get('comment','')}")
                st.markdown(f'<div class="highlight-card" style="color:#ffd6e0">{kn_txt}</div>', unsafe_allow_html=True)

    if "closing_line" in data:
        show_dual("Closing", data["closing_line"])


# ══════════════════════════════════════════════════════════════════════════════
# MODE 1 — CRICKET COMMENTARY
# ══════════════════════════════════════════════════════════════════════════════
if "Cricket" in mode:

    match_list   = get_match_list(dfs)
    match_labels = [m["label"] for m in match_list]
    chosen_label = st.selectbox("Select a Match", match_labels)
    chosen_no    = match_list[match_labels.index(chosen_label)]["match_no"]

    st.markdown("##### Or upload your own match data")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        uploaded_json = st.file_uploader("Upload JSON", type=["json"], key="ujson")
    with col_u2:
        uploaded_csv = st.file_uploader("Upload CSV", type=["csv"], key="ucsv")

    match_ctx = None
    if uploaded_json:
        try:
            raw = json.load(uploaded_json)
            match_ctx = load_match_data(raw)
            st.success("✅ Custom JSON loaded")
        except Exception as ex:
            st.error(f"JSON error: {ex}")
    elif uploaded_csv:
        try:
            match_ctx = load_match_data(uploaded_csv.read().decode("utf-8"), sport="cricket")
            st.success("✅ Custom CSV loaded")
        except Exception as ex:
            st.error(f"CSV error: {ex}")
    else:
        try:
            match_ctx = build_context_from_match(chosen_no, dfs)
        except Exception as ex:
            st.error(f"Could not build match context: {ex}")

    if not match_ctx:
        st.stop()

    # Match overview
    st.markdown("---")
    st.markdown("## 📋 Match Overview")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="v">{match_ctx.team1}</div><div class="l">Team 1</div></div>', unsafe_allow_html=True)
    with c2:
        stage = match_ctx.result.get("stage", "T20")
        st.markdown(f'<div class="stat-box"><div class="v" style="color:#e94560">VS</div><div class="l">{stage} · {match_ctx.date}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="v">{match_ctx.team2}</div><div class="l">Team 2</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">🏟️ {match_ctx.venue} &nbsp;|&nbsp; 🏆 Winner: <strong>{match_ctx.result.get("winner","TBD")}</strong> &nbsp;|&nbsp; Margin: {match_ctx.result.get("margin","")}</div>', unsafe_allow_html=True)

    for inn in match_ctx.innings_summaries:
        with st.expander(f"Innings {inn['innings_number']}: {inn['batting_team']} — {inn['total']} ({inn['overs']} ov, RR {inn['run_rate']})"):
            col_b, col_w = st.columns(2)
            with col_b:
                st.markdown("**Top Batsmen (tournament form)**")
                for b in inn["top_batsmen"]:
                    st.markdown(f"- **{b['player']}**: {b['runs']} runs | Avg {b.get('average','')} | SR {b.get('strike_rate','')} | {b['fours']}×4 {b['sixes']}×6")
            with col_w:
                st.markdown("**Top Bowlers (tournament form)**")
                for bw in inn["top_bowlers"]:
                    st.markdown(f"- **{bw['player']}**: {bw['wickets']} wkts | Econ {bw['economy']} | Best: {bw.get('best','')}")

    if match_ctx.key_moments:
        with st.expander("🏅 Tournament Awards"):
            for km in match_ctx.key_moments:
                st.markdown(f"• {km}")

    st.markdown("---")
    if st.button("🎙️ Generate Cricket Commentary", type="primary", use_container_width=True):
        with st.spinner("Generating with Groq AI — ~20 seconds..."):
            try:
                commentary = {}
                for i in range(len(match_ctx.innings_summaries)):
                    commentary[f"innings_{i+1}"] = gen_cricket_commentary(match_ctx, i)
                commentary["post_match"] = gen_cricket_post_match(match_ctx)
                st.session_state["cricket_commentary"] = commentary
                st.session_state["sport"] = "cricket"
                st.success("✅ Commentary ready! Scroll down.")
                st.rerun()
            except Exception as ex:
                st.error(f"Generation failed: {ex}")

    if st.session_state.get("sport") == "cricket" and "cricket_commentary" in st.session_state:
        display_cricket_commentary(st.session_state["cricket_commentary"])
        st.markdown("---")
        st.download_button(
            "⬇️ Download Commentary (JSON)",
            data=json.dumps(st.session_state["cricket_commentary"], ensure_ascii=False, indent=2),
            file_name="cricket_commentary.json",
            mime="application/json"
        )


# ══════════════════════════════════════════════════════════════════════════════
# MODE 2 — FOOTBALL COMMENTARY
# ══════════════════════════════════════════════════════════════════════════════
elif "Football" in mode:
    st.markdown("## ⚽ Football Match Commentary")

    st.markdown("### Enter Match Details")

    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("Home Team", value="Bengaluru FC")
        home_score = st.number_input("Home Goals", min_value=0, max_value=20, value=3)
        home_possession = st.slider("Home Possession %", 0, 100, 58)
        home_shots = st.number_input("Home Shots", min_value=0, value=14)
        home_shots_on = st.number_input("Home Shots on Target", min_value=0, value=7)
    with col2:
        away_team = st.text_input("Away Team", value="Chennaiyin FC")
        away_score = st.number_input("Away Goals", min_value=0, max_value=20, value=1)
        away_possession = 100 - home_possession
        st.markdown(f"**Away Possession:** {away_possession}%")
        away_shots = st.number_input("Away Shots", min_value=0, value=8)
        away_shots_on = st.number_input("Away Shots on Target", min_value=0, value=3)

    competition = st.text_input("Competition", value="Indian Super League")
    venue       = st.text_input("Venue", value="Sree Kanteerava Stadium, Bengaluru")
    match_date  = st.text_input("Date", value="2024-05-30")

    st.markdown("### Goals (optional)")
    goals_input = st.text_area(
        "One goal per line: minute, team, scorer (e.g. 18, Bengaluru FC, Sunil Chhetri)",
        value="18, Bengaluru FC, Sunil Chhetri\n34, Bengaluru FC, Alan Costa\n61, Chennaiyin FC, Nerijus Valskis\n78, Bengaluru FC, Cleiton Silva"
    )

    # Parse goals
    goals = []
    for line in goals_input.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            goals.append({
                "minute": parts[0],
                "team":   parts[1],
                "scorer": parts[2],
                "assist": parts[3] if len(parts) > 3 else None,
                "type":   "open_play"
            })

    winner = home_team if home_score > away_score else (away_team if away_score > home_score else "Draw")
    margin = f"{max(home_score, away_score)}-{min(home_score, away_score)}"

    # Show score card
    st.markdown(f"""
    <div class="football-score">
        <div class="teams">{home_team} &nbsp;&nbsp; vs &nbsp;&nbsp; {away_team}</div>
        <div class="score">{home_score} – {away_score}</div>
        <div class="teams">{competition} · {venue}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎙️ Generate Football Commentary", type="primary", use_container_width=True):
        with st.spinner("Generating football commentary with Groq AI..."):
            try:
                from src.data_parser import FootballMatchContext
                football_ctx = FootballMatchContext(
                    match_id="FB_MANUAL",
                    venue=venue,
                    home_team=home_team,
                    away_team=away_team,
                    competition=competition,
                    date=match_date,
                    score={"home": home_score, "away": away_score},
                    goals=goals,
                    key_moments=[],
                    stats={
                        "home": {
                            "possession": home_possession,
                            "shots": home_shots,
                            "shots_on_target": home_shots_on
                        },
                        "away": {
                            "possession": away_possession,
                            "shots": away_shots,
                            "shots_on_target": away_shots_on
                        }
                    },
                    player_ratings=[],
                    cards=[],
                    result={"winner": winner, "margin": margin}
                )

                result = gen_football_commentary(football_ctx)
                st.session_state["football_commentary"] = result
                st.session_state["sport"] = "football"
                st.success("✅ Football commentary ready! Scroll down.")
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
            mime="application/json"
        )


# ══════════════════════════════════════════════════════════════════════════════
# MODE 3 — TOURNAMENT STATS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("## 📊 ICC T20 World Cup 2026 — Tournament Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Points Table", "🏏 Top Batters", "🎯 Top Bowlers", "🥇 Awards"])

    with tab1:
        standings = get_standings(dfs)
        for grp, grp_df in standings.groupby("group"):
            st.markdown(f"#### Group {grp}")
            display = grp_df[["team", "matches_played", "won", "lost", "net_run_rate", "points", "qualified"]].copy()
            display.columns = ["Team", "P", "W", "L", "NRR", "Pts", "Qualified"]
            st.dataframe(display.reset_index(drop=True), use_container_width=True)

    with tab2:
        st.markdown("#### Top Run-Scorers")
        batters = get_top_batters(dfs, 10)
        batters.columns = ["Player", "Team", "Matches", "Runs", "Avg", "SR", "50s", "100s"]
        st.dataframe(batters.reset_index(drop=True), use_container_width=True)
        top5 = get_top_batters(dfs, 5)
        st.bar_chart(top5.set_index("player")["runs"])

    with tab3:
        st.markdown("#### Top Wicket-Takers")
        bowlers = get_top_bowlers(dfs, 10)
        bowlers.columns = ["Player", "Team", "Matches", "Wickets", "Econ", "Avg", "Best"]
        st.dataframe(bowlers.reset_index(drop=True), use_container_width=True)
        top5b = get_top_bowlers(dfs, 5)
        st.bar_chart(top5b.set_index("player")["wickets"])

    with tab4:
        st.markdown("#### 🥇 Tournament Awards")
        awards_df = get_awards(dfs)
        for _, r in awards_df.iterrows():
            st.markdown(f"**{r['award']}** — {r['player_or_detail']} ({r.get('team', '')})")