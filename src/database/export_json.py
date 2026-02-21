"""
Exports database data to JSON files for the React frontend.

Why? React (running in a browser) can't talk to SQLite directly.
So we pre-export everything the frontend needs as JSON files.
When someone takes the quiz, the React app loads these JSON files
and computes results client-side.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db_manager import get_connection

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'data')


def export_all():
    """Export all data needed by the frontend."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = get_connection()

    # ── 1. Quiz structure (categories + symptoms) ──
    rows = conn.execute("""
        SELECT sc.category_id, sc.category_name, sc.icon, sc.display_order,
               s.symptom_id, s.symptom_name, s.description
        FROM symptom_categories sc
        JOIN symptoms s ON sc.category_id = s.category_id
        ORDER BY sc.display_order, s.symptom_id
    """).fetchall()

    categories = {}
    for row in rows:
        cat_id = row["category_id"]
        if cat_id not in categories:
            categories[cat_id] = {
                "category_id": cat_id,
                "category_name": row["category_name"],
                "icon": row["icon"],
                "symptoms": []
            }
        categories[cat_id]["symptoms"].append({
            "symptom_id": row["symptom_id"],
            "symptom_name": row["symptom_name"],
            "description": row["description"],
        })

    save_json("quiz_structure.json", list(categories.values()))

    # ── 2. Life stages ──
    rows = conn.execute("""
        SELECT stage_id, stage_name, age_range_start, age_range_end
        FROM life_stages ORDER BY display_order
    """).fetchall()
    save_json("life_stages.json", [dict(r) for r in rows])

    # ── 3. Prevalence per symptom (overall) ──
    total = conn.execute("SELECT COUNT(*) as c FROM responses").fetchone()["c"]
    rows = conn.execute("""
        SELECT s.symptom_id, s.symptom_name, sc.icon as category_icon,
               COUNT(DISTINCT rs.response_id) as report_count
        FROM symptoms s
        JOIN symptom_categories sc ON s.category_id = sc.category_id
        LEFT JOIN response_symptoms rs ON s.symptom_id = rs.symptom_id
        GROUP BY s.symptom_id
    """).fetchall()

    prevalence = {}
    for row in rows:
        prevalence[row["symptom_id"]] = {
            "symptom_id": row["symptom_id"],
            "symptom_name": row["symptom_name"],
            "category_icon": row["category_icon"],
            "report_count": row["report_count"],
            "percentage": round(row["report_count"] * 100.0 / total, 1) if total else 0,
        }
    save_json("prevalence_overall.json", prevalence)

    # ── 4. Prevalence per life stage ──
    stages = conn.execute("SELECT stage_id, stage_name FROM life_stages").fetchall()
    prevalence_by_stage = {}

    for stage in stages:
        stage_total = conn.execute(
            "SELECT COUNT(*) as c FROM responses WHERE life_stage_id = ?",
            (stage["stage_id"],)
        ).fetchone()["c"]

        rows = conn.execute("""
            SELECT s.symptom_id, COUNT(DISTINCT rs.response_id) as report_count
            FROM symptoms s
            JOIN response_symptoms rs ON s.symptom_id = rs.symptom_id
            JOIN responses r ON rs.response_id = r.response_id
            WHERE r.life_stage_id = ?
            GROUP BY s.symptom_id
        """, (stage["stage_id"],)).fetchall()

        stage_data = {}
        for row in rows:
            stage_data[row["symptom_id"]] = {
                "report_count": row["report_count"],
                "percentage": round(row["report_count"] * 100.0 / stage_total, 1) if stage_total else 0,
            }
        prevalence_by_stage[stage["stage_id"]] = stage_data

    save_json("prevalence_by_stage.json", prevalence_by_stage)

    # ── 5. Co-occurrences ──
    rows = conn.execute("""
        SELECT symptom_id_a, symptom_id_b, co_occurrence_count, co_occurrence_pct
        FROM symptom_cooccurrences
        WHERE co_occurrence_pct >= 15
        ORDER BY co_occurrence_pct DESC
    """).fetchall()
    save_json("cooccurrences.json", [dict(r) for r in rows])

    # ── 6. Specialists + symptom mappings ──
    specs = conn.execute("SELECT * FROM specialists").fetchall()
    specialists = []
    for spec in specs:
        symptom_ids = conn.execute("""
            SELECT symptom_id, relevance_weight
            FROM symptom_specialist_map
            WHERE specialist_id = ?
        """, (spec["specialist_id"],)).fetchall()

        specialists.append({
            "specialist_id": spec["specialist_id"],
            "specialist_type": spec["specialist_type"],
            "description": spec["description"],
            "what_to_expect": spec["what_to_expect"],
            "icon": spec["icon"],
            "symptom_ids": [row["symptom_id"] for row in symptom_ids],
        })
    save_json("specialists.json", specialists)

    # ── 7. Severity distribution per symptom ──
    rows = conn.execute("""
        SELECT symptom_id,
               COUNT(*) as total,
               ROUND(SUM(CASE WHEN severity = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_mild,
               ROUND(SUM(CASE WHEN severity = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_moderate,
               ROUND(SUM(CASE WHEN severity = 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_severe
        FROM response_symptoms
        WHERE severity > 0
        GROUP BY symptom_id
    """).fetchall()
    save_json("severity.json", {row["symptom_id"]: dict(row) for row in rows})

    # ── 8. Total response count ──
    save_json("stats.json", {"total_responses": total})

    conn.close()
    print(f"\n🎉 All data exported to {os.path.abspath(OUTPUT_DIR)}")


def save_json(filename, data):
    """Save data as a JSON file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ {filename}")


if __name__ == "__main__":
    export_all()