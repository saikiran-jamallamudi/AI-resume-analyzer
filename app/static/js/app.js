const form = document.getElementById("analysis-form");
const resumeText = document.getElementById("resume-text");
const jobDescription = document.getElementById("job-description");
const fileInput = document.getElementById("resume-file");
const dropZone = document.getElementById("drop-zone");
const fileName = document.getElementById("file-name");
const analyzeButton = document.getElementById("analyze-button");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const errorBox = document.getElementById("error-box");
let currentAnalysis = null;
let selectedFile = null;

function updateCount(element, target) {
  element.textContent = `${target.value.length.toLocaleString()} characters`;
}
resumeText.addEventListener("input", () => updateCount(document.getElementById("resume-count"), resumeText));
jobDescription.addEventListener("input", () => updateCount(document.getElementById("jd-count"), jobDescription));

document.getElementById("browse-button").addEventListener("click", () => fileInput.click());
dropZone.addEventListener("click", (event) => {
  if (event.target.closest("button")) return;
  fileInput.click();
});
fileInput.addEventListener("change", () => setSelectedFile(fileInput.files[0]));
["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
}));
["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");
}));
dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (file) setSelectedFile(file);
});

function setSelectedFile(file) {
  if (!file) return;
  const extension = file.name.split(".").pop().toLowerCase();
  if (!["pdf", "docx"].includes(extension)) {
    showError("Please choose a PDF or DOCX file.");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    showError("The selected file is larger than 5 MB.");
    return;
  }
  selectedFile = file;
  fileInput.files = new DataTransfer().files;
  fileName.textContent = `✓ ${file.name}`;
  clearError();
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
  errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
}
function clearError() { errorBox.hidden = true; errorBox.textContent = ""; }

function addChips(container, skills, type) {
  container.replaceChildren();
  if (!skills.length) {
    const empty = document.createElement("span");
    empty.className = "empty-state";
    empty.textContent = type === "matched" ? "No matching skills detected yet." : "No missing catalog skills detected.";
    container.appendChild(empty);
    return;
  }
  skills.forEach((skill) => {
    const chip = document.createElement("span");
    chip.className = `skill-chip ${type}`;
    chip.textContent = skill;
    container.appendChild(chip);
  });
}

function renderAnalysis(data) {
  currentAnalysis = data;
  document.getElementById("result-summary").textContent = data.summary;
  document.getElementById("score-value").textContent = data.match_score;
  document.getElementById("score-ring").style.background =
    `conic-gradient(#7160e5 ${data.match_score * 3.6}deg, #e9e7f7 0deg)`;
  document.getElementById("score-caption").textContent =
    data.match_score >= 75 ? "Strong alignment" : data.match_score >= 45 ? "Moderate alignment" : "Room to improve";
  document.getElementById("skill-coverage").textContent = `${data.skill_coverage}%`;
  document.getElementById("skill-progress").style.width = `${data.skill_coverage}%`;
  document.getElementById("keyword-coverage").textContent = `${data.keyword_coverage}%`;
  document.getElementById("matched-count").textContent = data.matched_skills.length;
  document.getElementById("missing-count").textContent = data.missing_skills.length;
  document.getElementById("matched-pill").textContent = `${data.matched_skills.length} skills`;
  document.getElementById("missing-pill").textContent = `${data.missing_skills.length} skills`;
  addChips(document.getElementById("matched-skills"), data.matched_skills, "matched");
  addChips(document.getElementById("missing-skills"), data.missing_skills, "missing");

  const list = document.getElementById("recommendations-list");
  list.replaceChildren();
  data.recommendations.forEach((recommendation) => {
    const item = document.createElement("li");
    item.textContent = recommendation;
    list.appendChild(item);
  });
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  if (!selectedFile && resumeText.value.trim().length < 30) {
    showError("Paste at least 30 characters of resume text or upload a resume file.");
    return;
  }
  if (jobDescription.value.trim().length < 30) {
    showError("Paste a job description with at least 30 characters.");
    return;
  }

  const payload = new FormData();
  if (selectedFile) payload.append("resume", selectedFile);
  if (resumeText.value.trim()) payload.append("resume_text", resumeText.value);
  payload.append("job_description", jobDescription.value);

  analyzeButton.disabled = true;
  loading.hidden = false;
  results.hidden = true;
  try {
    const response = await fetch("/api/analyze", { method: "POST", body: payload });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not analyze these documents.");
    renderAnalysis(data);
  } catch (error) {
    showError(error.message || "Something went wrong. Please try again.");
  } finally {
    analyzeButton.disabled = false;
    loading.hidden = true;
  }
});

document.getElementById("download-button").addEventListener("click", async () => {
  if (!currentAnalysis) return;
  try {
    const response = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentAnalysis)
    });
    if (!response.ok) throw new Error("Report download failed.");
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "resume-analysis-report.json";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    showError(error.message);
  }
});
