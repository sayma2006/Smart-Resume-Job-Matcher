// ==========================================
// SMART RESUME–JOB MATCHER
// FRONTEND JAVASCRIPT
// ==========================================


// ==========================================
// GET HTML ELEMENTS
// ==========================================

const resumeInput = document.getElementById("resume");
const fileName = document.getElementById("fileName");

const jobDescription =
    document.getElementById("jobDescription");

const charCount =
    document.getElementById("charCount");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const results =
    document.getElementById("results");


// ==========================================
// SHOW SELECTED FILE NAME
// ==========================================

resumeInput.addEventListener("change", function () {

    if (resumeInput.files.length > 0) {

        fileName.textContent =
            resumeInput.files[0].name;

    } else {

        fileName.textContent =
            "No file selected";

    }
});


// ==========================================
// CHARACTER COUNT
// ==========================================

jobDescription.addEventListener(
    "input",
    function () {

        charCount.textContent =
            jobDescription.value.length +
            " characters";

    }
);


// ==========================================
// ANALYZE RESUME
// ==========================================

analyzeBtn.addEventListener(
    "click",
    async function () {

        // ------------------------------
        // Check resume
        // ------------------------------

        if (resumeInput.files.length === 0) {

            alert("Please upload your resume PDF.");

            return;
        }


        // ------------------------------
        // Check job description
        // ------------------------------

        if (
            jobDescription.value.trim() === ""
        ) {

            alert(
                "Please enter a job description."
            );

            return;
        }


        // ------------------------------
        // Disable button
        // ------------------------------

        analyzeBtn.disabled = true;

        analyzeBtn.textContent =
            "Analyzing...";


        // ------------------------------
        // Create form data
        // ------------------------------

        const formData = new FormData();

        formData.append(
            "resume",
            resumeInput.files[0]
        );

        formData.append(
            "job_description",
            jobDescription.value
        );


        try {

            // --------------------------
            // Send request to Flask
            // --------------------------

            const response = await fetch(
                "/analyze",
                {
                    method: "POST",
                    body: formData
                }
            );


            const result =
                await response.json();


            // --------------------------
            // Handle backend error
            // --------------------------

            if (!response.ok) {

                throw new Error(
                    result.error ||
                    "Something went wrong."
                );
            }


            // --------------------------
            // Get skill lists
            // --------------------------

            const matchedSkills =
                result.matched_skills || [];

            const missingSkills =
                result.missing_skills || [];

            const recommendedSkills =
                result.recommended_skills ||
                missingSkills;


            // --------------------------
            // Display results
            // --------------------------

            results.innerHTML = `

                <div class="results-header">

                    <h2>
                        Analysis Results
                    </h2>

                </div>


                <!-- FINAL SCORE -->

                <div class="score-card">

                    <div class="score-circle">

                        <span>
                            ${result.final_score}%
                        </span>

                    </div>

                    <h3>
                        ${result.match_level}
                    </h3>

                    <p>
                        ${result.match_message}
                    </p>

                </div>


                <!-- SCORE DETAILS -->

                <div class="score-details">

                    <div class="score-detail">

                        <h4>
                            Skill Match
                        </h4>

                        <strong>
                            ${result.skill_match_score}%
                        </strong>

                    </div>


                    <div class="score-detail">

                        <h4>
                            NLP Similarity
                        </h4>

                        <strong>
                            ${result.nlp_similarity_score}%
                        </strong>

                    </div>

                </div>


                <!-- MATCHED SKILLS -->

                <div class="skill-card">

                    <h3>
                        ✓ Matched Skills
                    </h3>

                    <div class="skill-list">

                        ${
                            matchedSkills.length > 0

                            ? matchedSkills
                                .map(
                                    skill =>
                                        `
                                        <span
                                            class="skill-tag matched-tag"
                                        >
                                            ${skill}
                                        </span>
                                        `
                                )
                                .join("")

                            : `
                                <p>
                                    No matched skills found.
                                </p>
                            `
                        }

                    </div>

                </div>


                <!-- MISSING SKILLS -->

                <div class="skill-card">

                    <h3>
                        ⚠ Missing Skills
                    </h3>

                    <div class="skill-list">

                        ${
                            missingSkills.length > 0

                            ? missingSkills
                                .map(
                                    skill =>
                                        `
                                        <span
                                            class="skill-tag missing-tag"
                                        >
                                            ${skill}
                                        </span>
                                        `
                                )
                                .join("")

                            : `
                                <p>
                                    No missing skills.
                                </p>
                            `
                        }

                    </div>

                </div>


                <!-- RECOMMENDED SKILLS -->

                <div class="recommendation-card">

                    <h3>
                        💡 Recommended Skills to Learn
                    </h3>

                    <p>
                        Based on the job description,
                        improving these skills may
                        increase your compatibility
                        with similar roles.
                    </p>

                    <div class="skill-list">

                        ${
                            recommendedSkills.length > 0

                            ? recommendedSkills
                                .map(
                                    skill =>
                                        `
                                        <span
                                            class="recommendation-tag"
                                        >
                                            ${skill}
                                        </span>
                                        `
                                )
                                .join("")

                            : `
                                <p>
                                    No additional skills
                                    recommended.
                                </p>
                            `
                        }

                    </div>

                </div>

            `;


            // --------------------------
            // Show results
            // --------------------------

            results.style.display = "block";


            // --------------------------
            // Scroll to results
            // --------------------------

            results.scrollIntoView({
                behavior: "smooth"
            });


        } catch (error) {

            alert(
                "Error: " +
                error.message
            );

        } finally {

            // --------------------------
            // Enable button again
            // --------------------------

            analyzeBtn.disabled = false;

            analyzeBtn.textContent =
                "🚀 Analyze Resume";

        }

    }
);