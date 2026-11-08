from .skill_extractor import load_skills

def build_recommendations(missing_skills, jd_skills, total_weight, skill_component_share, resume_skill_levels=None):
    """Rank skill gaps by estimated contribution to the overall score."""
    catalogue = load_skills()
    recommendations = []
    resume_skill_levels = resume_skill_levels or {}
    for skill in missing_skills:
        info = catalogue[skill]
        weighted_importance = info["weight"] * jd_skills[skill]
        impact = (
            weighted_importance / total_weight * 100 * skill_component_share
            if total_weight else 0
        )
        recommendations.append({
            "skill": skill,
            "category": info["category"],
            "impact_points": round(impact, 1),
            "hours": info["hours"],
            "resource": info.get("resource", ""),
            "priority": "Required" if jd_skills[skill] >= 1 else "Preferred",
            "status": (
                "In progress" if resume_skill_levels.get(skill, {}).get("level") == "learning"
                else "Foundational" if resume_skill_levels.get(skill, {}).get("level") == "foundational"
                else "Not detected"
            ),
        })
    return sorted(recommendations, key=lambda item: item["impact_points"], reverse=True)
