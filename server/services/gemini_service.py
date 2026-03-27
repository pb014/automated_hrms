import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3-flash-preview"


def generate_employee_bio(name: str, designation: str, department: str, joining_date: str, contact: str | None = None) -> str:
    prompt = f"""You are a professional HR content writer. Generate a brief, professional 
                employee bio (2-3 sentences) based on the following profile data.
                
                Employee Profile:
                - Name: {name}
                - Designation: {designation}
                - Department: {department}
                - Joining Date: {joining_date}
                - Contact: {contact}
                
                Guidelines:
                - Keep it professional and warm
                - Mention their role and department naturally
                - Do NOT invent skills, achievements, or qualifications not provided
                - Keep it to 2-3 sentences maximum
                - Write in third person
                
                Example output for reference:
                "Priya Mehta is a Senior Product Designer in the Design department, bringing her expertise to the team since March 2024. She plays a key role in shaping user experiences and contributing to the department's creative vision."
                
                Now generate a bio for the employee above:"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text or " "


def analyze_resume(resume_text: str, job_description: str, required_skills: str) -> dict:
    prompt = f"""You are an experienced HR recruiter analyzing a candidate's resume against a job description.
 
            JOB DESCRIPTION:
            {job_description}
            
            REQUIRED SKILLS:
            {required_skills}
            
            CANDIDATE'S RESUME:
            {resume_text}
            
            Analyze the resume and respond in EXACTLY this JSON format (no markdown, no extra text):
            {{
                "match_score": <number between 0-100>,
                "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
                "gaps": ["<gap 1>", "<gap 2>"],
                "interview_questions": [
                    "<question 1 tailored to this candidate>",
                    "<question 2>",
                    "<question 3>",
                    "<question 4>",
                    "<question 5>"
                ],
                "summary": "<2-3 sentence overall assessment with reasoning for the score>"
            }}
            
            Be specific and reference actual content from the resume. Do not be generic."""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        return json.loads(response.text)

    except json.JSONDecodeError:
        return {
            "match_score": 0,
            "strengths": [],
            "gaps": ["Could not parse resume"],
            "interview_questions": [],
            "summary": "Resume analysis failed — please try again."
        }

    except Exception as e:
        return {
            "match_score": 0,
            "strengths": [],
            "gaps": [str(e)],
            "interview_questions": [],
            "summary": f"Error: {str(e)}"
        }


def analyze_leave_patterns(leave_data: list) -> dict:
    prompt = f"""You are an HR analytics assistant. Analyze these leave records and identify:
 
            1. UNUSUAL PATTERNS: Employees who frequently take leave on Mondays or Fridays 
            (possible pattern of extending weekends), or suspicious clusters of sick leaves.
            2. CAPACITY RISKS: Departments where too many people are on leave at the same time.
            
            Leave Records:
            {json.dumps(leave_data, indent=2)}
            
            Respond in this JSON format:
            {{
                "unusual_patterns": [
                    {{"employee": "name", "pattern": "description of the pattern", "severity": "low/medium/high"}}
                ],
                "capacity_risks": [
                    {{"department": "name", "dates": "date range", "risk_level": "low/medium/high", "detail": "explanation"}}
                ],
                "recommendations": ["recommendation 1", "recommendation 2"]
            }}"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        return json.loads(response.text)

    except Exception as e:
        return {
            "error": str(e), "unusual_patterns": [], "capacity_risks": []
        }


def generate_review_summary(
    employee_name: str,
    self_assessment: str,
    self_rating: float,
    manager_ratings: dict,
    manager_comment: str = ""
) -> dict:
    avg_manager = sum(manager_ratings.values()) / \
        len(manager_ratings) if manager_ratings else 0

    prompt = f"""You are a senior HR professional writing a performance review summary.
 
                EMPLOYEE: {employee_name}
                
                SELF-ASSESSMENT:
                {self_assessment}
                Self-Rating: {self_rating}/5
                
                MANAGER RATINGS:
                {json.dumps(manager_ratings, indent=2)}
                Average Manager Rating: {avg_manager:.1f}/5
                Manager Comment: {manager_comment or "No comment provided"}
                
                Tasks:
                1. Write a balanced, professional review summary (one paragraph, 4-5 sentences)
                that synthesizes both the self-assessment and manager's evaluation.
                2. Flag any mismatches where the self-rating differs significantly from the 
                manager's average rating (difference > 1 point).
                3. Suggest 2-3 SPECIFIC, ACTIONABLE development recommendations based on the 
                lowest-rated areas. Be specific — don't say "improve communication", say 
                "Consider leading the next sprint demo to practice presenting technical work."
                
                Respond in this JSON format:
                {{
                    "summary": "<professional review paragraph>",
                    "flags": ["<mismatch description 1>", ...],
                    "development_actions": ["<specific action 1>", "<specific action 2>", "<specific action 3>"]
                }}"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        return json.loads(response.text)

    except Exception as e:
        return {
            "summary": f"Review generation failed: {str(e)}",
            "flags": [],
            "development_actions": []
        }


# Onboarding Chatbot
def answer_policy_question(question: str, context_chunks: list) -> dict:
    context = "\n\n".join(
        context_chunks) if context_chunks else "No policy documents uploaded yet."

    prompt = f"""You are a helpful onboarding assistant for new employees. 
                Answer the following question using ONLY the information provided in the context below.
                
                CONTEXT (from company policy documents):
                {context}
                
                QUESTION: {question}
                
                RULES:
                1. ONLY use information from the CONTEXT above to answer
                2. If the answer is NOT found in the context, respond with exactly:
                "I don't have information about that in our policy documents. Please contact HR at hr@company.com for assistance."
                3. Be friendly, concise, and helpful
                4. If partially relevant info exists, share what you can and direct them to HR for the rest
                
                Your answer:"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        answer = response.text.strip()

        # Check if the bot couldn't answer
        could_answer = "please contact hr" not in answer.lower(
        ) and "don't have information" not in answer.lower()

        return {
            "answer": answer,
            "could_answer": could_answer
        }
    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error. Please contact HR at hr@company.com. Error: {str(e)}",
            "could_answer": False
        }

# HR Analytics Summary


def generate_hr_summary(analytics_data: dict) -> str:
    prompt = f"""You are a senior HR advisor preparing a monthly HR summary report.
    CURRENT HR DATA:
    {json.dumps(analytics_data, indent=2)}
    
    Write a professional monthly HR summary covering:
    1. KEY HIGHLIGHTS: What's going well (headcount growth, filled positions, etc.)
    2. RISKS: Any concerning trends (high attrition, leave utilisation issues, etc.)
    3. RECOMMENDED ACTIONS: 2-3 specific things HR should do this month
    
    Keep the summary concise (3-4 paragraphs), professional, and actionable.
    Use actual numbers from the data provided."""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Summary generation failed: {str(e)}"
