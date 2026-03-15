# 🧠 Resume Intelligence Platform

A full-stack Resume Intelligence Platform with advanced ATS scoring, skill gap detection, resume recommendations, JWT authentication, and MongoDB persistence — powered by FastAPI and Angular.

---

## 🚀 Features

- 📂 **Multi-format Resume Parsing** — Extract structured data from PDF and DOCX files
- 🔍 **Skill Extraction** — Identify technical and soft skills using a curated database
- 🤝 **JD Matching** — Compare resumes against job descriptions with TF-IDF cosine similarity
- 📊 **ATS Scoring** — Calculate ATS compatibility scores (0–100) with keyword, skill coverage, and experience scoring
- � **Skill Gap Detection** — Identify matched and missing skills between resume and job description
- 💡 **Resume Recommendations** — Generate actionable improvement suggestions
- 🔐 **JWT Authentication** — Secure user registration and login
- 💾 **MongoDB Persistence** — Store resumes and analysis results per user
- 📜 **Analysis History** — Track resume improvements over time
- 🎨 **Angular Dashboard** — Full frontend with charts, drag-and-drop upload, and auth flow
- ⚡ **REST API** — Clean, scalable FastAPI backend with structured JSON responses

---

## 🏗️ System Architecture

```
Angular Frontend (port 4200)
       │
       │ /api proxy
       ▼
FastAPI Backend (port 8000)
       │
       ├── Routes → Services → MongoDB
       │
       └── Auth Middleware (JWT)
```

```
Client → [Auth Interceptor] → API Gateway
  → Resume Routes (public)
  → Auth Routes (public)
  → History Routes (protected)
  → Analyze Route (optional auth → persists if logged in)
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core backend language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| MongoDB | Database for users, resumes, and results |
| Motor | Async MongoDB driver |
| spaCy | NLP pipeline & entity recognition |
| pdfplumber | PDF text extraction |
| python-docx | DOCX file parsing |
| scikit-learn | TF-IDF vectorization & cosine similarity |
| python-jose | JWT token creation & validation |
| passlib + bcrypt | Password hashing |
| Angular 19 | Frontend framework |
| Chart.js | Data visualization |

---

## 📁 Project Structure

```
resume-intelligence-platform/
│
├── app.py                              # FastAPI entry point with DB lifecycle
├── requirements.txt
├── README.md
│
├── data/
│   └── skills_list.txt                 # Curated skills database
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                   # Settings, paths, MongoDB URI, JWT config
│   │   ├── database.py                 # Motor async MongoDB client
│   │   └── auth.py                     # JWT creation & auth dependencies
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── resume_routes.py            # Resume parsing & analysis endpoints
│   │   ├── auth_routes.py              # Register, login, me
│   │   └── history_routes.py           # Analysis history & resume retrieval
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── text_extractor.py           # PDF/DOCX text extraction
│   │   ├── resume_parser.py            # Resume parsing pipeline
│   │   ├── skill_extractor.py          # Skill identification
│   │   ├── jd_matcher.py               # JD matching & scoring
│   │   ├── ats_scorer.py               # ATS compatibility scorer (dual mode)
│   │   ├── skill_gap_analyzer.py       # Skill gap detection
│   │   ├── resume_recommender.py       # Resume improvement suggestions
│   │   ├── user_service.py             # User registration & authentication
│   │   └── analysis_service.py         # Persist & retrieve analysis results
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── response_models.py          # Pydantic response schemas
│   │   └── db_models.py                # MongoDB document schemas
│   │
│   └── utils/
│       └── __init__.py
│
└── frontend/                           # Angular 19 dashboard
    ├── proxy.conf.json
    └── src/app/
        ├── core/                       # Services, interceptors, guards
        ├── features/                   # Auth, upload, dashboard, history
        └── shared/                     # Navbar
```

---

## ⚙️ System Requirements

- Python **3.10 or higher**
- Node.js **18+** and npm (for Angular frontend)
- MongoDB running on `localhost:27017`
- pip (Python package manager)

---

## 📦 Installation

### Backend

```bash
cd Resume-Parser

pip install -r requirements.txt

python -m spacy download en_core_web_sm
```

### Frontend

```bash
cd frontend

