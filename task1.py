import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
input_file = folder / "Dataset.csv"

df = pd.read_csv(input_file)

print("Original dataset shape:", df.shape)
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Remove duplicate rows
df = df.drop_duplicates()

# Standardize text columns
for col in ["type", "title", "director", "country", "rating", "duration", "listed_in"]:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()

# Convert date_added to datetime
df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

# Save cleaned dataset
output_file = folder / "netflix_cleaned.csv"
df.to_csv(output_file, index=False)

print("\nCleaned dataset shape:", df.shape)
print("\nMissing values after cleaning:")
print(df.isnull().sum())
print(f"\nCleaned dataset saved to: {output_file}")
