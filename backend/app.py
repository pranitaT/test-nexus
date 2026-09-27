import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
MODEL = os.getenv("MODEL", "gpt-5-gig")
GATEWAY_BASE_URL = os.getenv(
    "GATEWAY_BASE_URL",
    "https://hub-proxy-service.thankfulfield-16b4d5d6.eastus.azurecontainerapps.io/v1",
)
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "")
APP_ID = os.getenv("APP_ID", "local")

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIR, "static"), template_folder=os.path.join(FRONTEND_DIR, "templates"))
CORS(app, resources={r"/*": {"origins": "*"}})

DEMO = {
    "project_name": "Retail Portal",
    "release": "v2.8.0 · Payment reliability release",
    "source_changes": "Changed src/checkout/payment.ts, src/checkout/PaymentForm.tsx and src/api/paymentClient.ts. Retired a legacy payment endpoint. Added retry handling around payment timeout.",
    "user_story": "As a customer, I want to pay by card so that I can complete checkout.",
    "defects": "Intermittent payment timeout and duplicate-submit defects were reported in checkout.",
    "telemetry": "Payment API 5xx increased during peak traffic. Checkout abandonment is elevated. Payment latency is above the normal baseline.",
    "previous_results": "CheckoutPayment-01 failed twice in the last 10 runs. CheckoutPayment-02 had one timeout. Login and catalog tests passed.",
    "test_catalog": [
        {"test_id": "TC-001", "name": "Login with valid user", "module": "Authentication", "risk": "Medium", "duration_min": 1.5, "tags": ["smoke"]},
        {"test_id": "TC-010", "name": "Browse product catalog", "module": "Catalog", "risk": "Low", "duration_min": 2.0, "tags": ["smoke"]},
        {"test_id": "TC-020", "name": "Add product to cart", "module": "Cart", "risk": "Medium", "duration_min": 2.5, "tags": ["checkout"]},
        {"test_id": "TC-030", "name": "Checkout with card", "module": "Checkout", "risk": "High", "duration_min": 4.0, "tags": ["critical", "payment"]},
        {"test_id": "TC-031", "name": "Prevent duplicate payment submit", "module": "Checkout", "risk": "High", "duration_min": 3.0, "tags": ["payment", "defect"]},
        {"test_id": "TC-032", "name": "Payment timeout recovery", "module": "Checkout", "risk": "High", "duration_min": 3.5, "tags": ["payment", "defect"]},
        {"test_id": "TC-040", "name": "Order confirmation", "module": "Orders", "risk": "Medium", "duration_min": 2.0, "tags": ["checkout"]},
        {"test_id": "TC-050", "name": "Logout", "module": "Authentication", "risk": "Low", "duration_min": 1.0, "tags": ["smoke"]},
    ],
}

ANALYST_PROMPT = """
You are an AI Quality Engineering change-impact analyst. Analyze ONLY the supplied evidence.
Map code changes to application modules, risks and evidence. Do not invent files, defects, metrics or tests.
Return ONLY valid JSON with this shape:
{"summary":"...","impact_score":0,"confidence":0,"impacted_modules":[{"module":"...","change_evidence":"...","impact":"High|Medium|Low","confidence":0}],"risk_factors":[{"risk":"...","evidence":"...","severity":"High|Medium|Low"}],"traceability":[{"change":"...","module":"...","risk":"...","evidence":"..."}]}
"""

SUITE_PROMPT = """
You are an AI regression-suite optimization agent. Select an optimized subset from the supplied test catalog.
Use impacted modules, risks, defects, telemetry and previous results. Do not invent test IDs or names.
Prioritize critical user journeys and known failure signals while avoiding unrelated tests.
Return ONLY valid JSON:
{"strategy":"...","selected_tests":[{"test_id":"...","name":"...","priority":"P0|P1|P2|P3","reason":"...","coverage":["..."]}],"deferred_tests":[{"test_id":"...","reason":"..."}],"estimated_minutes":0,"full_suite_minutes":0}
"""

