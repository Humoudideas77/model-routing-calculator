#!/usr/bin/env python3
"""
Model-routing cost calculator.

Routes a list of tasks to a model tier by complexity, estimates cost per
task and in total, and compares against a naive "everything on the top
model" baseline.

Routing rules:
  everyday          -> mid-tier model handles it directly.
  judgment-heavy     -> one top-tier call plans it, mid-tier executes.
                        (in practice this lands near 92% of top-tier-only
                        quality at roughly 63% of top-tier-only cost)
  long-unattended    -> top-tier model orchestrates, mid-tier subagents
                        execute the steps.
                        (roughly 96% of top-tier-only quality at roughly
                        46% of top-tier-only cost)

Pricing is supplied by the user in the input JSON (see examples/tasks.json)
and is NOT hardcoded here — this tool computes on whatever rates you give
it. Treat any example rates as placeholders, not real prices.

Usage:
    python3 route.py <tasks.json>

No third-party dependencies. Stdlib only.
"""
from __future__ import annotations

import json
import sys

EVERYDAY = "everyday"
JUDGMENT_HEAVY = "judgment-heavy"
LONG_UNATTENDED = "long-unattended"

# cost_ratio: fraction of the naive "whole task on top-tier" cost this
# route actually spends. quality_ratio: informational only, from the
# published routing results this tool encodes.
ROUTES = {
    EVERYDAY: {
        "recommended": "mid-tier model (direct)",
        "cost_ratio": None,  # computed directly from mid-tier rates instead
        "quality_note": "baseline (task never touches the top-tier model)",
    },
    JUDGMENT_HEAVY: {
        "recommended": "top-tier advisor (1 call, plans) + mid-tier executes",
        "cost_ratio": 0.63,
        "quality_note": "~92% of a top-tier-only result",
    },
    LONG_UNATTENDED: {
        "recommended": "top-tier orchestrates + mid-tier subagents execute",
        "cost_ratio": 0.46,
        "quality_note": "~96% of a top-tier-only result",
    },
}


def mtoken_cost(input_tokens: float, output_tokens: float, rates: dict) -> float:
    """Cost in currency units for input_tokens/output_tokens at rates
    given as $-per-million-tokens: {"in": ..., "out": ...}."""
    return (input_tokens / 1_000_000.0) * rates["in"] + (output_tokens / 1_000_000.0) * rates["out"]


def route_task(task: dict, pricing: dict) -> dict:
    complexity = task.get("complexity")
    if complexity not in ROUTES:
        raise ValueError(
            f"unknown complexity {complexity!r} for task {task.get('name', '?')!r}; "
            f"expected one of {sorted(ROUTES)}"
        )
    input_tokens = task["input_tokens"]
    output_tokens = task["output_tokens"]

    naive_cost = mtoken_cost(input_tokens, output_tokens, pricing["top_tier"])
    route = ROUTES[complexity]

    if complexity == EVERYDAY:
        est_cost = mtoken_cost(input_tokens, output_tokens, pricing["mid_tier"])
    else:
        est_cost = naive_cost * route["cost_ratio"]

    return {
        "name": task.get("name", "(unnamed task)"),
        "complexity": complexity,
        "recommended": route["recommended"],
        "quality_note": route["quality_note"],
        "est_cost": est_cost,
        "naive_cost": naive_cost,
    }


def build_report(tasks: list, pricing: dict) -> dict:
    rows = [route_task(t, pricing) for t in tasks]
    total_est = sum(r["est_cost"] for r in rows)
    total_naive = sum(r["naive_cost"] for r in rows)
    pct_saved = 0.0 if total_naive == 0 else (1 - total_est / total_naive) * 100
    return {"rows": rows, "total_est": total_est, "total_naive": total_naive, "pct_saved": pct_saved}


def print_report(report: dict) -> None:
    rows = report["rows"]
    name_w = max([len("Task")] + [len(r["name"]) for r in rows]) + 2
    comp_w = max([len("Complexity")] + [len(r["complexity"]) for r in rows]) + 2
    route_w = max([len("Recommended route")] + [len(r["recommended"]) for r in rows]) + 2

    header = f"{'Task':<{name_w}}{'Complexity':<{comp_w}}{'Recommended route':<{route_w}}{'Est. cost':>12}{'Naive cost':>12}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['name']:<{name_w}}{r['complexity']:<{comp_w}}{r['recommended']:<{route_w}}"
            f"{r['est_cost']:>12.4f}{r['naive_cost']:>12.4f}"
        )
    print("-" * len(header))
    print(f"{'TOTAL':<{name_w + comp_w + route_w}}{report['total_est']:>12.4f}{report['total_naive']:>12.4f}")
    print()
    print(f"Naive baseline (everything on the top-tier model): {report['total_naive']:.4f}")
    print(f"Routed estimate:                                    {report['total_est']:.4f}")
    print(f"Savings vs. naive baseline:                         {report['pct_saved']:.1f}%")


def selftest() -> None:
    """Assert-based check of the routing + cost math. Run on every
    invocation so a broken formula fails loudly before it ever quotes
    a number."""
    pricing = {"mid_tier": {"in": 3.0, "out": 15.0}, "top_tier": {"in": 15.0, "out": 75.0}}

    everyday = route_task(
        {"name": "e", "complexity": EVERYDAY, "input_tokens": 100_000, "output_tokens": 20_000}, pricing
    )
    # mid-tier direct: (0.1M * 3) + (0.02M * 15) = 0.3 + 0.3 = 0.6
    assert abs(everyday["est_cost"] - 0.6) < 1e-9, everyday
    # naive top-tier: (0.1M * 15) + (0.02M * 75) = 1.5 + 1.5 = 3.0
    assert abs(everyday["naive_cost"] - 3.0) < 1e-9, everyday

    judgment = route_task(
        {"name": "j", "complexity": JUDGMENT_HEAVY, "input_tokens": 100_000, "output_tokens": 20_000}, pricing
    )
    assert abs(judgment["naive_cost"] - 3.0) < 1e-9, judgment
    assert abs(judgment["est_cost"] - 3.0 * 0.63) < 1e-9, judgment

    long_task = route_task(
        {"name": "l", "complexity": LONG_UNATTENDED, "input_tokens": 100_000, "output_tokens": 20_000}, pricing
    )
    assert abs(long_task["naive_cost"] - 3.0) < 1e-9, long_task
    assert abs(long_task["est_cost"] - 3.0 * 0.46) < 1e-9, long_task

    report = build_report(
        [
            {"name": "e", "complexity": EVERYDAY, "input_tokens": 100_000, "output_tokens": 20_000},
            {"name": "j", "complexity": JUDGMENT_HEAVY, "input_tokens": 100_000, "output_tokens": 20_000},
        ],
        pricing,
    )
    assert abs(report["total_naive"] - 6.0) < 1e-9, report
    assert abs(report["total_est"] - (0.6 + 3.0 * 0.63)) < 1e-9, report
    expected_pct = (1 - report["total_est"] / report["total_naive"]) * 100
    assert abs(report["pct_saved"] - expected_pct) < 1e-9, report

    try:
        route_task({"name": "bad", "complexity": "unknown", "input_tokens": 1, "output_tokens": 1}, pricing)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unknown complexity")

    print("[selftest] routing + cost math OK", file=sys.stderr)


def main() -> None:
    selftest()

    if len(sys.argv) < 2:
        print("usage: python3 route.py <tasks.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    pricing = data["pricing"]
    tasks = data["tasks"]
    report = build_report(tasks, pricing)
    print_report(report)


if __name__ == "__main__":
    main()
