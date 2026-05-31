"""
kaggle_loader.py — Loads real Kaggle CSVs and builds CricketMatchContext objects
"""

import pandas as pd
from src.data_parser import CricketMatchContext


def load_tournament_data(data_dir: str = "data") -> dict:
    return {
        "matches":   pd.read_csv(f"{data_dir}/matches.csv"),
        "batting":   pd.read_csv(f"{data_dir}/batting_stats.csv"),
        "bowling":   pd.read_csv(f"{data_dir}/bowling_stats.csv"),
        "points":    pd.read_csv(f"{data_dir}/points_table.csv"),
        "awards":    pd.read_csv(f"{data_dir}/awards.csv"),
        "summary":   pd.read_csv(f"{data_dir}/tournament_summary.csv"),
    }


def get_match_list(dfs: dict) -> list[dict]:
    """Returns list of matches for display in dropdown."""
    rows = []
    for _, row in dfs["matches"].iterrows():
        rows.append({
            "label": f"Match {row['match_no']} | {row['team1']} vs {row['team2']} ({row['date']}) — {row['stage']}",
            "match_no": row["match_no"]
        })
    return rows


def build_context_from_match(match_no: int, dfs: dict) -> CricketMatchContext:
    """
    Given a match number and the loaded DataFrames,
    build a CricketMatchContext using real data.
    """
    matches_df  = dfs["matches"]
    batting_df  = dfs["batting"]
    bowling_df  = dfs["bowling"]
    awards_df   = dfs["awards"]

    # ── Match row ────────────────────────────────────────────────────────────
    row = matches_df[matches_df["match_no"] == match_no].iloc[0]

    team1  = str(row["team1"])
    team2  = str(row["team2"])
    winner = str(row["winner"])
    margin = str(row["margin"])
    venue  = str(row["venue"])
    date   = str(row["date"])
    stage  = str(row["stage"])

    # ── Batting stats for these two teams ───────────────────────────────────
    def team_batting(team: str) -> list[dict]:
        df = batting_df[batting_df["team"] == team].copy()
        df = df.sort_values("runs", ascending=False).head(5)
        out = []
        for _, r in df.iterrows():
            out.append({
                "player":           r["player"],
                "runs":             int(r["runs"]),
                "balls":            max(1, int(round(r["runs"] / max(r["strike_rate"], 1) * 100))),
                "fours":            int(r["fours"]),
                "sixes":            int(r["sixes"]),
                "dismissed":        "unknown",
                "dismissal_bowler": None,
                "average":          round(float(r["average"]), 2),
                "strike_rate":      round(float(r["strike_rate"]), 2),
            })
        return out

    def team_bowling(team: str) -> list[dict]:
        df = bowling_df[bowling_df["team"] == team].copy()
        df = df.sort_values("wickets", ascending=False).head(4)
        out = []
        for _, r in df.iterrows():
            out.append({
                "player":   r["player"],
                "overs":    float(r["overs"]),
                "wickets":  int(r["wickets"]),
                "runs":     int(r["runs_conceded"]),
                "economy":  round(float(r["economy"]), 2),
                "best":     str(r["best_figures"]),
            })
        return out

    # ── Key moments from awards ──────────────────────────────────────────────
    key_moments = []
    for _, r in awards_df.iterrows():
        award = str(r["award"])
        detail = str(r["player_or_detail"])
        team_name = str(r["team"]) if "team" in awards_df.columns else ""
        key_moments.append(f"{award}: {detail} ({team_name})")

    # ── Top performers (batting) across both teams ───────────────────────────
    both_batting = batting_df[batting_df["team"].isin([team1, team2])].copy()
    both_batting = both_batting.sort_values("runs", ascending=False).head(6)
    top_performers = []
    for _, r in both_batting.iterrows():
        top_performers.append({
            "player":      r["player"],
            "team":        r["team"],
            "runs":        int(r["runs"]),
            "balls":       max(1, int(round(r["runs"] / max(r["strike_rate"], 1) * 100))),
            "fours":       int(r["fours"]),
            "sixes":       int(r["sixes"]),
            "dismissed":   "unknown",
            "dismissal_bowler": None,
        })

    # ── Build innings summaries ──────────────────────────────────────────────
    # We only have tournament-level batting, not per-match scores.
    # So we use tournament batting as "form" context — honest and useful for LLM.
    innings_summaries = []
    for i, (bat_team, bowl_team) in enumerate([(team1, team2), (team2, team1)], 1):
        batsmen  = team_batting(bat_team)
        bowlers  = team_bowling(bowl_team)
        # Estimate total from top batters (realistic approximation)
        est_runs = sum(b["runs"] for b in batsmen[:4]) if batsmen else 150
        innings_summaries.append({
            "innings_number": i,
            "batting_team":   bat_team,
            "bowling_team":   bowl_team,
            "total":          f"~{est_runs // i} (est)",   # div by innings to scale down
            "overs":          20.0,
            "run_rate":       round((est_runs // i) / 20, 2),
            "top_batsmen":    batsmen[:3],
            "top_bowlers":    bowlers[:2],
        })

    # ── Assemble context ─────────────────────────────────────────────────────
    ctx = CricketMatchContext(
        match_id=str(match_no),
        venue=venue,
        team1=team1,
        team2=team2,
        format="T20",
        date=date,
        innings_summaries=innings_summaries,
        ball_by_ball=[],          # not in Kaggle dataset
        key_moments=key_moments,
        result={"winner": winner, "margin": margin, "stage": stage},
        top_performers=top_performers,
    )

    return ctx


def get_tournament_summary(dfs: dict) -> dict:
    """Extracts tournament-level facts for sidebar display."""
    summary = {}
    for _, row in dfs["summary"].iterrows():
        summary[str(row["field"])] = str(row["value"])
    return summary


def get_standings(dfs: dict) -> pd.DataFrame:
    return dfs["points"].sort_values(["group", "points"], ascending=[True, False])


def get_top_batters(dfs: dict, n: int = 5) -> pd.DataFrame:
    return dfs["batting"].sort_values("runs", ascending=False).head(n)[
        ["player", "team", "matches", "runs", "average", "strike_rate", "fifties", "hundreds"]
    ]


def get_top_bowlers(dfs: dict, n: int = 5) -> pd.DataFrame:
    return dfs["bowling"].sort_values("wickets", ascending=False).head(n)[
        ["player", "team", "matches", "wickets", "economy", "average", "best_figures"]
    ]


def get_awards(dfs: dict) -> pd.DataFrame:
    return dfs["awards"]