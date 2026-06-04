# Tool catalog — analysis & App Building surfaces

> Loaded on demand. SKILL.md keeps the lifecycle tools (flow control) + the behavioral one-liners; this is the full per-tool reference for the two workspace surfaces. The live MCP tool schemas (name/args/description) always reach you at call time — this file is the at-a-glance map of what each mode unlocks and when to reach for each.

## Analysis mode — `analysis_workspace__*` (read-only, org-scoped)

> **Scope:** Analysis is for understanding data + one-off Python scripts + scheduled jobs (crons) — **never a web app.** Building any web/app surface (page, UI, dashboard, form, frontend, backend/API endpoint) is App Building → `start_app_building(session_id=<current>)`, not an inline native-tool build here.

**Plus ALL native Claude Code tools** (Read/Write/Edit/Bash/Grep/Glob/WebSearch/WebFetch) — available in analysis for your own reasoning, scripts, and local scratch notes, NOT for building a web app (they're blocked only in App Building / vibe-edit).

| Tool | What it's for |
|---|---|
| `get_all_db_tables` | The lay of the land — every table, its description, its foreign keys. Start here. |
| `get_table_detail` | The exact columns + types of specific tables — the truth to read before you query. |
| `get_all_apis` / `get_collection_detail` | The roster of connected/known APIs and what each collection holds. |
| `get_api_endpoint_detail` | The precise shape of specific endpoints (params, models). |
| `run_select_query` | Read-only SELECT (SELECT/WITH/EXPLAIN, LIMIT required) against their live database. Only works when a database is connected. |
| `run_python` | Your notebook: pandas/numpy + a read-only `query(sql)` that returns a DataFrame straight from the DB. `df = query("SELECT …")`, then compute — cohorts, distributions, trends, correlations, outliers. State persists across calls within the project. Lifecycle modes on the same tool: `mode='interrupt'` aborts a hanging cell (keeps your namespace); `mode='restart'` bounces with explicit `max_mem_mb` (and optional `min_mem_mb`) — clears the namespace but bounds the next workload so a runaway can't take down the EC2. |
| `grep_database_context_files` | Search the DB docs the user uploaded — the source the schema was built from. |
| `grep_api_context_files` | Search the API docs the user uploaded — OpenAPI / Postman / integration notes. |
| `manage_crons` | List / add / remove / trigger per-project scheduled jobs (crons). Scripts + crons are the kind of automation that belongs in Analysis. |

## App Building mode — `coding_workspace__*` only (native tools blocked)

| Tool | Purpose |
|---|---|
| `read` | Read a file. Supports `offset` + `end_line` / `limit`. |
| `write` | Create or overwrite. |
| `edit` | Find-and-replace edit. |
| `bash` | Run a shell command in `app_root`. |
| `grep` | Search file contents. |
| `find` | List files matching a pattern. |
| `Agent` | Sub-agent for parallel investigation. |
| `web_search` | External lookup. |
| `todo_write` | Plan a multi-step change visibly. |
| `get_prd` | Read the PRD — the contract. |
| `get_repo_map` | File structure + symbol index, kept fresh by a daemon. |
| `get_existing_tables_summary` / `get_table_detail` | DB schema lookups. |
| `get_existing_apis_summary` / `get_api_endpoint_detail` | External API shapes. |
| `playwright_test` | Run a Python Playwright script — the ONLY validation tool. |

> An older `playwright_flow` JSON-step shortcut existed and was removed; `playwright_test` covers everything it could.
