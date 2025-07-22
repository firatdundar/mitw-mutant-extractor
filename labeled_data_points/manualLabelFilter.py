from pathlib import Path
import pandas as pd

# Define base paths
script_dir = Path(__file__).parent
input_csv_path = script_dir.parent / "emiw_artifact" / "consolidated.csv"
output_csv_path = script_dir / "filtered_consolidated.csv"

# Optional: print resolved paths for debugging
print("Reading from:", input_csv_path.resolve())
print("Writing to:", output_csv_path.resolve())

# Load the CSV
df = pd.read_csv(input_csv_path)

# Filter out rows where EquiManualLabel is empty or NaN
filtered_df = df[df['EquiManualLabel'].notna() & (df['EquiManualLabel'].astype(str).str.strip() != '')]

# Save filtered results
filtered_df.to_csv(output_csv_path, index=False)

# Show first few rows
print(filtered_df.head())