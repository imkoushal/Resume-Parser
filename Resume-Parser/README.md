# 📄 Resume Intelligence Platform

A Python-based REST API for parsing resumes, extracting skills, and matching candidates against job descriptions — built with FastAPI.

---

## 🚀 Features

- 📂 **Multi-format Support** — Parse resumes in PDF and DOCX formats
- 🔍 **Skill Extraction** — Identify technical and soft skills using a curated skills database
- 🤝 **JD Matching** — Compare resumes against job descriptions using TF-IDF vectorization and cosine similarity
- 📊 **Gap Analysis** — Highlight missing skills between a resume and a job description
- 🧹 **Text Cleaning** — Normalize and clean extracted text for better accuracy
- ⚡ **REST API** — Clean, scalable FastAPI backend with structured JSON responses

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| spaCy | NLP pipeline & entity recognition |
| pdfplumber | PDF text extraction |
| python-docx | DOCX file parsing |
| scikit-learn | TF-IDF vectorization & cosine similarity |

---

## 📁 Project Structure

```
resume-intelligence-platform/
│
├── app.py                         # FastAPI entry point
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── skills_list.txt            # Curated skills database
│
└── src/
    ├── __init__.py
    │
    ├── core/
    │   ├── __init__.py
    │   └── config.py              # Centralized settings & paths
    │
    ├── routes/
    │   ├── __init__.py
    │   └── resume_routes.py       # API endpoint definitions
    │
    ├── services/
    │   ├── __init__.py
    │   ├── text_extractor.py      # PDF/DOCX text extraction
    │   ├── resume_parser.py       # Resume parsing pipeline
    │   ├── skill_extractor.py     # Skill identification
    │   └── jd_matcher.py          # JD matching & scoring
    │
    ├── models/
    │   ├── __init__.py
    │   └── response_models.py     # Pydantic response schemas
    │
    └── utils/
        └── __init__.py
```

---

## ⚙️ System Requirements

- Python **3.8 or higher**
- pip (Python package manager)
- Internet connection (for initial dependency installation)

---

## 📦 Installation

1. **Download / unzip the project folder**

2. **Open a terminal** and navigate to the project directory:
   ```bash
   cd Resume-Parser
   ```

3. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the spaCy English language model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

---

## ▶️ How to Run

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive API docs (Swagger UI) available at: `http://localhost:8000/docs`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/parse-resume` | Upload resume → full parsed data |
| `POST` | `/extract-skills` | Upload resume → skills list only |
| `POST` | `/match-job-description` | Upload resume + JD → match report |
| `POST` | `/analyze-resume` | Upload resume + optional JD → full analysis |

### Example: Parse a Resume

```bash
curl -X POST -F "file=@resume.pdf" http://localhost:8000/parse-resume
```

### Example: Match Against a Job Description

```bash
curl -X POST \
  -F "file=@resume.pdf" \
  -F "job_description=We need a Python developer with 3+ years experience..." \
  http://localhost:8000/match-job-description
```

---

## 🧩 Module Overview

| Module | Description |
|---|---|
| `app.py` | FastAPI application — creates app, CORS, includes routes |
| `src/core/config.py` | Centralized paths and settings |
| `src/routes/resume_routes.py` | API endpoint definitions |
| `src/services/resume_parser.py` | Orchestrates the full resume parsing pipeline |
| `src/services/jd_matcher.py` | Matches resume against JD using TF-IDF + skill overlap |
| `src/services/skill_extractor.py` | Extracts and categorizes skills from text |
| `src/services/text_extractor.py` | Reads raw text from PDF/DOCX files |
| `src/models/response_models.py` | Pydantic schemas for all API responses |

---

## 🧮 How JD Matching Works

The job description matching uses two complementary strategies:

1. **Skill-set matching (70% weight)** — Extracts known skills from both the resume and the job description using a curated skills list, then computes a coverage score (`matched skills ÷ total JD skills`).

2. **TF-IDF cosine similarity (30% weight)** — Vectorizes the full resume text and JD text using TF-IDF (unigrams + bigrams) and measures lexical overlap via cosine similarity.

The final match score is a weighted blend of both.

---

## ⚠️ Limitations

- **Lexical matching only** — JD matching is based on TF-IDF and keyword overlap. It does not understand meaning or context.
- **Approximate experience calculation** — Years of experience are extracted using regex and may not always be accurate.
- **Skills list dependent** — Skill extraction relies on a curated `skills_list.txt`; unlisted skills may not be detected.

---

## 📖 Academic Usage Note

This project was developed as part of an academic submission. All source code is original and intended for educational purposes.

---

## 📄 License

This project is submitted for academic evaluation. Unauthorized redistribution is not permitted.
