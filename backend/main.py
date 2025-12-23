

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, get_db
import models
import os
import shutil
import datetime
import requests

from auth import create_jwt_token, verify_token
from rag_service import get_embedding, run_ai_analysis

N8N_WEBHOOK_URL = "http://academic_n8n:5678/webhook-test/assignment"
UPLOAD_DIR = "/app/uploads"

app = FastAPI(title="Academic Assignment Helper API")

with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.commit()
models.Base.metadata.create_all(bind=engine)
os.makedirs(UPLOAD_DIR, exist_ok=True)



@app.get("/", include_in_schema=False)
def read_root():
    return {"status": "System Operational 🚀"}

@app.post("/auth/register", tags=["Authentication"])
def register(data: dict, db: Session = Depends(get_db)):
    existing_user = db.query(models.Student).filter(models.Student.email == data.get("email")).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = models.Student(
        email=data.get("email"),
        password_hash=data.get("password"), 
        full_name=data.get("full_name"),
        student_id=data.get("student_id", "STU-001")
    )
    db.add(new_student)
    db.commit()
    return {"message": "Student registered successfully"}

@app.post("/auth/login", tags=["Authentication"])
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(models.Student).filter(models.Student.email == data.get("email")).first()
    if user and user.password_hash == data.get("password"):
        token = create_jwt_token(user.id)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Bad credentials")

@app.post("/upload", tags=["Assignments"])
def upload_assignment(file: UploadFile = File(...), user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_assignment = models.Assignment(student_id=int(user_id), filename=file.filename, uploaded_at=datetime.datetime.utcnow())
    db.add(new_assignment)
    db.commit()
    
    try:
        requests.post(N8N_WEBHOOK_URL, json={"filename": file.filename, "assignment_id": new_assignment.id})
    except:
        pass 

    return {"status": "File received", "assignment_id": new_assignment.id}

@app.get("/analysis/{assignment_id}", tags=["Assignments"])
def get_analysis(assignment_id: int, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment or assignment.student_id != int(user_id):
        raise HTTPException(status_code=404, detail="Assignment not found")

    result = db.query(models.AnalysisResult).filter(models.AnalysisResult.assignment_id == assignment_id).first()
    if not result:
        return {"status": "Processing", "message": "Analysis in progress..."}
    
    return {
        "assignment_id": assignment_id,
        "plagiarism_score": result.plagiarism_score,
        "suggested_sources": result.suggested_sources,
        "feedback": "Analysis Complete"
    }

@app.get("/sources", tags=["RAG Search"])
def get_sources(q: str = Query(..., min_length=3), user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    query_vector = get_embedding(q)
    results = db.query(models.AcademicSource).order_by(
        models.AcademicSource.embedding.l2_distance(query_vector)
    ).limit(2).all()
    return [{"id": r.id, "title": r.title, "content": r.content} for r in results]




@app.post("/seed-db")
def seed_database(db: Session = Depends(get_db)):
    sources = [
        {"title": "History of Ethiopia", "content": "Ethiopia is located in the Horn of Africa. It is a rugged, landlocked country split by the Great Rift Valley."},
        {"title": "Intro to AI", "content": "Artificial Intelligence is the simulation of human intelligence processes by machines, especially computer systems."},
        {"title": "Photosynthesis", "content": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy."}
    ]
    for s in sources:
        if not db.query(models.AcademicSource).filter_by(title=s["title"]).first():
            db.add(models.AcademicSource(title=s["title"], content=s["content"], embedding=get_embedding(s["content"])))
    db.commit()
    return {"message": "Seeded"}

@app.post("/internal/rag-search", include_in_schema=False)
def internal_rag_search(data: dict, db: Session = Depends(get_db)):
    text_query = data.get("text", "")
    query_vector = get_embedding(text_query[:500])
    results = db.query(models.AcademicSource).order_by(models.AcademicSource.embedding.l2_distance(query_vector)).limit(3).all()
    context = "\n".join([f"- {r.title}: {r.content}" for r in results])
    return {"context": context}

@app.post("/internal/analyze", include_in_schema=False)
def internal_analyze(data: dict):
    return run_ai_analysis(data.get('context'), data.get('text'))