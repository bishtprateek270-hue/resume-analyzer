import google.generativeai as genai
import json
import os
from typing import Dict, Any, Tuple

def validate_gemini_api_key(api_key: str) -> bool:
    """
    Validates the Gemini API key by making a lightweight model call.
    Returns True if valid, False otherwise.
    """
    if not api_key or not api_key.strip():
        return False
    try:
        genai.configure(api_key=api_key.strip())
        model = genai.GenerativeModel("gemini-3.5-flash")
        # Lightweight test request
        model.generate_content("test", generation_config={"max_output_tokens": 5})
        return True
    except Exception as e:
        print(f"API Key Validation Error: {e}")
        return False

def get_llm_analysis(resume_text: str, jd_text: str, score_details: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Invokes Gemini LLM in JSON mode to generate qualitative feedback,
    resume suggestions, projects recommendations, and hiring analysis.
    """
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is missing. Please configure it in Settings or your environment.")

    # Configure API
    genai.configure(api_key=api_key.strip())
    
    # Use gemini-1.5-flash for speed and cost-effectiveness
    model = genai.GenerativeModel("gemini-3.5-flash")
    
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
                "description": "Explain how this project bridges the candidate's skill gaps and fits the job description.",
                "tech_stack": ["React", "FastAPI", ...],
                "implementation_steps": ["step 1", "step 2", ...]
            }},
            {{
                "title": "Second Project Name",
                "description": "Detailed project idea focused on other missing technologies.",
                "tech_stack": ["AWS", "Docker", ...],
                "implementation_steps": ["step 1", "step 2", ...]
            }}
        ],
        "hiring_recommendation": "Strong Hire | Hire | Borderline | No Hire",
        "hiring_explanation": "Detailed explanation of the hiring decision, justification of how the skills/experience match, and resume formatting assessment."
    }}
    
    Ensure all text values in the JSON are clean and properly escaped. Do not include markdown code block formatting (like ```json) in the raw response text, just return the JSON object directly.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Clean response if markdown blocks are returned
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        analysis = json.loads(text)
        
        # Validate critical keys in JSON response
        required_keys = ["strengths", "weaknesses", "suggestions", "recommended_projects", "hiring_recommendation", "hiring_explanation"]
        for key in required_keys:
            if key not in analysis:
                analysis[key] = [] if "s" in key[-1] or "project" in key else "Not provided"
                
        return analysis
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Return fallback structures on error
        return {
            "strengths": ["Profile parsed but detailed strengths generation failed due to API connection issue."],
            "weaknesses": ["Profile parsed but detailed weaknesses generation failed due to API connection issue."],
            "suggestions": ["Ensure your API key is correct and you have an active internet connection to see suggestions."],
            "recommended_projects": [
                {
                    "title": "Fallback Project: Portfolio Showcase",
                    "description": "Build a responsive web application to highlight your current skill set.",
                    "tech_stack": list(score_details["matched_skills"])[:3] if score_details["matched_skills"] else ["Python"],
                    "implementation_steps": ["Initialize repo", "Build portfolio page", "Deploy to Vercel/Netlify"]
                }
            ],
            "hiring_recommendation": "Borderline",
            "hiring_explanation": f"LLM analysis failed: {str(e)}. Code-based ATS analysis succeeded."
        }
