# The ledger — follow-ups, clarifications, PRD tasks (the `todos` tool)

> **Read this when:** you're about to raise something to another employee, answer what was asked of your companion, put an approved PRD's tasks on people's lists, or report "where are we on X".

## One shared ledger

Catalyst keeps **one ToDo ledger per company**. Every employee's list is a filter over it (their name), and a Mindspace is another filter (its id). Your Wingman and every other employee's Wingman read and write the same rows — that is how work moves between people without leaving the workspace.

A row is Linear-shaped:

| field | values |
|---|---|
| `#number` | the id people use ("#42") |
| `kind` | `task` · `follow_up` · `clarification` · `prd` |
| `status` | `open` → `in_progress` (partly answered / underway) → `waiting` → `done` · `cancelled` |
| `priority` | `P0`–`P3` (default `P2`) |
| requester | who raised it — the only one who may **close** it |
| assignee | who must act — the only one who may **answer / complete** it |
| Mindspace | which problem it belongs to; `unclassified` when raised from the ScratchPad |

**Assignee is a name first.** Address a person by name or email. If they are on Catalyst the row links to them and their Wingman relays it on their next landing. If they are not, the row is still valid — name-only — and links the moment they join. Never refuse to raise something because "they're not on Catalyst".

## The tool — `todos`

| mode | what it does | who may |
|---|---|---|
| `list` | `scope=mine` (open, assigned to your companion) · `asked` (they raised) · `mindspace` (this Mindspace) · `open` (whole org). Filters: `status`, `kind`. | anyone |
| `create` | `title` (required), `kind`, `body`, `assignee` (name / email / `me`), `priority`, `due` (ISO date), `mindspace` (`current` default · `none`) | anyone |
| `answer` | `ref`, `answer`, `final` (`true` → done, `false` → partly answered) | the assignee |
| `update` | `ref` + `status` / `priority` / `due` / `assignee` / `title` | requester or assignee |
| `close` | `ref`, `outcome` (`done` · `cancelled`), `note` | the requester |
| `comment` | `ref`, `body` | anyone |
| `people` | who is on Catalyst in this org | anyone |

The tool is bound on every surface (Analyst, PM, Engineer; ScratchPad and Mindspace). In the **ScratchPad** `mindspace=current` means *none* — rows land unclassified; move to a Mindspace to classify.

## How it reaches people — the injection

You never poll the ledger. On every `/catalyst` landing (`open_scratchpad`) and every Mindspace entry, the response carries:

- `digest` — counts: `assigned_open` (waiting on your companion), `waiting_on_others` (they raised, others hold), `answers_new` (answers that came back). Turn it into **one line** in the greeting: *"Two follow-ups are waiting on you, and Sajal answered your question on Themis."* Empty → say nothing.
- `ledger_block` — the items themselves, two groups: **Waiting on YOUR companion** (open items others addressed to them — relay conversationally, then record the outcome with `answer` / `update`) and **Back on what your companion asked** (answers and completions, shown **once** — tell them, carry it into the work, then `close` what is settled).

At a Mindspace entry the block is filtered to that Mindspace; on landing it is org-wide.

## Etiquette (Polyborg rules, kept)

- A question is **self-contained** — the reader has their own context, not yours.
- Ask for the **fact**, never the reasoning behind why you want it.
- **Relay, then record.** Put the open item to your companion in their words; record their answer immediately and faithfully (`answer`). Never answer on their behalf from your own guess.
- **Close only what you raised.** An assignee marks work `done`; the requester closes the loop.
- Never delete — `cancelled` is the terminal state, with a `note`.

## The PM's program-management loop

1. `save_prd` — the approved PRD lands in the Mindspace **and** as a `prd` follow-up on your companion's own list (automatic, once per PRD file).
2. Create **one `task` per breakdown row** (`todos create kind=task`, `assignee` when the companion named one, `due` when they gave a date). Tasks sit on the same Mindspace as the PRD, so `list scope=mindspace` is the PRD's board.
3. "Where are we on X?" is answered from the ledger — `list scope=mindspace`, then the short truth: done / in progress / waiting, and on whom.
4. When the team uses an external tracker, that is a later adapter; the ledger is the source of truth today.

## Examples (shape, not script)

- *"Ask Sajal which slab applies in June"* → `create kind=clarification assignee="Sajal" title="Which JB slab applies for June?" body="For the Themis PRD's pay-out check."` → *"Logged #42 → Sajal. Their Wingman relays it on their next landing."*
- Landing shows `ledger_block` with `#42 answered by Sajal → "Jun 1–7 interim; Jun 8+ new."` → tell your companion, fold it into the PRD, `close ref=#42 note="In the PRD."`.
- Teammate: *"Priya should own the pincode upload"* → `create kind=task assignee="Priya" …` → if Priya isn't on Catalyst: *"Logged #43 → Priya. Not on Catalyst yet — it links the moment she joins."*
