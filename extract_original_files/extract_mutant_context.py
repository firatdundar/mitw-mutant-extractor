import os
import subprocess
import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm

# Set paths
PROJECT_ROOT = Path(__file__).resolve().parent
DEFECTS4J_PATH = PROJECT_ROOT / "defects4j"
CHECKOUT_DIR = PROJECT_ROOT / "extract_original_files" /"checked_out_projects"
JAVA_SAVE_DIR = PROJECT_ROOT / "extract_original_files" / "mutant_java_files"
CHECKOUT_DIR.mkdir(exist_ok=True)
JAVA_SAVE_DIR.mkdir(exist_ok=True)

# Setup environment
env = os.environ.copy()
env["PERL5LIB"] = str(DEFECTS4J_PATH / "framework" / "lib")
env["_JAVA_OPTIONS"] = "-XX:+IgnoreUnrecognizedVMOptions"

# Load CSV
CSV_PATH = PROJECT_ROOT / "labels_with_difference" / "original_mutant_differences_label.csv"
df = pd.read_csv(CSV_PATH)

# Track checked out projects to avoid repetition
checked_out_projects = {}
missing_files = []

for idx, row in tqdm(df.iterrows(), total=len(df)):
    subject = row["Subject"]             # e.g. Chart-1f
    project = subject.split("-")[0]      # e.g. Chart
    bug_id = subject.split("-")[1][:-1]  # '1f' -> '1'
    version = "f"                        # fixed version only
    mid = row["MID"]

    # Extract outer class file path
    outer_class = row["Class"].split("$")[0].strip()
    class_path = outer_class.replace(".", "/") + ".java"
    java_file_name = outer_class.split(".")[-1] + ".java"

    checkout_path = CHECKOUT_DIR / f"{subject}_fixed"

    if subject not in checked_out_projects:
        shutil.rmtree(checkout_path, ignore_errors=True)
        try:
            subprocess.run([
                "perl", str(DEFECTS4J_PATH / "framework/bin/defects4j"),
                "checkout", "-p", project,
                "-v", f"{bug_id}{version}",
                "-w", str(checkout_path)
            ], check=True, env=env)
            checked_out_projects[subject] = checkout_path
        except subprocess.CalledProcessError:
            print(f"[!] Checkout failed for {subject}")
            continue

    # Get source directory
    os.chdir(checkout_path)
    try:
        src_dir = subprocess.check_output([
            "perl", str(DEFECTS4J_PATH / "framework/bin/defects4j"),
            "export", "-p", "dir.src.classes"
        ], env=env).decode().strip()
    except subprocess.CalledProcessError:
        print(f"[!] Export failed for {subject}")
        continue

    # Resolve java file path
    java_file_path = Path(src_dir) / class_path
    if not java_file_path.is_absolute():
        java_file_path = checkout_path / java_file_path

    if not java_file_path.exists():
        # Fallback search for file by name in source directory
        print(f"[!] File not found: {java_file_path}, trying fallback...")
        fallback_candidates = list((checkout_path / src_dir).rglob(java_file_name))
        if fallback_candidates:
            java_file_path = fallback_candidates[0]
        else:
            print(f"[‼] Still missing: {java_file_name} for {subject}")
            missing_files.append({
                "Subject": subject,
                "MID": mid,
                "Class": row["Class"]
            })
            continue

    # Save the found file
    new_file_name = f"{subject}_{mid}_{java_file_name}"
    shutil.copy(java_file_path, JAVA_SAVE_DIR / new_file_name)

# Save missing file logs
if missing_files:
    missing_df = pd.DataFrame(missing_files)
    missing_df.to_csv(PROJECT_ROOT / "extract_original_files" / "missing_java_files.csv", index=False)
    print(f"⚠️ Missing files saved to: missing_java_files.csv")

# Done
print(f"✅ Extracted Java files saved in: {JAVA_SAVE_DIR}")