
import pandas as pd

# Sample match dataset
matches = [
    ["Arsenal", "Chelsea", 2, 1],
    ["Liverpool", "Manchester United", 3, 1],
    ["Chelsea", "Arsenal", 1, 2],
    ["Manchester City", "Liverpool", 2, 2],
    ["Tottenham", "Newcastle", 1, 1],
    ["Newcastle", "Tottenham", 2, 0],
    ["Manchester United", "Aston Villa", 0, 2],
    ["Aston Villa", "Manchester City", 1, 3]
]

df = pd.DataFrame(
    matches,
    columns=["home_team", "away_team", "home_goals", "away_goals"]
)

# Get all teams
teams = pd.unique(
    df[["home_team", "away_team"]].values.ravel()
)

# Initialize team statistics
statistics = []

for team in teams:

    home_matches = df[df["home_team"] == team]
    away_matches = df[df["away_team"] == team]

    played = len(home_matches) + len(away_matches)

    goals_scored = (
        home_matches["home_goals"].sum()
        + away_matches["away_goals"].sum()
    )

    goals_conceded = (
        home_matches["away_goals"].sum()
        + away_matches["home_goals"].sum()
    )

    wins = (
        (home_matches["home_goals"] > home_matches["away_goals"]).sum()
        + (away_matches["away_goals"] > away_matches["home_goals"]).sum()
    )

    draws = (
        (home_matches["home_goals"] == home_matches["away_goals"]).sum()
        + (away_matches["away_goals"] == away_matches["home_goals"]).sum()
    )

    losses = played - wins - draws

    points = (wins * 3) + draws

    statistics.append({
        "Team": team,
        "Played": played,
        "Won": wins,
        "Drawn": draws,
        "Lost": losses,
        "GF": goals_scored,
        "GA": goals_conceded,
        "GD": goals_scored - goals_conceded,
        "Points": points
    })

# Create league table
table = pd.DataFrame(statistics)

# Sort by points, then goal difference
table = table.sort_values(
    by=["Points", "GD", "GF"],
    ascending=False
).reset_index(drop=True)

table.index += 1
table.index.name = "Position"

print("\nEPL TEAM PERFORMANCE TABLE")
print(table.to_string())

print("\nTOP PERFORMING TEAM:")
print(table.iloc[0]["Team"])
