#!/usr/bin/env python3
"""Compare LLM-only labels vs Jev labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_map(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "emails" in data:
        data = data["emails"]
    out = {}
    for row in data:
        rid = row.get("id")
        if not rid:
            continue
        # normalize jev shape
        if "answers" in row:
            out[rid] = {
                "priority": row["answers"]["priority"]["choice"],
                "category": row["answers"]["category"]["choice"],
                "subject": row.get("subject"),
            }
        else:
            out[rid] = {
                "priority": row.get("priority"),
                "category": row.get("category"),
                "subject": row.get("subject"),
            }
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--llm", default="out/llm_only_results.json")
    p.add_argument("--jev", default="out/jev_results.json")
    p.add_argument("--out", default="out/compare.md")
    args = p.parse_args()

    llm = load_map(Path(args.llm))
    jev = load_map(Path(args.jev))
    ids = sorted(set(llm) & set(jev))
    if not ids:
        raise SystemExit("No overlapping ids between LLM and Jev results.")

    cat_ok = pri_ok = 0
    lines = [
        "# LLM-only vs Jev",
        "",
        f"Compared **{len(ids)}** emails.",
        "",
        "| id | LLM | Jev | category match | priority match |",
        "|----|-----|-----|----------------|----------------|",
    ]
    for i in ids:
        a, b = llm[i], jev[i]
        cm = a["category"] == b["category"]
        pm = a["priority"] == b["priority"]
        cat_ok += int(cm)
        pri_ok += int(pm)
        lines.append(
            f"| {i} | {a['category']}/{a['priority']} | {b['category']}/{b['priority']} | "
            f"{'yes' if cm else 'no'} | {'yes' if pm else 'no'} |"
        )
    lines += [
        "",
        f"- Category agreement: **{cat_ok}/{len(ids)}** ({100 * cat_ok / len(ids):.0f}%)",
        f"- Priority agreement: **{pri_ok}/{len(ids)}** ({100 * pri_ok / len(ids):.0f}%)",
        "",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
