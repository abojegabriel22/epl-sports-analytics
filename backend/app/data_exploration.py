
import pandas as pd

# Dataset location
file_path = "datasets/epl_2026_2027.csv"

# Load dataset
df = pd.read_csv(file_path)

print("=" * 60)
print("          EPL DATA EXPLORATION")
print("=" * 60)

# 1. Dataset dimensions
print("\n1. DATASET DIMENSIONS")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 2. Column names
print("\n2. DATASET COLUMNS")
print(df.columns.tolist())

# 3. First five records
print("\n3. FIRST FIVE RECORDS")
print(df.head().to_string())

# 4. Dataset information
print("\n4. DATASET INFORMATION")
df.info()

# 5. Missing values
print("\n5. MISSING VALUES")
print(df.isnull().sum())

# 6. Duplicate records
print("\n6. DUPLICATE RECORDS")
print(df.duplicated().sum())

# 7. Statistical summary
print("\n7. STATISTICAL SUMMARY")
print(df.describe(include="all").to_string())

print("\nEDA COMPLETED SUCCESSFULLY!")
