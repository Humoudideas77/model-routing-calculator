# Model-routing cost calculator (paste this into a chat)

Paste this whole file into a chat with an LLM, then add your own list of
tasks (name + complexity + rough input/output token estimate) and your own
per-model pricing. Ask it to run the calculation below.

## Instructions for the assistant

You are a calculator. For each task I give you, apply these rules exactly,
show your arithmetic, and give me a total plus % saved vs. a naive baseline
where everything ran on the top-tier model. Do not skip or round silently.

**Routing rules:**

1. `everyday` complexity -> route to the mid-tier model. Cost = mid-tier
   rates applied directly to that task's input/output tokens.
2. `judgment-heavy` complexity -> route to one top-tier call that plans the
   task, then the mid-tier model executes it. Cost = 63% of what it would
   cost to run that task's tokens entirely on the top-tier model. (This
   arrangement lands near 92% of a top-tier-only result.)
3. `long-unattended` complexity -> route to the top-tier model as
   orchestrator, with mid-tier models executing the steps. Cost = 46% of
   what it would cost to run that task's tokens entirely on the top-tier
   model. (This arrangement lands near 96% of a top-tier-only result.)

**Cost formula for a given rate table `{in, out}` in $ per 1,000,000
tokens:**

```
cost = (input_tokens / 1,000,000) * rate.in + (output_tokens / 1,000,000) * rate.out
```

**Naive baseline** (for comparison only): every task's cost computed with
the top-tier rates, regardless of its actual route.

**Output:** a table of task / complexity / recommended route / estimated
cost / naive cost, then totals and `% saved = (1 - total_est / total_naive) * 100`.

**Pricing — example rates, edit me before trusting a number:**

| Tier      | $ / 1M input tokens | $ / 1M output tokens |
|-----------|----------------------|------------------------|
| mid-tier  | 3.00                 | 15.00                  |
| top-tier  | 15.00                | 75.00                   |

These are placeholders, not real prices for any provider — replace them
with current rates from your provider's pricing page before treating any
total as fact.

## Worked example

Tasks:

1. "write release notes from a changelog" — everyday — 50,000 in / 10,000 out
2. "decide the database migration approach" — judgment-heavy — 80,000 in / 20,000 out
3. "refactor the whole module overnight, unattended" — long-unattended — 300,000 in / 70,000 out

With the example rates above:

| Task                                          | Complexity       | Route                                                  | Est. cost | Naive cost (all top-tier) |
|------------------------------------------------|-------------------|----------------------------------------------------------|-----------:|-----------------------------:|
| write release notes from a changelog            | everyday          | mid-tier model (direct)                                   | 0.3000    | 1.5000                       |
| decide the database migration approach          | judgment-heavy    | top-tier advisor (1 call, plans) + mid-tier executes       | 1.7010    | 2.7000                       |
| refactor the whole module overnight, unattended | long-unattended   | top-tier orchestrates + mid-tier subagents execute         | 4.4850    | 9.7500                       |
| **TOTAL**                                       |                   |                                                            | **6.4860**| **13.9500**                  |

- Naive baseline (everything on the top-tier model): **13.9500**
- Routed estimate: **6.4860**
- Savings vs. naive baseline: **53.5%**

Now apply the same rules to my task list below (replace this line with
your tasks and your real pricing).
