import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_employee_bio(name: str, designation: str, department: str, joining_date: str, skills: str) -> str:
    prompt = f"""Write a 2-3 sentence professional employee bio for internal HR records.

    Employee details:
    - Name: {name}
    - Designation: {designation}
    - Department: {department}
    - Joining Date: {joining_date}
    - Skills: {skills}

    Keep it professional and concise. Do not add any fictional information."""

    response = client.models.generate_content(
        model = "gemini-3.0-flash",
        contents = prompt
    )

    return response.text or " "
