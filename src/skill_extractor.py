import json
import re
from pathlib import Path
from functools import lru_cache

SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"

@lru_cache(maxsize=1)
def load_skills():
    with SKILLS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

def _alias_pattern(alias: str):
    alias = alias.strip()
    escaped = re.escape(alias)
    # Technical tokens need boundaries: Java must not match JavaScript, and
    # C++/C#/.NET/Node.js must retain their punctuation.
    if alias.lower() == ".net":
        return re.compile(r"(?<![A-Za-z0-9])" + escaped + r"(?![A-Za-z0-9])", re.I)
    return re.compile(r"(?<![A-Za-z0-9+#])" + escaped + r"(?![A-Za-z0-9+#])", re.I)

@lru_cache(maxsize=1)
def _patterns():
    result = {}
    for canonical, info in load_skills().items():
        # Generic words such as "testing" are too broad to count alone; require
        # a specific phrase or tool name instead (pytest, unit testing, etc.).
        canonical_aliases = [] if canonical == "testing" else [canonical]
        aliases = sorted(set(info["aliases"] + canonical_aliases), key=len, reverse=True)
        result[canonical] = [(alias, _alias_pattern(alias)) for alias in aliases]
    return result

def find_skills(text: str) -> set[str]:
    text = text or ""
    found = set()
    for canonical, aliases in _patterns().items():
        if any(pattern.search(text) for _, pattern in aliases):
            found.add(canonical)
    return found

def find_skill_evidence(text: str, skill: str):
    """Return the first literal alias found in the source text for explainability."""
    for alias, pattern in _patterns().get(skill, []):
        match = pattern.search(text or "")
        if match:
            return match.group(0)
    return skill



LEARNING_SECTION = re.compile(
    r"^(currently\s+learning|learning|currently\s+exploring|exploring|courses?\s+in\s+progress|in\s+progress)$", re.I
)
LEARNING_PHRASES = re.compile(
    r"\b(currently\s+learning|currently\s+strengthening|strengthening\s+(?:my\s+)?(?:skills|knowledge|proficiency)?|(?<!machine[- ])learning\s+(?:to\s+use|about|the\s+basics?\s+of)?|"
    r"studying|exploring|coursework\s+in|in\s+progress|beginning\s+to\s+learn)\b", re.I
)
FOUNDATIONAL_PHRASES = re.compile(
    r"\b(basic|basics|beginner|beginner-level|foundational|fundamentals?|"
    r"familiar\s+with|exposure\s+to|introductory|working\s+knowledge)\b", re.I
)
RESUME_SECTION_HEADINGS = re.compile(
    r"^(professional\s+)?(summary|objective|experience|work\s+experience|employment|education|academic\s+background|technical\s+skills|skills|projects?|certifications?|achievements?|publications?|currently\s+learning|learning|courses?\s+in\s+progress)\s*:?$", re.I
)

def find_resume_skill_levels(text: str) -> dict:
    """
    Classify resume skill mentions as demonstrated, foundational, or learning.
    Stronger evidence wins if a skill appears in more than one context.
    """
    levels = {}
    evidence = {}
    learning_section = False
    learning_continuation = False
    rank = {"learning": 0, "foundational": 1, "demonstrated": 2}

    for raw_line in (text or "").splitlines():
        line = raw_line.strip().strip("-•* ")
        if not line:
            continue
        heading = RESUME_SECTION_HEADINGS.match(line)
        if heading:
            heading_text = line.rstrip(":").strip()
            learning_section = bool(LEARNING_SECTION.match(heading_text))
            learning_continuation = False
            continue

        inherited_learning = learning_continuation
        learning_continuation = bool(re.search(
            r"\b(currently\s+(?:learning|strengthening|exploring)|beginning\s+to\s+learn)\s*$", line, re.I
        ))
        skills = find_skills(line)
        if not skills:
            continue

        if learning_section or inherited_learning or LEARNING_PHRASES.search(line):
            level = "learning"
        elif FOUNDATIONAL_PHRASES.search(line):
            level = "foundational"
        else:
            level = "demonstrated"

        for skill in skills:
            evidence_text = find_skill_evidence(line, skill)
            skill_level = level
            # A library appearing only in a project technology list is evidence
            # of exposure, not by itself proof of machine-learning proficiency.
            if skill == "machine learning" and evidence_text.lower() in {"scikit-learn", "scikit learn", "sklearn"}:
                skill_level = "foundational" if level == "demonstrated" else level
            if skill not in levels or rank[skill_level] > rank[levels[skill]]:
                levels[skill] = skill_level
                evidence[skill] = evidence_text

    return {skill: {"level": level, "evidence": evidence[skill]} for skill, level in levels.items()}

def remove_learning_content(text: str) -> str:
    """Remove explicit in-progress learning lines/sections from semantic input."""
    kept = []
    learning_section = False
    learning_continuation = False
    for raw_line in (text or "").splitlines():
        line = raw_line.strip().strip("-•* ")
        if not line:
            continue
        if RESUME_SECTION_HEADINGS.match(line):
            heading_text = line.rstrip(":").strip()
            learning_section = bool(LEARNING_SECTION.match(heading_text))
            learning_continuation = False
            if not learning_section:
                kept.append(raw_line)
            continue
        inherited_learning = learning_continuation
        learning_continuation = bool(re.search(
            r"\b(currently\s+(?:learning|strengthening|exploring)|beginning\s+to\s+learn)\s*$", line, re.I
        ))
        if learning_section or inherited_learning or LEARNING_PHRASES.search(line):
            continue
        kept.append(raw_line)
    return "\n".join(kept)

PREFERRED_MARKERS = re.compile(
    r"\b(preferred|preferable|nice to have|good to have|bonus|desirable|optional|plus)\b", re.I
)
REQUIRED_MARKERS = re.compile(
    r"\b(required|required skills|requirements|must have|qualifications|minimum qualifications)\b", re.I
)

def find_job_skills(jd_text: str) -> dict:
    """
    Return {canonical_skill: 1.0|required or 0.5|preferred}.
    Section headings update the priority for following lines.
    """
    result = {}
    current_priority = 1.0
    for raw_line in (jd_text or "").splitlines():
        line = raw_line.strip(" \t-•*")
        if not line:
            continue
        heading_like = len(line) < 65 and not re.search(r"[.!?]$", line)
        if heading_like:
            if PREFERRED_MARKERS.search(line):
                current_priority = 0.5
            elif REQUIRED_MARKERS.search(line):
                current_priority = 1.0

        line_priority = 0.5 if PREFERRED_MARKERS.search(line) and not heading_like else current_priority
        for skill in find_skills(line):
            result[skill] = max(result.get(skill, 0), line_priority)
    return result


def find_job_skill_alternatives(jd_text: str) -> list[list[str]]:
    """Find simple two-skill alternatives written as 'A or B' on one line.

    Only lines containing exactly two catalogue skills are grouped, avoiding
    accidental grouping of longer lists such as 'Python, Java or SQL'.
    """
    groups = []
    catalogue_order = list(load_skills())
    for line in (jd_text or "").splitlines():
        if not re.search(r"\bor\b", line, re.I):
            continue
        found = find_skills(line)
        ordered = [skill for skill in catalogue_order if skill in found]
        if len(ordered) == 2:
            groups.append(ordered)
    return groups
