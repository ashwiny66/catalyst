# Flow & tools — transitions, lifecycle, and the per-stage surfaces

> **What this is.** SKILL.md teaches *judgment* and names the stages; it deliberately doesn't list tools. This file is the operational map — the **transition** tools that move between stages, the **lifecycle** tools that work from any stage, and which **work surface** each stage unlocks. The live MCP schemas (name / args / description) always reach you at call time; reach for this when you need the at-a-glance "what moves me where."

## Transitions — enter a stage

You never track the stage yourself; you call a transition and the surface follows. A blocked tool's error names the transition to call.

| Transition | Enters | Notes |
|---|---|---|
| `start_analysis()` | **Discover** | Fresh read-only, org-scoped Mindspace. Binds `analysis_workspace__*` + all native tools + `run_python`. |
| `start_spec(msg)` | **Spec** | Shape a plan *with the user*, in conversation — a new build that needs shaping, or re-planning an existing app. You author the plan; hand to Build when they say yes. |
| `start_app_building(session_id?, prompt?, app_name?)` | **Build** | **With `session_id`** → continue THAT Mindspace (Discover→Build or Spec→Build), keeping its id + scaffolding the app on entry. **Without** → a fresh greenfield Mindspace. Pass the agreed plan as `prompt`. Drops into `coding_workspace__*`. |

**One Mindspace, many stages.** Moving between stages NEVER makes a new Mindspace — the id is stable. Entering a stage with nothing active CREATES the Mindspace; while one is active you CONTINUE it. Only `switch_mindspace` starts (or resumes) a *different* one.

## Lifecycle — stage-agnostic, safe from any tab

| Tool | Purpose |
|---|---|
| `ensure_auth` / `login` / `wait_for_login` / `logout` | The auth gate (see SKILL → Routing → Auth). `ensure_auth` is your first call, every activation. |
| `health_check` | Entry readiness; `ready_to_build: false` → read `fix_required` to the user and stop. |
| `list_mindspaces` | The shelf — render with full session_ids, never truncated. |
| `current_session` | "What am I in right now?" → `{active, mode, session_id, app_root}`. Safe from any tab. |
| `switch_mindspace(target_session_id?, confirm_clear_current?)` | **Non-destructive** pause/resume or clean slate — the primitive for "switch" / "step away" / "build new". Mid-Spec it may return `needs_confirm_clear_current` first; warn it can rewind a question or two, then re-call with `confirm_clear_current=true`. |
| `abandon_build(reason?)` (alias `end`) | Destructive — wipes local session state + marks the row abandoned. Works from any tab. Resurrectable. Only on an explicit "end / abandon / kill it." |
| `complete_build(summary)` | Finalize a build after the completion JSON — runs migrations, boots the dev servers, returns the URLs. Idempotent (a Stop hook also fires it as a safety net). |
| `mindspace_skill(mode)` | THIS Mindspace's durable skill (how the area works) — router + references. Read on entry; write a reference as you learn. (Bound in Discover + Build.) |
| `mindspace_memory(mode)` | THIS Mindspace's living memory (facts that proved true) — index + facts. Recall on entry; save the moment you learn. (Bound in Discover + Build.) |

## Work surfaces — one per stage

- **Discover → `analysis_workspace__*`** (read-only, org-scoped) **plus all native Claude Code tools** + `run_python` (pandas + a read-only `query(sql)→DataFrame`, state persisting across calls). For understanding their data + one-off scripts + scheduled jobs — **never a web app** (that's Build).
- **Build → `coding_workspace__*` only** (native file/shell tools blocked) — the full making surface: read / write / edit / bash / grep / find, `get_prd` (the contract), `get_repo_map` (daemon-fresh index), `run_python`, `run_select_query`, `playwright_test` (the one validation tool), **plus the automation families — jobs, scheduled jobs, subagents (autonomous AI checks), triggers.** A script, job, AI check, ML model, or web app all build here.
- Both stages also expose the user's **connected external tools** (discover → execute) and `mindspace_skill` / `mindspace_memory`.

Full per-tool catalog → `05-tools.md`.

## Status (the MCP writes it; you read it only for sanity)

`spec → db_finalize → generate → completed`. Treat `{completed, error, abandoned, generate-interrupted}` as equivalent — same actions available, nothing terminal.
