"""
Connects the database queries with the AI explainer.

This is the "brain" of the app — it:
1. Takes user quiz input (symptom IDs + life stage)
2. Runs SQL queries to get stats
3. Passes the stats to Gemini for explanation
4. Returns everything packaged up for the frontend
"""

import sys
import os

# Add paths so we can import from other folders
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
sys.path.insert(0, os.path.dirname(__file__))

from queries import (
    get_symptom_prevalence,
    get_cooccurring_symptoms,
    get_recommended_specialists,
    get_severity_distribution,
)
from explainer import explain_symptoms, explain_specialist_match


def get_full_results(symptom_ids, life_stage_id, life_stage_name):
    """
    The main function the frontend will call.

    Takes quiz answers, returns everything needed for the results page:
    - Prevalence stats
    - Co-occurring symptoms
    - AI explanation
    - Specialist recommendations with AI explanations
    - Severity distribution

    Args:
        symptom_ids: list of ints, e.g. [1, 3, 8, 22, 27]
        life_stage_id: int, e.g. 3
        life_stage_name: string, e.g. "Adult (25-34)"

    Returns:
        dict with all results
    """

    # ── Step 1: Run SQL queries ──
    print("📊 Running queries...")

    prevalence = get_symptom_prevalence(symptom_ids, life_stage_id)
    cooccurrences = get_cooccurring_symptoms(symptom_ids, limit=5)
    specialists = get_recommended_specialists(symptom_ids)
    severity = get_severity_distribution(symptom_ids)

    # ── Step 2: Get symptom names for the AI ──
    symptom_names = [row["symptom_name"] for row in prevalence]

    # ── Step 3: Generate AI explanation ──
    print("🤖 Generating AI explanation...")

    ai_explanation = explain_symptoms(
        symptom_names=symptom_names,
        life_stage=life_stage_name,
        prevalence_data=prevalence,
        cooccurrence_data=cooccurrences,
    )

    # ── Step 4: Generate AI specialist explanations ──
    print("👩‍⚕️ Generating specialist recommendations...")

    specialist_results = []
    for spec in specialists[:3]:  # top 3 specialists only
        matched_symptom_list = spec["matched_symptom_names"].split(", ")

        ai_spec_explanation = explain_specialist_match(
            specialist_type=spec["specialist_type"],
            specialist_description=spec["description"],
            matched_symptoms=matched_symptom_list,
            what_to_expect=spec["what_to_expect"],
        )

        specialist_results.append({
            "specialist_type": spec["specialist_type"],
            "icon": spec["icon"],
            "matching_symptoms": spec["matching_symptoms"],
            "matched_symptom_names": matched_symptom_list,
            "description": spec["description"],
            "what_to_expect": spec["what_to_expect"],
            "ai_explanation": ai_spec_explanation,
            "rank": spec["recommendation_rank"],
        })

    # ── Step 5: Package everything ──
    return {
        "symptom_names": symptom_names,
        "life_stage": life_stage_name,
        "prevalence": prevalence,
        "cooccurrences": cooccurrences,
        "severity": severity,
        "ai_explanation": ai_explanation,
        "specialists": specialist_results,
    }


# ──────────────────────────────────────────────
# DEMO — simulates a user taking the quiz
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Simulate: user is 25-34, selected these symptoms:
    # heavy periods (1), painful cramps (3), chronic fatigue (8),
    # hormonal acne (22), anxiety (27)
    test_symptom_ids = [1, 3, 8, 22, 27]
    test_life_stage_id = 3
    test_life_stage_name = "Adult (25-34)"

    print("\n🧪 === SIMULATING QUIZ RESULTS ===\n")
    print(f"Life stage: {test_life_stage_name}")
    print(f"Symptoms selected: IDs {test_symptom_ids}\n")

    results = get_full_results(
        test_symptom_ids,
        test_life_stage_id,
        test_life_stage_name,
    )

    # ── Display results ──
    print("\n" + "=" * 60)
    print("📊 YOU'RE NOT ALONE")
    print("=" * 60)
    for row in results["prevalence"]:
        bar = "█" * int(row["percentage"] / 2)
        print(f"  {row['symptom_name']}: {row['percentage']}% {bar}")

    print("\n" + "=" * 60)
    print("🔗 WOMEN WITH YOUR SYMPTOMS ALSO REPORT")
    print("=" * 60)
    for row in results["cooccurrences"]:
        print(f"  {row['symptom_name']}: {row['avg_co_pct']}% overlap")

    print("\n" + "=" * 60)
    print("💬 AI EXPLANATION")
    print("=" * 60)
    print(f"\n{results['ai_explanation']}")

    print("\n" + "=" * 60)
    print("👩‍⚕️ RECOMMENDED SPECIALISTS")
    print("=" * 60)
    for spec in results["specialists"]:
        print(f"\n  #{spec['rank']} {spec['icon']} {spec['specialist_type']}")
        print(f"  Matched symptoms: {', '.join(spec['matched_symptom_names'])}")
        print(f"\n  {spec['ai_explanation']}")

    print("\n" + "=" * 60)
    print("🌡️ SEVERITY BREAKDOWN")
    print("=" * 60)
    for row in results["severity"]:
        print(f"  {row['symptom_name']}: {row['pct_mild']}% mild | {row['pct_moderate']}% moderate | {row['pct_severe']}% severe")