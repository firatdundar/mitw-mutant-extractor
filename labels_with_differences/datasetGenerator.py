import os
import pandas as pd

# Path to the base directory containing project folders
base_dir = r"C:\Users\dundar\Desktop\Urbana2\ProjectV2\emiw_artifact\mutation_analysis_results"

# List of project directories (based on your screenshot)
project_dirs = [
    "Chart-1f", "Collections-28f", "Csv-16f", "Gson-18f", "JxPath-22f", "Lang-1f", "Math-1f"
]

# Read the filtered CSV (you must place this in the same folder or give correct path)
csv_path = r"C:\Users\dundar\Desktop\Urbana2\ProjectV2\LabeledData\filtered_consolidated.csv"

df = pd.read_csv(csv_path)

# Create a lookup dictionary for (Subject, MID) -> EquiManualBin
label_lookup = {
    (row.Subject.strip(), int(row.MID)): row.EquiManualBin for _, row in df.iterrows()
}

# Utility function to parse each line of mutants.log
def parse_line(line, project_name):
    if "|==>" not in line:
        return None
    try:
        mid = int(line.split(":")[0])
        original_code = line.split("|==>")[0].split(":")[-1].strip()
        mutated_code = line.split("|==>")[1].strip()
        key = (project_name, mid)
        if key not in label_lookup:
            return None  # skip if not labeled

        return {
            "Subject": project_name,
            "MID": mid,
            "OriginalCode": original_code,
            "MutatedCode": mutated_code,
            "EquiManualBin": label_lookup[key]
        }

    except Exception as e:
        return None

# Collect all parsed entries
all_entries = []

for project_dir in project_dirs:
    subject = project_dir  # Use full project name like 'Chart-1f'
    log_path = os.path.join(base_dir, project_dir, "mutants.log")
    if not os.path.exists(log_path):
        print(f"Missing log: {log_path}")
        continue

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_line(line, subject)
            if parsed:
                all_entries.append(parsed)

# Save to final CSV
output_df = pd.DataFrame(all_entries)
output_df.to_csv("original_mutant_differences_label.csv", index=False)

print(f"✅ Done. Parsed {len(output_df)} mutants. Output saved to mutant_dataset_final.csv")
