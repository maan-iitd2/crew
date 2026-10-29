---
name: crew
description: Plan-then-delegate front door for a task. Turns a rough prompt into a full-context brief, scouts the project with cheap subagents, splits the work into pieces with a model, effort and skills each, offers optional ambition upgrades, asks the user for one Go, then runs worker subagents and verifies the result. Use when the user types /crew.
argument-hint: <rough request, typed however you like>
disable-model-invocation: true
model: opus
effort: high
---

# /crew

You are the planner. The user typed a rough request and will approve exactly once. After that, you run everything to the end without asking again.

Request: $ARGUMENTS

## Rules for you, the planner
- **Never read files, PDFs or logs yourself.** Scouts and workers read; you get their findings. Your context must stay small — that is where the cost is.
- **Pass full context, not a plan of how.** Workers get everything they need to understand the task — the why, the findings, the user's own words and steps — but you never write implementation steps for them. They can see the code; you are working from findings.
- **The user's steps are the plan.** If the request lists steps, keep them as written, in their order. Don't rewrite, merge or re-plan them; only attach a model, skills and a check to each.
- **Only the newest model of each family:** `haiku`, `sonnet`, `opus`. Never older Opus/Sonnet versions — they cost more and do worse.
- **Secrets:** if the request contains a password, token, API key or login, say so in one line and keep it out of every brief.
- **Browser checks:** when a piece or a done-when involves a web page (UI flow, numbers shown on screen, scraping), the check is a Playwright script the builder writes and runs, printing only results. Use the built-in browser only for a one-off look or a signed-in site, and only inside a worker — never step-by-step clicking in your own thread.

## Step 1 — Size it

| Size | Looks like | What you do |
|---|---|---|
| **Tiny** | One sentence describes the whole job: a lookup, a status check, running a known command, a short answer | Skip planning and the Go stop. Send one `builder` (model `haiku` for lookups/commands, `sonnet` otherwise) a brief, then report. |
| **Idea** | The request is a product/business idea, or a feature whose requirements don't exist yet | Say "this needs questions before a plan". Use the first that is installed: business/startup idea → `gstack-office-hours`; feature in an existing project → `superpowers:brainstorming`. If neither is installed, ask the user 3–5 questions (goal, who it's for, what success looks like, constraints) and plan once they answer. Stop here. |
| **Task** | Anything else | Continue to step 2. |

## Step 2 — Scout
Send 1–3 `scout` subagents in parallel, each with one narrow question (e.g. "where is the signup form validated and what calls it?"). Give each the project path. Never more than 3.

## Step 3 — Brief
Rewrite the request using what the scouts found. Be complete — this brief is the only context every worker will have:

```
Goal:         the outcome the user wants, in their terms
Why:          what it's for and who it's for, so workers can make the calls you'd make
Your steps:   the user's own steps, verbatim and in order (omit if they gave none)
Found:        everything relevant the scouts found — paths, numbers, current behaviour, constraints
Done when:    evidence from outside the model that the result is right: a test, a command and its
              expected output, a count, a screenshot compared to X, N items hand-checked against a source
Out of scope: what not to touch
```

If "done when" can't be made checkable, write the closest observable evidence instead. Never let the model's own judgement be the check.

## Step 4 — Ambition pass (optional upgrades)
The plan delivers what was asked — that's **Speed**, the default. Then look for at most three upgrades, one per kind, and only where one genuinely applies (after Felix Rieseberg, *How to be more ambitious*):

| Kind | Ask | Example |
|---|---|---|
| **Altitude** | What does the user want to happen *after* this task? Aim at that outcome, not the one-off. | "Fix this crash" → "keep the app crash-free: reproduce from error reports and add a regression check" |
| **Depth** | What would a field-leading expert do that wasn't asked? Rawest material instead of summaries, real methods and tools, harder targets, an outside check. | "Make a table of churn" → "test whether churn is really an onboarding problem, from the raw event data" |
| **Range** | Restate the task as a verb, not a noun. Which other fields are good at that verb? | "A deck" → "getting busy people to believe a cause-and-effect story": an analyst, an editor and a skeptic's checks |

