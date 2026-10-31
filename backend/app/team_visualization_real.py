
import pandas as pd
import matplotlib.pyplot as plt

# Load actual team performance results
df = pd.read_csv("datasets/team_performance.csv")

# Sort teams by points for visualization
df = df.sort_values("Points", ascending=True)

# --------------------------------
# CHART 1: TEAM POINTS
# --------------------------------

plt.figure(figsize=(12, 8))

plt.barh(df["Team"], df["Points"])

plt.title("EPL Team Points - 2026/2027 Season")
plt.xlabel("Total Points")
plt.ylabel("Teams")

plt.tight_layout()
plt.savefig("datasets/team_points_real.png", dpi=300)
plt.show()

# --------------------------------
# CHART 2: GOALS SCORED
# --------------------------------

df_goals = df.sort_values("GF", ascending=True)

plt.figure(figsize=(12, 8))

plt.barh(df_goals["Team"], df_goals["GF"])

plt.title("EPL Goals Scored by Team")
plt.xlabel("Goals Scored")
plt.ylabel("Teams")

plt.tight_layout()
plt.savefig("datasets/team_goals_real.png", dpi=300)
plt.show()

# --------------------------------
# CHART 3: GOAL DIFFERENCE
# --------------------------------

df_gd = df.sort_values("GD", ascending=True)

plt.figure(figsize=(12, 8))

plt.barh(df_gd["Team"], df_gd["GD"])

plt.title("EPL Team Goal Difference")
plt.xlabel("Goal Difference")
plt.ylabel("Teams")

plt.tight_layout()
plt.savefig("datasets/team_goal_difference.png", dpi=300)
plt.show()

print("All three visualizations generated successfully!")
