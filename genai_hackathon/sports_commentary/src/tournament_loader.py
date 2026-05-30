import pandas as pd

def load_tournament_data():
    return {
        "matches": pd.read_csv("data/matches.csv"),
        "batting": pd.read_csv("data/batting_stats.csv"),
        "bowling": pd.read_csv("data/bowling_stats.csv"),
        "points": pd.read_csv("data/points_table.csv"),
        "awards": pd.read_csv("data/awards.csv"),
        "scorecards": pd.read_csv("data/key_scorecards.csv"),
        "squads": pd.read_csv("data/squads.csv"),
        "summary": pd.read_csv("data/tournament_summary.csv"),
        "venues": pd.read_csv("data/venues.csv")
    }