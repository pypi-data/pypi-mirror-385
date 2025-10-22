# Your Project — MethodCard

- **What:** Brief description of your scientific method/experiment
- **How:** `uv run run` → `uv run promote`
- **Expected metrics:** accuracy, precision, recall, f1 (computed from confusion matrix)
- **Data schema:** Input columns `x`, `y`, `value`, `ground_truth` → Output `processed_value`
- **Outputs:** `app/code/artifacts/processed.parquet`, `app/code/artifacts/metrics.json`
- **License:** ORL-1.0
- **Arcade onboarding:** [Threshold Classifier Sprint](../arcade/README.md) — score locally then run `uv run python app/notes/arcade/workflow.py --submission app/notes/arcade/baseline_submission.csv`
