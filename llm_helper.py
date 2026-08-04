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

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) recruiter and senior technical career advisor.
    You will analyze a candidate's resume text against a Job Description, using a set of deterministic score metrics that have already been calculated.

    Resume Text:
    ---
    {resume_text}
    ---

    Job Description:
    ---
    {jd_text}
    ---

    Deterministic Match Metrics:
    - Overall ATS Match Score: {score_details['ats_score']}%
    - Skills Score: {score_details['skills_score']}%
    - Experience Score: {score_details['experience_score']}% (Candidate Experience: {score_details['candidate_experience']} years, Required: {score_details['required_experience']} years)
    - Education Score: {score_details['education_score']}% (Candidate Education: {score_details['candidate_education']}, Required: {score_details['required_education']})
    - Matched Skills: {', '.join(score_details['matched_skills']) if score_details['matched_skills'] else 'None'}
    - Missing Skills Identified: {', '.join(score_details['missing_skills']) if score_details['missing_skills'] else 'None'}

    Based on this data, generate a structured evaluation in JSON format. The response must follow this JSON schema exactly:
    {{
        "strengths": ["bullet point 1", "bullet point 2", ...],
        "weaknesses": ["bullet point 1", "bullet point 2", ...],
        "suggestions": ["specific actionable change 1 with reference to wording/section", ...],
        "recommended_projects": [
            {{
                "title": "Project Name",
                "description": "Explain how this project bridges the candidate skill gaps and fits the job description.",
                "tech_stack": ["React", "FastAPI", ...]
            }},
            {{
                "title": "Second Project Name",
                "description": "Detailed project idea focused on other missing technologies.",
                "tech_stack": ["AWS", "Docker", ...]
            }}
        ],
        "hiring_recommendation": "Strong Hire | Hire | Borderline | No Hire",
        "hiring_explanation": "Detailed explanation of the hiring decision."
    }}

    Return only valid JSON. Do not include markdown code blocks like ```json.
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

        return analysis

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "strengths": ["Resume parsed successfully. Detailed analysis failed due to API error."],
            "weaknesses": ["Could not complete qualitative analysis."],
            "suggestions": ["Verify your API key is active and has quota remaining."],
            "recommended_projects": [
                {
                    "title": "Portfolio Showcase App",
                    "description": "Build a responsive portfolio to highlight your current skill set.",
                    "tech_stack": list(score_details.get("matched_skills", ["Python"]))[:3]
                }
            ],
            "hiring_recommendation": "Borderline",
            "hiring_explanation": f"LLM analysis failed: {str(e)}. Code-based ATS analysis succeeded."
        }
