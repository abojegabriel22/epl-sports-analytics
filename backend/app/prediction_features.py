
import pandas as pd

# Load cleaned EPL data
df = pd.read_csv("datasets/epl_cleaned.csv")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Store historical performance for each team
team_history = {}

prediction_records = []

# Process one date at a time to prevent data leakage
for match_date, daily_matches in df.groupby("Date", sort=True):

    daily_updates = []

    # Build features using only matches from earlier dates
    for _, match in daily_matches.iterrows():

        home = match["HomeTeam"]
        away = match["AwayTeam"]

        def get_team_stats(team):
            history = team_history.get(team, [])
            recent = history[-5:]

            if not recent:
                return {
                    "form_points": 0,
                    "avg_goals_scored": 0,
                    "avg_goals_conceded": 0,
                    "matches_played": len(history)
                }

            return {
                "form_points": sum(item["points"] for item in recent),
                "avg_goals_scored": sum(item["scored"] for item in recent) / len(recent),
                "avg_goals_conceded": sum(item["conceded"] for item in recent) / len(recent),
                "matches_played": len(history)
            }

        home_stats = get_team_stats(home)
        away_stats = get_team_stats(away)

        prediction_records.append({
            "Date": match_date,
            "HomeTeam": home,
            "AwayTeam": away,
            "HomeFormPoints": home_stats["form_points"],
            "AwayFormPoints": away_stats["form_points"],
            "HomeAvgGoalsScored": home_stats["avg_goals_scored"],
            "AwayAvgGoalsScored": away_stats["avg_goals_scored"],
            "HomeAvgGoalsConceded": home_stats["avg_goals_conceded"],
            "AwayAvgGoalsConceded": away_stats["avg_goals_conceded"],
            "HomeMatchesPlayed": home_stats["matches_played"],
            "AwayMatchesPlayed": away_stats["matches_played"],
            "HomeAdvantage": 1,
            "Result": match["FTR"]
        })

        # Calculate results, but don't update history yet
        home_goals = match["FTHG"]
        away_goals = match["FTAG"]

        if home_goals > away_goals:
            home_points, away_points = 3, 0
        elif home_goals < away_goals:
            home_points, away_points = 0, 3
        else:
            home_points, away_points = 1, 1

        daily_updates.append(
            (home, {
                "points": home_points,
                "scored": home_goals,
                "conceded": away_goals
            })
        )

        daily_updates.append(
            (away, {
                "points": away_points,
                "scored": away_goals,
                "conceded": home_goals
            })
        )

    # Update histories only after processing every match on this date
    for team, result in daily_updates:
        team_history.setdefault(team, []).append(result)

# Create and save the features dataset
features_df = pd.DataFrame(prediction_records)

features_df.to_csv("datasets/prediction_features.csv", index=False)

print("IMPROVED PREDICTION FEATURES")
print(features_df.head(10).to_string(index=False))

print("\nDataset shape:", features_df.shape)
print("\nMissing values:")
print(features_df.isnull().sum())

print("\nSaved to datasets/prediction_features.csv")
print("Feature engineering completed successfully!")
