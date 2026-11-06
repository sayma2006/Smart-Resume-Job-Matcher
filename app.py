from flask import Flask, render_template, request, jsonify
import os

from src.pdf_extractor import extract_text_from_pdf
from src.text_preprocessor import clean_text
from src.skill_extractor import extract_skills

from src.skill_matcher import (
    compare_skills,
    calculate_skill_match,
    calculate_final_score,
    get_recommended_skills
)

from src.nlp_matcher import calculate_nlp_similarity


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# ANALYZE RESUME
# ==========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ----------------------------------
        # Get uploaded resume
        # ----------------------------------

        resume_file = request.files["resume"]

        # ----------------------------------
        # Get job description
        # ----------------------------------

        job_description = request.form.get(
            "job_description",
            ""
        )

        # ----------------------------------
        # Create upload folder
        # ----------------------------------

        upload_folder = "data/uploads"

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        # ----------------------------------
        # Save uploaded PDF
        # ----------------------------------

        resume_path = os.path.join(
            upload_folder,
            resume_file.filename
        )

        resume_file.save(resume_path)

        # ----------------------------------
        # Extract text from resume
        # ----------------------------------

        resume_text = extract_text_from_pdf(
            resume_path
        )

        # ----------------------------------
        # Clean resume and job description
        # ----------------------------------

        cleaned_resume_text = clean_text(
            resume_text
        )

        cleaned_job_text = clean_text(
            job_description
        )

        # ----------------------------------
        # Extract skills
        # ----------------------------------

        resume_skills = extract_skills(
            cleaned_resume_text
        )

        job_skills = extract_skills(
            cleaned_job_text
        )

        # ----------------------------------
        # Compare skills
        # ----------------------------------

        matched_skills, missing_skills = compare_skills(
            resume_skills,
            job_skills
        )

        # ----------------------------------
        # Calculate weighted skill score
        # ----------------------------------

        skill_match_score = calculate_skill_match(
            matched_skills,
            job_skills
        )

        # ----------------------------------
        # Calculate NLP similarity
        # ----------------------------------

        nlp_similarity_score = calculate_nlp_similarity(
            cleaned_resume_text,
            cleaned_job_text
        )

        # ----------------------------------
        # Calculate final compatibility
        # ----------------------------------

        final_score = calculate_final_score(
            skill_match_score,
            nlp_similarity_score
        )

        # ----------------------------------
        # Recommend missing skills
        # ----------------------------------

        recommended_skills = get_recommended_skills(
            missing_skills
        )

        # ----------------------------------
        # Determine match level
        # ----------------------------------

        if final_score >= 80:

            match_level = "Excellent Match"

            match_message = (
                "Your resume strongly matches "
                "the requirements of this job."
            )

        elif final_score >= 60:

            match_level = "Good Match"

            match_message = (
                "Your resume matches many of "
                "the required skills, but some "
                "important skills are missing."
            )

        elif final_score >= 40:

            match_level = "Moderate Match"

            match_message = (
                "Your resume has some relevant "
                "skills, but several areas "
                "could be improved."
            )

        else:

            match_level = "Needs Improvement"

            match_message = (
                "Your resume currently has a low "
                "match with the requirements "
                "of this job."
            )

        # ----------------------------------
        # Return results
        # ----------------------------------

        return jsonify({

            "final_score": final_score,

            "match_level": match_level,

            "match_message": match_message,

            "skill_match_score": skill_match_score,

            "nlp_similarity_score": nlp_similarity_score,

            "resume_skills": resume_skills,

            "job_skills": job_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "recommended_skills": recommended_skills

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )




    