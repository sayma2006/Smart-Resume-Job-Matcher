# Master Build Prompt — Smart Resume–Job Matcher

You are a senior full-stack Python engineer, NLP engineer, product designer, and hackathon mentor. Upgrade the existing project in-place at:

`D:\ProjectS\Smart-Resume-Job-Matcher`

The project already contains a Flask backend, `src/` modules, a JSON skill catalogue, HTML/CSS/JavaScript frontend, tests, and a README. **Inspect the actual existing files before changing anything.** Preserve working functionality and avoid replacing the project with a disconnected demo.

## Non-negotiable delivery rules

1. Implement the complete working solution, not a tutorial or a sequence of tiny patches.
2. Provide complete final contents for every file you create or modify. Do not say “add this below”, “change these few lines”, or leave TODO placeholders for core features.
3. Keep the existing `.git/` and `venv/` folders. Do not delete user data, Git history, or unrelated files. Create a timestamped backup of changed source files before replacement.
4. Use Windows PowerShell commands and the exact project path above. Commands must be copy-pasteable; distinguish commands from terminal output.
5. Keep the default application runnable without paid APIs or API keys. Optional heavy features must degrade gracefully.
6. Do not claim accuracy, ATS certification, hiring probability, or model performance without a labelled evaluation dataset and measured results.
7. Use safe file handling, validate uploads, do not persist uploaded resumes, and never log resume contents or personal data.
8. After implementation, run tests and report exactly what passed, what failed, and what was not tested. Never claim a test passed unless it was run.

## Product goal

Build a polished, explainable, privacy-conscious resume-to-job-description decision-support tool. A user uploads a PDF resume and pastes one job description. The app extracts resume text, identifies skills, compares experience/education and semantic meaning, explains the result, prioritizes gaps, and gives a realistic learning plan. The score is an estimate for career planning, not a hiring decision.

## Backend and analysis requirements

### PDF and input safety
- Flask app with a clear application factory or clean route organization.
- Accept PDF only; enforce a configurable upload limit (default 5 MB), validate the actual PDF content, handle encrypted/corrupt/empty PDFs, and return helpful errors.
- Process uploaded PDF streams in memory; do not save them to `data/uploads`.
- Detect image-only/scanned PDFs. Add optional OCR support through `pytesseract` + `pdf2image`, but make it optional and document the separate Tesseract/Poppler installation. If OCR is unavailable, return a clear message and keep normal PDFs working.
- Validate job description length and handle empty, huge, malformed, and non-English text gracefully. Avoid crashing on empty vocabulary in TF-IDF.

### Skill ontology and extraction
- Use `data/skills.json` as a structured skill ontology with canonical skill names, aliases/synonyms, categories, importance weights, estimated learning hours, and reputable free resource links.
- Normalize aliases (for example `js`/`JavaScript`/`ES6`, `ML`/`machine learning`, `cpp`/`C++`) to canonical skills.
- Use robust token boundaries so `java` does not match `javascript`, and technical names such as `C++`, `C#`, `Node.js`, `CI/CD`, and `.NET` are handled correctly.
- Separate required skills from preferred/nice-to-have skills. Parse headings and inline phrases; required skills must contribute more than preferred skills. Do not silently treat every line as required.
- Return explainable evidence snippets from the resume for each matched skill. Escape content safely in the UI; never inject resume/JD text as raw HTML.
- Make the skill catalogue easy to extend and validate its schema.

### NLP and scoring
- Use Sentence Transformers `all-MiniLM-L6-v2` as the preferred semantic model, with lazy loading and CPU support. Keep TF-IDF as a transparent fallback if the package/model is unavailable or inference fails.
- Show which semantic method was actually used. Do not mislabel TF-IDF as embeddings.
- Use a hybrid score with visible components: weighted skill coverage, semantic fit, experience fit, and education fit when those requirements can be detected. Normalize active weights so they sum to 100%.
- Keep scoring weights and calibration in one documented configuration. Do not pretend the score is a probability of getting hired.
- Extract years of experience and degree level heuristically, explain that these detections can be imperfect, and do not penalize a candidate when the job description does not state a requirement.
- Add tests for aliases, false partial matches, required/preferred parsing, empty inputs, scoring bounds, missing experience/education, and fallback similarity.

### Recommendations and explainability
- Return matched skills, missing skills, priority, category, evidence, learning time, resource URL, and estimated score contribution.
- Rank skill gaps by their estimated contribution to the skill component. Clearly label score impact as an illustrative mathematical estimate, not a guaranteed score increase.
- Add resume-quality checks: common section headings, measurable outcomes in bullets, contact/profile links, and basic ATS-friendly text structure. Call these heuristic checks, not a certified ATS score.
- Include a concise disclaimer and warnings in API results.

