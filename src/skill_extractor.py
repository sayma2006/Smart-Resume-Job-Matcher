from src.skills import SKILLS


def extract_skills(text):
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return found_skills