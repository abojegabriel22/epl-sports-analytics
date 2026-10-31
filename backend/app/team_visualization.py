
import pandas as pd
import matplotlib.pyplot as plt

# Sample team statistics
data = {
    "Team": [
        "Arsenal",
        "Liverpool",
        "Manchester City",
        "Newcastle",
        "Aston Villa",
        "Tottenham",
        "Chelsea",
        "Manchester United"
    ],

    "Points": [6, 4, 4, 4, 3, 1, 0, 0],
    "Goals_Scored": [4, 5, 5, 3, 3, 1, 2, 1],
    "Goals_Conceded": [2, 3, 3, 1, 3, 3, 4, 5]
}

df = pd.DataFrame(data)

# Chart 1: Team points comparison
plt.figure(figsize=(12, 6))

plt.bar(df["Team"], df["Points"])

plt.title("EPL Team Points Comparison")
plt.xlabel("Teams")
plt.ylabel("Points")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig("team_points.png")
plt.show()

# Chart 2: Goals scored vs conceded
plt.figure(figsize=(10, 6))

plt.plot(
    df["Team"],
    df["Goals_Scored"],
    marker="o",
    label="Goals Scored"
)

plt.plot(
    df["Team"],
    df["Goals_Conceded"],
    marker="o",
    label="Goals Conceded"
)

plt.title("EPL Goals Performance")
plt.xlabel("Teams")
plt.ylabel("Goals")

plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()

plt.savefig("team_goals.png")
plt.show()

print("Charts generated successfully!")
