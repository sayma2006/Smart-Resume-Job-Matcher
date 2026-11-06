# ==========================================
# SMART RESUME–JOB MATCHER
# WEIGHTED SKILL MATCHING
# ==========================================


# ==========================================
# SKILL WEIGHTS
# ==========================================
#
# Higher weight = greater importance
# to the job match.
#
# ==========================================

SKILL_WEIGHTS = {

    # Machine Learning / AI
    "machine learning": 3.0,
    "nlp": 3.0,
    "artificial intelligence": 3.0,

    # Backend / API
    "fastapi": 2.5,
    "rest api": 2.5,

    # Programming Languages
    "python": 2.0,
    "java": 2.0,
    "c++": 2.0,
    "javascript": 1.8,

    # Data / Database
    "sql": 1.5,
    "mysql": 1.5,

    # Web
    "html": 1.0,
    "css": 1.0,

    # Development Tools
    "git": 1.0,
    "github": 1.0,

    # Computer Science
    "dsa": 1.5,

    # Other
    "rest": 2.0
}


# ==========================================
# GET SKILL WEIGHT
# ==========================================

def get_skill_weight(skill):

    skill = skill.lower().strip()

    return SKILL_WEIGHTS.get(
        skill,
        1.0
    )


# ==========================================
# COMPARE SKILLS
# ==========================================

def compare_skills(
    resume_skills,
    job_skills
):

    resume_set = {
        skill.lower().strip()
        for skill in resume_skills
    }

    job_set = {
        skill.lower().strip()
        for skill in job_skills
    }

    matched_skills = (
        resume_set.intersection(job_set)
    )

    missing_skills = (
        job_set.difference(resume_set)
    )

    return (
        list(matched_skills),
        list(missing_skills)
    )


# ==========================================
# WEIGHTED SKILL MATCH SCORE
# ==========================================

def calculate_skill_match(
    matched_skills,
    job_skills
):

    if len(job_skills) == 0:
        return 0

    # --------------------------------------
    # Total importance of all job skills
    # --------------------------------------

    total_weight = sum(
        get_skill_weight(skill)
        for skill in job_skills
    )

    # --------------------------------------
    # Importance of matched skills
    # --------------------------------------

    matched_weight = sum(
        get_skill_weight(skill)
        for skill in matched_skills
    )

    # --------------------------------------
    # Calculate percentage
    # --------------------------------------

    match_percentage = (
        matched_weight /
        total_weight
    ) * 100

    # Prevent score above 100
    match_percentage = min(
        match_percentage,
        100
    )

    return round(
        match_percentage,
        2
    )


# ==========================================
# FINAL SCORE
# ==========================================

def calculate_final_score(
    skill_score,
    nlp_score
):

    # Skill matching is given 70% importance.
    # NLP similarity contributes 30%.

    final_score = (
        skill_score * 0.70
    ) + (
        nlp_score * 0.30
    )

    return round(
        final_score,
        2
    )


# ==========================================
# RECOMMENDED SKILLS
# ==========================================

def get_recommended_skills(
    missing_skills
):

    recommended_skills = sorted(
        missing_skills,
        key=get_skill_weight,
        reverse=True
    )

    return recommended_skills
