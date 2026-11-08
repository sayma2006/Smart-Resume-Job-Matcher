"""Evaluate the heuristic matcher against a human-labelled CSV dataset.

CSV columns: resume_text,job_description,label
Allowed labels: poor,partial,good
Use anonymized examples only. This script does not create or invent labels.
"""
import argparse
import csv
from pathlib import Path

from scipy.stats import spearmanr

from src.scorer import analyze

LABEL_SCORE = {"poor": 0, "partial": 1, "good": 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="Path to your labelled evaluation CSV")
    args = parser.parse_args()
    path = Path(args.csv_path)
    if not path.is_file():
        raise SystemExit(f"CSV not found: {path}")

    human, model = [], []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"resume_text", "job_description", "label"}
        if not required.issubset(reader.fieldnames or []):
            raise SystemExit("CSV must contain: resume_text, job_description, label")
        for row_number, row in enumerate(reader, start=2):
            label = (row.get("label") or "").strip().lower()
            if label not in LABEL_SCORE:
                raise SystemExit(f"Invalid label on CSV row {row_number}: {label!r}")
            result = analyze(row.get("resume_text", ""), row.get("job_description", ""))
            human.append(LABEL_SCORE[label])
            model.append(float(result["overall"]))

    if len(human) < 3:
        raise SystemExit("Add at least 3 labelled pairs; 20–30 or more are recommended.")
    correlation = spearmanr(human, model)
    print(f"Pairs evaluated: {len(human)}")
    print(f"Spearman rank correlation: {correlation.statistic:.3f}")
    print("Interpret this cautiously: a small, subjective dataset is not proof of hiring accuracy.")


if __name__ == "__main__":
    main()
