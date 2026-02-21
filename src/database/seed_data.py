"""
Seeds the AmIOkay database with:
1. Symptom categories & symptoms (curated)
2. Life stages
3. Specialist types & symptom mappings
4. Simulated anonymous survey responses (realistic distributions)

The survey data is synthetic but modeled on real prevalence rates
from medical literature (e.g., ~10% of women have PCOS,
~30% experience PMS that affects daily life, etc.)
"""

import random
import sys
import os

# Add parent directory to path so we can import db_manager
sys.path.insert(0, os.path.dirname(__file__))
from db_manager import get_connection, initialize_database


def seed_life_stages(conn):
    """Insert life stage options for the quiz."""
    stages = [
        ("Teens (13-17)", 13, 17, 1),
        ("Young Adult (18-24)", 18, 24, 2),
        ("Adult (25-34)", 25, 34, 3),
        ("Adult (35-44)", 35, 44, 4),
        ("Perimenopause (45-54)", 45, 54, 5),
        ("Menopause & Beyond (55+)", 55, 99, 6),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO life_stages (stage_name, age_range_start, age_range_end, display_order) VALUES (?, ?, ?, ?)",
        stages
    )
    print("  ✅ Life stages")


def seed_symptoms(conn):
    """
    Insert symptom categories and symptoms.
    These are real, commonly reported women's health symptoms
    organized into logical groups for the quiz UI.
    """
    categories = {
        "Menstrual & Cycle": {
            "icon": "🩸",
            "order": 1,
            "symptoms": [
                ("Heavy periods", "Soaking through a pad/tampon every 1-2 hours"),
                ("Irregular cycles", "Cycles shorter than 21 or longer than 35 days"),
                ("Painful cramps", "Pain that interferes with daily activities"),
                ("Spotting between periods", "Light bleeding outside your period"),
                ("Missed periods", "Skipping one or more cycles (not pregnant)"),
                ("PMS mood changes", "Irritability, sadness, or anxiety before your period"),
                ("Bloating around period", "Abdominal swelling or tightness near your cycle"),
            ]
        },
        "Energy & Sleep": {
            "icon": "😴",
            "order": 2,
            "symptoms": [
                ("Chronic fatigue", "Feeling tired even after a full night's sleep"),
                ("Insomnia", "Difficulty falling or staying asleep"),
                ("Afternoon energy crash", "Severe energy drop in the mid-afternoon"),
                ("Brain fog", "Difficulty concentrating, forgetfulness"),
                ("Waking up exhausted", "Not feeling rested despite sleeping 7+ hours"),
            ]
        },
        "Pain & Physical": {
            "icon": "💪",
            "order": 3,
            "symptoms": [
                ("Chronic pelvic pain", "Ongoing pain in the lower abdomen"),
                ("Pain during intercourse", "Discomfort or pain during sex"),
                ("Lower back pain", "Persistent ache in the lower back"),
                ("Headaches or migraines", "Recurring headaches, especially around your cycle"),
                ("Joint pain", "Aching or stiffness in joints"),
                ("Breast tenderness", "Soreness or sensitivity in breasts"),
            ]
        },
        "Skin, Hair & Body": {
            "icon": "✨",
            "order": 4,
            "symptoms": [
                ("Hormonal acne", "Breakouts along jawline, chin, or cheeks"),
                ("Hair thinning", "Noticeable hair loss or thinning"),
                ("Excess body hair", "Unwanted hair growth on face, chest, or back"),
                ("Unexplained weight gain", "Gaining weight without diet/lifestyle changes"),
                ("Difficulty losing weight", "Weight that won't budge despite effort"),
                ("Dry skin", "Persistent skin dryness not helped by moisturizer"),
            ]
        },
        "Mental & Emotional": {
            "icon": "🧠",
            "order": 5,
            "symptoms": [
                ("Anxiety", "Persistent worry, nervousness, or unease"),
                ("Depression or low mood", "Ongoing sadness, loss of interest"),
                ("Mood swings", "Rapid emotional shifts without clear cause"),
                ("Irritability", "Getting frustrated or upset more easily than usual"),
                ("Low self-esteem", "Negative self-perception tied to physical symptoms"),
                ("Feeling overwhelmed", "Difficulty coping with normal daily demands"),
            ]
        },
        "Digestive": {
            "icon": "🫄",
            "order": 6,
            "symptoms": [
                ("Bloating", "Frequent abdominal bloating unrelated to cycle"),
                ("Nausea", "Feeling sick to your stomach regularly"),
                ("Constipation", "Infrequent or difficult bowel movements"),
                ("Food sensitivities", "Reactions to foods you used to tolerate"),
            ]
        },
        "Bladder & Pelvic Floor": {
            "icon": "🚿",
            "order": 7,
            "symptoms": [
                ("Frequent urination", "Needing to pee more often than normal"),
                ("Urinary leakage", "Leaking when coughing, sneezing, or exercising"),
                ("Pelvic pressure", "Feeling of heaviness in the pelvic area"),
            ]
        },
    }

    for cat_name, cat_info in categories.items():
        conn.execute(
            "INSERT OR IGNORE INTO symptom_categories (category_name, display_order, icon) VALUES (?, ?, ?)",
            (cat_name, cat_info["order"], cat_info["icon"])
        )
        # Get the category ID
        row = conn.execute(
            "SELECT category_id FROM symptom_categories WHERE category_name = ?",
            (cat_name,)
        ).fetchone()
        cat_id = row["category_id"]

        for symptom_name, description in cat_info["symptoms"]:
            conn.execute(
                "INSERT OR IGNORE INTO symptoms (symptom_name, category_id, description) VALUES (?, ?, ?)",
                (symptom_name, cat_id, description)
            )

    print("  ✅ Symptom categories & symptoms")


