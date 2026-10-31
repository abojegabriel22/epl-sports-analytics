
import pandas as pd

# Load the cleaned EPL dataset
df = pd.read_csv("datasets/epl_cleaned.csv")

# Convert Date to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Sort matches chronologically
df = df.sort_values("Date").reset_index(drop=True)

# Store each team's previous match results
team_history = {}

# Store form analysis for every team
form_records = []

# Process matches one at a time
for _, match in df.iterrows():

    home = match["HomeTeam"]
    away = match["AwayTeam"]

    home_goals = match["FTHG"]
    away_goals = match["FTAG"]

    # Get each team's previous five results
    home_form = team_history.get(home, [])[-5:]
    away_form = team_history.get(away, [])[-5:]

    form_records.append({
        "Date": match["Date"],
        "HomeTeam": home,
        "AwayTeam": away,
        "HomePreviousForm": "-".join(home_form) if home_form else "No history",
        "AwayPreviousForm": "-".join(away_form) if away_form else "No history",
        "HomeFormPoints": sum(
            3 if result == "W" else 1 if result == "D" else 0
            for result in home_form
        ),
        "AwayFormPoints": sum(
            3 if result == "W" else 1 if result == "D" else 0
            for result in away_form
        )
    })

    # Determine the current match result
    if home_goals > away_goals:
        home_result, away_result = "W", "L"
    elif home_goals < away_goals:
        home_result, away_result = "L", "W"
    else:
        home_result, away_result = "D", "D"

    # Update team histories AFTER recording previous form
    team_history.setdefault(home, []).append(home_result)
    team_history.setdefault(away, []).append(away_result)

# Convert results to a DataFrame
form_df = pd.DataFrame(form_records)

# Save the form analysis
form_df.to_csv("datasets/team_form_analysis.csv", index=False)

print("TEAM FORM ANALYSIS")
print(form_df.tail(10).to_string(index=False))

print("\nSaved to datasets/team_form_analysis.csv")
print("\nTeam form analysis completed successfully!")
