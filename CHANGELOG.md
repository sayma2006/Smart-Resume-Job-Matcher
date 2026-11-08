# Changelog

## Final integration build

- Based the application on the stronger v3 architecture.
- Fixed scanned-PDF handling by importing the environment module and improved PDF validation.
- Added safe, in-memory upload validation and a job-description length limit.
- Added C# and .NET to the skill ontology and expanded boundary tests.
- Added dedicated evaluation dependencies and expanded the test suite.
- Added a chart fallback for environments where the Chart.js CDN is unavailable.
- Added a sample job description from the original project.
- Removed duplicate sample resume PDFs, stale caches, and compiled Python files from the deliverable.


## Matching logic refinement

- Classify resume skill mentions as demonstrated, foundational, or currently learning.
- Award full credit for demonstrated skills, partial credit for foundational knowledge, and no demonstrated-skill credit for in-progress learning.
- Display in-progress skills separately and mark them in the learning roadmap.
- Exclude explicitly learning-only lines from semantic similarity input.
- Avoid experience penalties for fresher/entry-level job descriptions and zero-to-one-year ranges.
- Add regression tests for proficiency classification and fresher eligibility.


## Matching accuracy follow-up

- Carry learning-status cues across PDF line wraps so phrases such as "currently strengthening automated testing" are not misclassified as demonstrated skills.
- Treat a standalone generic word such as "testing" in a document disclaimer as insufficient skill evidence; require a specific testing tool or phrase.
- Classify a library-only scikit-learn mention as foundational exposure rather than full machine-learning proficiency.
- Recognize hyphenated "machine-learning" wording and preserve foundational classification.
- Treat simple two-skill "A or B" job requirements as alternatives, so a demonstrated Flask skill satisfies "Flask or Django" without a separate Django penalty.
- Expose explicit fresher eligibility in the analysis response and display it in the dashboard.
- Add regression coverage for the sample resume's PDF-wrapped learning cues, skill alternatives, and fresher eligibility.
