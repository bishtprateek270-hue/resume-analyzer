from google import genai
from google.genai import types
import json
import os
from typing import Dict, Any

# Ordered list of preferred models (newest first). The app will try each in order.
CANDIDATE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

def _get_client(api_key: str):
    return genai.Client(api_key=api_key.strip())


def _score_to_decision(ats_score: int) -> str:
    """
    Maps ATS score to a standardised hiring decision tier.
      >= 80  →  Strong Hire
      65-79  →  Hire
      50-64  →  Borderline
      35-49  →  No Hire
      < 35   →  Strong No Hire
    """
    if ats_score >= 80:
        return "Strong Hire"
    elif ats_score >= 65:
        return "Hire"
    elif ats_score >= 50:
        return "Borderline"
    elif ats_score >= 35:
        return "No Hire"
    else:
        return "Strong No Hire"


def _find_working_model(client) -> str:
    """
    Tries each candidate model in order and returns the first that works.
    Falls back to gemini-2.0-flash if none resolve.
    """
    for model_name in CANDIDATE_MODELS:
        try:
            client.models.generate_content(
                model=model_name,
                contents="hi",
                config=types.GenerateContentConfig(max_output_tokens=3)
            )
            return model_name
        except Exception:
            continue
    return CANDIDATE_MODELS[-1]  # last resort

def validate_gemini_api_key(api_key: str) -> bool:
    """
    Validates the Gemini API key by making a lightweight model call.
    Returns True if valid, False otherwise.
    """
    if not api_key or not api_key.strip():
        return False
    try:
        client = _get_client(api_key)
        _find_working_model(client)
        return True
    except Exception as e:
        print(f"API Key Validation Error: {e}")
        return False


def get_llm_analysis(resume_text: str, jd_text: str, score_details: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Invokes Gemini LLM to generate qualitative feedback,
    resume suggestions, project recommendations, and hiring analysis.
    """
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is missing.")

    client = _get_client(api_key)
    model_name = _find_working_model(client)

    ats_score = score_details.get('ats_score', 0)
    expected_decision = _score_to_decision(ats_score)

    prompt = f"""
    You are an expert ATS recruiter and senior technical career advisor.
    Analyse the candidate's resume against the job description using the deterministic metrics below.

    Resume Text:
    ---
    {resume_text}
    ---

    Job Description:
    ---
    {jd_text}
    ---

    Deterministic Match Metrics:
    - Overall ATS Match Score: {ats_score}%
    - Skills Score: {score_details['skills_score']}%
    - Experience Score: {score_details['experience_score']}% (Candidate: {score_details['candidate_experience']} yrs, Required: {score_details['required_experience']} yrs)
    - Education Score: {score_details['education_score']}% (Candidate: {score_details['candidate_education']}, Required: {score_details['required_education']})
    - Matched Skills: {', '.join(score_details['matched_skills']) if score_details['matched_skills'] else 'None'}
    - Missing Skills: {', '.join(score_details['missing_skills']) if score_details['missing_skills'] else 'None'}

    IMPORTANT — Hiring Decision Tiers (must follow these exactly based on ATS score):
      >= 80%  →  "Strong Hire"
      65-79%  →  "Hire"
      50-64%  →  "Borderline"
      35-49%  →  "No Hire"
      < 35%   →  "Strong No Hire"

    The ATS score is {ats_score}%, so the hiring_recommendation MUST be "{expected_decision}".

    Return a JSON object with this exact schema:
    {{
        "strengths": ["bullet 1", "bullet 2", ...],
        "weaknesses": ["bullet 1", "bullet 2", ...],
        "suggestions": ["specific actionable improvement 1", ...],
        "recommended_projects": [
            {{
                "title": "Project Name",
                "description": "How this bridges the skill gap for this job.",
                "tech_stack": ["Tech1", "Tech2"]
            }}
        ],
        "hiring_recommendation": "{expected_decision}",
        "hiring_explanation": "Detailed reasoning that references the ATS score of {ats_score}% and key matched/missing skills."
    }}

    Return only valid JSON. No markdown code blocks.
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        analysis = json.loads(text)

        # Ensure required keys exist
        required_keys = ["strengths", "weaknesses", "suggestions", "recommended_projects", "hiring_recommendation", "hiring_explanation"]
        for key in required_keys:
            if key not in analysis:
                analysis[key] = [] if key in ["strengths", "weaknesses", "suggestions", "recommended_projects"] else "Not provided"

        # Always enforce score-based hiring decision — LLM sometimes drifts
        analysis["hiring_recommendation"] = expected_decision

        return analysis

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        decision = _score_to_decision(ats_score)
        return {
            "strengths": ["Resume parsed and ATS score calculated successfully."],
            "weaknesses": ["Qualitative AI analysis unavailable — API quota may be exhausted."],
            "suggestions": ["Verify your Gemini API key is active and has remaining quota."],
            "recommended_projects": [
                {
                    "title": "Portfolio Showcase App",
                    "description": "Build a responsive portfolio to highlight your current skill set and bridge missing skills.",
                    "tech_stack": list(score_details.get("matched_skills", ["Python"]))[:4]
                }
            ],
            "hiring_recommendation": decision,
            "hiring_explanation": (
                f"ATS Score: {ats_score}% → Tier: {decision}. "
                f"(AI explanation unavailable — {str(e).split('.')[0]}. "
                f"Code-based ATS analysis completed successfully.)"
            )
        }
