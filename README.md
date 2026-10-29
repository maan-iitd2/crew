# /crew

A Claude Code skill that turns one rough prompt into planned, delegated, verified work. Opus plans, cheaper models do the pieces, and you approve once.

```
/crew the signup form accepts empty emails, find out why and fix it
```

1. **Sizes the task.** Tiny jobs skip planning and go straight to one cheap worker. Vague ideas get questions first instead of a plan built on guesses.
2. **Scouts.** 1–3 Haiku agents map the relevant files. The planner never reads files itself, which keeps its context small.
3. **Writes a full-context brief:** goal, why, your own steps verbatim, everything the scouts found, a *done when* check that doesn't rely on the model's judgement, and what's out of scope. It passes full context but never plans the how; if you listed steps, those are the plan.
4. **Suggests optional upgrades,** using the four kinds of ambition from Felix Rieseberg's [How to be more ambitious](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/). Speed is the default; **Altitude** aims at the outcome you want after the task, **Depth** works the way a top expert would (raw data, real methods, an outside check), and **Range** borrows from other fields. Nothing is added unless you pick it.
5. **Plans the pieces,** each with an agent, a model, the skills to load and a check.
6. **Asks you once:** Go / Go with upgrades / Change / Cancel.
7. **Runs** the pieces as subagents, in parallel where they're independent. Big fan-outs run as a dynamic workflow.
8. **Verifies.** A fresh, read-only verifier tries to break the result, with at most 2 fix rounds.
9. **Reports** the evidence and which model did what.

## Why

Most of a long Claude Code session's cost comes from **re-reading a growing context on every tool call**, not from new output. In the sessions this was built from, 53–71% of spend was that re-reading, at 300–570K tokens per call. Delegating reads to subagents keeps the main thread small, and sending each piece to the cheapest model that does it well cuts the rest.

| Work | Model | Reason |
|---|---|---|
| Lookups, status checks, scouting | Haiku | Far cheaper; built for lookups and routing |
| Setup, shell, docs, slides, scoped code | Sonnet | Matches or beats Opus on shell and document work, at half the price |
| Root-cause debugging, multi-file fixes, facts that must be right | Opus | Leads on real-repo fixes and factual recall |

The pattern follows Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (an Opus lead with Sonnet workers) and the [Claude Code best practices](https://code.claude.com/docs/en/best-practices) (explore, then plan, then code; give Claude a check it can run).

## Install

Requires Claude Code with skills and custom subagents.

```bash
git clone https://github.com/maan-iitd2/crew.git
cd crew
python install.py              # add --opusplan to also set your default model to opusplan
```

That installs `~/.claude/skills/crew` plus three agents in `~/.claude/agents`: `scout` (Haiku, read-only), `builder` (Sonnet; Opus when the plan says so) and `verifier` (Sonnet, read-only). Anything it overwrites is backed up to `~/.claude/backups/crew-install/`.

**WSL or remote hosts:** Claude there reads its own `~/.claude`, so run `install.py` there too.

**Optional skills it uses when present:** [superpowers](https://github.com/obra/superpowers) (debugging, TDD, brainstorming), [gstack](https://github.com/garrytan/gstack) (`gstack-office-hours` for startup ideas), `frontend-design`, and the document skills. Edit the skills table in `skills/crew/SKILL.md` to match what you have.

## Customize

Everything lives in four Markdown files. Change the model-routing table, the skills table or the size thresholds in `skills/crew/SKILL.md`, and each worker's behaviour in `agents/*.md`.

## Uninstall

Delete `~/.claude/skills/crew` and `~/.claude/agents/{scout,builder,verifier}.md`.

## License

MIT
