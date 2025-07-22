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
- The output of this script is a CSV file named `original_mutant_differences_label.csv`, which contains detailed metadata for each manually labeled mutant. Each row in the file corresponds to a single mutant and includes the following columns:

| Column Name       | Description |
|-------------------|-------------|
| `Subject`         | The project version the mutant belongs to (e.g., `Chart-1f`). |
| `MID`             | Mutation ID — a unique identifier for the mutant within the subject. |
| `MutationOperator`| The type of mutation applied (e.g., `ROR`, `LVR`, `COR`, `STD`). |
| `OperatorBefore`  | The operator or expression in the original code before mutation. |
| `OperatorAfter`   | The operator or expression after mutation. |
| `Class`           | Fully qualified name of the Java class containing the mutation. |
| `Method`          | The method signature where the mutation was applied. |
| `Line`            | The line number in the source file where the mutation occurs. |
| `CharOffset`      | The character offset (position in the file) of the mutation. |
| `OriginalCode`    | The original source code part before the mutation. |
| `MutatedCode`     | The mutated version of the code part. |
| `EquiManualBin`   | Manual binary label indicating whether the mutant is **equivalent**: <br> `TRUE` = equivalent mutant (does not change program behavior), <br> `FALSE` = non-equivalent (changes behavior). |

📌 _Note: Resulting CSVs from the scripts are already included in their corresponding folders._