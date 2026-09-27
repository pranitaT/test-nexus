# Gig Garage deployment checklist

## Backend first

Deploy the Flask backend first.

Configure:

MODEL
GATEWAY_BASE_URL
GATEWAY_API_KEY
APP_ID

Copy the backend App ID from the deployed URL.

## Frontend

Configure the backend App ID in:

frontend/static/js/api.js

Default:

`/<BACKEND_APP_ID>/api/...`

The supplied participant text does not define another exact syntax.

Deploy frontend second and capture its App ID.

## Network verification

Browser DevTools → Network.

Verify the App ID is present for:
- /api/demo
- /api/analyze-impact
- /api/recommend-suite
- /api/generate-scenarios
- /api/generate-playwright
- /api/run-playwright

502/503/blank page should trigger an App-ID route check first.

## Secret

Never expose the gateway key in frontend code or Git.
