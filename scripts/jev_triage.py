#!/usr/bin/env python3
"""Call TypeSafe Jev (System One) to triage emails. No personal data required."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

QUESTIONS = {
    "priority": {
        "type": "choice",
        "instructions": "How urgently must a human or system act on this email?",
        "criteria": {
            "red": "Money at risk, hard deadline, blocking failure, or angry customer needing action",
            "yellow": "Needs a reply or review soon, but not emergency",
            "green": "FYI, newsletter, promo, receipt to file, or no action",
        },
    },
    "category": {
        "type": "choice",
        "instructions": "Which category fits `subject` and `body` best?",
        "criteria": {
            "billing": "Charges, invoices, refunds, duplicate payments",
            "partnership": "Sponsorship, partnership, sales collab asks",
            "bug": "Product broken, outage, technical failure",
            "automation": "Routine bot or status alerts that are informational",
            "newsletter": "Editorial newsletters and digests",
            "promo": "Marketing and retail promotions",
            "social": "Social network notifications",
            "receipt": "Order or payment confirmations to archive",
            "personal": "Personal non-work conversation",
            "other": "None of the above",
        },
    },
    "needs_reply": {
        "type": "noul",
        "instructions": "Does the sender expect a reply?",
    },
    "needs_human": {
        "type": "noul",
        "instructions": "Should a human review before any automated reply?",
        "criteria": {
            "true": "Angry tone, missing details, high stakes, or ambiguous ask",
            "false": "Clear request that software or a template can handle",
        },
    },
}


def call_jev(api_key: str, mail: dict) -> dict:
    payload = {
        "model": MODEL,
        "state": {
            "from": mail.get("from"),
            "subject": mail.get("subject"),
            "body": mail.get("body"),
        },
        "questions": QUESTIONS,
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    ms = (time.perf_counter() - t0) * 1000
    data = json.loads(raw.decode())
    usage = data.get("usage") or {}
    tin = usage.get("input_tokens") or 0
    return {
        "id": mail.get("id"),
        "subject": mail.get("subject"),
        "model": data.get("model"),
        "latency_ms": round(ms, 1),
        "input_tokens": tin,
        "output_tokens": usage.get("output_tokens") or 0,
        "cost_usd": round(tin * 0.042 / 1e6, 8),
        "answers": data.get("answers"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage emails with TypeSafe Jev")
    parser.add_argument("--input", default="fixtures/test_emails.json")
    parser.add_argument("--output", default="out/jev_results.json")
    parser.add_argument("--summary", default="out/jev_summary.json")
    args = parser.parse_args()

    api_key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("TYPESAFE_AI_API_KEY")
    if not api_key:
        raise SystemExit("Set TYPESAFE_API_KEY (see README). Never commit the key.")

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    mails = payload["emails"] if isinstance(payload, dict) else payload

    results = []
    for mail in mails:
        try:
            results.append(call_jev(api_key, mail))
            print(f"OK {mail.get('id')} {results[-1]['latency_ms']}ms")
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:300]
            raise SystemExit(f"Jev HTTP {e.code}: {err}") from e

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    cats = Counter()
    pris = Counter()
    for r in results:
        ans = r.get("answers") or {}
        if "category" in ans:
            cats[ans["category"].get("choice")] += 1
        if "priority" in ans:
            pris[ans["priority"].get("choice")] += 1

    summary = {
        "n": len(results),
        "by_category": dict(cats),
        "by_priority": dict(pris),
        "latency_ms_avg": round(sum(r["latency_ms"] for r in results) / max(len(results), 1), 1),
        "input_tokens": sum(r["input_tokens"] for r in results),
        "cost_usd": round(sum(r["cost_usd"] for r in results), 8),
        "endpoint": API_URL,
        "model": MODEL,
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"JEV_DONE n={len(results)}")


if __name__ == "__main__":
    main()
