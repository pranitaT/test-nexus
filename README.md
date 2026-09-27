# AI Impactathon 2026 — AI-Powered Intelligent Regression Testing

Flask-based hackathon MVP for the assigned AI regression-testing problem.

## What it does

Source changes + user story + defects + telemetry + previous test results
are sent through an explicit AI workflow:

change analysis -> impacted modules -> risk -> optimized regression suite
-> additional scenarios -> Playwright test generation -> traceability.

## Hackathon constraints reflected here

- Use approved Persistent environments/resources only.
- Use self-created/mock/public sample data.
- Do not use client code/data/applications/project information.
- Cloud budget: $50/team/subscription.
- LLM budget: $10/team.
- Use the supplied GenAI Hub gateway.
- Keep API keys server-side.
- Use the Gig Garage GitLab repository and deployment process.
- Mandatory submission artifacts include deck, demo recording, repository and IaC.

## Gateway

The supplied GenAI Hub Starter uses:

MODEL
GATEWAY_BASE_URL
GATEWAY_API_KEY

This repository follows that pattern and defaults to `gpt-5-gig`.

## Local run

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open:

http://localhost:5000

## Deployment order

1. Deploy backend first.
2. Copy backend App ID.
3. Configure the frontend with that backend App ID.
4. Deploy frontend.
5. Copy frontend App ID.
6. Verify every backend network request contains the required App ID.

The supplied material does not state the exact Gig Garage URL syntax, so App-ID route construction is isolated in:

`frontend/static/js/api.js`

Default style:

`/<BACKEND_APP_ID>/api/...`

If the official deployment guide specifies another exact shape, change that one function only.

## No unnecessary Azure services

The application uses the supplied GenAI gateway. It does not require creating Azure OpenAI or other new Azure services for the core demo.

## Demo

1. Load Demo.
2. Analyze Impact.
3. Recommend Suite.
4. Generate Scenarios.
5. Generate Playwright.
6. Show traceability.

The demo data is fictional Retail Portal data.
