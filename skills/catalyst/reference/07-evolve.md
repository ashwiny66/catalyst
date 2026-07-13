# Evolve — strengthen a Mindspace skill (on request)

The Curator's heavier capability. **Reflect** (§4 of SKILL.md) keeps a skill *current* after every job; **Evolve** makes a skill measurably *stronger* — a deliberate optimization loop the user asks for by name ("make this skill better", "strengthen / evolve / perfect this skill"). Never in the normal flow.

**Read this file in full before you run Evolve, and adhere to it step by step.** Evolve is driven by the `evolve_skill` tool, but the tool only holds the state and hands you the next directive — *you* are the intelligence at every step (generate, judge, rewrite). **No model API, no external optimizer runs — your own reasoning does each step.** If you skip a step or lower the bar below, the result is a skill that looks changed but isn't stronger.

## The core idea

Improve the skill against test cases **derived from the skill itself**, and keep the new version **only if it measurably beats the old one on cases held back from the tuning.** No sessions are read — that's the Curator's Reflect job. Evolve is skill-in → stronger-skill-out.

The honesty comes from one discipline: you tune on the *training* cases, but the keep/discard decision is made on *holdout* cases the rewrite never saw. A skill can always be made to look good on the cases you tuned it against; only a real improvement survives the holdout.

## Show your work — Evolve is VERBOSE (the opposite of Reflect)

Reflect is silent — tool calls, no prose. **Evolve is loud.** The user asked for this pass and is watching the skill get measurably stronger; make the optimization legible, never a black box. **Narrate every step and show the numbers.** At each step surface, in prose the user can read:

- **The cases** you generated — a compact table (`task · difficulty · category`).
- **The scores** for the skill/candidate — a per-case table with `correctness / procedure / conciseness / composite` and the average. Real numbers, per case.
- **The evaluations** — for each low case, the concrete **gap**: what the skill was missing that caused the miss.
- **The rewrite** — *what* you changed and *why*: a tight diff or bullet list of the edits, not "improved it."
- **The holdout comparison** — baseline vs evolved, per case and on average, and the **improvement delta**.
- **The final diff** — the full before→after of the skill body with the score delta, before you recommend applying.

Never collapse a step to "scored and rewrote." Show the scores, the gaps, and the diff every time — that transparency *is* the point of Evolve. (This is the one place the "speak in outcomes, not implementation" rule flips: here the mechanics — scores, evaluations, diffs — are exactly what the user wants to see.)

## The loop — step through the `evolve_skill` tool

Each call returns the next directive. Do exactly what it says, then call back.

**1. `evolve_skill(action="start")`** → returns the current skill body + a directive to write test cases.
- Generate **~20 diverse test cases** *from the skill*. Each case:
  - `task_input` — a realistic task a user would actually ask that this skill should handle. **Not** a restatement of a skill heading — a real request.
  - `expected_behavior` — a rubric of what a good response must **do**: the steps, checks, and outputs that mark success. Describe success, **never echo the skill's own words** (a rubric that quotes the skill teaches nothing).
  - `difficulty` — easy | medium | hard.
  - `category` — which aspect of the skill it exercises.
- Cover the skill's whole range: easy happy-paths, medium variations, and **hard edge cases and the pitfalls the skill warns about** — that's where weakness hides.
- Submit: `evolve_skill(action="cases", cases=[...])`.

**2. Iterate.** The tool splits the cases (train / holdout), withholds the holdout, and returns the **train** tasks + the current skill body. For each iteration it asks you to score-and-rewrite:
- **Score** the skill on each train task. For each task, judge whether *following this skill* would produce a response that satisfies the rubric, on three axes (0.0–1.0 each):
  - `correctness` — would it solve the task the user asked?
  - `procedure` — would it follow the right approach/steps/checks the rubric expects?
  - `conciseness` — complete without bloat.
  - The tool combines them (`0.5·correctness + 0.3·procedure + 0.2·conciseness`). For every low case, name the **gap**: what the skill is missing that caused the miss.
  - Judge honestly. A skill that scores itself 1.0 everywhere learned nothing — hunt for the real gaps, especially on the hard cases.
  - **Show the user** the per-case score table (`correctness / procedure / conciseness / composite`) + the average, and the gap you found on each low case — before you rewrite.
- **Rewrite** the skill **body** to fix the lowest-scoring gaps: add the missing step, the unstated pitfall, the clearer instruction, the check it never mandated. Constraints, non-negotiable:
  - **Frontmatter is frozen** — never touch `name` / `description`. Only the body evolves.
  - **Smallest change that fixes the gap** — patch, don't rewrite wholesale.
  - **Keep the section structure** (headings stay) and **don't bloat** (stay within the size/growth guard the tool enforces — a rejected candidate wastes the round).
  - **Show the user** what you changed and why — a diff or a tight bullet list of the edits, tied to the gaps above. Not "improved it."
- Submit: `evolve_skill(action="iterate", scores=[...], new_body="<rewritten body>")`. The tool records the scores, stores the rewrite as the next candidate, and advances. It tells you when to score-and-rewrite again vs. when iterations are done.

**3. `evolve_skill` returns the holdout.** When iterations are exhausted the tool hands you the **holdout** tasks (unseen during tuning) plus the **baseline** body and the **best candidate** body. Score **both** on the holdout tasks, same three axes, same honesty.
- Submit: `evolve_skill(action="gate", baseline_scores=[...], candidate_scores=[...])`.

**4. The gate decides.** The tool compares the holdout averages:
- Before you gate, **show the user the holdout table** — baseline vs evolved, per case and on average, with the **improvement delta**.
- **Candidate beats baseline** → the tool writes the proposed skill. **Show the user the score delta + the full before→after diff** of the skill body (what changed and why), recommend applying, and on their yes call `evolve_skill(action="apply")` — which writes the evolved body to the skill (frontmatter preserved). **Never `apply` without the user seeing the delta + diff and saying yes.**
- **No measurable gain** → report it plainly ("no measurable improvement — keeping the current skill") and stop. **Never apply a candidate that didn't clear the holdout gate.**

`evolve_skill(action="status")` returns the current run state if you lose the thread; `action="discard"` drops the run.

## The bar (adhere — this is what separates a real Evolve from theater)

- **Real cases, honest rubrics.** Tasks are things a user would ask, not skill headings; rubrics describe success, not the skill's phrasing.
- **Judge to find gaps, not to pass.** All-1.0 scoring means you didn't look hard enough.
- **Minimal, structural rewrites.** Smallest fix; frontmatter frozen; headings kept; no bloat.
- **The holdout is the truth.** Tuning always looks good; only holdout improvement counts. Didn't beat baseline → keep baseline.
- **Narrate everything.** Every step shows its cases, its scores (per case + average), the gaps, and the diff — see "Show your work." A silent Evolve is a failed Evolve.
- **Human-approved.** The user sees the delta + diff and approves before anything is written.

## Retraining a model the Mindspace built

The same measured discipline applies when the user asks to **retrain a model** the Mindspace produced: define the success rubric, assemble the evaluation cases, score the current model, and keep a retrained version only if it **measurably beats** the incumbent on held-back cases. Same loop, same holdout honesty — the artifact is a model instead of a skill body.
