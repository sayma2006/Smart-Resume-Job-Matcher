from src.skill_extractor import find_job_skills, find_skills


def test_java_does_not_match_javascript():
    assert "java" not in find_skills("I build applications with JavaScript.")
    assert "java" in find_skills("I have used Java and JavaScript.")


def test_aliases_map_to_canonical_skill():
    assert "machine learning" in find_skills("Built a model using sklearn.")
    assert "javascript" in find_skills("Used JS and ES6.")


def test_special_character_skills():
    found = find_skills("C++, C#, Node.js, CI/CD and ASP.NET")
    assert {"c++", "c#", "node.js", "ci/cd", ".net"}.issubset(found)


def test_preferred_section_is_lower_priority():
    result = find_job_skills("Required Skills\nPython\nNice to have\nDocker")
    assert result["python"] == 1.0
    assert result["docker"] == 0.5


def test_required_heading_resets_preferred_priority():
    result = find_job_skills(
        "Preferred Skills\nDocker\nRequired Skills\nPython"
    )
    assert result["docker"] == 0.5
    assert result["python"] == 1.0


def test_empty_text_returns_no_skills():
    assert find_skills("") == set()
    assert find_job_skills("") == {}


def test_currently_learning_section_is_classified_separately():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels(
        "Skills\nPython, Java\nCurrently Learning\nDocker, pytest"
    )
    assert result["python"]["level"] == "demonstrated"
    assert result["docker"]["level"] == "learning"
    assert result["testing"]["level"] == "learning"


def test_learning_phrase_on_same_line_is_detected():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels("Currently learning Docker and pytest.")
    assert result["docker"]["level"] == "learning"
    assert result["testing"]["level"] == "learning"


def test_basic_knowledge_is_foundational():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels("Basic React and machine learning fundamentals.")
    assert result["react"]["level"] == "foundational"
    assert result["machine learning"]["level"] == "foundational"


def test_demonstrated_evidence_overrides_learning_mention():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels(
        "Currently Learning\nDocker\nProjects\nBuilt and deployed an application using Docker and Flask."
    )
    assert result["docker"]["level"] == "demonstrated"



def test_remove_learning_content_keeps_demonstrated_sections():
    from src.skill_extractor import remove_learning_content

    text = "Skills\nPython, Java\nCurrently Learning\nDocker, pytest\nProjects\nBuilt with Flask."
    cleaned = remove_learning_content(text)
    assert "Python" in cleaned
    assert "Flask" in cleaned
    assert "Docker" not in cleaned
    assert "pytest" not in cleaned


def test_currently_strengthening_testing_is_in_progress():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels(
        "Professional Summary\nCurrently strengthening automated testing and deployment skills.\n"
        "Additional Information\nCurrently learning: Docker, pytest."
    )
    assert result["testing"]["level"] == "learning"
    assert result["docker"]["level"] == "learning"


def test_hyphenated_machine_learning_is_foundational_when_described_as_familiar():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels("Familiar with machine-learning fundamentals.")
    assert result["machine learning"]["level"] == "foundational"


def test_scikit_learn_library_name_is_only_foundational_evidence():
    from src.skill_extractor import find_resume_skill_levels

    result = find_resume_skill_levels("Project stack: Python, Flask, scikit-learn.")
    assert result["machine learning"]["level"] == "foundational"


def test_or_alternative_is_detected_as_one_group():
    from src.skill_extractor import find_job_skill_alternatives

    assert find_job_skill_alternatives("Knowledge of Flask or Django framework.") == [["flask", "django"]]


def test_learning_cue_at_end_of_wrapped_pdf_line_applies_to_next_line():
    from src.skill_extractor import find_resume_skill_levels, remove_learning_content

    resume = (
        "Professional Summary\n"
        "Familiar with machine-learning fundamentals and currently strengthening\n"
        "automated testing and deployment skills.\n"
        "Projects\nBuilt a Flask API."
    )
    result = find_resume_skill_levels(resume)
    assert result["testing"]["level"] == "learning"
    cleaned = remove_learning_content(resume)
    assert "automated testing" not in cleaned
    assert "Built a Flask API" in cleaned


def test_generic_testing_word_in_disclaimer_is_not_skill_evidence():
    from src.skill_extractor import find_skills

    assert "testing" not in find_skills(
        "Fictional sample resume created only for testing a resume-analysis application."
    )


def test_sample_resume_skill_levels_handle_wrapped_summary_and_project_stack():
    from src.skill_extractor import find_resume_skill_levels

    resume = (
        "Professional Summary\n"
        "Familiar with machine-learning fundamentals and currently strengthening\n"
        "automated testing and deployment skills.\n"
        "Foundations\nData Structures, OOP, debugging, basic machine learning\n"
        "Project Experience\nSmart Resume Matcher | Python, Flask, scikit-learn\n"
        "Additional Information\nCurrently learning: Docker, pytest, and cloud deployment fundamentals."
    )
    levels = find_resume_skill_levels(resume)
    assert levels["machine learning"]["level"] == "foundational"
    assert levels["testing"]["level"] == "learning"
    assert levels["docker"]["level"] == "learning"
