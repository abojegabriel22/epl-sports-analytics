
import pandas as pd

# Define the datasets
season_files = {
    "2025/2026": "datasets/epl_2025_2026.csv",
    "2026/2027": "datasets/epl_2026_2027.csv"
}

# Columns needed for our analysis
required_columns = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR"
]

all_seasons = []

# Load and prepare each season
for season, file_path in season_files.items():

    print(f"Loading {season} season...")

    df = pd.read_csv(file_path)

    # Check that all required columns exist
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{season} is missing columns: {missing_columns}"
        )

    # Select only the required columns
    df = df[required_columns].copy()

    # Add season information
    df["Season"] = season

    # Convert data types
    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    for column in ["FTHG", "FTAG"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove incomplete records
    df = df.dropna(
        subset=required_columns
    )

    all_seasons.append(df)

# Combine both seasons
combined_df = pd.concat(
    all_seasons,
    ignore_index=True
)

# Sort chronologically
combined_df = combined_df.sort_values(
    by=["Date", "HomeTeam", "AwayTeam"]
).reset_index(drop=True)

# Check for duplicate matches
duplicates = combined_df.duplicated(
    subset=["Date", "HomeTeam", "AwayTeam"]
).sum()

print("\nDuplicate matches:", duplicates)

if duplicates > 0:
    raise ValueError("Duplicate matches detected!")

# Save the combined dataset
output_path = "datasets/epl_multi_season.csv"

combined_df.to_csv(
    output_path,
    index=False
)

# Display results
print("\nMULTI-SEASON DATASET CREATED")
print("=" * 45)

print("Total matches:", len(combined_df))

print("\nMatches per season:")
print(combined_df["Season"].value_counts())

print("\nDate range:")
print("From:", combined_df["Date"].min())
print("To:", combined_df["Date"].max())

print("\nFirst five records:")
print(combined_df.head().to_string(index=False))

print("\nSaved to:", output_path)
