
import pandas as pd

# Load the original dataset
file_path = "datasets/epl_2026_2027.csv"
df = pd.read_csv(file_path)

print("ORIGINAL DATASET")
print("Shape:", df.shape)

# Select columns relevant to our initial analysis
selected_columns = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
    "HS",
    "AS",
    "HST",
    "AST",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR",
    "HxG",
    "AxG"
]

# Create a smaller working dataset
clean_df = df[selected_columns].copy()

# Convert dates into datetime format
clean_df["Date"] = pd.to_datetime(
    clean_df["Date"],
    dayfirst=True,
    errors="coerce"
)

# Convert numerical columns
numeric_columns = [
    "FTHG", "FTAG", "HTHG", "HTAG",
    "HS", "AS", "HST", "AST",
    "HC", "AC", "HY", "AY", "HR", "AR",
    "HxG", "AxG"
]

for column in numeric_columns:
    clean_df[column] = pd.to_numeric(
        clean_df[column],
        errors="coerce"
    )

# Remove rows missing essential match information
essential_columns = [
    "Date", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR"
]

clean_df = clean_df.dropna(
    subset=essential_columns
)

# Sort matches chronologically
clean_df = clean_df.sort_values("Date")

# Reset row numbering
clean_df = clean_df.reset_index(drop=True)

# Save cleaned dataset
clean_df.to_csv(
    "datasets/epl_cleaned.csv",
    index=False
)

print("\nCLEANING COMPLETED")
print("Cleaned shape:", clean_df.shape)
print("\nFirst five cleaned matches:")
print(clean_df.head().to_string(index=False))

print("\nMissing values after cleaning:")
print(clean_df.isnull().sum())

print("\nSaved to datasets/epl_cleaned.csv")