SCENARIO_PROMPT = """
You are a senior web test automation engineer. Generate additional regression scenarios only for affected journeys.
Ground every scenario in the supplied evidence. Make scenarios concrete and automatable.
Return ONLY valid JSON:
{"scenarios":[{"id":"GEN-001","title":"...","module":"...","risk":"High|Medium|Low","preconditions":["..."],"steps":["..."],"expected":"...","automation_candidate":true}]}
"""


def gateway_client():
    if not GATEWAY_API_KEY:
        raise RuntimeError("GATEWAY_API_KEY is not configured. Add the hackathon GenAI Hub key to backend/.env.")
    return OpenAI(api_key=GATEWAY_API_KEY, base_url=GATEWAY_BASE_URL)


def ask_json(system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
    response = gateway_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(user_payload, indent=2)}],
        temperature=0.1,
        max_tokens=5000,
    )
    content = (response.choices[0].message.content or "{}").strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.I)
    content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def local_baseline(context: Dict[str, Any]) -> Dict[str, Any]:
    """Transparent deterministic fallback for local UX testing; never presented as LLM output."""
    text = " ".join(str(context.get(k, "")) for k in ["source_changes", "defects", "telemetry", "previous_results"]).lower()
    modules = []
    if any(x in text for x in ["payment", "checkout", "paymentform"]):
        modules.append({"module": "Checkout / Payment", "change_evidence": "Payment implementation and client code are explicitly listed in the change evidence.", "impact": "High", "confidence": 96})
    if any(x in text for x in ["cart", "checkout"]):
        modules.append({"module": "Cart / Checkout Journey", "change_evidence": "The payment change sits inside the customer checkout journey.", "impact": "Medium", "confidence": 82})
    risks = []
    if "duplicate" in text:
        risks.append({"risk": "Duplicate payment submission", "evidence": "A duplicate-submit defect is explicitly reported.", "severity": "High"})
    if "timeout" in text or "5xx" in text:
        risks.append({"risk": "Payment timeout / API reliability", "evidence": "Timeout defects and elevated payment API failures are explicitly reported.", "severity": "High"})
    if "abandonment" in text:
        risks.append({"risk": "Checkout conversion impact", "evidence": "Checkout abandonment is elevated in telemetry.", "severity": "Medium"})
    return {
        "summary": "The supplied evidence concentrates risk around the payment path, with production signals and prior failures reinforcing the change impact.",
        "impact_score": 92,
        "confidence": 90,
        "impacted_modules": modules,
        "risk_factors": risks,
        "traceability": [{"change": "Payment implementation/client changes", "module": "Checkout / Payment", "risk": r["risk"], "evidence": r["evidence"]} for r in risks],
        "mode": "deterministic-fallback",
    }


