"""
AI-powered symptom explanations for AmIOkay.

Uses Google Gemini (free tier) to generate:
1. Empathetic explanations of why symptoms co-occur
2. Personalized specialist recommendations

Key design decisions:
- Prompts are carefully written to be warm, non-diagnostic, and evidence-aware
- We pass in real data from our SQL queries so the AI has context
- Responses are short (2-3 paragraphs max) to keep the UI clean
- We explicitly tell the AI it is NOT a doctor
"""

import os
import sys
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.0-flash"


def explain_symptoms(symptom_names, life_stage, prevalence_data, cooccurrence_data):
    """
    Generate an empathetic explanation of why the user's symptoms
    commonly appear together.

    Args:
        symptom_names: list of strings, e.g. ["Irregular cycles", "Hormonal acne", "Fatigue"]
        life_stage: string, e.g. "Adult (25-34)"
        prevalence_data: list of dicts from get_symptom_prevalence()
            Each dict has: symptom_name, percentage
        cooccurrence_data: list of dicts from get_cooccurring_symptoms()
            Each dict has: symptom_name, avg_co_pct

    Returns:
        string — the AI-generated explanation
    """

    # Format the data into readable context for the AI
    prevalence_text = "\n".join(
        f"  - {row['symptom_name']}: reported by {row['percentage']}% of women"
        for row in prevalence_data
    )

    cooccurrence_text = "\n".join(
        f"  - {row['symptom_name']}: {row['avg_co_pct']}% overlap"
        for row in cooccurrence_data[:5]
    ) if cooccurrence_data else "  No strong co-occurrences found."

    prompt = f"""You are a warm, knowledgeable women's health educator writing for the app 
"AmIOkay" — a tool that helps women understand their symptoms are more common than they think.

A user in the life stage "{life_stage}" reported these symptoms:
{', '.join(symptom_names)}

Here is real data from our anonymous database:

HOW COMMON ARE THEIR SYMPTOMS:
{prevalence_text}

SYMPTOMS THAT COMMONLY CO-OCCUR WITH THEIRS:
{cooccurrence_text}

Write a response that:
1. Opens with a warm, reassuring statement (they came here because they're worried)
2. Explains in plain language WHY these symptoms often appear together (mention hormonal connections, stress responses, or physiological links as relevant)
3. References the real percentages naturally (e.g., "Nearly 40% of women in your age group report this too")
4. Ends with a gentle, empowering note

RULES:
- 2-3 short paragraphs MAX
- Never diagnose or name specific conditions
- Never say "you might have X"
- Use "many women" and "it's common" language
- Be warm but not condescending
- Write at an 8th grade reading level
- Do NOT use bullet points or headers
- Do NOT start with "Hey there" or "Hey girl" — keep it warm but professional"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return "We're having trouble generating your explanation right now. But know this — your symptoms are more common than you think, and you're not alone."


def explain_specialist_match(specialist_type, specialist_description, matched_symptoms, what_to_expect):
    """
    Generate a personalized explanation of why this specialist
    is recommended based on the user's specific symptoms.

    Args:
        specialist_type: string, e.g. "Endocrinologist"
        specialist_description: string, what this specialist does
        matched_symptoms: list of strings, symptoms that mapped to this specialist
        what_to_expect: string, what to expect at first visit

    Returns:
        string — personalized recommendation
    """

    prompt = f"""You are a warm, knowledgeable women's health educator for the app "AmIOkay."

Based on a user's symptoms, we're recommending they consider seeing a {specialist_type}.

About this specialist: {specialist_description}

The user's symptoms that relate to this specialist:
{', '.join(matched_symptoms)}

What to expect at a first visit: {what_to_expect}

Write a short, warm explanation (1-2 paragraphs) that:
1. Connects their specific symptoms to why this type of specialist could help
2. Normalizes seeing this specialist (it's not scary or dramatic)
3. Briefly mentions what a first visit looks like to reduce anxiety

RULES:
- Never diagnose — say "a specialist can help figure out what's going on"
- Be warm, not clinical
- 1-2 short paragraphs only
- No bullet points or headers
- Don't start with "Hey" — keep it warm but professional"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return f"Based on your symptoms, a {specialist_type} could be a great next step. {what_to_expect}"


def generate_quiz_intro():
    """
    Generate a warm intro message for the quiz page.
    Called once when the app loads — can be cached.
    """

    prompt = """Write a 2-sentence intro for a women's health quiz on an app called "AmIOkay."

The quiz is anonymous and helps women see that their symptoms are shared by many others.

Tone: warm, reassuring, slightly empowering. Like a kind older sister who happens to know a lot about health.

RULES:
- Exactly 2 sentences
- No bullet points
- Don't mention AI or technology
- Don't start with "Hey" or "Welcome"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return "Your body is always talking to you. Let's find out what it's saying — and how many other women are hearing the same thing."