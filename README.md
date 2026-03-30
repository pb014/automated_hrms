# AI-Powered Human Resource Management System (HRMS)

A full-stack HRMS where AI is woven into core HR workflows — from recruitment to performance reviews to policy Q&A. Built as an internship assessment project.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, Pydantic
- **Frontend:** React (Vite), TailwindCSS v4, Axios, React Router
- **AI/LLM:** Google Gemini API (gemini-3.0-flash-preview, can change this according to limits)
- **RAG:** sentence-transformers (all-MiniLM-L6-v2) + FAISS for document-grounded chatbot

## Features

- **Employee Management** — CRUD, search, CSV export, AI-generated professional bios, duplicate/incomplete profile detection
- **Recruitment & ATS** — Job postings, resume PDF upload, AI resume scoring (match %, strengths, gaps, interview questions), hiring pipeline with stage management
- **Leave & Attendance** — Leave requests with balance tracking, manager approvals, attendance marking, AI-powered unusual leave pattern detection and team capacity risk analysis
- **Performance Reviews** — Review cycles, self-assessment + manager ratings (5 parameters), AI-generated balanced summaries with mismatch flags and development actions
- **Onboarding Assistant** — Role-based checklists with progress tracking, policy PDF upload, RAG-powered chatbot that answers only from uploaded documents, frequently asked questions tracking
- **HR Analytics** — Headcount by department, attrition rate, average tenure, open vs filled positions, leave utilisation, AI-generated monthly HR summary

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- mamba/conda (or pip)
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Backend
```bash
cd server
mamba env create -f environment.yml
mamba activate hrms
# Or with pip: pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run the server
uvicorn main:app --reload
```

### Frontend
```bash
cd client
npm install
npm run dev
```

### Environment Variables
Create `.env` in the server folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Create `.env` in the client folder:
```
VITE_API_URL=your_frontend_URL
```

## Project Structure
```
hrms/
├── server/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py           # SQLite + SQLAlchemy setup
│   ├── models/               # 13 database table definitions
│   ├── schemas/              # Pydantic request/response validation
│   ├── routers/              # 6 route modules (one per feature)
│   └── services/             # Gemini AI service + RAG service
├── client/
│   └── src/
│       ├── api.js            # All API calls
│       ├── components/       # Layout, StatsCard
│       └── pages/            # 6 page components
```
