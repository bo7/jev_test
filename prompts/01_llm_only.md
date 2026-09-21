# Prompt A — LLM only (Codex / Claude Code / similar)

Use your configured model only. Do **not** call TypeSafe Jev or any external decision API.

## Goal
Classify every email in `fixtures/test_emails.json` (or the matching `[DEMO][CUSTOMER1]` messages in the connected inbox).

## Labels (use exactly these strings)

**priority:** `red` | `yellow` | `green`

- `red` — money at risk, hard deadline, blocking failure, or angry customer needing action  
- `yellow` — needs a reply or review soon, not an emergency  
- `green` — FYI / newsletter / promo / receipt to archive / no action  

**category:** `billing` | `partnership` | `bug` | `automation` | `newsletter` | `promo` | `social` | `receipt` | `personal` | `other`

## Output
Write `out/llm_only_results.json` as a JSON array:

```json
[
  { "id": "demo_refund", "subject": "...", "priority": "red", "category": "billing" }
]
```

Also write `out/llm_only_summary.json` with `{ "n", "by_category", "by_priority" }`.

When finished, print: `LLM_ONLY_DONE n=<count>`

Then record tokens/time from your CLI (`/status`, `/usage`, or equivalent) into `out/llm_only_metrics.json` if you can.
