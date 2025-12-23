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
🛠️ Tech Stack
Framework: FastAPI (Python 3.9)
Automation: n8n (Community Edition)
Database: PostgreSQL 15 + pgvector extension
AI/LLM: Google Gemini (Analysis)
Embeddings: all-MiniLM-L6-v2 (Local execution via Sentence-Transformers)
🚀 Setup & Installation
1. Environment Configuration
Copy the template file and add your Google Gemini API Key:
code
Bash
cp .env.example .env
Edit .env and set GEMINI_API_KEY=your_actual_key_here.
2. Deployment
Orchestrate all services using Docker Compose:
code
Bash
docker-compose up --build
This starts the Backend (port 8000), n8n (port 5678), and Postgres (port 5432).
3. n8n Workflow Configuration
Access n8n at http://localhost:5678.
Import workflows/assignment_analysis_workflow.json.
Create a Postgres Credential:
Host: postgres
Database: academic_helper
User: student
Password: secure_password
Update the AI Analyze node with your Gemini API Key if prompted.
Set the workflow to Active.
🔌 API Endpoints
Authentication
POST /auth/register: Register a new student account.
POST /auth/login: Returns JWT. Use credentials student@example.com / password123.
Assignments (Secure - Requires JWT)
POST /upload: Accepts PDF/Text assignment. Triggers n8n analysis.
GET /analysis/{id}: Retrieves plagiarism scores, sources, and AI feedback.
GET /sources: Search academic sources via RAG similarity search.
Internal (Service Communication)
POST /seed-db: Pre-populates the vector database with academic sources.
POST /internal/rag-search: Performs vector similarity search for n8n context.
POST /internal/analyze: Routes processed text to Gemini for structured feedback.
🧠 RAG Implementation Details
Document Ingestion: Academic sources are converted into 384-dimensional vectors using sentence-transformers and stored in a pgvector column.
Context Retrieval: During analysis, the system performs an l2_distance similarity search to find the top 3 relevant sources for the submitted assignment.
Augmented Generation: Retrieved context is injected into a strict JSON-prompt for the LLM to ensure grounding and minimize hallucinations.
🔒 Security
JWT Authentication: All sensitive endpoints require a Bearer Token.
Role Permissions: Tokens are issued specifically with student role claims.
Network Isolation: Database and internal service routes are contained within the Docker bridge network.