### API and reports
- Provide both the browser form route and a documented JSON endpoint such as `POST /api/analyze`.
- Document request fields, response schema, status codes, upload limits, and example response in README/API docs.
- Generate a downloadable PDF report containing overall score, component breakdown, matched skills/evidence, skill gaps, resources, warnings, and limitations.
- Add safe error handling and useful server logs without exposing uploaded content.

### Validation and evaluation
- Add a small evaluation utility and a documented CSV format for 20–30 anonymized resume/JD pairs with human labels (`good`, `partial`, `poor`).
- Compare human labels against score bands and, where possible, report correlation or classification metrics. Do not fabricate sample outcomes or claim improvement without actual labelled data.
- Include a comparison utility for TF-IDF-only versus embedding/hybrid scoring if feasible. Make clear that evaluation depends on the user's real labelled examples.

### Optional enhancements
- Add a multi-job comparison mode: one resume, multiple job descriptions, ranked results, with clear per-job score breakdowns. Keep the single-job flow simple and fully functional.
- Optional LLM feedback may be added only behind an environment variable and a documented provider/API key. The app must work without it. Never send resume data to an external API without an explicit user action and a clear privacy notice.
- Docker support and SQLite analysis history are optional; if added, history must be opt-in, explain what is stored, and provide deletion controls. Do not store resume files.

## Frontend design requirements — animated, dynamic, premium

Build a professional career-tech dashboard, not a generic AI-looking landing page. Visual direction: deep navy/charcoal, warm orange accents, restrained teal/green for positive matches, muted red for gaps, clean white/light surfaces, excellent typography and whitespace. Avoid excessive gradients, neon, glassmorphism overload, and oversized decorative graphics.

Use responsive HTML/CSS/vanilla JavaScript (or preserve the existing stack). Chart.js is acceptable via a pinned CDN or local dependency. The interface must work on desktop and mobile.

Required interactions:
- Drag-and-drop PDF upload plus browse button, file name, file size/type validation, and clear/reset action.
- Job description textarea with live character count.
- Analyze button with disabled state and a polished animated loading overlay. Show meaningful analysis stages (extracting, parsing skills, semantic comparison, preparing report) without pretending the backend exposes real progress; label these as visual stages if simulated.
- Subtle entrance animations for cards and result sections, animated score count-up, animated circular compatibility gauge, animated score-breakdown chart, and smooth progress bar for the what-if simulator.
- Respect `prefers-reduced-motion`; animations must not make the interface inaccessible.
- Dark/light mode toggle with preference persistence.
- Matched skills in green and missing skills in red/amber; required/preferred labels must be distinguishable.
- Expandable evidence details showing why a skill was counted.
- Skill-gap roadmap with resource links and estimated learning time.
- What-if simulator: selecting missing skills updates an explicitly illustrative projected score; do not change the real analysis result.
- Resume quality suggestions, experience/education comparison, warnings, and PDF report download.
- Empty, loading, success, and error states; accessible labels, keyboard support, focus styles, and semantic HTML.
- Avoid rendering user-provided text with `innerHTML`; use safe DOM text APIs.

## Repository polish
- Write a strong README with one-line pitch, features, screenshots/GIF placeholder instructions, architecture diagram (Mermaid), tech stack, setup, run/test commands, scoring formula, API docs, privacy, limitations, evaluation instructions, and deployment guide.
- Add LICENSE and `.env.example` if missing. Ensure `.gitignore` excludes venv, caches, environment secrets, uploaded files, and local evaluation data where appropriate.
- Provide GitHub repository description and topic suggestions (`flask`, `nlp`, `resume-parser`, `sentence-transformers`, `scikit-learn`, `career-tools`, `python`). Do not claim to have edited GitHub settings unless you actually have access and performed it.
- Add a sensible commit plan with meaningful commit messages; do not create fake commits.

## Deployment
- Provide a Render or Railway deployment configuration and production server dependency (for example Gunicorn). Keep local Windows development instructions separate from Linux hosting instructions.
- Configure debug mode off in production, environment-based secret/config values, and upload limits.
- Clearly list any OCR/system packages needed on the host. Do not claim deployment is complete until a live URL has been tested.

## Expected final response

After implementation, provide:
1. A concise feature checklist of what is actually implemented.
2. The exact final project tree.
3. Complete final file contents or a single complete ZIP archive with every required file.
4. Exact PowerShell commands for backup, branch creation, dependency installation, tests, and running the app.
5. A short manual test checklist.
6. Known limitations and features that remain optional/not implemented.
7. A polished demo script and honest hackathon pitch.

Start by inspecting the current project files and tests. Then implement the complete coherent version. Do not ask me to paste files that already exist in the project folder.
