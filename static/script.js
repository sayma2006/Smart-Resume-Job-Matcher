const form = document.getElementById("analysisForm");
const fileInput = document.getElementById("resume");
const dropzone = document.getElementById("dropzone");
const fileLabel = document.getElementById("fileLabel");
const jobDescription = document.getElementById("jobDescription");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorMessage = document.getElementById("errorMessage");
let gaugeChart = null;
let breakdownChart = null;
let baseScore = 0;
let recommendations = [];
let loaderTimer = null;
const loaderMessages = [
  "Reading resume content…",
  "Mapping skills and aliases…",
  "Comparing experience and semantic context…",
  "Preparing your skill-gap roadmap…"
];

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file && (file.type !== "application/pdf" || file.size > 5 * 1024 * 1024)) {
    errorMessage.textContent = file.size > 5 * 1024 * 1024 ? "PDF must be 5 MB or smaller." : "Please choose a PDF file.";
    fileInput.value = "";
  }
  fileLabel.textContent = fileInput.files[0] ? `${fileInput.files[0].name} · ${(fileInput.files[0].size / 1024 / 1024).toFixed(2)} MB` : "Drop your PDF here or browse";
});
const clearButton = document.getElementById("clearForm");
if (clearButton) clearButton.addEventListener("click", () => {
  form.reset(); fileLabel.textContent = "Drop your PDF here or browse";
  document.getElementById("charCount").textContent = "0 characters";
  errorMessage.textContent = ""; document.getElementById("results").classList.add("hidden");
});
jobDescription.addEventListener("input", () => {
  document.getElementById("charCount").textContent = `${jobDescription.value.length} characters`;
});
["dragenter", "dragover"].forEach(type => dropzone.addEventListener(type, event => {
  event.preventDefault(); dropzone.classList.add("dragover");
}));
["dragleave", "drop"].forEach(type => dropzone.addEventListener(type, event => {
  event.preventDefault(); dropzone.classList.remove("dragover");
}));
dropzone.addEventListener("drop", event => {
  const file = event.dataTransfer.files[0];
  if (file && file.type === "application/pdf") {
    const transfer = new DataTransfer(); transfer.items.add(file); fileInput.files = transfer.files;
    fileInput.dispatchEvent(new Event("change"));
  } else {
    errorMessage.textContent = "Please drop a PDF file.";
  }
});

const themeToggle = document.getElementById("themeToggle");
if (localStorage.getItem("srjm-theme") === "dark") document.body.classList.add("dark");
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("srjm-theme", document.body.classList.contains("dark") ? "dark" : "light");
  if (baseScore) drawGauge(baseScore);
});

function showLoader() {
  const loader = document.getElementById("analysisLoader");
  const status = document.getElementById("loaderStatus");
  const steps = [...document.querySelectorAll(".loader-steps span")];
  loader.classList.remove("hidden");
  let index = 0;
  steps.forEach((step, i) => step.classList.toggle("active", i === 0));
  status.textContent = loaderMessages[0];
  loaderTimer = setInterval(() => {
    index = Math.min(index + 1, loaderMessages.length - 1);
    status.textContent = loaderMessages[index];
    steps.forEach((step, i) => step.classList.toggle("active", i <= index));
  }, 1150);
}
function hideLoader() {
  if (loaderTimer) clearInterval(loaderTimer);
  loaderTimer = null;
  document.getElementById("analysisLoader").classList.add("hidden");
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorMessage.textContent = "";
  if (!fileInput.files[0]) { errorMessage.textContent = "Please upload a PDF resume."; return; }
  if (jobDescription.value.trim().length < 30) { errorMessage.textContent = "Please enter a job description with at least 30 characters."; return; }

  const data = new FormData();
  data.append("resume", fileInput.files[0]);
  data.append("job_description", jobDescription.value);
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing resume…";
  showLoader();
  try {
    const response = await fetch("/analyze", { method: "POST", body: data });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Analysis failed.");
    renderResults(result);
  } catch (error) {
    errorMessage.textContent = error.message;
  } finally {
    hideLoader();
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = 'Analyze compatibility <span>→</span>';
  }
});

