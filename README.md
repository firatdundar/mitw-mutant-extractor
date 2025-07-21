# MITW Mutant Extractor

This repository provides scripts and preprocessed data based on the dataset introduced in the paper:

**"Equivalent Mutants in the Wild: Identifying and Efficiently Suppressing Equivalent Mutants for Java Programs"**  
📄 _Honglin Shu, Zhao Tian, Rui Abreu, Zhendong Su_ (ISSTA 2024 - ACM SIGSOFT Distinguished Paper Award)

---

## 🛠 Requirements

To use this repository, you **must download and extract the supplementary material** shared by the authors of the paper:

📦 **Supplementary Dataset Download:**  
https://figshare.com/articles/dataset/Supplementary_Material_for_i_Equivalent_Mutants_in_the_Wild_Identifying_and_Efficiently_Suppressing_Equivalent_Mutants_for_Java_Programs_i_/26948143/1?file=49088374

After downloading, **place the `emiw_artifact` folder in the same directory as this repository**.

---

## 📁 Folder Overview

### `labeled_data_points/`
- Contains the **script** to extract **manually labeled mutants** from the supplementary dataset and the **CSV output** from that process.
- These mutants are extracted from the full dataset using the manual equivalence labels provided by the authors.
- The CSV output has the same structure as the original dataset but is filtered to only include labeled data.

### `labels_with_differences/`
- Uses the resulting CSV from `labeled_data_points/` to reconstruct **original and mutated code parts** for each mutant.
- The script accesses the relevant files inside the `emiw_artifact` structure and uses the information in each project's `mutants.log` file to identify the differences between original and mutant code. This includes line numbers and class-level metadata.
- Output is a CSV file that includes the **Subject, Mutant ID (MID), OriginalCode, MutatedCode,** and the **EquiManualBin** label.

📌 _Note: Resulting CSVs from the scripts are already included in their corresponding folders._