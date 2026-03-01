# 📄 Resume Parser

A Python-based resume parsing tool that extracts key information from resumes, identifies skills, and matches candidates against job descriptions — all through an interactive Streamlit web interface.

---

## 🚀 Features

- 📂 **Multi-format Support** — Parse resumes in PDF, DOCX, and TXT formats
- 🔍 **Skill Extraction** — Identify technical and soft skills using a curated skills database
- 🤝 **JD Matching** — Compare resumes against job descriptions using TF-IDF vectorization and cosine similarity
- 📊 **Gap Analysis** — Highlight missing skills between a resume and a job description
- 🧹 **Text Cleaning** — Normalize and clean extracted text for better accuracy
- 🌐 **Streamlit UI** — Clean, interactive web interface for uploading resumes and viewing results

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core language |
| Streamlit | Web interface |
| spaCy | NLP pipeline & entity recognition |
| pdfplumber / PyMuPDF | PDF text extraction |
| python-docx | DOCX file parsing |
| scikit-learn | TF-IDF vectorization & cosine similarity |
| pandas / numpy | Data handling |

---

## 📁 Project Structure

```
Resume-Parser/
│
├── app.py                  # Main Streamlit application entry point
├── src/
│   ├── __init__.py         # Package initializer
│   ├── resume_parser.py    # Core resume parsing logic
│   ├── jd_matcher.py       # Job description matching & scoring
│   ├── skill_extractor.py  # Skill identification and extraction
│   └── text_extractor.py   # Raw text extraction from PDF/DOCX/TXT
├── data/
│   └── skills_list.txt     # Curated list of known skills
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
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
streamlit run app/app.py
```

The app will open automatically in your default web browser at `http://localhost:8501`.

---

## 🌐 Deployment

This application is compatible with **Streamlit Community Cloud** for seamless deployment.

**Deployment settings:**

- **Branch:** `main`
- **Main file path:** `app/app.py`

No environment-specific configuration is required.

---

## 🧩 Module Overview

| Module | Description |
|---|---|
| `app.py` | Streamlit application — UI, routing, and user interaction |
| `resume_parser.py` | Orchestrates the full resume parsing pipeline |
| `jd_matcher.py` | Matches resume against job description using TF-IDF cosine similarity + skill overlap |
| `skill_extractor.py` | Extracts and categorizes skills from text |
| `text_extractor.py` | Reads and extracts raw text from PDF/DOCX/TXT files |

---

## 🧮 How JD Matching Works

The job description matching in `jd_matcher.py` uses two complementary strategies:

1. **Skill-set matching (70% weight)** — Extracts known skills from both the resume and the job description using a curated skills list, then computes a coverage score (`matched skills ÷ total JD skills`).

2. **TF-IDF cosine similarity (30% weight)** — Vectorizes the full resume text and JD text using TF-IDF (unigrams + bigrams) and measures lexical overlap via cosine similarity.

The final match score is a weighted blend of both. This is **lexical text matching**, not deep semantic understanding.

---

## ⚠️ Limitations

- **Lexical matching only** — JD matching is based on TF-IDF and keyword overlap. It does not understand meaning or context (no semantic embeddings are used).
- **Approximate experience calculation** — Years of experience are extracted using a regex pattern on the raw text and may not always be accurate.
- **Skills list dependent** — Skill extraction relies on a curated `skills_list.txt`; unlisted or novel skills may not be detected.

---

## 📖 Academic Usage Note

This project was developed as part of an academic submission. All source code is original and intended for educational purposes. The application demonstrates practical use of NLP techniques including named entity recognition, TF-IDF vectorization, and cosine similarity for resume analysis and job description matching.

---

## 🔁 Reproducibility Note

All dependencies are listed in `requirements.txt`. No virtual environment, cache, or compiled files are included in the repository. This project is fully reproducible on any system with **Python 3.8+**.

---

## 📄 License

This project is submitted for academic evaluation. Unauthorized redistribution is not permitted.