def seed_specialists(conn):
    """Insert specialist types and map them to symptoms."""
    specialists = [
        {
            "type": "OB-GYN (Gynecologist)",
            "description": "Specializes in the female reproductive system — periods, hormones, fertility, and pelvic health.",
            "what_to_expect": "They'll ask about your cycle history, symptoms, and may recommend blood tests or an ultrasound. It's a conversation first — exams only if needed.",
            "icon": "👩‍⚕️",
            "symptoms": [
                "Heavy periods", "Irregular cycles", "Painful cramps",
                "Spotting between periods", "Missed periods", "Pain during intercourse",
                "Chronic pelvic pain",
            ]
        },
        {
            "type": "Endocrinologist",
            "description": "Hormone specialist — they diagnose and treat conditions where your hormones are out of balance.",
            "what_to_expect": "Expect blood work to check hormone levels (thyroid, insulin, testosterone, etc.). They'll look at the full picture — symptoms, labs, and history.",
            "icon": "🔬",
            "symptoms": [
                "Irregular cycles", "Excess body hair", "Hormonal acne",
                "Hair thinning", "Unexplained weight gain", "Difficulty losing weight",
                "Chronic fatigue", "Missed periods",
            ]
        },
        {
            "type": "Therapist / Psychologist",
            "description": "Mental health professional who helps with emotional and psychological well-being through talk therapy.",
            "what_to_expect": "First session is usually getting to know you — your background, what you're dealing with, and your goals. No pressure, no judgment.",
            "icon": "🧠",
            "symptoms": [
                "Anxiety", "Depression or low mood", "Mood swings",
                "Irritability", "Low self-esteem", "Feeling overwhelmed",
                "PMS mood changes", "Insomnia",
            ]
        },
        {
            "type": "Pelvic Floor Physical Therapist",
            "description": "Specializes in the muscles that support your bladder, uterus, and bowel. More common than you think!",
            "what_to_expect": "They'll assess your pelvic floor strength and coordination. Treatment often includes exercises, stretches, and lifestyle tips. It's not scary — think of it like PT for your core.",
            "icon": "🏋️‍♀️",
            "symptoms": [
                "Urinary leakage", "Frequent urination", "Pelvic pressure",
                "Pain during intercourse", "Chronic pelvic pain",
            ]
        },
        {
            "type": "Dermatologist",
            "description": "Skin and hair specialist who can identify whether skin/hair issues have a hormonal root cause.",
            "what_to_expect": "Visual examination of your skin/hair, questions about your cycle and medications. May recommend topical treatments or refer to an endocrinologist if hormonal.",
            "icon": "🪞",
            "symptoms": [
                "Hormonal acne", "Hair thinning", "Excess body hair", "Dry skin",
            ]
        },
        {
            "type": "Gastroenterologist",
            "description": "Digestive system specialist — helps with gut issues that may be connected to hormonal changes.",
            "what_to_expect": "They'll ask about your diet, bowel habits, and symptom patterns. May recommend dietary changes, tests, or further investigation.",
            "icon": "🫄",
            "symptoms": [
                "Bloating", "Nausea", "Constipation", "Food sensitivities",
            ]
        },
        {
            "type": "Primary Care Doctor",
            "description": "Your general doctor — a great starting point if you're unsure where to begin. They can run initial tests and refer you to specialists.",
            "what_to_expect": "A general check-up, blood work, and a conversation about all your symptoms. They're your quarterback — they coordinate your care.",
            "icon": "🩺",
            "symptoms": [
                "Chronic fatigue", "Brain fog", "Afternoon energy crash",
                "Waking up exhausted", "Headaches or migraines", "Joint pain",
                "Lower back pain", "Breast tenderness",
            ]
        },
    ]

    for spec in specialists:
        conn.execute(
            "INSERT OR IGNORE INTO specialists (specialist_type, description, what_to_expect, icon) VALUES (?, ?, ?, ?)",
            (spec["type"], spec["description"], spec["what_to_expect"], spec["icon"])
        )
        # Get specialist ID
        row = conn.execute(
            "SELECT specialist_id FROM specialists WHERE specialist_type = ?",
            (spec["type"],)
        ).fetchone()
        spec_id = row["specialist_id"]

        # Map symptoms to this specialist
        for symptom_name in spec["symptoms"]:
            sym_row = conn.execute(
                "SELECT symptom_id FROM symptoms WHERE symptom_name = ?",
                (symptom_name,)
            ).fetchone()
            if sym_row:
                conn.execute(
                    "INSERT OR IGNORE INTO symptom_specialist_map (symptom_id, specialist_id, relevance_weight) VALUES (?, ?, ?)",
                    (sym_row["symptom_id"], spec_id, 1.0)
                )

    print("  ✅ Specialists & symptom mappings")


