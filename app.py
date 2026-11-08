
import io
import os
from xml.sax.saxutils import escape

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.pdf_parser import extract_text_from_pdf
from src.scorer import analyze


app = Flask(__name__)

# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

MAX_CONTENT_LENGTH_MB = max(
    1, int(os.getenv("MAX_CONTENT_LENGTH_MB", "5"))
)

MAX_JOB_DESCRIPTION_CHARS = 20000

MAX_CONTENT_LENGTH_BYTES = (
    MAX_CONTENT_LENGTH_MB * 1024 * 1024
)

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH_BYTES


# --------------------------------------------------
# ERROR RESPONSE FOR OVERSIZED REQUESTS
# --------------------------------------------------

def too_large(_error=None):
    return jsonify({
        "error": (
            "The uploaded request is too large. "
            f"Maximum request size is {MAX_CONTENT_LENGTH_MB} MB."
        )
    }), 413


# Check the Content-Length before processing the request body.
@app.before_request
def check_request_size():

    content_length = request.content_length

    if (
        content_length is not None
        and content_length > MAX_CONTENT_LENGTH_BYTES
    ):
        return too_large()


# Handle Werkzeug's request-size exception globally.
@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(error):
    return too_large(error)


# --------------------------------------------------
# RESUME ANALYSIS FUNCTION
# --------------------------------------------------

def _get_analysis():

    uploaded = request.files.get("resume")

    job_description = request.form.get(
        "job_description", ""
    ).strip()

    # Validate uploaded resume
    if uploaded is None or not uploaded.filename:

        return None, (
            {"error": "Please select a resume PDF."},
            400,
        )

    if not uploaded.filename.lower().endswith(".pdf"):

        return None, (
            {"error": "Only PDF resumes are supported."},
            400,
        )

    # Validate job description
    if not job_description:

        return None, (
            {"error": "Please enter a job description."},
            400,
        )

    if len(job_description) < 30:

        return None, (
            {
                "error": (
                    "Please enter a job description "
                    "with at least 30 characters."
                )
            },
            400,
        )

    if len(job_description) > MAX_JOB_DESCRIPTION_CHARS:

        return None, (
            {
                "error": (
                    f"Job description must be "
                    f"{MAX_JOB_DESCRIPTION_CHARS:,} "
                    "characters or fewer."
                )
            },
            400,
        )

    # Process PDF directly from memory.
    # The uploaded resume is never saved to disk.
    resume_text = extract_text_from_pdf(uploaded.stream)

    result = analyze(resume_text, job_description)

    return result, None


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# --------------------------------------------------
# RESUME ANALYSIS API
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
@app.route("/api/analyze", methods=["POST"])
def analyze_route():

    try:

        result, error = _get_analysis()

        if error:

            payload, status = error

            return jsonify(payload), status

        return jsonify(result)

    except RequestEntityTooLarge:

        return too_large()

    except ValueError as exc:

        return jsonify({"error": str(exc)}), 422

    except Exception as exc:

        # Additional protection for HTTP 413 exceptions.
        if getattr(exc, "code", None) == 413:
            return too_large(exc)

        # Never log resume or job-description contents.
        app.logger.exception("Resume analysis failed")

        return jsonify({
            "error": (
                "Analysis failed unexpectedly. "
                "Check the server terminal for details."
            )
        }), 500


# --------------------------------------------------
# DOWNLOAD ANALYSIS REPORT AS PDF
# --------------------------------------------------

