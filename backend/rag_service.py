import os
import re
import json
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return embedding_model.encode(text).tolist()

def clean_json_response(text):
    text = re.sub(r"```json\n|\n```", "", text)
    try:
        return json.loads(text)
    except:
        return {"error": "AI did not return valid JSON", "raw_text": text}

def run_ai_analysis(context, student_text):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are a strict academic grader. Analyze this text based on the context provided.
    
    Context (Reference Material):
    {context}
    
    Student Submission:
    {student_text}[:2000]
    
    Respond with a JSON object ONLY. Structure:
    {{
        "plagiarism_score": (float between 0.0 and 1.0, where 1.0 is copied),
        "suggested_sources": ["list", "of", "relevant", "sources"],
        "feedback": "Your qualitative feedback here"
    }}
    """
    response = model.generate_content(prompt)
    return clean_json_response(response.text)