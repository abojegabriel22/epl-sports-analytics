
import pandas as pd

# Sample EPL match dataset
matches = {
    "date": [
        "2025-08-15",
        "2025-08-16",
        "2025-08-17",
        "2025-08-18",
        "2025-08-19",
        "2025-08-20",
        "2025-08-21",
        "2025-08-22"
    ],

    "home_team": [
        "Arsenal",
        "Liverpool",
        "Chelsea",
        "Manchester City",
        "Tottenham",
        "Newcastle",
        "Manchester United",
        "Aston Villa"
    ],

    "away_team": [
        "Chelsea",
        "Manchester United",
        "Arsenal",
        "Liverpool",
        "Newcastle",
        "Tottenham",
        "Aston Villa",
        "Manchester City"
    ],

    "home_goals": [2, 3, 1, 2, 1, 2, 0, 1],
    "away_goals": [1, 1, 2, 2, 1, 0, 2, 3]
}

# Convert dictionary into a DataFrame
df = pd.DataFrame(matches)

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Determine match results
def get_result(row):
    if row["home_goals"] > row["away_goals"]:
        return "Home Win"
    elif row["home_goals"] < row["away_goals"]:
        return "Away Win"
    return "Draw"

df["result"] = df.apply(get_result, axis=1)

# Display dataset
print("\nEPL MATCH DATASET")
print(df.to_string(index=False))

# Calculate total goals
total_goals = df["home_goals"].sum() + df["away_goals"].sum()

# Calculate match outcomes
print("\nMATCH STATISTICS")
print("Total matches:", len(df))
print("Total goals:", total_goals)
print("\nMatch outcomes:")
print(df["result"].value_counts())

# Calculate average goals per match
print("\nAverage goals per match:", round(total_goals / len(df), 2))