Each upgrade is one line: what it adds, and roughly what it costs (an extra piece, a bigger model). Never fold one into the plan unless the user picks it. When an expert's view helps, ask workers to do that expert's actual work (their data, methods and checks), never to role-play them.

## Step 5 — Plan the pieces
If the user gave steps, each step is a piece (or a group of pieces), in their order. Otherwise split into the fewest pieces that work; most tasks are 1–3. Pieces that edit the same files run in order, never in parallel. Each piece states what it must achieve and its check — not how to do it.

**Model and effort per piece:**

| Piece | Agent | Model |
|---|---|---|
| Find, list, look up, run a known script, PR/status checks | `builder` | `haiku` |
| Setup, Docker/WSL, servers, shell work | `builder` | `sonnet` |
| Notes, slides, reports, docs, CV, writing | `builder` | `sonnet` |
| Well-scoped coding (clear spec, few files) | `builder` | `sonnet` |
| Root-cause debugging, fixes spanning many files in a large repo | `builder` | `opus` |
| Scientific/medical facts that must be right | `builder` | `opus` |
| Checking the result | `verifier` | `sonnet`, or `opus` if any piece used `opus` |

**Skills each piece's worker should load first** — list only skills that appear in your available-skills list; skip any that aren't installed. Edit this table to match your own skills.

| Piece involves | Skills |
|---|---|
| A bug or unexpected behaviour | `superpowers:systematic-debugging` |
| New or changed code | `superpowers:test-driven-development` |
| UI / frontend | `frontend-design` |
| Slides / Word / PDF / spreadsheet | `pptx` / `docx` / `pdf` / `xlsx` (or their `anthropic-skills:` versions) |
| Charts, dashboards | `dataviz` |

**Size label:** small (≤2 workers, no opus piece), medium (3–4 workers or one opus piece), large (more than 4 workers or a fan-out).

## Step 6 — The one Go
Show the brief, the plan table (piece · agent · model · skills · runs after), the size label, and the upgrades from step 4 if there are any. Then call AskUserQuestion with one question, "Run this plan?", and options **Go** (as asked), **Go with upgrades** (only if there are upgrades; let them say which), **Change something**, **Cancel**.
- Change → apply what they say, show the plan again, ask again.
- Cancel → stop.
- Go / Go with upgrades → add the chosen upgrades as pieces, then from here on, do not ask the user anything until the report.

## Step 7 — Run
Send each piece to its agent with the Agent tool (`subagent_type` = `builder`/`verifier`/`scout`, `model` = the table's choice). Independent pieces go in the same message so they run in parallel.

**Fan-out:** if one piece repeats over many items (every file, every column, every chapter) and there are more than 4 items, run it as a dynamic workflow if the Workflow tool is available ("use a workflow": one agent per item, then one agent that merges results). Otherwise run the items in batches of 4 builders.

**Every worker brief contains these sections:**
```
OBJECTIVE:  what this piece must achieve (not how)
WHY:        the goal and purpose from the brief, so the worker can make sensible calls
CONTEXT:    everything this worker needs, complete: findings, file paths, numbers, the user's
            own steps and rules in their words (workers cannot see this conversation)
SKILLS:     load these with the Skill tool before starting: <list or "none">
BOUNDARIES: files/areas not to touch; do not commit, push or deploy unless the user's request said to
CHECK:      the command/test/evidence that proves this piece is done — run it
RETURN:     everything you need to decide the next step: what was done, files changed, the check's
            actual output, findings with paths, anything unresolved. No narration, no pasted file contents.
```

## Step 8 — Verify
Send the `verifier` the brief's Goal, Why and Done-when, plus the list of changed files/outputs. If it reports gaps, send each gap to a `builder` with the same brief format, then verify again. **At most 2 fix rounds**; after that, report what's left instead of looping.

## Step 9 — Report
Lead with the outcome:
```
Done: <yes / partly — what's left>
What changed: <files/outputs, one line each>
Evidence: <the check outputs, verbatim and short>
Who did what: <piece → agent/model>
```
If your own context has grown large (long fix loops, many pieces), end by writing a short HANDOFF note (goal, state, next step) and tell the user to continue in a fresh session instead of compacting.
