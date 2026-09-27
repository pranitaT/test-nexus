const state = {context:{}, impact:null, suite:null, scenarios:null};
const $ = id => document.getElementById(id);

function error(message) {
  $("error").textContent = message || "";
  $("error").classList.toggle("hidden", !message);
}

function context() {
  return {
    project_name: $("project_name").value,
    source_changes: $("source_changes").value,
    user_story: $("user_story").value,
    defects: $("defects").value,
    telemetry: $("telemetry").value,
    previous_results: $("previous_results").value,
    test_catalog: state.context.test_catalog || []
  };
}

function writeContext(x) {
  state.context = x;
  $("project_name").value = x.project_name || "";
  $("source_changes").value = x.source_changes || "";
  $("user_story").value = x.user_story || "";
  $("defects").value = x.defects || "";
  $("telemetry").value = x.telemetry || "";
  $("previous_results").value = x.previous_results || "";
}

function badge(x) {
  return `<span class="badge ${(x || "").toLowerCase()}">${x || ""}</span>`;
}

function stats() {
  $("stat-modules").textContent = state.impact?.impacted_modules?.length || 0;
  $("stat-risk").textContent = state.impact?.risk_factors?.filter(x => x.severity === "High").length || 0;
  $("stat-tests").textContent = state.suite?.selected_tests?.length || 0;
  $("stat-scenarios").textContent = state.scenarios?.scenarios?.length || 0;
}

async function loadDemo() {
  try { writeContext(await api("/api/demo")); error(""); }
  catch(e) { error(e.message); }
}

async function analyze() {
  try {
    state.context = context();
    state.impact = await api("/api/analyze-impact", {
      method:"POST", body:JSON.stringify(state.context)
    });
    $("impact-section").classList.remove("hidden");
    $("impact-summary").textContent = state.impact.summary || "";
    $("modules").innerHTML = (state.impact.impacted_modules || []).map(m =>
      `<div class="item"><div class="item-head"><strong>${m.module}</strong>${badge(m.impact)}</div>
      <p>${m.change_evidence}</p><small>Confidence: ${m.confidence}%</small></div>`
    ).join("");
    $("risks").innerHTML = (state.impact.risk_factors || []).map(r =>
      `<div class="row">${badge(r.severity)}<div><strong>${r.risk}</strong><p>${r.evidence}</p></div></div>`
    ).join("");
    $("traceability").innerHTML = (state.impact.traceability || []).map(t =>
      `<div class="trace"><span>${t.change}</span><b>→</b><span>${t.module}</span><b>→</b><span>${t.risk}</span></div>`
    ).join("");
    stats(); error("");
  } catch(e) { error(e.message); }
}

async function suite() {
  if (!state.impact) return error("Analyze impact first.");
  try {
    const x = await api("/api/recommend-suite", {
      method:"POST",
      body:JSON.stringify({...context(), impact_analysis:state.impact})
    });
    state.suite = x;
    $("suite-section").classList.remove("hidden");
    $("suite-strategy").textContent = x.strategy || "";
    $("selected-tests").innerHTML = (x.selected_tests || []).map(t =>
      `<div class="item"><div class="item-head"><strong>${t.test_id} · ${t.name}</strong>${badge(t.priority)}</div>
      <p>${t.reason}</p><small>Coverage: ${(t.coverage || []).join(", ")}</small></div>`
    ).join("");
    stats(); error("");
  } catch(e) { error(e.message); }
}

async function scenarios() {
  if (!state.impact) return error("Analyze impact first.");
  try {
    state.scenarios = await api("/api/generate-scenarios", {
      method:"POST",
      body:JSON.stringify({
        ...context(),
        impact_analysis:state.impact,
        selected_tests:state.suite?.selected_tests || []
      })
    });
    $("scenario-section").classList.remove("hidden");
    $("playwright-section").classList.remove("hidden");
    $("generated-scenarios").innerHTML = (state.scenarios.scenarios || []).map(s =>
      `<div class="item"><div class="item-head"><strong>${s.id} · ${s.title}</strong>${badge(s.risk)}</div>
      <small>${s.module}</small><ul>${(s.steps || []).map(x => `<li>${x}</li>`).join("")}</ul>
      <p><strong>Expected:</strong> ${s.expected}</p></div>`
    ).join("");
    stats(); error("");
  } catch(e) { error(e.message); }
}

async function playwright() {
  try {
    const x = await api("/api/generate-playwright", {
      method:"POST",
      body:JSON.stringify({
        test_url:$("test_url").value,
        scenarios:state.scenarios?.scenarios || []
      })
    });
    $("playwright-output").textContent = x.generated_test || "";
    error("");
  } catch(e) { error(e.message); }
}

async function prepareRun() {
  try {
    const x = await api("/api/run-playwright", {
      method:"POST",
      body:JSON.stringify({
        test_url:$("test_url").value,
        scenarios:state.scenarios?.scenarios || []
      })
    });
    $("playwright-output").textContent = JSON.stringify(x, null, 2);
    error("");
  } catch(e) { error(e.message); }
}

async function health() {
  try {
    const x = await api("/health");
    $("backend-status").textContent = `Backend OK · ${x.model} · App ID: ${x.app_id}`;
  } catch(e) {
    $("backend-status").textContent = "Backend route unavailable";
  }
}

$("demo").onclick = loadDemo;
$("impact").onclick = analyze;
$("suite").onclick = suite;
$("scenarios").onclick = scenarios;
$("generate-playwright").onclick = playwright;
$("run-playwright").onclick = prepareRun;

loadDemo();
health();
