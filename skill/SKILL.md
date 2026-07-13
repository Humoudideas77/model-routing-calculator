---
name: model-routing-calculator
description: Recommend which model tier (mid-tier vs. top-tier) to use for a list of tasks based on complexity, and estimate the cost of that routing vs. running everything on the top-tier model. Use when the user wants to plan or justify multi-model routing across a set of tasks, estimate LLM spend, or compare a routed approach against an all-top-tier baseline.
license: MIT
user-invocable: true
---

# Model-routing cost calculator

Recommends a model tier per task by complexity, and estimates cost against
a naive "everything on the top-tier model" baseline.

## Routing rules

| Complexity        | Route                                                    | Cost vs. running the task entirely on the top-tier model |
|--------------------|-----------------------------------------------------------|-------------------------------------------------------------|
| `everyday`         | mid-tier model handles it directly                        | mid-tier rate on the task's actual tokens                   |
| `judgment-heavy`    | one top-tier call plans it, mid-tier model executes        | ~63% (lands near ~92% of top-tier-only quality)              |
| `long-unattended`   | top-tier model orchestrates, mid-tier subagents execute    | ~46% (lands near ~96% of top-tier-only quality)              |

## Running it

This skill wraps `route.py`, bundled one directory up from this file
(`SKILL_DIR/../route.py`). Locate `SKILL_DIR` as the absolute path of the
directory containing this `SKILL.md` (your harness reports this when it
reads the file), then run:

```bash
python3 "${SKILL_DIR}/../route.py" <path-to-tasks.json>
```

The script runs an assert-based self-check of its own math before
touching the input file, then prints a per-task table plus totals and %
saved vs. the naive baseline.

### Input file

A JSON file with a `pricing` table (`mid_tier`/`top_tier`, each `{in, out}`
in $ per 1,000,000 tokens — **example rates, edit to your real prices, not
facts**) and a `tasks` list (`name`, `complexity`, `input_tokens`,
`output_tokens`). See `SKILL_DIR/../examples/tasks.json` for a working
sample, or build one from the user's own task list.

### If you can't execute Python

Compute the numbers directly using the table above: multiply the task's
input/output tokens by the mid-tier or top-tier rates as directed, apply
the 63%/46% multipliers to the top-tier cost for the judgment-heavy /
long-unattended rows, then sum and compare to the naive (all top-tier)
total for the % saved.
