const codeInput = document.getElementById("code-input");
const fileInput = document.getElementById("file-input");
const analyzeBtn = document.getElementById("analyze-btn");
const message = document.getElementById("message");
const results = document.getElementById("results");
let latestReport = null;
let formattedCode = null;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  if (!file.name.endsWith(".py")) {
    message.textContent = "Please select a .py Python file.";
    fileInput.value = "";
    return;
  }
  if (file.size > 1024 * 1024) {
    message.textContent = "Please select a file smaller than 1 MB.";
    fileInput.value = "";
    return;
  }
  codeInput.value = await file.text();
  codeInput.dataset.filename = file.name;
  message.textContent = `Loaded ${file.name}. Select Analyze code to continue.`;
});

document.getElementById("clear-btn").addEventListener("click", () => {
  codeInput.value = "";
  codeInput.dataset.filename = "pasted_code.py";
  message.textContent = "";
});

analyzeBtn.addEventListener("click", async () => {
  message.textContent = "Analyzing source code…";
  analyzeBtn.disabled = true;
  try {
    const data = new FormData();
    data.append("code", codeInput.value);
    data.append("filename", codeInput.dataset.filename || "pasted_code.py");
    const response = await fetch("/analyze", { method: "POST", body: data });
    const report = await response.json();
    if (!response.ok) throw new Error(report.error || "Analysis failed.");
    latestReport = report;
    renderReport(report);
    message.textContent = "Analysis completed. Review findings before making changes.";
    results.classList.remove("hidden");
    results.scrollIntoView({behavior:"smooth", block:"start"});
    document.getElementById("original-preview").textContent = codeInput.value;
    document.getElementById("refactored-preview").textContent = "Select “Preview safe cleanup” to see the formatting-only preview.";
    formattedCode = null;
    document.getElementById("use-refactored-btn").disabled = true;
  } catch (error) {
    message.textContent = error.message;
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderReport(r) {
  document.getElementById("issue-total").textContent = r.issues.length;
  document.getElementById("high-total").textContent = r.summary?.high ?? 0;
  document.getElementById("mi-total").textContent = r.maintainability_index ?? "N/A";
  document.getElementById("score-total").textContent = `${r.score}/100`;
  document.getElementById("result-subtitle").textContent = `${r.filename || "Python source"} · Static analysis report`;
  const syntax = document.getElementById("syntax-error");
  if (r.syntax_error) {
    syntax.classList.remove("hidden");
    syntax.textContent = `Syntax error on line ${r.syntax_error.line}: ${r.syntax_error.message}. Metrics may be incomplete.`;
  } else {
    syntax.classList.add("hidden");
  }
  document.getElementById("code-stats").innerHTML = [
    ["Lines of code", r.lines], ["Non-empty lines", r.non_empty_lines],
    ["Functions", r.functions], ["Classes", r.classes],
    ["Total complexity", r.total_complexity], ["Maintainability index", r.maintainability_index ?? "N/A"],
    ["Medium severity", r.summary?.medium ?? 0], ["Low severity", r.summary?.low ?? 0]
  ].map(([label,value]) => `<div class="stat"><small>${esc(label)}</small><strong>${esc(value)}</strong></div>`).join("");
  renderIssues();
  const summary = r.summary || {high:0,medium:0,low:0};
  const max = Math.max(1, summary.high, summary.medium, summary.low);
  document.getElementById("severity-chart").innerHTML = ["High","Medium","Low"].map(level => {
    const count = summary[level.toLowerCase()] || 0;
    return `<div class="bar-row"><div class="bar-label"><span>${level}</span><strong>${count}</strong></div><div class="bar-track"><div class="bar ${level.toLowerCase()}" style="width:${count/max*100}%"></div></div></div>`;
  }).join("");
  document.getElementById("analysis-note").textContent = `${r.score_note || ""} ${r.analysis_note || ""}`;
}

function renderIssues() {
  if (!latestReport) return;
  const filter = document.getElementById("severity-filter").value;
  const issues = latestReport.issues.filter(i => filter === "All" || i.severity === filter);
  const container = document.getElementById("issues-container");
  if (!issues.length) {
    container.innerHTML = '<div class="issue-card"><p>No findings match this filter.</p></div>';
    return;
  }
  container.innerHTML = issues.map(i => `<article class="issue-card">
    <div class="issue-top"><h4>${esc(i.title)}</h4><span class="severity ${i.severity.toLowerCase()}">${esc(i.severity)}</span></div>
    <p>${esc(i.description)}</p><p><strong>Recommendation:</strong> ${esc(i.recommendation)}</p>
    <div class="issue-line">Line ${esc(i.line ?? "N/A")}</div>
  </article>`).join("");
}
document.getElementById("severity-filter").addEventListener("change", renderIssues);

document.getElementById("format-btn").addEventListener("click", async () => {
  const code = codeInput.value;
  if (!code.trim()) { message.textContent = "Paste or upload code first."; return; }
  const data = new FormData();
  data.append("code", code);
  try {
    const response = await fetch("/refactor", {method:"POST", body:data});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not create preview.");
    formattedCode = result.code;
    document.getElementById("original-preview").textContent = code;
    document.getElementById("refactored-preview").textContent = result.code;
    document.getElementById("refactor-changes").textContent = result.changes.join(" ");
    document.getElementById("use-refactored-btn").disabled = false;
  } catch (error) {
    message.textContent = error.message;
  }
});
document.getElementById("use-refactored-btn").addEventListener("click", () => {
  if (formattedCode !== null) {
    codeInput.value = formattedCode;
    message.textContent = "Formatted preview copied into the editor. Re-analyze to inspect it.";
    codeInput.scrollIntoView({behavior:"smooth",block:"center"});
  }
});
document.getElementById("download-btn").addEventListener("click", async () => {
  if (!latestReport) return;
  const response = await fetch("/report", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({report:latestReport})
  });
  if (!response.ok) { message.textContent = "Report export failed."; return; }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "technical_debt_report.json"; a.click();
  URL.revokeObjectURL(url);
});
