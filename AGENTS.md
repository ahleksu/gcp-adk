# Repo conventions

This file is for whoever (human or AI coding agent) touches this repo next. It covers
commit/PR practice and the operational rules this project's scaffold (`agents-cli`)
expects agents to follow. It is not agent behavior documentation — for that, see
`app/agent.py` directly.

## Commit messages: Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary, imperative mood>

<optional body — the why, not the what>
```

Common types:

| Type | When |
|------|------|
| `feat` | New agent capability, new tool, new behavior |
| `fix` | Bug fix |
| `docs` | README/GCP_SETUP/AGENTS.md changes only |
| `chore` | Dependency bumps, tooling, `.gitignore`, etc. |
| `refactor` | Code change with no behavior change |
| `test` | Test-only changes |

Examples:
```
feat(agent): add a currency-conversion tool
fix(env): stop GOOGLE_CLOUD_PROJECT from overriding the API key
docs(setup): clarify Vertex AI org-policy troubleshooting step
```

Keep commits small and scoped to one logical change. Don't bundle a dependency bump with
a behavior change — separate commits, even in the same session.

## Branches and PRs

- Branch names: `<type>/<short-description>`, e.g. `feat/currency-tool`,
  `fix/env-precedence`.
- One PR per logical change, same scoping rule as commits above.
- PR description: what changed and why (the *why* matters more — the diff already shows
  the what). Link back to the milestone or issue if there is one.
- Don't force-push a branch others may have pulled; prefer a new commit over rewriting
  history once a PR is open for review.
- Squash-merge is fine for single-purpose PRs; use a merge commit if the PR intentionally
  preserves multiple meaningful commits (e.g. a multi-step migration).

## Architectural Decision Records (ADRs)

Log non-obvious architectural or technical decisions as ADRs under `docs/` — one
markdown file per decision, not a running log in this file. A decision is
"non-obvious" if a future reader (human or agent) could plausibly make a different
choice without knowing why this one was picked: credential/auth approach, package
manager, which tool generated the scaffold, a rejected alternative and why, etc. Pure
implementation details that follow obviously from the code don't need one.

- **Location & naming:** `docs/NNNN-short-kebab-title.md`, zero-padded four-digit
  sequence starting at `0001`, incrementing — never reuse or renumber.
- **Template:**
  ```markdown
  # ADR NNNN: <Title>

  ## Status
  Accepted | Superseded by ADR NNNN | Deprecated

  ## Context
  What prompted this decision — the constraint, requirement, or tradeoff in play.

  ## Decision
  What was chosen, stated plainly.

  ## Alternatives considered
  What else was on the table and why it lost.

  ## Consequences
  What this makes easier, harder, or forecloses.
  ```
- **When to write one:** at the time the decision is made, in the same PR/commit as
  the change it justifies — not retroactively reconstructed later.
- **Superseding a decision:** don't edit an old ADR's Decision section. Write a new
  ADR, and update the old one's Status to point at it — the history of *why* it
  changed is the point.

## Operational rules for coding agents working in this repo

These come from the `agents-cli` scaffold this project was generated with — they apply
whether you're a human or an AI agent making changes here.

- **Code preservation.** Only modify the code the current task actually targets. Don't
  drive-by refactor `app/app_utils/` (generated serving/A2A wiring — treat as
  read-only), and don't change `app/agent.py`'s `MODEL` constant unless the task
  explicitly asks you to change the model.
- **Always run Python through `uv`**: `uv run python ...`, `uv run pytest`, `uv run adk
  ...`. Don't invoke a bare `python`/`pytest` — it won't see this project's venv.
- **Tests vs. eval — know the difference.** `uv run pytest tests/unit` checks code
  structure (imports, wiring) with no API key needed. `uv run pytest tests/unit
  tests/integration` additionally makes a real model call. Never write a `pytest` test
  that asserts on what the LLM actually said (non-deterministic) — that's what
  `tests/eval/` and `agents-cli eval` are for, if this project grows past prototype
  stage.
- **Stop on repeated errors.** If the same error shows up 3+ times in a row, stop and
  find the root cause instead of retrying with small variations.
- **Secrets stay in `.env`, never in code or commits.** `.env` is gitignored; only
  `.env.example` (with placeholder values) is tracked. If you ever see a real key in a
  diff, stop and remove it before committing.

## Useful commands

| Command | What it does |
|---|---|
| `agents-cli install` | Install deps (`uv sync` under the hood) |
| `agents-cli playground` | Local web UI to chat with the agent |
| `agents-cli run "prompt"` | One-off non-interactive prompt |
| `uv run pytest tests/unit` | Structural tests, no API key needed |
| `uv run ty check` | Type-check |
| `uv run ruff check .` | Lint |
| `agents-cli info` | Show resolved project config |