npm install
```

---

## ▶️ How to Run

### Start MongoDB

Ensure MongoDB is running on `localhost:27017`.

### Start the Backend

```bash
uvicorn app:app --reload
```

Backend available at: `http://localhost:8000`
Swagger docs at: `http://localhost:8000/docs`

### Start the Frontend

```bash
cd frontend
ng serve
```

Frontend available at: `http://localhost:4200`

---

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/parse-resume` | Upload resume → full parsed data |
| `POST` | `/extract-skills` | Upload resume → skills list only |
| `POST` | `/match-job-description` | Upload resume + JD → match report |

### Analysis Endpoint (optional auth)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze-resume` | Full analysis pipeline (persists results if authenticated) |

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create new user account → JWT token |
| `POST` | `/auth/login` | Authenticate user → JWT token |
| `GET` | `/auth/me` | Get current user info (requires auth) |

### History Endpoints (require authentication)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analysis/history` | List past analysis results |
| `GET` | `/resumes` | List uploaded resumes |
| `GET` | `/resumes/{resume_id}` | Get specific resume by ID |

---

## 📋 Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123","full_name":"John Doe"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

### Analyze a Resume (with auth)

```bash
curl -X POST http://localhost:8000/analyze-resume \
  -H "Authorization: Bearer <token>" \
  -F "file=@resume.pdf" \
  -F "job_description=We need a Python developer with 3+ years experience..."
```

### View Analysis History

```bash
curl http://localhost:8000/analysis/history \
  -H "Authorization: Bearer <token>"
```

---

## 🧩 Module Overview

| Module | Description |
|---|---|
| `app.py` | FastAPI app — CORS, DB lifecycle, router registration |
| `src/core/config.py` | Centralized settings — paths, MongoDB URI, JWT config |
| `src/core/database.py` | Motor async MongoDB client with lifecycle hooks |
| `src/core/auth.py` | JWT creation, required/optional auth dependencies |
| `src/routes/resume_routes.py` | Resume parsing & analysis endpoints |
| `src/routes/auth_routes.py` | Register, login, me endpoints |
| `src/routes/history_routes.py` | History & resume retrieval endpoints |
| `src/services/resume_parser.py` | Resume parsing pipeline |
| `src/services/jd_matcher.py` | JD matching with TF-IDF + skill overlap |
| `src/services/skill_extractor.py` | Skill extraction from text |
| `src/services/text_extractor.py` | PDF/DOCX text extraction |
| `src/services/ats_scorer.py` | ATS scoring (resume-only & resume+JD modes) |
| `src/services/skill_gap_analyzer.py` | Skill gap detection between resume and JD |
| `src/services/resume_recommender.py` | Improvement suggestion generation |
| `src/services/user_service.py` | User creation & authentication (bcrypt) |
| `src/services/analysis_service.py` | Persist & retrieve analysis results |
| `src/models/response_models.py` | Pydantic response schemas |
| `src/models/db_models.py` | MongoDB document factory functions |

---

## 🧮 How ATS Scoring Works

The ATS scorer operates in **two modes**:

### Resume-only Mode

| Component | Weight | Method |
|---|---|---|
| Keyword quality | 40% | Content quality heuristic (word count, vocabulary richness) |
| Skill density | 40% | Ratio of detected skills to total word count |
| Experience signals | 20% | Action verbs + measurable achievements |

### Resume + JD Mode

| Component | Weight | Method |
|---|---|---|
| Keyword match | 40% | TF-IDF cosine similarity between resume and JD |
| Skill coverage | 40% | Percentage of JD skills found in resume |
| Experience signals | 20% | Action verbs + measurable achievements |

---

## ⚠️ Limitations

- **Lexical matching only** — JD matching is based on TF-IDF and keyword overlap; no semantic understanding
- **Approximate experience calculation** — Years are extracted via regex and may be imprecise
- **Skills list dependent** — Extraction relies on `skills_list.txt`; unlisted skills may not be detected
- **MongoDB required** — Persistence features require MongoDB running locally

---

## 📖 Academic Usage Note

This project was developed as part of an academic submission. All source code is original and intended for educational purposes.

---

## 📄 License

This project is submitted for academic evaluation. Unauthorized redistribution is not permitted.
