import os
import subprocess
import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # extract_java_files/.. = root
DEFECTS4J_PATH = PROJECT_ROOT / "defects4j"
CHECKOUT_DIR = PROJECT_ROOT / "extract_java_files" / "checked_out_projects"
JAVA_SAVE_DIR = PROJECT_ROOT / "extract_java_files" / "mutant_java_files"
CHECKOUT_DIR.mkdir(exist_ok=True)
JAVA_SAVE_DIR.mkdir(exist_ok=True)

# === Environment ===
env = os.environ.copy()
env["PERL5LIB"] = str(DEFECTS4J_PATH / "framework" / "lib")
env["_JAVA_OPTIONS"] = "-XX:+IgnoreUnrecognizedVMOptions"

# === Load CSV
CSV_PATH = PROJECT_ROOT / "label_difference" / "original_mutant_differences_label.csv"
df = pd.read_csv(CSV_PATH)

# === Track checkouts ===
checked_out_projects = {}
missing_files = []
checkout_failures = []

for idx, row in tqdm(df.iterrows(), total=len(df)):
    subject = row["Subject"]             # e.g. Chart-1f
    project = subject.split("-")[0]      # e.g. Chart
    bug_id = subject.split("-")[1][:-1]  # '1f' -> '1'
    version = "f"                        # fixed version only
    mid = row["MID"]

    full_class = row["Class"].strip()
    outer_class = full_class.split("$")[0].strip()
    class_path = outer_class.replace(".", "/") + ".java"

    # ✅ Updated inner class name handling
    last_part = full_class.split(".")[-1]
    java_file_name = last_part if last_part.startswith("$") else last_part.split("$")[0]
    java_file_name += ".java"

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
            print(f"[!] ❌ Checkout failed for {subject}. Try manually:\n"
                  f"perl defects4j/framework/bin/defects4j checkout -p {project} -v {bug_id}{version} -w <path>")
            checkout_failures.append(subject)
            continue

    # === Get source directory ===
    os.chdir(checkout_path)
    try:
        src_dir = subprocess.check_output([
            "perl", str(DEFECTS4J_PATH / "framework/bin/defects4j"),
            "export", "-p", "dir.src.classes"
        ], env=env).decode().strip()
    except subprocess.CalledProcessError:
        print(f"[!] Export failed for {subject}")
        continue

    # === Locate Java file ===
    java_file_path = Path(src_dir) / class_path
    if not java_file_path.is_absolute():
        java_file_path = checkout_path / java_file_path

    found = False

    if java_file_path.exists():
        found = True
    else:
        # Fallback 1: Outer class file
        fallback_java_name = Path(class_path).name
        fallback_candidates = list((checkout_path / src_dir).rglob(fallback_java_name))
        if fallback_candidates:
            java_file_path = fallback_candidates[0]
            found = True
        else:
            # Fallback 2: Match filename partially (handles inner classes)
            for candidate in (checkout_path / src_dir).rglob("*.java"):
                if java_file_name in candidate.name:
                    java_file_path = candidate
                    found = True
                    break

    if not found:
        print(f"[‼] Still missing: {full_class} → {java_file_name} for {subject}")
        missing_files.append({
            "Subject": subject,
            "MID": mid,
            "Class": full_class,
            "ExpectedFilename": f"{subject}_{mid}_{java_file_name}"
        })
        continue

    # === Save file ===
    new_file_name = f"{subject}_{mid}_{java_file_name}"
    shutil.copy(java_file_path, JAVA_SAVE_DIR / new_file_name)

# === Save logs
if missing_files:
    pd.DataFrame(missing_files).to_csv(PROJECT_ROOT / "extract_java_files" / "missing_java_files.csv", index=False)
    print(f"⚠️ Missing files saved to: missing_java_files.csv")

if checkout_failures:
    with open(PROJECT_ROOT / "extract_java_files" / "checkout_failures.txt", "w") as f:
        for item in checkout_failures:
            f.write(item + "\n")
    print(f"🛠️ Checkout failures saved to: checkout_failures.txt")

print(f"✅ Java files extracted to: {JAVA_SAVE_DIR}")