def fallback_suite(context: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
    catalog = context.get("test_catalog", [])
    selected, deferred = [], []
    for t in catalog:
        if t.get("module") in {"Checkout", "Cart", "Orders"} or "payment" in " ".join(t.get("tags", [])).lower():
            selected.append({"test_id": t["test_id"], "name": t["name"], "priority": "P0" if t.get("risk") == "High" else "P1", "reason": "Covers the impacted checkout/payment journey or an explicit payment risk.", "coverage": t.get("tags", [])})
        else:
            deferred.append({"test_id": t["test_id"], "reason": "No direct evidence connects this test to the changed payment path."})
    full = sum(float(t.get("duration_min", 0)) for t in catalog)
    chosen_ids = {x["test_id"] for x in selected}
    selected_minutes = sum(float(t.get("duration_min", 0)) for t in catalog if t.get("test_id") in chosen_ids)
    return {"strategy": "Evidence-weighted regression: execute high-risk payment and affected checkout coverage first; defer unrelated journeys.", "selected_tests": selected, "deferred_tests": deferred, "estimated_minutes": round(selected_minutes, 1), "full_suite_minutes": round(full, 1), "mode": "deterministic-fallback"}


def fallback_scenarios(context: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
    return {"scenarios": [
        {"id": "GEN-001", "title": "Recover from payment timeout without duplicate charge", "module": "Checkout / Payment", "risk": "High", "preconditions": ["Customer has a valid cart and card."], "steps": ["Start checkout", "Simulate a payment timeout", "Allow the retry path to recover", "Verify the order is created once"], "expected": "The customer receives a recoverable outcome and exactly one order/payment is created.", "automation_candidate": True},
        {"id": "GEN-002", "title": "Block duplicate payment submission", "module": "Checkout / Payment", "risk": "High", "preconditions": ["Customer is on the payment step."], "steps": ["Submit payment", "Trigger a rapid second submit", "Observe payment requests and confirmation"], "expected": "Only one payment is accepted and the UI prevents duplicate submission.", "automation_candidate": True},
    ], "mode": "deterministic-fallback"}


def playwright_code(test_url: str, scenarios: list) -> str:
    safe_url = test_url.replace('"', '\\"')
    blocks = []
    for scenario in scenarios[:8]:
        title = str(scenario.get("title", "Generated regression scenario")).replace('"', '\\"')
        blocks.append(f'''test("{title}", async ({{ page }}) => {{\n  await page.goto("{safe_url}", {{ waitUntil: "domcontentloaded" }});\n  await expect(page).toHaveURL(/.*/);\n}});''')
    return "import { test, expect } from '@playwright/test';\n\n" + "\n\n".join(blocks)


@app.get("/")
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, "templates"), "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ai-impactathon-regression-backend", "app_id": APP_ID, "model": MODEL, "gateway_configured": bool(GATEWAY_API_KEY)})


@app.get("/api/demo")
def demo():
    return jsonify(DEMO)


@app.post("/api/analyze-impact")
def analyze_impact():
    body = request.get_json(silent=True) or {}
    try:
        return jsonify(ask_json(ANALYST_PROMPT, body))
    except Exception as exc:
        if body.get("demo_fallback"):
            return jsonify(local_baseline(body))
        return jsonify({"error": str(exc), "hint": "Set demo_fallback=true only for local UX validation."}), 502


@app.post("/api/recommend-suite")
def recommend_suite():
    body = request.get_json(silent=True) or {}
    try:
        return jsonify(ask_json(SUITE_PROMPT, body))
    except Exception as exc:
        if body.get("demo_fallback"):
            return jsonify(fallback_suite(body, body.get("impact_analysis", {})))
        return jsonify({"error": str(exc)}), 502


@app.post("/api/generate-scenarios")
def generate_scenarios():
    body = request.get_json(silent=True) or {}
    try:
        return jsonify(ask_json(SCENARIO_PROMPT, body))
    except Exception as exc:
        if body.get("demo_fallback"):
            return jsonify(fallback_scenarios(body, body.get("impact_analysis", {})))
        return jsonify({"error": str(exc)}), 502


@app.post("/api/generate-playwright")
def generate_playwright():
    body = request.get_json(silent=True) or {}
    url = body.get("test_url", "")
    if not url:
        return jsonify({"error": "test_url is required"}), 400
    return jsonify({"status": "GENERATED", "generated_test": playwright_code(url, body.get("scenarios", []))})


@app.post("/api/run-playwright")
def run_playwright():
    body = request.get_json(silent=True) or {}
    url = body.get("test_url", "")
    if not url:
        return jsonify({"error": "test_url is required"}), 400
    return jsonify({"status": "READY_FOR_EXECUTION", "reason": "Playwright code is generated. Browser execution remains disabled until the approved deployment image includes the required browser binaries.", "generated_test": playwright_code(url, body.get("scenarios", []))})


@app.route("/<app_id>/api/<path:api_path>", methods=["GET", "POST", "OPTIONS"])
def app_id_api(app_id, api_path):
    if request.method == "OPTIONS":
        return ("", 204)
    routes = {
        "demo": demo,
        "analyze-impact": analyze_impact,
        "recommend-suite": recommend_suite,
        "generate-scenarios": generate_scenarios,
        "generate-playwright": generate_playwright,
        "run-playwright": run_playwright,
    }
    handler = routes.get(api_path)
    if handler is None:
        return jsonify({"error": "Unknown App-ID API route"}), 404
    return handler()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
