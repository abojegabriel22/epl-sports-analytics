
import pandas as pd

files = {
    "2025/2026": "datasets/epl_2025_2026.csv",
    "2026/2027": "datasets/epl_2026_2027.csv"
}

for season, file_path in files.items():

    print("\n" + "=" * 60)
    print(f"SEASON: {season}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    print("Shape:", df.shape)
    print("\nFirst five rows:")
    print(df.head().to_string(index=False))

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values in important columns:")
    important_columns = [
        "Date", "HomeTeam", "AwayTeam",
        "FTHG", "FTAG", "FTR"
    ]

    for column in important_columns:
        if column in df.columns:
            print(f"{column}: {df[column].isnull().sum()}")

    print("\nDuplicate rows:", df.duplicated().sum())

    if "Date" in df.columns:
        dates = pd.to_datetime(
            df["Date"], dayfirst=True, errors="coerce"
        )

        print("Earliest date:", dates.min())
        print("Latest date:", dates.max())

    print("\nUnique home teams:", df["HomeTeam"].nunique())
    print("Unique away teams:", df["AwayTeam"].nunique())

print("\nSEASON INSPECTION COMPLETED!")
