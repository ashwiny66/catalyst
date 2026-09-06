# The ledger — clarifications, requests, PRDs (the `todos` tool)

> **Read this when:** you're about to raise something to another employee, answer what was asked of your companion, set up or use the org's project-management tool, or report "where are we on X".

## One shared ledger

Catalyst keeps **one ToDo ledger per company**. Every employee's list is a filter over it (their user id), and a Mindspace is another filter (its id). Your Wingman and every other employee's Wingman read and write the same rows — that is how work moves between people without leaving the workspace.

**Each row is a conversation** between the requester and the assignee (their Wingmen relay both sides). Three kinds:

| kind | what it is |
|---|---|
| `clarification` | a question only that person can answer |
| `request` | work that person must do |
| `prd` | one task per saved PRD — the PRD's own requirement rows live in the org's **project-management tool**, never as ledger rows |

**Status is whose move it is** — the only vocabulary anyone sees, derived per viewer:

- **Waiting for your response** — the ball is with you (addressed to you and unanswered, or your ask came back and it's your move).
- **Waiting for <name>'s response** — you raised it; the ball is with them.
- **You replied** — you answered; it's with the other side now.
- **Completed** (or **Cancelled**).

Every `answer` or `comment` by one side hands the ball to the other, and every state change is a timestamped event — the row's thread is its comments and events in order.

**Assignee is a person, exactly.** `mode='people'` lists everyone on Catalyst in the org with their `user_id` — pass it as `assignee_user_id` so the row is stamped to precisely the right person. A name or email also works (unique match links it); someone not on Catalyst stays name-only and links the moment they join. Never refuse to raise something because "they're not on Catalyst".

## The tool — `todos`

| mode | what it does | who may |
|---|---|---|
| `list` | `scope=mine` (on your companion) · `asked` (they raised) · `mindspace` (this Mindspace) · `open` (whole org). Filters: `status`, `kind`. | anyone |
| `people` | everyone in the org with `user_id · name · email` — look up before addressing | anyone |
| `create` | `title` (required), `kind` (`clarification` · `request`), `body`, `assignee_user_id` (from people) or `assignee` (name / email / `me`), `priority`, `due`, `mindspace` (`current` default · `none`) | anyone |
| `answer` | `ref`, `answer`, `final` (`true` → Completed, `false` → a reply; ball to them) | the assignee |
| `comment` | `ref`, `body` — a reply in the thread; hands the ball to the other side | anyone (a third party's comment moves no ball) |
| `update` | `ref` + `status` / `priority` / `due` / `assignee_user_id` / `assignee` / `title` | requester or assignee |
| `close` | `ref`, `outcome` (`done` · `cancelled`), `note` | the requester |
| `tracker` | the org's project-management tool + how tasks are stored there | anyone |
| `tracker_set` | save that convention (`app`, `instructions`) after asking your companion | anyone |

The tool is bound on every surface (Analyst, PM, Engineer; ScratchPad and Mindspace). In the **ScratchPad** `mindspace=current` means *none* — rows land unclassified; move to a Mindspace to classify.

## How it reaches people — the injection

You never poll the ledger. On every `/catalyst` landing (`open_scratchpad`) and every Mindspace entry, the response carries:

- `digest` — counts: `assigned_open` (waiting for your companion's response), `waiting_on_others` (their asks the other side holds), `answers_new` (what came back). Turn it into **one line** in the greeting: *"Two things are waiting on you, and Sajal answered your question on Themis."* Empty → say nothing.
- `ledger_block` — the items themselves, two groups: **Waiting for your companion's response** (their move — relay conversationally, then record with `answer` / `comment` / `update` / `close`) and **Back on what they asked** (answers and completions, shown **once** — tell them, carry it into the work, then `close` what is settled).

At a Mindspace entry the block is filtered to that Mindspace; on landing it is org-wide.

## Etiquette (Polyborg rules, kept)

- A question is **self-contained** — the reader has their own context, not yours.
- Ask for the **fact**, never the reasoning behind why you want it.
- **Relay, then record.** Put the open item to your companion in their words; record their answer immediately and faithfully (`answer`). Never answer on their behalf from your own guess.
- **Close only what you raised.** An assignee replies and completes; the requester closes the loop.
- Never delete — `cancelled` is the terminal state, with a `note`.

## The org's project-management tool

One connected app can be **marked as where the company tracks work**, with free-text instructions for HOW — companies differ (one folder or initiative per quarter; a space per team; "always ask which sprint"). `todos` mode='tracker' reads it; the Tools setup writes it, and so can you (`tracker_set`) after asking your companion. **If the convention isn't set up, always ask how and where tasks should be stored — then save what you learned.**

**The two Catalyst references are YOUR rule, not the convention's.** On every task you create in that tool, stamp the **Mindspace id** and the **PRD id** as custom fields — find them or create them (`external_tools_discover` → `external_tools_execute`); a tool without custom fields carries both in the task body. That stamp is how any Wingman later finds the work from the Mindspace, whatever the org's filing habits.

## The PM's tracking loop

1. `save_prd` — the approved PRD lands in the Mindspace's PRD folder **and** as one `prd` task on your companion's list (automatic, once per PRD file). Its return carries the PRD id, the Mindspace id, and the org's tracker convention.
2. Create **one task per Requirements-table row** in the org's project-management tool, per the convention (ask what it leaves open — which quarter's folder, say). Stamp both Catalyst references on each.
3. **Write back**: add each created task's ID to the PRD's Requirements table (an '<App> ID' column) and re-save the PRD (same name — it updates in place). The PRD now says where every row is tracked.
4. *"Where are we on X?"* — read the PRD's Requirements table, query the tool by those IDs, and answer in their words: done / in progress / waiting, and on whom.
5. No tool marked → the breakdown stays inside the PRD; the `prd` row on the ledger is the single tracked item.

## Examples (shape, not script)

- *"Ask Sajal which slab applies in June"* → `people` (find Sajal's user_id) → `create kind=clarification assignee_user_id=<id> title="Which JB slab applies for June?" body="For the Themis PRD's pay-out check."` → *"Logged #42 → Sajal. Their Wingman relays it on their next landing."*
- Landing shows `#42 replied by Sajal → "Jun 1–7 interim; Jun 8+ new."` → tell your companion, fold it into the PRD, `close ref=#42 note="In the PRD."`.
- Sajal's reply raises a counter-question → `comment ref=#42 body="June — payouts week only."` — the ball goes back to Sajal, timestamped.
- *"Priya should own the pincode upload"* → `create kind=request assignee="Priya" …` → if Priya isn't on Catalyst: *"Logged #43 → Priya. Not on Catalyst yet — it links the moment she joins."*
