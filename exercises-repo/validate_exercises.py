#!/usr/bin/env python3
"""
Exercise Repository Validator

Checks the structure and integrity of `exercises.json` used by Magic Notebooks.

What it validates:
 1) JSON parse + presence of top-level keys
 2) Unique exercise IDs
 3) Required fields and allowed enums (difficulty, format, autocheck.strategy)
 4) Rubric integrity (criteria sum matches total_points)
 5) Date formats (ISO-8601)
 6) Autocheck reference expression is parseable by SymPy (if available)
 7) Light linting (empty strings, short statements)

Usage:
    python validate_exercises.py [path/to/exercises.json]

Exit codes:
    0 = OK (possibly with warnings)
    1 = Found errors

Optional dependency:
    sympy (for parsing `autocheck.reference_expr`). If missing, this check is skipped with a warning.
"""
from __future__ import annotations
import json
import sys
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import sympy as sp
    SYMPY_OK = True
except Exception:
    SYMPY_OK = False

ALLOWED_DIFFICULTY = {"easy", "medium", "hard"}
ALLOWED_FORMAT = {"open-ended", "multiple-choice", "proof", "coding"}
ALLOWED_AUTOCHECK = {"symbolic_equivalence", "numeric_sampling"}

REQUIRED_FIELDS = [
    "id", "topic", "subtopic", "difficulty", "format",
    "statement_md_es", "answer_type", "expected_answer",
    "rubric", "autocheck", "meta"
]

RUBRIC_REQUIRED = {"total_points", "criteria"}
CRITERION_REQUIRED = {"name", "points", "description"}
META_REQUIRED = {"author", "source", "created", "updated"}

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

@dataclass
class Finding:
    kind: str   # 'ERROR' | 'WARN'
    where: str
    msg: str


def iso_date_ok(s: str) -> bool:
    if not isinstance(s, str) or not ISO_DATE_RE.match(s):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False


def sympy_parse_ok(expr: str) -> bool:
    if not SYMPY_OK:
        return True  # can't check; handled as warning elsewhere
    try:
        sp.sympify(expr)
        return True
    except Exception:
        return False


def validate_rubric(ex: Dict[str, Any], idx: int) -> List[Finding]:
    findings: List[Finding] = []
    rb = ex.get("rubric", {})
    missing = RUBRIC_REQUIRED - set(rb.keys())
    if missing:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric", f"Missing keys: {sorted(missing)}"))
        return findings
    if not isinstance(rb.get("criteria"), list) or not rb["criteria"]:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric.criteria", "Must be a non-empty list"))
        return findings
    pts_sum = 0
    for j, c in enumerate(rb["criteria"]):
        if not isinstance(c, dict):
            findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric.criteria[{j}]", "Criterion must be an object"))
            continue
        miss = CRITERION_REQUIRED - set(c.keys())
        if miss:
            findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric.criteria[{j}]", f"Missing keys: {sorted(miss)}"))
        if not isinstance(c.get("points"), int) or c["points"] < 0:
            findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric.criteria[{j}].points", "Must be a non-negative integer"))
        else:
            pts_sum += c["points"]
    if isinstance(rb.get("total_points"), int):
        if pts_sum != rb["total_points"]:
            findings.append(Finding("WARN", f"ex[{idx}]/{ex.get('id','?')}.rubric", f"Criteria points sum to {pts_sum} but total_points={rb['total_points']}") )
    else:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.rubric.total_points", "Must be an integer"))
    return findings


def validate_meta(ex: Dict[str, Any], idx: int) -> List[Finding]:
    findings: List[Finding] = []
    meta = ex.get("meta", {})
    miss = META_REQUIRED - set(meta.keys())
    if miss:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.meta", f"Missing keys: {sorted(miss)}"))
        return findings
    for k in ("created", "updated"):
        v = meta.get(k)
        if not iso_date_ok(v):
            findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.meta.{k}", f"Not ISO-8601 date (YYYY-MM-DD): {v}"))
    return findings


def validate_autocheck(ex: Dict[str, Any], idx: int) -> List[Finding]:
    findings: List[Finding] = []
    ac = ex.get("autocheck", {})
    if not isinstance(ac, dict):
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.autocheck", "Must be an object"))
        return findings
    strategy = ac.get("strategy")
    if strategy not in ALLOWED_AUTOCHECK:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.autocheck.strategy", f"Unknown: {strategy}. Allowed: {sorted(ALLOWED_AUTOCHECK)}"))
    ref = ac.get("reference_expr")
    if not isinstance(ref, str) or not ref.strip():
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.autocheck.reference_expr", "Missing/empty") )
    elif SYMPY_OK and not sympy_parse_ok(ref):
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.autocheck.reference_expr", "SymPy could not parse expression"))
    elif not SYMPY_OK:
        findings.append(Finding("WARN", f"ex[{idx}]/{ex.get('id','?')}.autocheck.reference_expr", "sympy not installed; skipping parse check"))
    return findings


def validate_required_fields(ex: Dict[str, Any], idx: int) -> List[Finding]:
    findings: List[Finding] = []
    miss = set(REQUIRED_FIELDS) - set(ex.keys())
    if miss:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}", f"Missing required fields: {sorted(miss)}"))
    # enums
    diff = ex.get("difficulty")
    if diff and diff not in ALLOWED_DIFFICULTY:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.difficulty", f"Invalid: {diff}. Allowed: {sorted(ALLOWED_DIFFICULTY)}"))
    fmt = ex.get("format")
    if fmt and fmt not in ALLOWED_FORMAT:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.format", f"Invalid: {fmt}. Allowed: {sorted(ALLOWED_FORMAT)}"))
    # light content checks
    stmt = ex.get("statement_md_es", "").strip()
    if len(stmt) < 8:
        findings.append(Finding("WARN", f"ex[{idx}]/{ex.get('id','?')}.statement_md_es", "Statement seems too short"))
    ans = ex.get("expected_answer", "").strip()
    if not ans:
        findings.append(Finding("ERROR", f"ex[{idx}]/{ex.get('id','?')}.expected_answer", "Empty"))
    return findings


def main(path: str) -> int:
    findings: List[Finding] = []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "exercises" not in data or not isinstance(data["exercises"], list):
        print("ERROR: Top-level key 'exercises' must be a list.")
        return 1

    exercises = data["exercises"]
    ids = []

    for i, ex in enumerate(exercises):
        # required set
        findings += validate_required_fields(ex, i)
        findings += validate_rubric(ex, i)
        findings += validate_meta(ex, i)
        findings += validate_autocheck(ex, i)
        # collect id
        ex_id = ex.get("id")
        ids.append(ex_id)

    # uniqueness
    seen = set()
    for i, ex_id in enumerate(ids):
        if ex_id in seen:
            findings.append(Finding("ERROR", f"ex[{i}]/{ex_id}", "Duplicate id"))
        else:
            seen.add(ex_id)

    # Report
    errors = [f for f in findings if f.kind == "ERROR"]
    warns = [f for f in findings if f.kind == "WARN"]

    print("="*72)
    print(f"Validated: {len(exercises)} exercises | Errors: {len(errors)} | Warnings: {len(warns)}")
    print("-"*72)
    for f in findings:
        print(f"{f.kind:<5} @ {f.where}: {f.msg}")
    print("="*72)

    return 1 if errors else 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "exercises.json"
    sys.exit(main(path))
