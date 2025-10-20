# Vigil Arcade: Threshold Classifier Sprint

A 10-minute onboarding challenge for the Universal Science Starter. Build a tiny
classifier for the sample microscopy table and ship your first Vigil receipt.

## Launch in Vigil

Open the repository in Vigil using this URL (same as the main README):

```
vigil://labs.example/acme-lab/imaging-starter@refs/heads/main?img=sha256:58b3e701ed9da8768554a21ffe7fa9afd995702d002b4b5d4798365a79310277&inputs=s3://demo-bucket/microscopy/
```

To avoid drift, you can always regenerate the canonical Vigil URL directly from
`vigil.yaml`:

```bash
vigil url
```

## Objective

Predict whether each record in `app/data/samples/data.csv` belongs to the
positive class. Submit a CSV with two columns:

| column | description                  |
| ------ | ---------------------------- |
| `x`    | integer identifier from data |
| `prediction` | `0` or `1` label          |

Accuracy ≥ 0.9 passes the challenge. Perfect accuracy is achievable with a
simple threshold on the `value` column.

## Files in this folder

- `score.py` – reusable scorer that prints confusion-matrix metrics.
- `workflow.py` – evaluates a submission, persists artifacts, and promotes on success.
- `baseline_submission.csv` – ready-to-run example that meets the accuracy target.

## How to play

1. **Inspect the data** – open `app/data/samples/data.csv` or load it in a notebook.
2. **Create predictions** – save them as `my_predictions.csv` with the schema above.
3. **Score locally** – run:
   ```bash
   uv run python app/notes/arcade/score.py my_predictions.csv
   ```
4. **Run the workflow** – this checks the threshold and promotes successful runs:
   ```bash
   uv run python app/notes/arcade/workflow.py --submission my_predictions.csv
   ```
5. **Share the receipt** – the workflow copies your submission to
   `app/code/artifacts/arcade/`, writes `metrics.json`, and calls `promote.py` to
   mint a Vigil receipt.

## Need a hint?

The `value` column is monotonic. A cutoff near `0.55` separates the two classes.
You can also inspect `baseline_submission.csv` for a working example.
