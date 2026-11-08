import re
from .preprocess import clean_text
from .recommender import build_recommendations
from .similarity import semantic_similarity
from .skill_extractor import find_job_skills, find_job_skill_alternatives, find_resume_skill_levels, load_skills, remove_learning_content

WEIGHTS = {"skills": 0.60, "semantic": 0.30, "experience": 0.10}
YEARS_PATTERN = re.compile(r"\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", re.I)
YEAR_RANGE_PATTERN = re.compile(r"\b(\d{1,2})\s*(?:-|–|—|to)\s*(\d{1,2})\s*(?:years?|yrs?)\b", re.I)
WORD_YEAR_PATTERN = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:years?|yrs?)\b", re.I)
WORD_NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
FRESHER_LANGUAGE = re.compile(
    r"\b(freshers?|entry[- ]level|no\s+(?:prior\s+)?experience|without\s+experience|up\s+to\s+(?:one|two|three|\d+)\s+(?:years?|yrs?))\b",
    re.I,
)

EDUCATION_LEVELS = [
    ("phd", re.compile(r"\b(ph\.?d|doctorate|doctoral)\b", re.I)),
    ("masters", re.compile(r"\b(master'?s|m\.?tech|m\.?e\.?|m\.?sc|mba|postgraduate)\b", re.I)),
    ("bachelors", re.compile(r"\b(bachelor'?s|b\.?tech|b\.?e\.?|b\.?sc|undergraduate)\b", re.I)),
    ("diploma", re.compile(r"\b(diploma|polytechnic)\b", re.I)),
]
EDU_RANK = {"unknown": 0, "diploma": 1, "bachelors": 2, "masters": 3, "phd": 4}

def _required_years(text):
    """Return the minimum explicit experience requirement, or None if optional."""
    source = text or ""
    # A fresher/entry-level statement or an upper-bound-only range is not a
    # minimum experience requirement and must not penalize a new graduate.
    if FRESHER_LANGUAGE.search(source):
        return None

    range_match = YEAR_RANGE_PATTERN.search(source)
    if range_match:
        minimum = int(range_match.group(1))
        return minimum if 0 < minimum <= 40 else None

    # '0-1 years' is commonly written without a space and is covered above.
    # Do not interpret 'up to 1 year' as a one-year minimum.
    if re.search(r"\bup\s+to\b", source, re.I):
        return None

    values = [int(value) for value in YEARS_PATTERN.findall(source)]
    values.extend(WORD_NUMBERS[value.lower()] for value in WORD_YEAR_PATTERN.findall(source))
    values = [value for value in values if 0 < value <= 40]
    return min(values) if values else None

def _resume_years(text):
    values = [int(value) for value in YEARS_PATTERN.findall(text or "")]
    values = [value for value in values if 0 < value <= 40]
    return max(values) if values else None

def _education_level(text):
    for level, pattern in EDUCATION_LEVELS:
        if pattern.search(text or ""):
            return level
    return "unknown"

def _required_education(text):
    # Detect a stated minimum qualification, not every education mention.
    patterns = [
        ("phd", r"\b(ph\.?d|doctorate|doctoral)\b"),
        ("masters", r"\b(master'?s|m\.?tech|m\.?e\.?|m\.?sc|mba)\b"),
        ("bachelors", r"\b(bachelor'?s|b\.?tech|b\.?e\.?|b\.?sc|undergraduate)\b"),
        ("diploma", r"\b(diploma|polytechnic)\b"),
    ]
    lower = (text or "").lower()
    if not re.search(r"\b(required|minimum|must have|qualification|degree)\b", lower):
        return None
    for level, pattern in patterns:
        if re.search(pattern, lower):
            return level
    return None

def _resume_quality_checks(resume_text):
    text = resume_text or ""
    lower = text.lower()
    checks = []
    sections = {
        "Experience": [r"\bexperience\b", r"\bwork history\b"],
        "Education": [r"\beducation\b", r"\bacademic\b"],
        "Skills": [r"\bskills\b", r"\btechnical skills\b"],
        "Projects": [r"\bprojects?\b"],
    }
    missing_sections = [
        label for label, patterns in sections.items()
        if not any(re.search(pattern, lower) for pattern in patterns)
    ]
    if missing_sections:
        checks.append({
            "type": "section",
            "severity": "medium",
            "message": "Consider adding clearly labelled sections: " + ", ".join(missing_sections) + "."
        })
    bullets = [line.strip() for line in text.splitlines() if re.match(r"^\s*[-•*]", line)]
    if bullets and not any(re.search(r"\b\d+%|\b\d+\+?\s*(users|clients|projects|hours|days|months|years)\b", line, re.I) for line in bullets):
        checks.append({
            "type": "impact",
            "severity": "low",
            "message": "Add measurable outcomes to relevant experience or project bullets where truthful (for example, users served, time saved or accuracy achieved)."
        })
    if not re.search(r"\blinkedin\.com\b", lower):
        checks.append({"type": "profile", "severity": "low", "message": "Add a LinkedIn profile URL if you use LinkedIn."})
    if not re.search(r"\bgithub\.com\b", lower):
        checks.append({"type": "profile", "severity": "low", "message": "Add a GitHub profile URL if you have public projects."})
    return checks

