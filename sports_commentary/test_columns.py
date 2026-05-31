import pandas as pd, os

files = [
    "data/matches.csv", "data/batting_stats.csv", "data/bowling_stats.csv",
    "data/points_table.csv", "data/awards.csv", "data/key_scorecards.csv",
    "data/squads.csv", "data/tournament_summary.csv", "data/venues.csv"
]

for f in files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        print(f"\n{'='*40}")
        print(f"FILE: {f}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(df.head(2).to_string())
    else:
        print(f"\nMISSING: {f}")