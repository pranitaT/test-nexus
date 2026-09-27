# Deployment Runbook

## Local

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
# add the team GenAI Hub key
python backend\app.py
```

## Pre-deployment checklist

- [ ] `pytest -q` passes.
- [ ] `backend/.env` is not committed.
- [ ] No real gateway key appears in source, README, screenshots or deck.
- [ ] Only mock/public evidence is loaded.
- [ ] No unapproved Azure resource is required.
- [ ] `GET /health` works.
- [ ] `GET /api/demo` works.
- [ ] AI impact analysis works through the approved GenAI Hub.
- [ ] Suite optimization works.
- [ ] Scenario generation works.
- [ ] Playwright generation works.

## Gig Garage

1. Deploy backend first using the event-provided workflow.
2. Copy the backend App ID.
3. Set the frontend backend App ID using the routing mechanism supported by Gig Garage.
4. Deploy frontend.
5. Copy frontend App ID.
6. Open browser DevTools → Network.
7. Verify frontend API calls contain the required backend App ID according to the official platform syntax.
8. Run the full demo.

Do not guess the platform's App-ID URL format. Use the exact format in the official event deployment instructions.

## Browser automation

The repository generates Playwright scaffolding but does not silently install or execute browser binaries. Enable actual browser execution only in an approved image/environment that includes the required browsers.