def analyze(resume_text: str, jd_text: str) -> dict:
    # Explicit learning-only content is excluded from semantic similarity so
    # it cannot indirectly inflate the match score either.
    resume_clean = clean_text(remove_learning_content(resume_text))
    jd_clean = clean_text(jd_text)
    catalogue = load_skills()

    resume_skill_levels = find_resume_skill_levels(resume_text)
    jd_skills = find_job_skills(jd_text)

    # A requirement phrased as "Flask or Django" is one alternative, not two
    # independent mandatory skills. Keep the best-supported option; if neither
    # is present, show only the first option as the representative gap.
    for alternatives in find_job_skill_alternatives(jd_text):
        supported = [
            skill for skill in alternatives
            if resume_skill_levels.get(skill, {}).get("level") in {"demonstrated", "foundational"}
        ]
        chosen = supported[0] if supported else alternatives[0]
        for skill in alternatives:
            if skill != chosen:
                jd_skills.pop(skill, None)

    # Demonstrated skills receive full credit; foundational knowledge receives
    # partial credit; skills explicitly being learned receive no match credit.
    proficiency_credit = {"demonstrated": 1.0, "foundational": 0.5, "learning": 0.0}
    total_skill_weight = sum(catalogue[skill]["weight"] * priority for skill, priority in jd_skills.items())
    matched = [
        skill for skill in jd_skills
        if skill in resume_skill_levels and resume_skill_levels[skill]["level"] in {"demonstrated", "foundational"}
    ]
    missing = [skill for skill in jd_skills if skill not in matched]
    achieved_weight = sum(
        catalogue[skill]["weight"] * jd_skills[skill]
        * proficiency_credit[resume_skill_levels[skill]["level"]]
        for skill in matched
    )
    skill_score = achieved_weight / total_skill_weight * 100 if total_skill_weight else 0.0

    semantic = semantic_similarity(resume_clean, jd_clean)

    required_years = _required_years(jd_text)
    resume_years = _resume_years(resume_text)
    experience_score = None
    if required_years is not None:
        experience_score = min((resume_years or 0) / required_years, 1.0) * 100

    required_education = _required_education(jd_text)
    resume_education = _education_level(resume_text)
    education_score = None
    if required_education:
        education_score = min(EDU_RANK[resume_education] / max(EDU_RANK[required_education], 1), 1.0) * 100

    components = {"skills": (skill_score, WEIGHTS["skills"]), "semantic": (semantic["score"], WEIGHTS["semantic"])}
    if experience_score is not None:
        components["experience"] = (experience_score, WEIGHTS["experience"])
    if education_score is not None:
        components["education"] = (education_score, 0.05)

    denominator = sum(weight for _, weight in components.values())
    overall = sum(score * weight for score, weight in components.values()) / denominator if denominator else 0.0

    skill_share = WEIGHTS["skills"] / denominator if denominator else 0
    recommendations = build_recommendations(missing, jd_skills, total_skill_weight, skill_share, resume_skill_levels)

    matched_details = [{
        "skill": skill,
        "category": catalogue[skill]["category"],
        "priority": "Required" if jd_skills[skill] >= 1 else "Preferred",
        "proficiency": resume_skill_levels[skill]["level"],
        "credit": proficiency_credit[resume_skill_levels[skill]["level"]],
        "evidence": resume_skill_levels[skill]["evidence"],
    } for skill in sorted(matched)]
    developing = [
        {"skill": skill, "evidence": details["evidence"], "status": "Currently learning"}
        for skill, details in sorted(resume_skill_levels.items())
        if details["level"] == "learning" and skill in jd_skills
    ]

    warnings = []
    if not jd_skills:
        warnings.append("No catalogue skills were found in the job description. Add a more detailed job description or expand the skill catalogue.")
    if semantic["method"] == "tfidf":
        warnings.append("Sentence embeddings are unavailable; semantic fit is using the TF-IDF fallback.")
    if required_years is not None and resume_years is None:
        warnings.append("The job description specifies years of experience as a minimum requirement, but no clear years value was detected in the resume.")
    if developing:
        warnings.append("Skills listed as currently learning are shown separately and do not receive demonstrated-skill match credit.")

    return {
        "overall": round(float(overall), 1),
        "breakdown": {
            "skills": round(float(skill_score), 1),
            "semantic": semantic["score"],
            "experience": None if experience_score is None else round(float(experience_score), 1),
            "education": None if education_score is None else round(float(education_score), 1),
        },
        "weights_used": {name: round(weight / denominator, 3) for name, (_, weight) in components.items()},
        "method": semantic["method"],
        "matched": matched_details,
        "developing": developing,
        "missing": recommendations,
        "years": {
            "required": required_years,
            "found": resume_years,
            "fresher_eligible": bool(FRESHER_LANGUAGE.search(jd_text or "")),
        },
        "education": {"required": required_education, "found": resume_education},
        "resume_quality": _resume_quality_checks(resume_text),
        "warnings": warnings,
        "disclaimer": "This is an informational decision-support estimate, not a hiring decision or a probability of getting hired.",
    }
