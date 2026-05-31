import pandas as pd

files = [
    "matches.csv",
    "batting_stats.csv",
    "bowling_stats.csv",
    "points_table.csv",
    "awards.csv",
    "tournament_summary.csv"
]

for file in files:
    print("\n" + "="*50)
    print(file)

    df = pd.read_csv(f"data/{file}")

    print(df.columns.tolist())
    print(df.head(2))