# Smart Resume–Job Matcher

A privacy-conscious, explainable resume-to-job-description analysis web app. Upload a text-based PDF, paste a job description, and review a heuristic compatibility estimate, skill evidence, skill gaps, and a learning roadmap.

> **Important:** The score is a decision-support indicator, not a hiring probability, an ATS certification, or a prediction of interview selection. The weights and similarity normalization have not been validated against a representative human-labelled dataset.

## Features

- Flask web application with a responsive dashboard and animated result presentation.
- PDF text extraction directly from the uploaded in-memory stream; uploaded resumes are not saved to disk.
- 5 MB default request limit, PDF parsing validation, encrypted/scanned-PDF guidance, and 50-page limit.
- Skill catalogue with canonical names, aliases, categories, importance weights, learning-time estimates, and learning links.
- Boundary-aware skill detection for names such as Java/JavaScript, C++, C#, Node.js, CI/CD, and .NET.
- Required/preferred skill parsing and weighted skill coverage.
- Semantic similarity using local Sentence Transformers when the optional package/model is installed; TF-IDF fallback otherwise.
- Optional experience and education comparisons when the job description contains detectable requirements.
- Explainable matched-skill evidence and prioritized gap recommendations.
- Resume skill proficiency classification: demonstrated (full credit), foundational (partial credit), and currently learning (no demonstrated-skill credit, shown separately).
- Fresher-aware experience parsing: entry-level roles, freshers, and upper-bound-only ranges such as 0–1 years are not treated as minimum experience requirements.
- Illustrative what-if simulator, resume-structure suggestions, score breakdown, and downloadable PDF report.
- JSON API at `POST /api/analyze` and `POST /analyze`.
- Health endpoint at `GET /health`.
- Pytest unit and route tests.
- Render deployment starter configuration.

## Technology stack

Python, Flask, pypdf, scikit-learn, NumPy, ReportLab, HTML, CSS, JavaScript, and Chart.js. Sentence Transformers is an optional local embedding enhancement. If Chart.js cannot load from its CDN, the dashboard uses canvas-based chart fallbacks.

## Windows setup

Open PowerShell:

```powershell
cd "D:\ProjectS\Smart-Resume-Job-Matcher-Final"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once in the current PowerShell window and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Run the application

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

### Optional semantic embeddings

The default install works without a model download and uses TF-IDF. To enable the local `all-MiniLM-L6-v2` Sentence Transformers model:

```powershell
pip install -r requirements-ml.txt
```

The first model use may download model files and can take longer. If model loading fails, the application falls back to TF-IDF. The app does not call a paid external AI API.

### Optional OCR for scanned PDFs

The default build expects selectable text in the PDF. OCR requires additional Python packages and separately installed Windows applications:

```powershell
pip install -r requirements-ocr.txt
```

Install Tesseract OCR and Poppler separately. Then set the Tesseract executable path and enable OCR in the same PowerShell session:

```powershell
$env:OCR_ENABLED = "1"
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
python app.py
```

Ensure Poppler's `bin` directory is available on `PATH`. If OCR dependencies or system applications are missing, the app returns a readable error and normal text-based PDF analysis remains available.

## Tests

Install the base requirements, then run:

```powershell
pytest -q
```

The regression suite covers skill aliases and token boundaries, required/preferred parsing, demonstrated/foundational/learning proficiency, fresher eligibility, score bounds, optional experience/education behavior, PDF error handling, API validation, and PDF report generation.

## Scoring approach

The scorer combines:
- Skill coverage: nominal weight 60%.
- Semantic similarity: nominal weight 30%.
- Experience comparison: nominal weight 10%, included only when a years-of-experience requirement is detected.
- Education comparison: included as an additional 5% component when a minimum education requirement is detected.

Only applicable components are included, and the active weights are normalized to sum to 100%. Skill coverage uses the catalogue importance multiplied by the required/preferred priority. Preferred requirements receive a lower priority multiplier. Demonstrated resume skills receive full credit; foundational mentions (for example, “basic React”) receive partial credit; skills explicitly described as currently learning are shown separately and receive no demonstrated-skill credit. A skill can still be recommended as a gap while it is in progress.

The semantic score uses a heuristic normalization and should not be interpreted as calibrated probability. Experience and education extraction are also heuristic; resumes and job descriptions may express these details in ways the parser does not recognize. Review the evidence and warnings rather than relying on the overall score alone.

## API

`POST /api/analyze` accepts `multipart/form-data`:

| Field | Description |
|---|---|
| `resume` | PDF file |
| `job_description` | Job description text (30–20,000 characters) |

The JSON response contains `overall`, `breakdown`, `weights_used`, `method`, `matched`, `developing`, `missing`, `years`, `education`, `resume_quality`, `warnings`, and `disclaimer`. Matched skill items include `proficiency`, `credit`, and evidence; gap items include a status such as `In progress`, `Foundational`, or `Not detected`.

## Privacy and security

- Resume PDFs are parsed from memory and are not written to `data/uploads`.
- Do not add personal resumes, `.env` files, API keys, or private evaluation datasets to Git.
- The app does not log resume text or job-description contents.
- Uploaded request size is limited by `MAX_CONTENT_LENGTH_MB` (default: 5).
- Job description length is limited to 20,000 characters.
- This is a local decision-support tool; do not use it as the sole basis for employment decisions.

## Evaluation

The `evaluation/evaluation_template.csv` file contains only column headers. It does not contain fabricated labelled examples.

Create your own anonymized CSV with columns `resume_text,job_description,label` and labels `poor`, `partial`, or `good`. Keep real resumes and personally identifiable information private. Then install the evaluation dependency and run:

```powershell
pip install -r requirements-evaluation.txt
python evaluation/evaluate.py evaluation/your_labelled_pairs.csv
```

Use at least 20–30 independently reviewed pairs as an initial evaluation set. Spearman correlation is a basic ranking check, not proof of accuracy or fairness. Document the review process and do not publish private resume text.

## Deployment (Render)

A starter `render.yaml` and `requirements-prod.txt` are included. Connect the repository to Render and deploy the web service. The production start command is `gunicorn app:app`; `FLASK_DEBUG` defaults to off. A deployment is not considered verified until the live URL, upload flow, and report download have been tested.

## Project structure

```text
Smart-Resume-Job-Matcher/
├── app.py
├── data/
│   ├── skills.json
│   └── example_job_description.txt
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── preprocess.py
│   ├── skill_extractor.py
│   ├── similarity.py
│   └── scorer.py
│   └── recommender.py
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── tests/
├── evaluation/
├── requirements.txt
├── requirements-ml.txt
├── requirements-ocr.txt
├── requirements-evaluation.txt
└── README.md
```

## Suggested GitHub metadata

**Description:** Explainable resume-to-job matching with NLP similarity, skill-gap analysis, and a practical learning roadmap.

**Topics:** `flask`, `python`, `nlp`, `resume-parser`, `sentence-transformers`, `scikit-learn`, `career-tools`, `job-matching`.
