"""
SQL queries that power the AmIOkay app.

These are the queries the frontend will call via an API.
Each function demonstrates different SQL concepts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db_manager import run_query


# ──────────────────────────────────────────────
# QUIZ DATA (feeds the quiz UI)
# ──────────────────────────────────────────────

def get_quiz_structure():
    """
    Returns all symptom categories with their symptoms.
    The frontend uses this to render the quiz.
    Demonstrates: JOIN + GROUP ordering
    """
    return run_query("""
        SELECT 
            sc.category_name,
            sc.icon,
            s.symptom_id,
            s.symptom_name,
            s.description
        FROM symptom_categories sc
        JOIN symptoms s ON sc.category_id = s.category_id
        ORDER BY sc.display_order, s.symptom_id
    """)


def get_life_stages():
    """Returns life stages for the quiz dropdown."""
    return run_query("""
        SELECT stage_id, stage_name, age_range_start, age_range_end
        FROM life_stages
        ORDER BY display_order
    """)


# ──────────────────────────────────────────────
# "AM I OKAY?" STATS
# ──────────────────────────────────────────────

def get_symptom_prevalence(symptom_ids, life_stage_id=None):
    """
    For each symptom the user selected, what % of women also report it?
    Optionally filtered by life stage.

    Demonstrates: Subquery, conditional filtering, aggregation
    """
    placeholders = ','.join(['?' for _ in symptom_ids])

    if life_stage_id:
        return run_query(f"""
            SELECT 
                s.symptom_id,
                s.symptom_name,
                sc.icon as category_icon,
                COUNT(DISTINCT rs.response_id) as report_count,
                ROUND(
                    COUNT(DISTINCT rs.response_id) * 100.0 / 
                    (SELECT COUNT(*) FROM responses WHERE life_stage_id = ?),
                    1
                ) as percentage
            FROM symptoms s
            JOIN symptom_categories sc ON s.category_id = sc.category_id
            LEFT JOIN response_symptoms rs ON s.symptom_id = rs.symptom_id
            INNER JOIN responses r ON rs.response_id = r.response_id
            WHERE s.symptom_id IN ({placeholders})
              AND r.life_stage_id = ?
            GROUP BY s.symptom_id
            ORDER BY percentage DESC
        """, (life_stage_id, *symptom_ids, life_stage_id))


def get_cooccurring_symptoms(symptom_ids, limit=10):
    """
    "Women who report YOUR symptoms also commonly experience..."
    Finds symptoms that co-occur with the user's selected symptoms
    but that the user DIDN'T select.

    Demonstrates: NOT IN, JOIN, aggregation, HAVING
    """
    placeholders = ','.join(['?' for _ in symptom_ids])

    return run_query(f"""
        SELECT 
            s.symptom_name,
            sc.category_name,
            sc.icon,
            ROUND(AVG(sco.co_occurrence_pct), 1) as avg_co_pct,
            COUNT(*) as matched_with_count
        FROM symptom_cooccurrences sco
        JOIN symptoms s ON sco.symptom_id_b = s.symptom_id
        JOIN symptom_categories sc ON s.category_id = sc.category_id
        WHERE sco.symptom_id_a IN ({placeholders})
          AND sco.symptom_id_b NOT IN ({placeholders})
        GROUP BY sco.symptom_id_b
        HAVING matched_with_count >= 2
        ORDER BY avg_co_pct DESC
        LIMIT ?
    """, (*symptom_ids, *symptom_ids, limit))


# ──────────────────────────────────────────────
# SPECIALIST MATCHING
# ──────────────────────────────────────────────

def get_recommended_specialists(symptom_ids):
    """
    Based on the user's symptoms, which specialists should they see?
    Ranked by how many of their symptoms map to that specialist.

    Demonstrates: JOIN across 3 tables, weighted scoring, RANK window function
    """
    placeholders = ','.join(['?' for _ in symptom_ids])

    return run_query(f"""
        WITH specialist_scores AS (
            SELECT
                sp.specialist_id,
                sp.specialist_type,
                sp.description,
                sp.what_to_expect,
                sp.icon,
                COUNT(*) as matching_symptoms,
                SUM(ssm.relevance_weight) as total_score,
                GROUP_CONCAT(s.symptom_name, ', ') as matched_symptom_names
            FROM symptom_specialist_map ssm
            JOIN specialists sp ON ssm.specialist_id = sp.specialist_id
            JOIN symptoms s ON ssm.symptom_id = s.symptom_id
            WHERE ssm.symptom_id IN ({placeholders})
            GROUP BY sp.specialist_id
        )
        SELECT *,
            RANK() OVER (ORDER BY total_score DESC) as recommendation_rank
        FROM specialist_scores
        ORDER BY total_score DESC
    """, symptom_ids)


# ──────────────────────────────────────────────
# ANALYTICS (bonus — shows off more SQL skills)
# ──────────────────────────────────────────────

def get_top_symptoms_by_life_stage():
    """
    What are the top 5 most reported symptoms for each life stage?
    Demonstrates: Window function (ROW_NUMBER) + CTE
    """
    return run_query("""
        WITH ranked AS (
            SELECT
                ls.stage_name,
                s.symptom_name,
                COUNT(*) as report_count,
                ROW_NUMBER() OVER (
                    PARTITION BY ls.stage_id
                    ORDER BY COUNT(*) DESC
                ) as rank
            FROM responses r
            JOIN life_stages ls ON r.life_stage_id = ls.stage_id
            JOIN response_symptoms rs ON r.response_id = rs.response_id
            JOIN symptoms s ON rs.symptom_id = s.symptom_id
            GROUP BY ls.stage_id, s.symptom_id
        )
        SELECT stage_name, symptom_name, report_count, rank
        FROM ranked
        WHERE rank <= 5
        ORDER BY stage_name, rank
    """)


def get_severity_distribution(symptom_ids):
    """
    For selected symptoms, how severe do people rate them?
    Demonstrates: CASE WHEN, percentage calculation
    """
    placeholders = ','.join(['?' for _ in symptom_ids])

    return run_query(f"""
        SELECT
            s.symptom_name,
            COUNT(*) as total,
            ROUND(SUM(CASE WHEN rs.severity = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_mild,
            ROUND(SUM(CASE WHEN rs.severity = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_moderate,
            ROUND(SUM(CASE WHEN rs.severity = 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_severe
        FROM response_symptoms rs
        JOIN symptoms s ON rs.symptom_id = s.symptom_id
        WHERE rs.symptom_id IN ({placeholders})
          AND rs.severity > 0
        GROUP BY rs.symptom_id
    """, symptom_ids)


# ──────────────────────────────────────────────
# DEMO
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n📋 === QUIZ STRUCTURE ===")
    structure = get_quiz_structure()
    current_cat = ""
    for row in structure:
        if row["category_name"] != current_cat:
            current_cat = row["category_name"]
            print(f"\n  {row['icon']} {current_cat}")
        print(f"     [{row['symptom_id']}] {row['symptom_name']}")

    # Simulate a user who selected these symptoms
    test_symptoms = [1, 3, 8, 22, 27]  # heavy periods, painful cramps, fatigue, acne, anxiety
    print(f"\n\n🧪 === SIMULATING USER WITH SYMPTOMS {test_symptoms} ===")

    print("\n📊 Symptom Prevalence:")
    for row in get_symptom_prevalence(test_symptoms):
        print(f"  {row['symptom_name']}: {row['percentage']}% of women report this")

    print("\n🔗 Co-occurring Symptoms:")
    for row in get_cooccurring_symptoms(test_symptoms, limit=5):
        print(f"  {row['icon']} {row['symptom_name']}: {row['avg_co_pct']}% overlap")

    print("\n👩‍⚕️ Recommended Specialists:")
    for row in get_recommended_specialists(test_symptoms):
        print(f"  #{row['recommendation_rank']} {row['icon']} {row['specialist_type']} ({row['matching_symptoms']} symptom matches)")
        print(f"     Matched: {row['matched_symptom_names']}")

    print("\n📈 Top Symptoms by Life Stage:")
    current_stage = ""
    for row in get_top_symptoms_by_life_stage():
        if row["stage_name"] != current_stage:
            current_stage = row["stage_name"]
            print(f"\n  {current_stage}:")
        print(f"     #{row['rank']} {row['symptom_name']} ({row['report_count']} reports)")

    print("\n🌡️ Severity Distribution:")
    for row in get_severity_distribution(test_symptoms):
        print(f"  {row['symptom_name']}: {row['pct_mild']}% mild, {row['pct_moderate']}% moderate, {row['pct_severe']}% severe")