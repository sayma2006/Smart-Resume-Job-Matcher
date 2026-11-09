# Smart Resume–Job Matcher

An explainable, privacy-conscious web application that analyzes a resume against a job description. Upload a text-based PDF, provide a job description, and receive a compatibility estimate, matched skills, skill gaps, and a personalized learning roadmap.

> **Important:** The compatibility score is a decision-support indicator. It is not a hiring probability, ATS certification, or prediction of interview selection. The scoring weights and similarity normalization have not been validated against a representative human-labelled dataset.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Optional Enhancements](#optional-enhancements)
- [Running Tests](#running-tests)
- [Scoring Methodology](#scoring-methodology)
- [API Documentation](#api-documentation)
- [Privacy and Security](#privacy-and-security)
- [Evaluation](#evaluation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

## Features

- **Resume analysis:** Extracts text from PDF resumes directly from an in-memory upload stream.
- **Privacy-conscious processing:** Uploaded resumes are not saved to disk.
- **Skill extraction:** Identifies skills using a catalogue of 158 canonical entries with aliases, categories, importance weights, and learning resources. The catalogue spans programming, web, data, AI/ML, mobile, cybersecurity, cloud, testing, DevOps, databases, and more.
- **Boundary-aware detection:** Distinguishes similar skill names such as Java and JavaScript, C and C++, C#, Node.js, CI/CD, and .NET.
- **Requirement analysis:** Identifies required and preferred skills in job descriptions.
- **Weighted skill matching:** Calculates skill coverage based on skill importance and requirement priority.
- **Semantic similarity:** Uses local Sentence Transformers when the optional package and model are available, with TF-IDF as a fallback.
- **Experience and education analysis:** Performs optional comparisons when detectable requirements are present.
- **Explainable results:** Displays matched skills, supporting evidence, developing skills, and missing skills.
- **Proficiency classification:** Classifies resume skills as demonstrated, foundational, or currently learning.
- **Fresher-aware analysis:** Handles entry-level roles and upper-bound-only experience ranges such as 0–1 years.
- **Learning roadmap:** Recommends prioritized skill improvements.
- **What-if simulator:** Illustrates how adding skills could affect the estimated compatibility score.
- **Resume quality suggestions:** Provides recommendations for improving resume structure.
- **Visual dashboard:** Includes score breakdowns, a category-level skill coverage radar chart, and an animated results presentation.
- **Theme and interaction polish:** Supports dark/light theme switching, responsive styling, and a score celebration animation for compatibility scores of 75% or higher.
- **PDF report:** Generates a downloadable analysis report.
- **REST API:** Supports resume analysis through JSON endpoints.
- **Input validation:** Includes PDF validation, upload-size restrictions, and a 50-page limit.
- **Automated testing:** Includes Pytest tests for core functionality and application routes.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming language | Python |
| Backend framework | Flask |
| PDF processing | pypdf |
| NLP and text processing | scikit-learn, NumPy |
| Semantic similarity | Sentence Transformers (optional) |
| Frontend | HTML5, CSS3, JavaScript |
| Data visualization | Chart.js with canvas-based fallbacks |
| PDF report generation | ReportLab |
| Testing | Pytest |
| Deployment starter | Render, Gunicorn |

Sentence Transformers is an optional local embedding enhancement. The application does not require a paid external AI API.

## Getting Started

### Prerequisites

- Python installed on your Windows system.
- Git (optional, for cloning the repository).
- PowerShell.
- A text-based PDF resume for testing.

### 1. Clone the repository

```powershell
git clone https://github.com/sayma2006/Smart-Resume-Job-Matcher.git
```

### 2. Navigate to the project directory

```powershell
cd Smart-Resume-Job-Matcher
```

If you have already downloaded the project, navigate to its existing folder instead.

### 3. Create a virtual environment

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run the following command in the current PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Upgrade pip and install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Run the application

```powershell
python app.py
```

Open the following address in your browser:

**http://127.0.0.1:5000**

The application should now be available locally.

## Optional Enhancements

### Semantic Embeddings

The default installation uses TF-IDF similarity and does not require downloading an embedding model.

To enable the optional Sentence Transformers enhancement:

```powershell
python -m pip install -r requirements-ml.txt
```

The first model use may download the `all-MiniLM-L6-v2` model files and take additional time.

If model loading fails, the application falls back to TF-IDF.

### OCR Support for Scanned PDFs

The default application expects selectable text in uploaded PDFs.

For scanned PDFs, install the optional OCR dependencies:

```powershell
python -m pip install -r requirements-ocr.txt
```

You must also install the following Windows applications separately:

- Tesseract OCR
- Poppler

Configure OCR in the current PowerShell session:

```powershell
$env:OCR_ENABLED = "1"
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
python app.py
```

Ensure Poppler's `bin` directory is available in your system `PATH`.

If OCR dependencies or external applications are unavailable, the application provides an error message while normal text-based PDF analysis remains available.

## Running Tests

The project includes automated tests for the scoring engine, skill extraction, PDF processing, API validation, and report generation.

Install the base dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the test suite:

```powershell
python -m pytest -q
```

The regression suite covers:

- Skill aliases and token boundaries.
- Required and preferred skill extraction.
- Demonstrated, foundational, and currently learning proficiency.
- Fresher eligibility and experience parsing.
- Score bounds and optional scoring components.
- PDF validation and error handling.
- API request validation.
- PDF report generation.

## Scoring Methodology

The application combines multiple components to estimate resume-to-job compatibility.

| Component | Nominal Weight |
|---|---:|
| Skill coverage | 60% |
| Semantic similarity | 30% |
| Experience comparison | 10% |
| Education comparison | Additional 5% when applicable |

Only applicable components are included in the final calculation. Their active weights are normalized to sum to 100%.

### Skill Coverage

Skill coverage is calculated using the skill catalogue's importance values and the priority assigned to job requirements.

- Required skills receive higher priority.
- Preferred skills receive a lower priority multiplier.
- Demonstrated skills receive full credit.
- Foundational skills receive partial credit.
- Skills explicitly described as currently learning receive no demonstrated-skill credit but are displayed separately.

### Semantic Similarity

The application compares resume content and job-description text using semantic similarity when the optional embedding model is available. Otherwise, it uses TF-IDF as a fallback.

The semantic score uses heuristic normalization and is not a calibrated probability.

### Experience and Education

Experience and education comparisons are included when the application detects relevant requirements in the job description.

These extraction processes are heuristic. Some resume formats and job-description expressions may not be recognized correctly.

**Recommendation:** Review matched-skill evidence, missing skills, and warnings alongside the overall score instead of relying on the score alone.

## API Documentation

The application provides two resume-analysis endpoints:

- `POST /api/analyze`
- `POST /analyze`
- `POST /download-report` (returns a generated PDF report)

Both endpoints accept `multipart/form-data`.

### Request Parameters

| Field | Type | Description |
|---|---|---|
| `resume` | PDF file | Resume document to analyze |
| `job_description` | Text | Job description (30–20,000 characters) |

### Example API Request

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=Python Developer. Required: Python, Flask, SQL."
```

### Response Information

The JSON response contains:

| Field | Description |
|---|---|
| `overall` | Overall compatibility estimate |
| `breakdown` | Individual scoring components |
| `weights_used` | Active normalized scoring weights |
| `method` | Similarity method used |
| `matched` | Matched skills and supporting evidence |
| `developing` | Foundational or currently learning skills |
| `missing` | Skills not demonstrated in the resume |
| `years` | Experience comparison information |
| `education` | Education comparison information |
| `resume_quality` | Resume structure suggestions |
| `warnings` | Analysis warnings |
| `disclaimer` | Score interpretation disclaimer |

Matched skill items include proficiency, credit, and evidence information. Skill-gap items may include statuses such as `In progress`, `Foundational`, or `Not detected`.

### Health Check

The application also provides:

```http
GET /health
```

This endpoint can be used to check application health.

## Privacy and Security

Privacy-conscious processing is an important design consideration.

- Resume PDFs are processed from an in-memory stream.
- Uploaded resumes are not written to the `data/uploads` directory.
- Resume text and job-description contents are not logged by the application.
- Maximum request size is configurable through `MAX_CONTENT_LENGTH_MB` (default: 5 MB).
- Job-description length is limited to 20,000 characters.
- Personal resumes, `.env` files, API keys, and private evaluation datasets should never be committed to Git.
- The application is intended as a decision-support tool, not as the sole basis for employment decisions.

## Evaluation

The `evaluation/evaluation_template.csv` file contains the required column headers and one instructional placeholder row. Replace that placeholder with your own anonymized, human-reviewed example pairs before running an evaluation; it is not a validated benchmark dataset.

To evaluate the scoring approach, create an anonymized CSV containing the following columns:

```csv
resume_text,job_description,label
```

Use these labels:

- `poor`
- `partial`
- `good`

Install the evaluation dependencies:

```powershell
python -m pip install -r requirements-evaluation.txt
```

Run the evaluation script:

```powershell
python evaluation/evaluate.py evaluation/your_labelled_pairs.csv
```

Use at least 20–30 independently reviewed pairs as an initial evaluation set.

Spearman correlation can provide a basic ranking assessment, but it does not establish accuracy, fairness, or real-world hiring performance.

Keep real resumes and personally identifiable information private. Do not publish private resume text in the evaluation dataset.

## Deployment

The repository includes:

- `render.yaml`
- `requirements-prod.txt`

These files provide a starter configuration for deploying the Flask application on Render.

The production start command is:

```bash
gunicorn app:app
```

`FLASK_DEBUG` defaults to off.

### Deployment Verification

A deployment should only be considered verified after testing:

1. The live application URL.
2. Resume PDF upload.
3. Job-description submission.
4. Analysis result generation.
5. PDF report download.
6. Error handling for invalid and oversized uploads.

The presence of deployment configuration files does not mean that the application is already deployed or verified.

## Project Structure

```text
Smart-Resume-Job-Matcher/
│
├── app.py
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
│
├── data/
│   ├── skills.json
│   ├── example_job_description.txt
│   └── uploads/
│       └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── preprocess.py
│   ├── skill_extractor.py
│   ├── similarity.py
│   ├── scorer.py
│   └── recommender.py
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── test_app.py
│   ├── test_pdf_parser.py
│   ├── test_scorer.py
│   └── test_skills.py
│
├── evaluation/
│   ├── evaluate.py
│   └── evaluation_template.csv
│
├── requirements.txt
├── requirements-ml.txt
├── requirements-ocr.txt
├── requirements-evaluation.txt
├── requirements-prod.txt
├── pytest.ini
└── render.yaml
```

## GitHub Repository

**Repository:** https://github.com/sayma2006/Smart-Resume-Job-Matcher

**Suggested Description:**

Explainable resume-to-job matching with NLP similarity, skill-gap analysis, and a practical learning roadmap.

**Suggested Topics:**

`flask` · `python` · `nlp` · `resume-parser` · `sentence-transformers` · `scikit-learn` · `career-tools` · `job-matching`

---

*Developed as a project exploring Python-based web development, natural language processing, resume analysis, and explainable skill matching.*