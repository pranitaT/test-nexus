# RegrAI — AI-Powered Intelligent Regression Testing

A Flask + static-web application for the AI Impactathon regression-testing challenge.

## The judge story

**RegrAI does not simply generate tests. It makes a release decision explainable.**

`Evidence → Impact → Risk → Optimized Suite → Coverage Gaps → Automation`

The platform combines:
- source-code change evidence
- user story / business intent
- known defects
- application telemetry
- previous test results
- existing test catalog

It then produces an evidence-backed impact analysis, prioritizes a smaller regression suite, generates missing risk scenarios, and hands those scenarios to Playwright automation.

## What makes the demo compelling

1. **Impact score + confidence** — immediately communicates risk.
2. **Decision traceability** — shows Change → Module → Risk.
3. **Risk-aware suite optimization** — selected and deferred tests are visible.
4. **Execution economics** — estimated minutes and reduction versus the full suite.
5. **Coverage-gap generation** — AI creates targeted scenarios for the affected journey.
6. **Automation handoff** — generated Playwright is visible as the final engineering artifact.
7. **Transparent architecture** — the GenAI Hub is the only LLM gateway; no client data is required.

## Repository

```text
AI_Impactathon_Flask_Regression/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── templates/index.html
│   └── static/{css/app.css,js/app.js,js/api.js}
├── sample-data/demo-project.json
├── tests/test_app.py
├── docs/
├── iac/
├── Dockerfile
└── docker-compose.yml
```

## 1. Local setup — Windows PowerShell

```powershell
cd AI_Impactathon_Flask_Regression
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install pytest
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

Set the team GenAI Hub key in `backend/.env`. **Do not commit this file or paste the key into Git.**

Then:

```powershell
python backend\app.py
```

Open:

```text
http://localhost:5000
```

## 2. End-to-end local demo

Click in this order:

1. **Load live demo scenario**
2. **Analyze change impact**
3. Review the impacted modules, risk signals and decision traceability.
4. **Build optimized suite**
5. Review selected vs deferred tests and execution reduction.
6. **Generate missing scenarios**
7. Review the AI-generated failure-mode scenarios.
8. Enter the approved application/test URL.
9. **Generate Playwright**
10. Show the generated automation in the final panel.

This is the recommended 3–5 minute judge demonstration.

## 3. API smoke tests

PowerShell:

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod http://localhost:5000/api/demo
```

Run automated tests:

```powershell
pytest -q
```

Expected: all tests pass.

## 4. Docker

```powershell
docker build -t regr-ai .
docker run --rm -p 5000:5000 --env-file backend\.env regr-ai
```

Then open `http://localhost:5000`.

## 5. Gig Garage deployment

Follow the supplied hackathon deployment workflow and use the provided GitLab repository/environment. Do not create unapproved cloud resources.

Recommended sequence:

1. Push this repository to the assigned Gig Garage GitLab repo.
2. Deploy the **backend application first**.
3. Copy the backend App ID from the deployment result.
4. Configure the frontend with that backend App ID.
5. Deploy the frontend application.
6. Copy the frontend App ID.
7. Validate every browser network request.
8. Confirm API calls reach the backend with the required App-ID routing.
9. Run the complete demo in the deployed environment.

The exact App-ID URL syntax is platform-specific. This project centralizes routing in `frontend/static/js/api.js`; use the official Gig Garage syntax supplied by the event rather than inventing a URL format.

## 6. Secrets and constraints

- Use the approved GenAI Hub endpoint and team key supplied by the hackathon.
- Never commit the real gateway key.
- Use mock/public data only.
- Do not use client code, client data, client applications or client project information.
- Stay within the event's team LLM/cloud budget.
- Do not disable TLS verification as a shortcut for certificate issues.
- Do not add arbitrary Azure resources when the event environment does not permit them.

## 7. AI workflow

### Agent 1 — Change Impact Analyst
Inputs: code changes + user story + defects + telemetry + previous results.
Output: impacted modules, impact score, confidence, risk signals and traceability.

### Agent 2 — Regression Optimizer
Inputs: impact analysis + test catalog + evidence.
Output: selected tests, priorities, rationale, deferred tests and estimated execution time.

### Agent 3 — Coverage Gap Engineer
Inputs: impact analysis + selected tests + evidence.
Output: targeted additional regression scenarios with steps and expected results.

### Automation Handoff
The scenario objects are converted into Playwright test scaffolding. Browser execution is intentionally separated so only approved browser binaries and deployment images are used.

## 8. Architecture

```text
Browser UI
   │
   ▼
Flask API
   ├── Evidence / demo data
   ├── Impact Analyst ───────┐
   ├── Suite Optimizer       │
   ├── Scenario Generator    ├── Approved GenAI Hub
   └── Playwright Handoff ───┘
```

No database is required for the demo. The design keeps the domain logic in the backend and the presentation in the static frontend so it can be moved into an approved deployment image without introducing extra infrastructure.

## 9. Important distinction

The deterministic fallback code exists only for local UX validation when explicitly requested by the developer/tester. It is labeled in API output as `deterministic-fallback` and must not be represented as an LLM result in the judging demo.
