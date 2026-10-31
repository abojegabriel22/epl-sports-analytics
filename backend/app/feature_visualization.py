
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load feature importance results
df = pd.read_csv(
    "datasets/random_forest_feature_importance.csv"
)

# Sort features by importance
df = df.sort_values(
    by="Importance",
    ascending=True
)

# Create output directory
output_directory = Path("datasets")
output_directory.mkdir(exist_ok=True)

# Create chart
plt.figure(figsize=(11, 8))

plt.barh(
    df["Feature"],
    df["Importance"]
)

plt.title(
    "EPL Match Prediction - Feature Importance",
    fontsize=14
)

plt.xlabel("Importance Score")
plt.ylabel("Features")

plt.tight_layout()

# Save chart
chart_path = (
    output_directory /
    "feature_importance_chart.png"
)

plt.savefig(chart_path, dpi=300)

plt.show()

print("Feature importance chart saved to:", chart_path)
