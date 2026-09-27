# Findings incorporated from the supplied hackathon material

## Deployment

Backend first -> capture backend App ID -> configure frontend -> frontend second.

Every network request must carry the required App ID. Missing App ID can lead to 502/503/blank-page behavior.

The exact App-ID route syntax is not present in the supplied text, so this repository isolates it instead of inventing a platform-specific format.

## GenAI Hub

The supplied starter uses:
- MODEL
- GATEWAY_BASE_URL
- GATEWAY_API_KEY

Available models stated in the supplied material:
- gpt-5-gig
- claude-sonnet-5-gig

The Flask implementation uses the OpenAI-compatible gateway server-side.

## Security

Use only approved Persistent environments.
Do not use client code, client data, client applications or client project information.
Use mock/self-created/public data.

The demo is fictional.

## Budget

Cloud: $50/team/subscription.
LLM: $10/team.

The app avoids background AI calls and unnecessary cloud resources.

## Gig Garage

Use company SSO, correct team, My Tasks, Gig Garage GitLab, Deployment and My Bids.
Mandatory submission artifacts: maximum 5-slide deck, maximum 10-minute recording, GitLab repository and IaC.

## Assigned problem

Inputs:
- source-code changes
- user stories
- defect history
- application telemetry
- previous test execution

Outputs:
- impacted modules
- high-risk tests
- optimized regression suite
- additional scenarios
- CI/CD integration path
- traceability

## SSL/Zscaler

The supplied GenAI Hub starter documents organization-approved certificate setup for Zscaler environments. This repo does not disable TLS verification. Follow the approved certificate process if needed.
