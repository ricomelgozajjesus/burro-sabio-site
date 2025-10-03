# Burro-Sabio Magic Notebooks — Exercise Repository

This folder contains the **curated exercise repository** used by Magic Notebooks. It is the foundational library from which activities are dispatched to students, combined with AI‑generated problems when needed.

---

## 📂 File: `exercises.json`
- Contains all curated exercises in a structured JSON format.
- Includes both metadata (tags, difficulty, topic) and pedagogical elements (solutions, rubrics, hints).

### JSON Structure
Each entry follows this schema:

```json
{
  "id": "unique string identifier",
  "topic": "main subject area (e.g., Derivatives)",
  "subtopic": "specific rule or concept (e.g., Product Rule)",
  "difficulty": "easy | medium | hard",
  "format": "open-ended | multiple-choice | proof | coding",
  "statement_md_es": "Problem statement in Spanish (Markdown + LaTeX)",
  "statement_md_en": "Optional English version",
  "answer_type": "symbolic | numeric | text",
  "expected_answer": "Canonical solution (LaTeX/text)",
  "accepted_equivalents": ["Optional list of algebraically equivalent answers"],
  "rubric": {
    "total_points": 10,
    "criteria": [
      {"name": "Proceso", "points": 4, "description": "Steps and reasoning"},
      {"name": "Resultado", "points": 4, "description": "Correct result"},
      {"name": "Presentación", "points": 2, "description": "Notation/clarity"}
    ]
  },
  "hints": ["Optional hints for progressive disclosure"],
  "solution_steps_md_es": "Worked solution (Markdown + LaTeX, Spanish)",
  "tags": ["keywords for search"],
  "autocheck": {
    "strategy": "symbolic_equivalence | numeric_sampling",
    "reference_expr": "String expression for automated validation",
    "domain": "optional domain restriction"
  },
  "media": {
    "images": [],
    "datasets": []
  },
  "meta": {
    "author": "J. J. Rico + BS Team",
    "source": "BS curated | textbook | AI‑generated",
    "created": "YYYY-MM-DD",
    "updated": "YYYY-MM-DD"
  }
}
```

---

## 🧩 Features
- **Multilingual support:** Statements can be in Spanish and/or English.
- **AI compatibility:** The `autocheck` field allows integration with symbolic/numeric validators.
- **Pedagogical depth:** Includes hints, rubrics, and solution steps.

---

## 🚀 How to Use
1. **Notebook Assembler** reads this JSON to fetch problems by topic/difficulty.
2. **AI Generator** may remix curated items, adding variants.
3. **Evaluation Service** uses `expected_answer` and `autocheck` for scoring.
4. **Dashboard** can display stats by tag, topic, or difficulty.

---

## 📌 Conventions
- **IDs:** Use prefix conventions (e.g., `der-prod-001` for derivative/product rule).
- **Dates:** ISO‑8601 (`YYYY-MM-DD`).
- **Difficulty:** Calibrated to student cohorts (easy ~ warm-up, hard ~ exam level).

---

## 📖 Example Entries
See the five sample exercises in `exercises.json` (derivatives: product, quotient, two chain rule, mixed exp+log).

---

## 🔮 Next Steps
- Add more chapters/topics (limits, integrals, algebra).
- Consider migrating to a lightweight DB (SQLite/Firebase) when scaling.
- Integrate with `Magic Notebooks` assembler and dashboard.

---

© 2025 Burro-Sabio Project — Learning Infrastructure for Cognitive Companions.