def seed_simulated_responses(conn, num_responses=2000):
    """
    Generate realistic anonymous quiz responses.

    Why simulate? We need data to power the "Am I Okay?" stats.
    In a real product, this would come from actual users.

    The symptom clusters below are modeled on real prevalence data:
    - ~10% of women have PCOS-like symptoms
    - ~30% experience significant PMS
    - ~25% report chronic fatigue
    - etc.
    """
    # Get all symptom IDs
    symptoms = conn.execute("SELECT symptom_id, symptom_name FROM symptoms").fetchall()
    symptom_map = {row["symptom_name"]: row["symptom_id"] for row in symptoms}

    # Get life stages
    stages = conn.execute("SELECT stage_id FROM life_stages").fetchall()
    stage_ids = [row["stage_id"] for row in stages]

    # Define realistic symptom clusters with prevalence rates
    # Each cluster: (probability a person has this cluster, list of symptoms)
    clusters = [
        # PCOS-like cluster (~12% of women)
        (0.12, [
            "Irregular cycles", "Hormonal acne", "Excess body hair",
            "Difficulty losing weight", "Hair thinning", "Anxiety",
        ]),
        # PMS/PMDD-like cluster (~25%)
        (0.25, [
            "PMS mood changes", "Bloating around period", "Painful cramps",
            "Mood swings", "Breast tenderness", "Irritability",
        ]),
        # Endometriosis-like cluster (~10%)
        (0.10, [
            "Painful cramps", "Chronic pelvic pain", "Pain during intercourse",
            "Heavy periods", "Bloating", "Chronic fatigue",
        ]),
        # Fatigue/thyroid-like cluster (~20%)
        (0.20, [
            "Chronic fatigue", "Brain fog", "Afternoon energy crash",
            "Waking up exhausted", "Unexplained weight gain", "Dry skin",
        ]),
        # Mental health cluster (~30%)
        (0.30, [
            "Anxiety", "Depression or low mood", "Insomnia",
            "Feeling overwhelmed", "Irritability", "Brain fog",
        ]),
        # Pelvic floor cluster (~15%)
        (0.15, [
            "Urinary leakage", "Frequent urination", "Pelvic pressure",
            "Lower back pain",
        ]),
        # Digestive cluster (~20%)
        (0.20, [
            "Bloating", "Constipation", "Food sensitivities", "Nausea",
        ]),
    ]

    print(f"  🎲 Generating {num_responses} simulated responses...")

    for i in range(num_responses):
        # Pick a random life stage (weighted: more responses from 25-44 age range)
        weights = [0.08, 0.18, 0.28, 0.25, 0.15, 0.06]
        stage_id = random.choices(stage_ids, weights=weights, k=1)[0]

        # Insert the response
        cursor = conn.execute(
            "INSERT INTO responses (life_stage_id) VALUES (?)",
            (stage_id,)
        )
        response_id = cursor.lastrowid

        # Determine which symptoms this person has
        person_symptoms = set()
        for probability, cluster_symptoms in clusters:
            if random.random() < probability:
                # They have this cluster — but not necessarily ALL symptoms in it
                # Each symptom in the cluster has a 50-80% chance of being selected
                for symptom_name in cluster_symptoms:
                    if random.random() < random.uniform(0.5, 0.8):
                        if symptom_name in symptom_map:
                            person_symptoms.add(symptom_name)

        # Also add 0-2 random "stray" symptoms (people are complex!)
        all_symptom_names = list(symptom_map.keys())
        for _ in range(random.randint(0, 2)):
            person_symptoms.add(random.choice(all_symptom_names))

        # Insert this person's symptoms
        for symptom_name in person_symptoms:
            severity = random.choices([0, 1, 2, 3], weights=[0.2, 0.35, 0.3, 0.15], k=1)[0]
            conn.execute(
                "INSERT OR IGNORE INTO response_symptoms (response_id, symptom_id, severity) VALUES (?, ?, ?)",
                (response_id, symptom_map[symptom_name], severity)
            )

    print(f"  ✅ {num_responses} anonymous responses generated")


