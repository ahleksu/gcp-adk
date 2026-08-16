# ADR 0002: Scaffold with `agents-cli scaffold create`, not a hand-built minimal layout

## Status
Accepted

## Context
The project brief called for a "minimal Hello World" single-turn agent. Google's
`agents-cli scaffold create --agent adk --prototype` template is not minimal in file
count: even in prototype mode it generates A2A protocol wiring
(`app/fast_api_app.py`, `app/app_utils/`), a `Dockerfile`, a `Makefile`,
`agents-cli-manifest.yaml`, and `tests/eval/` boilerplate — none of that was strictly
asked for, and a hand-built 3-file layout (`agent.py`, `__init__.py`, `.env`,
matching ADK's own bare quickstart) would be truer to "minimal."

## Decision
Use the full `agents-cli scaffold create` output as-is, rather than hand-building a
bare-minimum layout.

## Alternatives considered
- **Hand-built 3-file layout.** Rejected — while closer to literally "minimal," it
  would only use the Agents CLI for the final smoke-test run (`agents-cli run`), not
  for scaffolding itself. The project requirement was that the Agents CLI be
  "initialized and used at least once in the workflow (not just mentioned)" — running
  `scaffold create` is the tool's own primary, intended entry point, and is a much
  more genuine exercise of it than only using it for a one-off prompt at the end.

## Consequences
- The repo ships files unused by this prototype (`Dockerfile`, A2A wiring,
  `tests/eval/`) — inert until someone opts into deployment via
  `agents-cli scaffold enhance`. Documented explicitly in `README.md`'s "Non-goals"
  section so a reader doesn't mistake their presence for a deployment requirement.
- The scaffold's project-root convention (`agents-cli scaffold create <name>` always
  creates a fresh `<name>/` subdirectory) initially left the project nested one level
  too deep (`gcp-adk/app/app/agent.py`); this was manually flattened so
  `gcp-adk/` itself is the project root and `app/` holds only the Python package —
  not something `agents-cli` supports directly via a flag.
- Generated infra (`app/app_utils/`, `app/fast_api_app.py`) is treated as read-only
  per the code-preservation rule in `AGENTS.md` — future agent code changes belong in
  `app/agent.py` only.
- The generated `app/fast_api_app.py` initializes Cloud Logging at import time, even
  for this local prototype. Therefore `agents-cli run` and `agents-cli playground`
  need local ADC and `GCLOUD_PROJECT`, independently of the authorization key used for
  model calls. This unexpected scaffold consequence is recorded in ADR 0004.
