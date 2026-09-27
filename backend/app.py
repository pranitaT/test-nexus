import json
import os

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

app = Flask(
    __name__,
    static_folder=os.path.join(FRONTEND_DIR, "static"),
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
)
CORS(app, resources={r"/api/*": {"origins": "*"}})

ANALYST_PROMPT = r'''
You are an AI Quality Engineering analyst.
Analyze web-application changes for regression testing.
Use only evidence supplied by the user. Do not invent facts.
Return ONLY valid JSON:
{
  "summary": "string",
  "impacted_modules": [
    {
      "module": "string",
      "change_evidence": "string",
      "impact": "High|Medium|Low",
      "confidence": 0
    }
  ],
  "risk_factors": [
    {
      "risk": "string",
      "evidence": "string",
      "severity": "High|Medium|Low"
    }
  ],
  "traceability": [
    {
      "change": "string",
      "module": "string",
      "risk": "string"
    }
  ]
}
'''

SUITE_PROMPT = r'''
You are an AI regression-test selection agent.
Select an optimized regression suite from the supplied test catalog.
Use impacted modules, risk, defects, telemetry, previous results and journey coverage.
Do not invent tests.
Return ONLY valid JSON:
{
  "strategy": "string",
  "selected_tests": [
    {
      "test_id": "string",
      "name": "string",
      "priority": "P0|P1|P2|P3",
      "reason": "string",
      "coverage": ["string"]
    }
  ],
  "deferred_tests": [
    {"test_id": "string", "reason": "string"}
  ]
}
'''

SCENARIO_PROMPT = r'''
You are a senior web test automation engineer.
Generate additional regression scenarios for affected user journeys.
Use only supplied evidence.
Return ONLY valid JSON:
{
  "scenarios": [
    {
      "id": "GEN-001",
      "title": "string",
      "module": "string",
      "risk": "High|Medium|Low",
      "preconditions": ["string"],
      "steps": ["string"],
      "expected": "string",
      "automation_candidate": true
    }
  ]
}
'''

DEMO = {
    "project_name": "Retail Portal",
    "source_changes": (
        "Changed src/checkout/payment.ts, src/checkout/PaymentForm.tsx and "
        "src/api/paymentClient.ts. Retired a legacy payment endpoint."
    ),
    "user_story": "As a customer, I want to pay by card so that I can complete checkout.",
    "defects": "Intermittent payment timeout and duplicate-submit defects.",
    "telemetry": "Payment API 5xx increased during peak traffic. Checkout abandonment is elevated.",
    "previous_results": "CheckoutPayment-01 failed twice in the last 10 runs. Login and catalog tests passed.",
    "test_catalog": [
        {"test_id": "TC-001", "name": "Login with valid user", "module": "Authentication", "risk": "Medium"},
        {"test_id": "TC-010", "name": "Browse product catalog", "module": "Catalog", "risk": "Low"},
        {"test_id": "TC-020", "name": "Add product to cart", "module": "Cart", "risk": "Medium"},
        {"test_id": "TC-030", "name": "Checkout with card", "module": "Checkout", "risk": "High"},
        {"test_id": "TC-031", "name": "Prevent duplicate payment submit", "module": "Checkout", "risk": "High"},
        {"test_id": "TC-032", "name": "Payment timeout recovery", "module": "Checkout", "risk": "High"},
        {"test_id": "TC-040", "name": "Order confirmation", "module": "Orders", "risk": "Medium"},
        {"test_id": "TC-050", "name": "Logout", "module": "Authentication", "risk": "Low"}
    ]
}

def gateway_client():
    if not GATEWAY_API_KEY:
        raise RuntimeError("GATEWAY_API_KEY is not configured.")
    return OpenAI(api_key=GATEWAY_API_KEY, base_url=GATEWAY_BASE_URL)

def ask_json(system_prompt, user_payload):
    response = gateway_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, indent=2)}
        ],
        temperature=0.1,
        max_tokens=5000,
    )
    content = (response.choices[0].message.content or "{}").strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content
        if content.endswith("```"):
            content = content[:-3].strip()
    return json.loads(content)

def playwright_code(test_url, scenarios):
    blocks = []
    for scenario in scenarios[:10]:
        title = str(scenario.get("title", "Generated regression scenario"))
        title = title.replace("\\", "\\\\").replace('"', '\\"')
        blocks.append(
            'test("' + title + '", async ({ page }) => {\n'
            '  await page.goto("' + test_url + '", { waitUntil: "domcontentloaded" });\n'
            '  await expect(page).toHaveURL(/.*/);\n'
            '});'
        )
    return "import { test, expect } from '@playwright/test';\n\n" + "\n\n".join(blocks)

@app.get("/")
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, "templates"), "index.html")

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ai-impactathon-regression-backend",
        "app_id": APP_ID,
        "model": MODEL,
        "gateway_configured": bool(GATEWAY_API_KEY)
    })

@app.get("/api/demo")
def demo():
    return jsonify(DEMO)

def _strip_app_prefix(app_id, path):
    # Allows direct App-ID-prefixed routes in addition to platform-level routing.
    # The configured APP_ID is preferred, but a non-empty prefix is accepted so
    # Gig Garage can terminate the route without requiring application changes.
    return path


def _forward_json_api(handler):
    return handler()


@app.route("/<app_id>/api/<path:api_path>", methods=["GET", "POST", "OPTIONS"])
def app_id_api(app_id, api_path):
    # The frontend's App-ID route is deployment-specific. If Gig Garage passes
    # the App ID through to Flask, dispatch the same API endpoints here.
    if api_path == "demo" and request.method == "GET":
        return demo()
    if api_path == "analyze-impact" and request.method == "POST":
        return analyze_impact()
    if api_path == "recommend-suite" and request.method == "POST":
        return recommend_suite()
    if api_path == "generate-scenarios" and request.method == "POST":
        return generate_scenarios()
    if api_path == "generate-playwright" and request.method == "POST":
        return generate_playwright()
    if api_path == "run-playwright" and request.method == "POST":
        return run_playwright()
    return jsonify({"error": "Unknown App-ID API route"}), 404


@app.post("/api/analyze-impact")
def analyze_impact():
    try:
        body = request.get_json(silent=True) or {}
        return jsonify(ask_json(ANALYST_PROMPT, body))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

@app.post("/api/recommend-suite")
def recommend_suite():
    try:
        body = request.get_json(silent=True) or {}
        return jsonify(ask_json(SUITE_PROMPT, body))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

@app.post("/api/generate-scenarios")
def generate_scenarios():
    try:
        body = request.get_json(silent=True) or {}
        return jsonify(ask_json(SCENARIO_PROMPT, body))
    except Exception as exc:
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
    return jsonify({
        "status": "GENERATED_NOT_EXECUTED",
        "reason": "Playwright code is ready. Install approved Playwright/browser binaries in the execution image before enabling browser execution.",
        "generated_test": playwright_code(url, body.get("scenarios", []))
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
