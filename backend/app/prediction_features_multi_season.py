
import pandas as pd
from collections import defaultdict

# Load the combined dataset
df = pd.read_csv("datasets/epl_multi_season.csv")

df["Date"] = pd.to_datetime(df["Date"])

# Sort matches chronologically
df = df.sort_values(
    by=["Date", "HomeTeam", "AwayTeam"]
).reset_index(drop=True)

# Store each team's previous match history
team_history = defaultdict(list)

# Get overall and venue-specific features
def get_team_features(team, venue):

    history = team_history[team]

    last_five = history[-5:]

    venue_history = [
        match for match in history
        if match["Venue"] == venue
    ][-5:]

    def calculate_stats(matches):

        if not matches:
            return {
                "FormPoints": 0,
                "AvgGoalsScored": 0,
                "AvgGoalsConceded": 0
            }

        return {
            "FormPoints": sum(
                match["Points"] for match in matches
            ),
            "AvgGoalsScored": sum(
                match["Scored"] for match in matches
            ) / len(matches),
            "AvgGoalsConceded": sum(
                match["Conceded"] for match in matches
            ) / len(matches)
        }

    overall = calculate_stats(last_five)
    venue_stats = calculate_stats(venue_history)

    return {
        "FormPoints": overall["FormPoints"],
        "AvgGoalsScored": overall["AvgGoalsScored"],
        "AvgGoalsConceded": overall["AvgGoalsConceded"],
        "MatchesPlayed": len(history),

        "VenueFormPoints": venue_stats["FormPoints"],
        "VenueAvgGoalsScored": venue_stats["AvgGoalsScored"],
        "VenueAvgGoalsConceded": venue_stats["AvgGoalsConceded"],
        "VenueMatchesPlayed": len(venue_history)
    }


feature_rows = []

# Process one date at a time to prevent same-day data leakage
for match_date, daily_matches in df.groupby("Date", sort=True):

    daily_updates = []

    for _, match in daily_matches.iterrows():

        home = match["HomeTeam"]
        away = match["AwayTeam"]

        home_features = get_team_features(home, "Home")
        away_features = get_team_features(away, "Away")

        # Build features before updating histories
        feature_rows.append({
            "Date": match_date,
            "HomeTeam": home,
            "AwayTeam": away,

            "HomeFormPoints":
                home_features["FormPoints"],

            "AwayFormPoints":
                away_features["FormPoints"],

            "HomeAvgGoalsScored":
                home_features["AvgGoalsScored"],

            "AwayAvgGoalsScored":
                away_features["AvgGoalsScored"],

            "HomeAvgGoalsConceded":
                home_features["AvgGoalsConceded"],

            "AwayAvgGoalsConceded":
                away_features["AvgGoalsConceded"],

            "HomeMatchesPlayed":
                home_features["MatchesPlayed"],

            "AwayMatchesPlayed":
                away_features["MatchesPlayed"],

            "HomeVenueFormPoints":
                home_features["VenueFormPoints"],

            "AwayVenueFormPoints":
                away_features["VenueFormPoints"],

            "HomeVenueAvgGoalsScored":
                home_features["VenueAvgGoalsScored"],

            "AwayVenueAvgGoalsScored":
                away_features["VenueAvgGoalsScored"],

            "HomeVenueAvgGoalsConceded":
                home_features["VenueAvgGoalsConceded"],

            "AwayVenueAvgGoalsConceded":
                away_features["VenueAvgGoalsConceded"],

            "HomeVenueMatchesPlayed":
                home_features["VenueMatchesPlayed"],

            "AwayVenueMatchesPlayed":
                away_features["VenueMatchesPlayed"],

            "Result": match["FTR"]
        })

        # Prepare history updates
        if match["FTR"] == "H":
            home_points = 3
            away_points = 0

        elif match["FTR"] == "D":
            home_points = 1
            away_points = 1

        else:
            home_points = 0
            away_points = 3

        daily_updates.append({
            "Team": home,
            "Venue": "Home",
            "Scored": int(match["FTHG"]),
            "Conceded": int(match["FTAG"]),
            "Points": home_points
        })

        daily_updates.append({
            "Team": away,
            "Venue": "Away",
            "Scored": int(match["FTAG"]),
            "Conceded": int(match["FTHG"]),
            "Points": away_points
        })

    # Update histories after all matches on the date
    for update in daily_updates:

        team_history[update["Team"]].append({
            "Venue": update["Venue"],
            "Scored": update["Scored"],
            "Conceded": update["Conceded"],
            "Points": update["Points"]
        })


# Convert features into a DataFrame
features_df = pd.DataFrame(feature_rows)

# Save the new feature dataset
output_path = "datasets/prediction_features_multi_season.csv"

features_df.to_csv(output_path, index=False)

# Display results
print("\nIMPROVED MULTI-SEASON FEATURES CREATED")
print("=" * 50)

print("Total matches:", len(features_df))
print("Dataset shape:", features_df.shape)

print("\nMissing values:")
print(features_df.isnull().sum())

print("\nFirst five records:")
print(features_df.head().to_string(index=False))

print("\nLast five records:")
print(features_df.tail().to_string(index=False))

print("\nSaved to:", output_path)