function animateNumber(element, target) {
  const start = performance.now();
  const duration = 1050;
  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    element.textContent = `${(target * eased).toFixed(1)}%`;
    if (progress < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function makeText(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function renderResults(result) {
  document.getElementById("results").classList.remove("hidden");
  document.getElementById("results").classList.add("results-enter");
  baseScore = result.overall;
  recommendations = result.missing || [];
  animateNumber(document.getElementById("overallScore"), result.overall);
  document.getElementById("verdict").textContent =
    result.overall >= 75 ? "Strong alignment" : result.overall >= 55 ? "Promising alignment" : result.overall >= 35 ? "Partial alignment" : "More development needed";
  document.getElementById("disclaimer").textContent = result.disclaimer;
  document.getElementById("methodNote").textContent =
    `Semantic method: ${result.method}. Similarity scores are heuristic estimates, not hiring probabilities.`;

  const warnings = document.getElementById("warnings");
  warnings.replaceChildren();
  (result.warnings || []).forEach(message => warnings.appendChild(makeText("div", "notice", message)));

  drawGauge(result.overall);
  drawBreakdown(result.breakdown, result.weights_used);
  renderMatched(result.matched || []);
  renderDeveloping(result.developing || []);
  renderMissing(recommendations);
  renderQuality(result.resume_quality || []);
  renderProfile(result.years, result.education);
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}

function drawGauge(value) {
  const canvas = document.getElementById("scoreGauge");
  const color = value >= 75 ? "#16a34a" : value >= 55 ? "#e49a36" : "#d05b50";
  if (gaugeChart) { gaugeChart.destroy(); gaugeChart = null; }
  if (typeof Chart !== "undefined") {
    gaugeChart = new Chart(canvas, {
      type: "doughnut",
      data: { datasets: [{ data: [value, 100 - value], backgroundColor: [color, document.body.classList.contains("dark") ? "#344158" : "#e9edf3"], borderWidth: 0 }] },
      options: { cutout: "82%", rotation: -90, circumference: 360, plugins: { legend: { display: false }, tooltip: { enabled: false } } }
    });
    return;
  }
  // Canvas fallback keeps the dashboard usable if the optional chart CDN is unavailable.
  const context = canvas.getContext("2d");
  if (!context) return;
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 220, height = canvas.clientHeight || 220;
  canvas.width = width * ratio; canvas.height = height * ratio;
  context.scale(ratio, ratio);
  const radius = Math.min(width, height) * 0.42;
  context.lineWidth = Math.max(10, radius * 0.18);
  context.lineCap = "round";
  context.strokeStyle = document.body.classList.contains("dark") ? "#344158" : "#e9edf3";
  context.beginPath(); context.arc(width / 2, height / 2, radius, 0, Math.PI * 2); context.stroke();
  context.strokeStyle = color;
  context.beginPath(); context.arc(width / 2, height / 2, radius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * value / 100); context.stroke();
}
function drawBreakdown(breakdown, weights) {
  const labels = [], values = [];
  Object.entries(breakdown).forEach(([key, value]) => {
    if (value !== null && value !== undefined) { labels.push(key[0].toUpperCase() + key.slice(1)); values.push(value); }
  });
  if (breakdownChart) { breakdownChart.destroy(); breakdownChart = null; }
  const canvas = document.getElementById("breakdownChart");
  if (typeof Chart !== "undefined") {
    breakdownChart = new Chart(canvas, {
      type: "bar",
      data: { labels, datasets: [{ data: values, backgroundColor: ["#172554", "#e49a36", "#1b8a62", "#6383bc"], borderRadius: 7, barThickness: 17 }] },
      options: { indexAxis: "y", responsive: true, scales: { x: { min: 0, max: 100, grid: { color: "rgba(130,145,165,.15)" }, ticks: { callback: value => `${value}%` } }, y: { grid: { display: false } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: context => `${context.raw}%` } } } }
    });
  } else {
    const context = canvas.getContext("2d");
    if (context) {
      const ratio = window.devicePixelRatio || 1;
      const width = canvas.clientWidth || 420, height = Math.max(150, labels.length * 42 + 24);
      canvas.width = width * ratio; canvas.height = height * ratio;
      context.scale(ratio, ratio);
      context.font = "12px sans-serif";
      labels.forEach((label, index) => {
        const y = 24 + index * 42;
        context.fillStyle = getComputedStyle(document.body).color;
        context.fillText(label, 4, y);
        context.fillStyle = document.body.classList.contains("dark") ? "#344158" : "#e9edf3";
        context.fillRect(110, y - 12, Math.max(20, width - 135), 12);
        context.fillStyle = ["#172554", "#e49a36", "#1b8a62", "#6383bc"][index % 4];
        context.fillRect(110, y - 12, Math.max(0, (width - 135) * Math.max(0, Math.min(100, values[index])) / 100), 12);
        context.fillStyle = getComputedStyle(document.body).color;
        context.fillText(`${Number(values[index]).toFixed(1)}%`, Math.max(115, width - 42), y);
      });
    }
  }
  document.getElementById("weightNote").textContent = `Normalized component weights: ${Object.entries(weights || {}).map(([key, value]) => `${key} ${Math.round(value * 100)}%`).join(" · ")}`;
}
function renderMatched(items) {
  const container = document.getElementById("matchedSkills");
  container.replaceChildren();
  document.getElementById("matchedCount").textContent = items.length;
  if (!items.length) { container.appendChild(makeText("p", "muted small", "No catalogue skills were matched.")); return; }
  items.forEach(item => {
    const details = document.createElement("details");
    details.className = "evidence-item";
    const level = item.proficiency === "foundational" ? "Foundational · partial credit" : "Demonstrated · full credit";
    const summary = makeText("summary", `chip ${item.priority === "Preferred" ? "preferred" : ""}`, `${item.skill} · ${level}`);
    const evidence = makeText("p", "evidence-text", `Resume evidence: “${item.evidence || item.skill}” · ${item.priority} · ${level}`);
    details.append(summary, evidence);
    container.appendChild(details);
  });
}
function renderDeveloping(items) {
  const panel = document.getElementById("developingPanel");
  const container = document.getElementById("developingSkills");
  if (!panel || !container) return;
  container.replaceChildren();
  document.getElementById("developingCount").textContent = items.length;
  panel.hidden = items.length === 0;
  items.forEach(item => {
    const details = document.createElement("details");
    details.className = "evidence-item";
    const summary = makeText("summary", "chip preferred", `${item.skill} · In progress`);
    const evidence = makeText("p", "evidence-text", `Resume evidence: “${item.evidence || item.skill}” · not yet counted as demonstrated`);
    details.append(summary, evidence);
    container.appendChild(details);
  });
}

function renderMissing(items) {
  const container = document.getElementById("missingSkills");
  container.replaceChildren();
  document.getElementById("missingCount").textContent = items.length;
  if (!items.length) { container.appendChild(makeText("p", "muted small", "No catalogue skill gaps were detected.")); }
  items.forEach(item => {
    const row = document.createElement("div"); row.className = "gap-item";
    const name = makeText("span", "gap-name", item.skill);
    const impact = makeText("span", "impact", `+${item.impact_points} pts*`);
    const meta = makeText("span", "gap-meta", `${item.category} · ${item.priority} · ${item.status || "Not detected"} · approx. ${item.hours} learning hours`);
    const actions = document.createElement("div"); actions.className = "gap-actions";
    const checkboxLabel = document.createElement("label");
    const checkbox = document.createElement("input"); checkbox.type = "checkbox"; checkbox.dataset.impact = item.impact_points;
    checkbox.addEventListener("change", updateProjection);
    checkboxLabel.append(checkbox, document.createTextNode(" Include in learning plan"));
    actions.appendChild(checkboxLabel);
    if (item.resource) { const link = document.createElement("a"); link.href = item.resource; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = "Learning resource ↗"; actions.appendChild(link); }
    row.append(name, impact, meta, actions); container.appendChild(row);
  });
  updateProjection();
}
function updateProjection() {
  let extra = 0;
  document.querySelectorAll("#missingSkills input:checked").forEach(input => extra += Number(input.dataset.impact || 0));
  const projected = Math.min(100, baseScore + extra);
  document.getElementById("currentProjection").textContent = `${baseScore.toFixed(1)}%`;
  document.getElementById("projectedScore").textContent = `${projected.toFixed(1)}%`;
  document.getElementById("projectionBar").style.width = `${projected}%`;
  document.getElementById("projectedScore").classList.remove("score-pop");
  void document.getElementById("projectedScore").offsetWidth;
  document.getElementById("projectedScore").classList.add("score-pop");
}
function renderQuality(items) {
  const container = document.getElementById("resumeQuality"); container.replaceChildren();
  if (!items.length) { container.appendChild(makeText("p", "muted small", "No basic structure issues were detected by the automated checks.")); return; }
  items.forEach(item => container.appendChild(makeText("div", "suggestion", item.message)));
}
function renderProfile(years, education) {
  const container = document.getElementById("profileChecks"); container.replaceChildren();
  const rows = [
    ["Required experience", years?.fresher_eligible ? "Freshers / up to 1 year accepted" : years?.required == null ? "Not specified" : `${years.required}+ years`],
    ["Detected experience", years?.found == null ? "Not detected" : `${years.found} years`],
    ["Required education", education?.required || "Not specified"],
    ["Detected education", education?.found || "Not detected"]
  ];
  rows.forEach(([label, value]) => {
    const row = document.createElement("div"); row.className = "profile-row";
    row.append(makeText("span", "muted", label), makeText("strong", "", value));
    container.appendChild(row);
  });
}
document.getElementById("downloadReport").addEventListener("click", async () => {
  errorMessage.textContent = "";
  const data = new FormData();
  if (fileInput.files[0]) data.append("resume", fileInput.files[0]);
  data.append("job_description", jobDescription.value);
  try {
    const response = await fetch("/download-report", { method: "POST", body: data });
    if (!response.ok) {
      const error = await response.json(); throw new Error(error.error || "Report download failed.");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a"); link.href = url; link.download = "resume_match_report.pdf"; link.click();
    URL.revokeObjectURL(url);
  } catch (error) { errorMessage.textContent = error.message; }
});
