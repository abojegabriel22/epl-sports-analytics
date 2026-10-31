
import pandas as pd

# Load cleaned EPL dataset
df = pd.read_csv("datasets/epl_cleaned.csv")

# Get all unique teams
teams = sorted(
    set(df["HomeTeam"].unique()) |
    set(df["AwayTeam"].unique())
)

team_stats = []

for team in teams:
    # Matches played at home
    home = df[df["HomeTeam"] == team]

    # Matches played away
    away = df[df["AwayTeam"] == team]

    played = len(home) + len(away)

    # Goals scored and conceded
    goals_for = home["FTHG"].sum() + away["FTAG"].sum()
    goals_against = home["FTAG"].sum() + away["FTHG"].sum()

    # Wins, draws and losses
    home_wins = (home["FTR"] == "H").sum()
    away_wins = (away["FTR"] == "A").sum()

    draws = (
        (home["FTR"] == "D").sum() +
        (away["FTR"] == "D").sum()
    )

    wins = home_wins + away_wins
    losses = played - wins - draws

    points = wins * 3 + draws

    team_stats.append({
        "Team": team,
        "Played": played,
        "Won": wins,
        "Drawn": draws,
        "Lost": losses,
        "GF": goals_for,
        "GA": goals_against,
        "GD": goals_for - goals_against,
        "Points": points
    })

# Create league table
table = pd.DataFrame(team_stats)

table = table.sort_values(
    by=["Points", "GD", "GF"],
    ascending=False
)

table.insert(
    0,
    "Position",
    range(1, len(table) + 1)
)

print("\nEPL TEAM PERFORMANCE TABLE")
print(table.to_string(index=False))

# Save results
table.to_csv(
    "datasets/team_performance.csv",
    index=False
)

print("\nTeam performance analysis completed!")
print("Saved to datasets/team_performance.csv")
