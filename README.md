# jeff_test — Inbox triage: coding agent vs TypeSafe Jev

Compare **typed decision triage** with [TypeSafe Jev](https://typesafe.ai) against a **coding-agent LLM** (OpenAI Codex CLI, Claude Code, or similar) on the same small set of demo emails.

**GitHub description (suggested):**  
`Compare TypeSafe Jev vs Codex/Claude Code for inbox triage — tokens, latency, and label agreement.`

## What you need

1. A coding agent CLI with an inbox or file access (Codex, Claude Code, Cursor agent, etc.)
2. A connected mailbox **or** just the fixtures in this repo (no real PII required)
3. A TypeSafe API key for the Jev path

## Get a Jev API key

Official path (recommended):

1. Join early access / sign in at [typesafe.ai](https://typesafe.ai)
2. Create a key in the console: [console.typesafe.ai](https://console.typesafe.ai) (API Keys)
3. Export it locally — **never commit it**:

```bash
export TYPESAFE_API_KEY="your_key_here"
```

Docs and HTTP API: [TypeSafe docs](https://typesafe.ai) · endpoint `POST https://api.typesafe.ai/v1/systemone`  
Deep dive: [Flavio Copes — Jev](https://flaviocopes.com/jev/)

> Avoid unofficial reseller domains that wrap Jev behind their own keys and higher prices. Prefer `console.typesafe.ai` or Vercel AI Gateway model id `typesafe-ai/jev`.

## How the Jev API is used

Jev is a **System One** model: you send a **state** (here: from/subject/body) plus typed **questions** (`choice`, `noul`, `score`). It returns structured answers with probabilities — not free-form prose.

This repo’s `scripts/jev_triage.py` posts JSON like:

```json
{
  "model": "jev-latest",
  "state": { "from": "...", "subject": "...", "body": "..." },
  "questions": {
    "priority": { "type": "choice", "instructions": "...", "criteria": { "red": "...", "yellow": "...", "green": "..." } },
    "category": { "type": "choice", "instructions": "...", "criteria": { "billing": "...", "...": "..." } }
  }
}
```

Pricing (as publicly documented): about **$0.042 per million input tokens**, output free. Confirm on TypeSafe’s site before billing decisions.

## Demo emails

Synthetic messages live in [`fixtures/test_emails.json`](fixtures/test_emails.json):

| id | Scenario | Expected (rough) |
|----|----------|------------------|
| `demo_refund` | Duplicate charge / refund | billing + red |
| `demo_partnership` | Newsletter sponsorship | partnership + yellow |
| `demo_urgent_bug` | Angry, vague outage | bug + red (often needs human) |

Optional: send the same subjects/bodies into a connected inbox so the agent can discover them via mail tools. Prefer the fixture file for a clean public demo.

## Run the comparison with Codex (same idea for other CLIs)

From the repo root:

```bash
mkdir -p out
export TYPESAFE_API_KEY=...   # for prompt B only
```

### Prompt A — LLM only

Paste [`prompts/01_llm_only.md`](prompts/01_llm_only.md) into Codex (or Claude Code / Cursor).

Expected outputs:

- `out/llm_only_results.json`
- `out/llm_only_summary.json`
- Optional: `/status` + `/usage` (Codex) → note tokens/time in `out/llm_only_metrics.json`

### Prompt B — LLM + Jev

Paste [`prompts/02_llm_with_jev.md`](prompts/02_llm_with_jev.md).

Or run Jev directly:

```bash
python3 scripts/jev_triage.py \
  --input fixtures/test_emails.json \
  --output out/jev_results.json \
  --summary out/jev_summary.json

python3 scripts/compare_results.py \
  --llm out/llm_only_results.json \
  --jev out/jev_results.json \
  --out out/compare.md
```

### Analogous CLIs

| Tool | How to run |
|------|------------|
| OpenAI Codex | Interactive session or `codex exec -m <model> "$(cat prompts/01_llm_only.md)"` |
| Claude Code | Paste the prompt; use `/usage`-style metrics if available |
| Cursor agent | Open this folder and paste Prompt A then B |

Keep **agent orchestration tokens** separate from **Jev API tokens** when you write up results.

## License

[MIT](LICENSE) — recommended for a small public demo so others can reuse the prompts and scripts freely. You can also publish with **no license** (all rights reserved by default), but that blocks reuse.

## Safety

- Do not commit API keys, `.env`, or real mailbox exports.
- This repository ships **synthetic** fixtures only.