def compute_cooccurrences(conn):
    """
    Pre-compute how often symptoms appear together.

    This query says: "For every pair of symptoms, count how many
    people reported BOTH, and what percentage of people who reported
    symptom A also reported symptom B."

    We store the results so the frontend doesn't have to compute
    this on every page load.
    """
    print("  📊 Computing symptom co-occurrences...")

    # Clear old data
    conn.execute("DELETE FROM symptom_cooccurrences")

    conn.execute("""
        INSERT INTO symptom_cooccurrences (symptom_id_a, symptom_id_b, co_occurrence_count, co_occurrence_pct)
        SELECT
            rs1.symptom_id as symptom_id_a,
            rs2.symptom_id as symptom_id_b,
            COUNT(DISTINCT rs1.response_id) as co_count,
            ROUND(
                COUNT(DISTINCT rs1.response_id) * 100.0 / 
                NULLIF((SELECT COUNT(DISTINCT response_id) FROM response_symptoms WHERE symptom_id = rs1.symptom_id), 0),
                1
            ) as co_pct
        FROM response_symptoms rs1
        JOIN response_symptoms rs2 
            ON rs1.response_id = rs2.response_id
            AND rs1.symptom_id < rs2.symptom_id
        GROUP BY rs1.symptom_id, rs2.symptom_id
        HAVING co_count >= 10
    """)

    print("  ✅ Co-occurrences computed")


def seed_all():
    """Run the full seeding pipeline."""
    print("\n🌱 Seeding AmIOkay database...\n")

    initialize_database()
    conn = get_connection()

    seed_life_stages(conn)
    seed_symptoms(conn)
    seed_specialists(conn)
    seed_simulated_responses(conn, num_responses=2000)
    compute_cooccurrences(conn)

    conn.commit()

    # Print summary stats
    counts = {
        "Symptom categories": conn.execute("SELECT COUNT(*) as c FROM symptom_categories").fetchone()["c"],
        "Symptoms": conn.execute("SELECT COUNT(*) as c FROM symptoms").fetchone()["c"],
        "Life stages": conn.execute("SELECT COUNT(*) as c FROM life_stages").fetchone()["c"],
        "Specialists": conn.execute("SELECT COUNT(*) as c FROM specialists").fetchone()["c"],
        "Responses": conn.execute("SELECT COUNT(*) as c FROM responses").fetchone()["c"],
        "Symptom reports": conn.execute("SELECT COUNT(*) as c FROM response_symptoms").fetchone()["c"],
        "Co-occurrence pairs": conn.execute("SELECT COUNT(*) as c FROM symptom_cooccurrences").fetchone()["c"],
    }
    conn.close()

    print(f"\n🎉 Database seeded!\n")
    for label, count in counts.items():
        print(f"   {label}: {count}")


if __name__ == "__main__":
    seed_all()