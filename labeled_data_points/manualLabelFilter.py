import pandas as pd

# Load the CSV
df = pd.read_csv("consolidated.csv")

# Filter out rows where EquiManualLabel is empty or NaN
filtered_df = df[df['EquiManualLabel'].notna() & (df['EquiManualLabel'].astype(str).str.strip() != '')]

# Optional: Save to new CSV
filtered_df.to_csv("filtered_consolidated.csv", index=False)

# Display first few rows
print(filtered_df.head())