@app.route("/download-report", methods=["POST"])
def download_report():

    try:

        result, error = _get_analysis()

        if error:

            payload, status = error

            return jsonify(payload), status

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=42,
            leftMargin=42,
            topMargin=42,
            bottomMargin=42,
        )

        styles = getSampleStyleSheet()

        story = [

            Paragraph(
                "Smart Resume–Job Matcher",
                styles["Title"],
            ),

            Paragraph(
                "Resume and Job Description Analysis Report",
                styles["Heading2"],
            ),

            Spacer(1, 12),

            Paragraph(
                (
                    "Overall compatibility: "
                    f"<b>{escape(str(result['overall']))}%</b>"
                ),
                styles["Heading2"],
            ),

            Paragraph(
                escape(result["disclaimer"]),
                styles["BodyText"],
            ),

            Spacer(1, 12),

            Paragraph(
                "Score breakdown",
                styles["Heading2"],
            ),
        ]

        # Score breakdown table
        rows = [["Component", "Score"]]

        for key, value in result["breakdown"].items():

            if value is not None:

                rows.append([
                    escape(key.title()),
                    f"{escape(str(value))}%",
                ])

        table = Table(
            rows,
            hAlign="LEFT",
        )

        table.setStyle(TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#172554"),
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#CBD5E1"),
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

        ]))

        story.extend([

            table,

            Spacer(1, 14),

            Paragraph(
                "Matched skills",
                styles["Heading2"],
            ),

        ])

        # Matched skills
        matched_text = ", ".join(

            (
                f"{escape(item['skill'])} "
                f"({escape(item.get('proficiency', 'demonstrated'))}; "
                f"{escape(item.get('priority', ''))})"
            )

            for item in result["matched"]

        ) or "None detected"

        story.append(
            Paragraph(
                matched_text,
                styles["BodyText"],
            )
        )

        # Skills currently being learned
        if result.get("developing"):

            story.extend([

                Spacer(1, 10),

                Paragraph(
                    "Skills currently being learned",
                    styles["Heading2"],
                ),

            ])

            developing_text = ", ".join(

                escape(item["skill"])

                for item in result["developing"]

            )

            story.append(
                Paragraph(
                    developing_text,
                    styles["BodyText"],
                )
            )

        # Missing skills and recommendations
        story.extend([

            Spacer(1, 10),

            Paragraph(
                "Skill gaps and recommendations",
                styles["Heading2"],
            ),

        ])

        for item in result["missing"]:

            line = (

                f"<b>{escape(item['skill'])}</b> "
                f"({escape(item['priority'])}) — "

                f"estimated learning time: "
                f"{escape(str(item['hours']))} hours; "

                f"illustrative score contribution: "
                f"{escape(str(item['impact_points']))} points. "

                f"{escape(item.get('resource', ''))}"

            )

            story.extend([

                Paragraph(
                    line,
                    styles["BodyText"],
                ),

                Spacer(1, 5),

            ])

        # Resume improvement suggestions
        if result["resume_quality"]:

            story.extend([

                Spacer(1, 10),

                Paragraph(
                    "Resume improvement suggestions",
                    styles["Heading2"],
                ),

            ])

            for item in result["resume_quality"]:

                story.append(
                    Paragraph(
                        "• " + escape(item["message"]),
                        styles["BodyText"],
                    )
                )

        # Warnings and notes
        if result["warnings"]:

            story.extend([

                Spacer(1, 10),

                Paragraph(
                    "Notes",
                    styles["Heading2"],
                ),

            ])

            for warning in result["warnings"]:

                story.append(
                    Paragraph(
                        "• " + escape(warning),
                        styles["BodyText"],
                    )
                )

        # Generate PDF in memory
        document.build(story)

        buffer.seek(0)

        return send_file(

            buffer,

            mimetype="application/pdf",

            as_attachment=True,

            download_name="resume_match_report.pdf",

        )

    except RequestEntityTooLarge:

        return too_large()

    except ValueError as exc:

        return jsonify({"error": str(exc)}), 422

    except Exception as exc:

        if getattr(exc, "code", None) == 413:
            return too_large(exc)

        app.logger.exception("Report generation failed")

        return jsonify({
            "error": "Could not generate the report."
        }), 500


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    debug = (
        os.getenv("FLASK_DEBUG", "0")
        .strip()
        .lower()
        in {"1", "true", "yes"}
    )

    app.run(debug=debug)
