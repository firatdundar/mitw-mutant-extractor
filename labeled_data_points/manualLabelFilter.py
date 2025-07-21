import pandas as pd
import os

# Load the CSV from emiw_artifact folder (go up one level from labeled_data_points)
csv_path = os.path.join("..", "emiw_artifact", "consolidated.csv")
df = pd.read_csv(csv_path)

# Filter out rows where EquiManualLabel is empty or NaN
filtered_df = df[df['EquiManualLabel'].notna() & (df['EquiManualLabel'].astype(str).str.strip() != '')]

# Save to new CSV in the current directory (labeled_data_points)
filtered_df.to_csv("filtered_consolidated.csv", index=False)

# Display first few rows
print(filtered_df.head())