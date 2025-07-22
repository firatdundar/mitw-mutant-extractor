from pathlib import Path
import pandas as pd

# === Setup paths ===
script_dir = Path(__file__).parent
base_dir = script_dir.parent / "emiw_artifact" / "mutation_analysis_results"
csv_path = script_dir.parent / "labeled_data_points" / "filtered_consolidated.csv"
output_csv_path = script_dir / "original_mutant_differences_label.csv"

print("Reading from:", csv_path.resolve())
print("Writing to:", output_csv_path.resolve())

# === Load labeled mutant data ===
df = pd.read_csv(csv_path)

# Project folders
project_dirs = [
    "Chart-1f", "Collections-28f", "Csv-16f", "Gson-18f", "JxPath-22f", "Lang-1f", "Math-1f"
]

# Lookup: (Subject, MID) -> EquiManualBin
label_lookup = {
    (row.Subject.strip(), int(row.MID)): row.EquiManualBin for _, row in df.iterrows()
}

# === Log line parser ===
def parse_line(line: str, project_name: str):
    if "|==>" not in line:
        return None
    try:
        parts = line.strip().split(":")
        mid = int(parts[0])
        mutation_operator = parts[1]
        operator_before = parts[2]
        operator_after = parts[3]
        class_and_method = parts[4]
        line_number = int(parts[5])
        char_offset = int(parts[6])
        mutated_parts = ":".join(parts[7:]).split("|==>")
        original_code = mutated_parts[0].strip()
        mutated_code = mutated_parts[1].strip()

        # Class and method
        if "@" in class_and_method:
            class_name, method_signature = class_and_method.split("@", 1)
        else:
            class_name = class_and_method
            method_signature = ""

        key = (project_name, mid)
        if key not in label_lookup:
            return None

        return {
            "Subject": project_name,
            "MID": mid,
            "MutationOperator": mutation_operator,
            "OperatorBefore": operator_before,
            "OperatorAfter": operator_after,
            "Class": class_name,
            "Method": method_signature,
            "Line": line_number,
            "CharOffset": char_offset,
            "OriginalCode": original_code,
            "MutatedCode": mutated_code,
            "EquiManualBin": label_lookup[key],
        }
    except Exception:
        return None

# === Process all project logs ===
all_entries = []

for project_dir in project_dirs:
    subject = project_dir
    log_path = base_dir / project_dir / "mutants.log"

    if not log_path.exists():
        print(f"⚠️ Missing: {log_path}")
        continue

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_line(line, subject)
            if parsed:
                all_entries.append(parsed)

# === Save result ===
output_df = pd.DataFrame(all_entries)
output_df.to_csv(output_csv_path, index=False)

print(f"✅ Done. Parsed {len(output_df)} mutants.")