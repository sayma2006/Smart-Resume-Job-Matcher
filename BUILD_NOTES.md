# Build and validation notes

## Matching refinements in this package

- Resume skill mentions are classified as `demonstrated`, `foundational`, or `learning`.
- Demonstrated skills receive full skill credit; foundational mentions receive 50% skill credit; currently-learning mentions receive no demonstrated-skill credit.
- In-progress skills appear separately in the dashboard and are marked `In progress` in the learning roadmap.
- Explicit learning-only lines/sections are excluded from semantic similarity input to prevent them from indirectly increasing semantic fit.
- Fresher/entry-level wording and zero-to-one-year experience ranges are not treated as a minimum experience requirement.
- PDF reports include the in-progress skills and matched-skill proficiency labels.

## Validation performed while preparing this archive

- Python compilation: passed.
- JavaScript syntax check (`node --check static/script.js`): passed.
- Skills, scorer, and PDF parser tests: 22 passed.
- The four Flask route/report tests were not executable in the packaging environment because Flask is not installed in that environment. Flask is declared in `requirements.txt`.

After extracting this archive in the project's existing virtual environment, run:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

The complete suite contains 26 tests, including the four Flask route/report tests.
