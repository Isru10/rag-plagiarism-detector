# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

A comprehensive backend + n8n automation system designed to process academic assignments. It features a Retrieval-Augmented Generation (RAG) pipeline for research suggestions and AI-powered plagiarism detection.

## 📂 Project Structure

```text
academic-assignment-helper/
├── backend/
│   ├── main.py            # API Routes & Application Entry
│   ├── auth.py            # JWT Security & Authentication Logic
│   ├── models.py          # SQLAlchemy Database Models
│   ├── database.py        # Database Connection Configuration
│   ├── rag_service.py     # Embedding Generation & AI Analysis Logic
│   ├── requirements.txt   # Python Dependencies
│   └── Dockerfile         # Backend Container Definition
├── workflows/
│   └── assignment_analysis_workflow.json  # n8n Workflow Export
├── data/
│   └── sample_academic_sources.json       # Seed Data for RAG
├── docker-compose.yml     # Multi-container Orchestration
├── .env.example           # Environment Template
└── README.md              # Documentation
```

### Tech Stack
Framework: FastAPI (Python 3.9)<br>
Automation: n8n (Community Edition)<br>
Database: PostgreSQL 15 + pgvector extension<br>
AI/LLM: Google Gemini (Analysis)<br>
Embeddings: all-MiniLM-L6-v2 (Local execution via Sentence-Transformers)<br>
### Setup & Installation
1. **Environment Configuration**
Copy the template file and add your<br> Google Gemini API Key:<br>
cp .env.example .env <br>
Edit .env and set<br>
GEMINI_API_KEY=your_actual_key_here.<br>
**2. Deployment**
Orchestrate all services using Docker Compose:<br>
docker-compose up --build<br>
This starts the Backend (port 8000), n8n (port 5678), and Postgres (port 5432).
**3. n8n Workflow Configuration**
Access n8n at http://localhost:5678.<br>
Import workflows/assignment_analysis_workflow.json.<br>
Create a Postgres Credential:<br>
Host: postgres<br>
Database: academic_helper<br>
User: student<br>
Password: secure_password<br>
Update the AI Analyze node with your Gemini API Key if prompted.
Set the workflow to Active.<br>
### API Endpoints

**POST /auth/register**: Register a new student account.<br>
**POST /auth/login**: Returns JWT. Use credentials student@example.com / password123.<br>
Assignments (Secure - Requires JWT)<br>
**POST /upload**: Accepts PDF/Text <br> assignment. Triggers n8n analysis.<br>
**GET /analysis/{id}**: Retrieves plagiarism scores, sources, and AI feedback.<br>
**GET /sources**: Search academic sources via RAG similarity search.<br>
Internal (Service Communication) <br>
POST /seed-db: Pre-populates the vector database with academic sources.<br>
POST /internal/rag-search: Performs vector similarity search for n8n context.<br>
POST /internal/analyze: Routes processed text to Gemini for structured feedback.<br>
### RAG Implementation Details
Document Ingestion: Academic sources are converted into 384-dimensional vectors using sentence-transformers and stored in a pgvector column.<br>
**Context Retrieval**: During analysis, the system performs an l2_distance similarity search to find the top 3 relevant sources for the submitted assignment.<br>
**Augmented Generation**: Retrieved context is injected into a strict JSON-prompt for the LLM to ensure grounding and minimize hallucinations.<br>
### Security
**JWT Authentication**: All sensitive endpoints require a Bearer Token.<br>
**Role Permissions**: Tokens are issued specifically with student role claims.<br>
**Network Isolation**: Database and internal service routes are contained within the Docker bridge network.<br>
