name: Validate Exercises

on:
  push:
    paths:
      - 'exercise-repo/**'
      - '.github/workflows/validate-exercises.yml'
  pull_request:
    paths:
      - 'exercise-repo/**'
      - '.github/workflows/validate-exercises.yml'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install sympy

      - name: Run validator
        run: |
          set -o pipefail
          python exercise-repo/validate_exercises.py exercise-repo/exercises.json | tee exercise-repo/validation_summary.txt

      - name: Upload validation report (artifact)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: validation-logs
          path: exercise-repo/validation_summary.txt
