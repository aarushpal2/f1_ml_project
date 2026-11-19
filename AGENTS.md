# F1 Tire Degradation Project

## Goal
Estimate tire degradation (sec/lap) by compound for five drivers
(VER, HAM, LEC, NOR, ALO) using OpenF1 lap data.

## Data
- Source: OpenF1 (https://api.openf1.org/v1). FastF1 is NOT used.
- Raw files live in data/raw/<year>/<session_key>/*.parquet and are read-only.
- Processed output goes in data/processed/.

## Rules
- Use the .venv; don't install new packages without asking.
- Never make network calls. Raw data is already downloaded.
- Never modify data/raw/. Never commit data/ or .venv/.
- Code goes in src/f1deg/, scripts in scripts/, tests in tests/.
- Functions are small and take/return DataFrames.
- Add or update a test for any cleaning logic. Run `pytest` before saying a task is done.
- Do NOT write models, regressions, or plots. Data cleaning only.
- Every filtering choice must be explained in your final summary.