"""
prompt_builder.py — Simplified prompts for Groq JSON mode
"""

from src.data_parser import CricketMatchContext, FootballMatchContext

CRICKET_SYSTEM_PROMPT = "You are a cricket commentator. Respond in JSON only."
FOOTBALL_SYSTEM_PROMPT = "You are a football commentator. Respond in JSON only."


def build_cricket_over_by_over_prompt(ctx: CricketMatchContext, innings_index: int = 0):
    inn = ctx.innings_summaries[innings_index]

    bat1 = inn['top_batsmen'][0]['player'] if inn['top_batsmen'] else "top batsman"
    bat2 = inn['top_batsmen'][1]['player'] if len(inn['top_batsmen']) > 1 else "second batsman"
    bowl1 = inn['top_bowlers'][0]['player'] if inn['top_bowlers'] else "top bowler"

    bat_runs = inn['top_batsmen'][0]['runs'] if inn['top_batsmen'] else 0
    bowl_wkts = inn['top_bowlers'][0]['wickets'] if inn['top_bowlers'] else 0

    user_prompt = f"""Generate cricket innings commentary as JSON.

Innings {inn['innings_number']}: {inn['batting_team']} vs {inn['bowling_team']}
Venue: {ctx.venue}, Date: {ctx.date}
Score: {inn['total']} in {inn['overs']} overs, Run Rate: {inn['run_rate']}
Winner: {ctx.result.get('winner','TBD')} by {ctx.result.get('margin','')}
Star batsman: {bat1} ({bat_runs} runs), {bat2}
Star bowler: {bowl1} ({bowl_wkts} wickets)

Return valid JSON with these exact keys:
{{
  "innings_opener": "dramatic one sentence opening",
  "over_narratives": [
    {{"over_range": "1-6 (Powerplay)", "commentary": "two vivid sentences about powerplay"}},
    {{"over_range": "7-15 (Middle overs)", "commentary": "two vivid sentences about middle overs"}},
    {{"over_range": "16-20 (Death overs)", "commentary": "two vivid sentences about death overs"}}
  ],
  "key_moment_highlights": [
    "one sentence about {bat1}",
    "one sentence about {bowl1}",
    "one sentence about the innings momentum"
  ],
  "innings_closer": "dramatic one sentence wrap-up"
}}"""

    return CRICKET_SYSTEM_PROMPT, user_prompt


def build_cricket_post_match_prompt(ctx: CricketMatchContext):
    performers = "\n".join([
        f"{p['player']} ({p['team']}): {p['runs']} runs, {p['fours']}x4, {p['sixes']}x6"
        for p in ctx.top_performers[:4]
    ]) or "No data"

    moments = "\n".join([f"- {m}" for m in ctx.key_moments[:5]]) or "No data"

    innings_txt = "\n".join([
        f"Innings {s['innings_number']}: {s['batting_team']} {s['total']} in {s['overs']} overs (RR {s['run_rate']})"
        for s in ctx.innings_summaries
    ])

    user_prompt = f"""Generate post-match cricket analysis as JSON.

Match: {ctx.team1} vs {ctx.team2}, {ctx.venue}, {ctx.date}
Stage: {ctx.result.get('stage','')}
Result: {ctx.result.get('winner','TBD')} won by {ctx.result.get('margin','')}

{innings_txt}

Top performers:
{performers}

Awards and context:
{moments}

Return valid JSON with these exact keys:
{{
  "match_headline": "one punchy headline",
  "match_summary": "three sentence broadcaster-style summary",
  "player_of_match": {{
    "name": "player name",
    "team": "team name",
    "reason": "two sentences why they deserve it"
  }},
  "turning_point": "one sentence on the decisive moment",
  "top_performances": [
    {{"player": "name", "stat": "key stat", "comment": "one sentence"}},
    {{"player": "name", "stat": "key stat", "comment": "one sentence"}},
    {{"player": "name", "stat": "key stat", "comment": "one sentence"}}
  ],
  "closing_thought": "one memorable closing sentence"
}}"""

    return CRICKET_SYSTEM_PROMPT, user_prompt


def build_football_commentary_prompt(ctx: FootballMatchContext):
    goals_text = "\n".join([
        f"{g['minute']}': {g['team']} — {g['scorer']}" +
        (f" (assist: {g['assist']})" if g.get('assist') else "")
        for g in ctx.goals
    ]) or "No goals"

    moments_text = "\n".join([
        f"{m['minute']}': {m['event']}" for m in ctx.key_moments
    ]) or "No moments"

    home_s = ctx.stats.get("home", {})
    away_s = ctx.stats.get("away", {})
    score  = ctx.score

    goal_entries = ",\n".join([
        f'    {{"minute": "{g["minute"]}", "description": "dramatic two sentence goal description"}}'
        for g in ctx.goals
    ]) if ctx.goals else '    {"minute": "N/A", "description": "No goals scored"}'

    user_prompt = f"""Generate football match commentary as JSON.

Match: {ctx.home_team} vs {ctx.away_team}, {ctx.competition}
Venue: {ctx.venue}, Date: {ctx.date}
Score: {ctx.home_team} {score.get('home',0)}-{score.get('away',0)} {ctx.away_team}
Winner: {ctx.result.get('winner','TBD')}

Goals:
{goals_text}

Key moments:
{moments_text}

Stats: {ctx.home_team} {home_s.get('possession',0)}% possession, {home_s.get('shots',0)} shots
       {ctx.away_team} {away_s.get('possession',0)}% possession, {away_s.get('shots',0)} shots

Return valid JSON with these exact keys:
{{
  "match_intro": "two sentence atmosphere setter",
  "first_half_commentary": "three vivid sentences about first half",
  "second_half_commentary": "three vivid sentences about second half",
  "goal_highlights": [
{goal_entries}
  ],
  "post_match_analysis": {{
    "match_headline": "one punchy headline",
    "match_summary": "three sentence summary",
    "player_of_match": {{
      "name": "player name",
      "team": "team name",
      "reason": "two sentences justification"
    }},
    "tactical_breakdown": "two sentences on tactics",
    "turning_point": "one sentence decisive moment",
    "top_performances": [
      {{"player": "name", "rating": "8/10", "comment": "one sentence"}},
      {{"player": "name", "rating": "7/10", "comment": "one sentence"}}
    ]
  }},
  "closing_line": "one memorable closing sentence"
}}"""

    return FOOTBALL_SYSTEM_PROMPT, user_prompt