# 4-Minute Judge Demo

## 0:00 — Problem

“Traditional regression treats every release the same. RegrAI asks a different question: **what changed, what evidence says it is risky, and what is the smallest suite that protects the release?**”

## 0:25 — Evidence

Load the Retail Portal scenario. Point to:
- payment code changes
- checkout user story
- timeout/duplicate defects
- payment 5xx telemetry
- previous payment failures

Say: “The model is not deciding from code alone. It sees engineering evidence from five signals.”

## 1:00 — Impact

Click **Analyze change impact**.

Point to the impact score, impacted payment module, high-risk signals and traceability.

Say: “Every decision is explainable: change → affected module → risk → evidence.”

## 1:45 — Optimized suite

Click **Build optimized suite**.

Point to selected vs deferred tests and execution reduction.

Say: “Instead of running the same regression pack, the optimizer concentrates execution on the changed and high-risk journey while explicitly showing what was deferred and why.”

## 2:30 — Coverage gaps

Click **Generate missing scenarios**.

Show the duplicate-submit and timeout-recovery scenarios.

Say: “The AI also looks for coverage gaps. These scenarios are generated from the observed risk—not generic random test cases.”

## 3:10 — Automation

Click **Generate Playwright**.

Say: “The final output is not a recommendation sitting in a dashboard. It becomes automation-ready engineering output.”

## 3:40 — Close

“RegrAI turns regression from a fixed checklist into an evidence-driven release decision: **impact, prioritize, explain, generate, automate**.”
