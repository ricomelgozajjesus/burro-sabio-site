#!/usr/bin/env python3
"""
Convert exercises from YAML -> JSON and (optionally) validate with the existing validator.

Usage:
    python exercises-repo/build_exercises_json.py --validate

Writes:
    build/exercises.json

Requires:
    pyyaml (yaml)
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: pyyaml is required. pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]  # repo root
SRC = ROOT / "exercises-repo" / "exercises.yaml"
OUT_DIR = ROOT / "build"
OUT = OUT_DIR / "exercises.json"
VALIDATOR = ROOT / "exercises-repo" / "validate_exercises.py"

def main(validate: bool) -> int:
    if not SRC.exists():
        print(f"ERROR: source YAML not found: {SRC}", file=sys.stderr)
        return 1

    with open(SRC, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {OUT.relative_to(ROOT)}")

    if validate:
        if not VALIDATOR.exists():
            print(f"WARN: validator not found: {VALIDATOR}")
            return 0
        print("Running validator on build/exercises.json ...")
        proc = subprocess.run([sys.executable, str(VALIDATOR), str(OUT)], capture_output=False)
        return proc.returncode
    return 0

if __name__ == "__main__":
    validate_flag = "--validate" in sys.argv
    sys.exit(main(validate_flag))
