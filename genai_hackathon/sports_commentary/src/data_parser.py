"""
data_parser.py — Parses cricket (T20) and football match stats
Supports JSON and CSV input formats
"""

import json
import pandas as pd
import io
from dataclasses import dataclass, field


@dataclass
class CricketMatchContext:
    match_id: str
    venue: str
    team1: str
    team2: str
    format: str
    date: str
    innings_summaries: list = field(default_factory=list)
    ball_by_ball: list = field(default_factory=list)
    key_moments: list = field(default_factory=list)
    result: dict = field(default_factory=dict)
    top_performers: list = field(default_factory=list)


@dataclass
class FootballMatchContext:
    match_id: str
    venue: str
    home_team: str
    away_team: str
    competition: str
    date: str
    score: dict = field(default_factory=dict)
    goals: list = field(default_factory=list)
    key_moments: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    player_ratings: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    result: dict = field(default_factory=dict)


def parse_cricket_json(data: dict) -> CricketMatchContext:
    info = data["match_info"]
    ctx = CricketMatchContext(
        match_id=info["match_id"],
        venue=info["venue"],
        team1=info["team1"],
        team2=info["team2"],
        format=info.get("format", "T20"),
        date=info["date"],
        result=data.get("result", {})
    )

    for inning in data.get("innings", []):
        summary = {
            "innings_number": inning["innings_number"],
            "batting_team": inning["batting_team"],
            "bowling_team": inning["bowling_team"],
            "total": f"{inning['total_runs']}/{inning['total_wickets']}",
            "overs": inning["total_overs"],
            "run_rate": round(inning["total_runs"] / inning["total_overs"], 2),
            "top_batsmen": sorted(inning["batting"], key=lambda x: x["runs"], reverse=True)[:3],
            "top_bowlers": sorted(inning["bowling"], key=lambda x: x["wickets"], reverse=True)[:2],
        }
        ctx.innings_summaries.append(summary)

        for ball in inning.get("ball_by_ball", []):
            if ball.get("event") in ("wicket", "six", "boundary"):
                ctx.ball_by_ball.append({
                    "over": ball["over"],
                    "ball": ball["ball"],
                    "bowler": ball["bowler"],
                    "batsman": ball["batsman"],
                    "event": ball["event"],
                    "runs": ball.get("runs", 0),
                    "innings": inning["innings_number"],
                    "batting_team": inning["batting_team"]
                })

    for inn in data.get("innings", []):
        for batsman in inn["batting"]:
            if batsman["runs"] >= 50:
                ctx.key_moments.append(
                    f"{batsman['player']} scored {batsman['runs']} off {batsman['balls']} balls "
                    f"({'not out' if batsman['dismissed'] == 'not_out' else 'dismissed by ' + (batsman['dismissal_bowler'] or 'unknown')})"
                )
        for bowler in inn["bowling"]:
            if bowler["wickets"] >= 2:
                ctx.key_moments.append(
                    f"{bowler['player']} took {bowler['wickets']} wickets for {bowler['runs']} runs "
                    f"(economy: {bowler['economy']})"
                )

    all_batsmen = []
    for inn in data.get("innings", []):
        for b in inn["batting"]:
            all_batsmen.append({**b, "team": inn["batting_team"]})
    ctx.top_performers = sorted(all_batsmen, key=lambda x: x["runs"], reverse=True)[:5]

    return ctx


def parse_football_json(data: dict) -> FootballMatchContext:
    info = data["match_info"]
    return FootballMatchContext(
        match_id=info["match_id"],
        venue=info["venue"],
        home_team=info["home_team"],
        away_team=info["away_team"],
        competition=info.get("competition", "Football"),
        date=info["date"],
        score=data.get("score", {}),
        goals=data.get("goals", []),
        key_moments=data.get("key_moments", []),
        stats=data.get("stats", {}),
        player_ratings=data.get("player_ratings", []),
        cards=data.get("cards", []),
        result=data.get("result", {})
    )


def parse_cricket_csv(csv_text: str) -> CricketMatchContext:
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().lower() for c in df.columns]

    batting_team = df["batting_team"].iloc[0] if "batting_team" in df.columns else "Team A"
    bowling_team = df["bowling_team"].iloc[0] if "bowling_team" in df.columns else "Team B"
    total_runs = int(df["runs"].sum())
    wickets = int((df["event"] == "wicket").sum()) if "event" in df.columns else 0

    ball_by_ball = []
    for _, row in df.iterrows():
        event = str(row.get("event", "")).lower()
        if event in ("wicket", "six", "boundary", "four"):
            ball_by_ball.append({
                "over": row.get("over", 0),
                "ball": row.get("ball", 0),
                "bowler": row.get("bowler", ""),
                "batsman": row.get("batsman", ""),
                "event": event,
                "runs": row.get("runs", 0),
                "innings": 1,
                "batting_team": batting_team
            })

    return CricketMatchContext(
        match_id="CSV_IMPORT",
        venue="Unknown Venue",
        team1=batting_team,
        team2=bowling_team,
        format="T20",
        date="",
        ball_by_ball=ball_by_ball,
        innings_summaries=[{
            "innings_number": 1,
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "total": f"{total_runs}/{wickets}",
            "overs": float(df["over"].max()) if "over" in df.columns else 20.0,
            "run_rate": round(total_runs / max(float(df["over"].max()), 1), 2) if "over" in df.columns else 0,
            "top_batsmen": [],
            "top_bowlers": []
        }],
        result={}
    )


def load_match_data(source, sport: str = None):
    if isinstance(source, dict):
        data = source
    elif isinstance(source, str):
        if source.strip().startswith("{"):
            data = json.loads(source)
        elif source.endswith(".json"):
            with open(source) as f:
                data = json.load(f)
        elif source.endswith(".csv"):
            with open(source) as f:
                csv_text = f.read()
            return parse_cricket_csv(csv_text)
        else:
            return parse_cricket_csv(source)
    else:
        raise ValueError("Unsupported source type")

    detected_sport = sport or data.get("match_info", {}).get("sport", "cricket")
    if detected_sport == "football":
        return parse_football_json(data)
    else:
        return parse_cricket_json(data)