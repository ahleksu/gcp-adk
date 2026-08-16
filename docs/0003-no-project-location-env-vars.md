# ADR 0003: Keep GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION out of .env

## Status
Accepted

## Context
While following Google's general Gemini Enterprise Agent Platform "Start using the
SDK" quickstart (docs.cloud.google.com/gemini-enterprise-agent-platform/models/start),
two env vars were added to local `.env`: `GOOGLE_CLOUD_PROJECT` and
`GOOGLE_CLOUD_LOCATION`, alongside a `uv add google-genai`. That guide's SDK setup
section is written for the Application Default Credentials (ADC) auth path, where
those two vars are required inputs.

This project uses a different auth path — an Agent Platform authorization key backed
by a service account, per [ADR 0001](0001-vertex-ai-api-key-over-ai-studio.md) — and ADR 0001's
Consequences section already flagged that these two vars conflict with the API-key
path. That warning was easy to miss in practice: the quickstart doc doesn't mention
this project's auth choice at all, `uv add google-genai` succeeds either way, and the
resulting failure at runtime doesn't obviously point back to the two env vars as the
cause (the SDK swaps to ADC and fails there instead of complaining about the vars
themselves).

## Decision
Confirmed and recorded directly at the point of failure: `GOOGLE_CLOUD_PROJECT` and
`GOOGLE_CLOUD_LOCATION` must never be set in this project's `.env`. When
`google-genai` sees either var set, it switches from API-key auth to ADC and
silently ignores `GOOGLE_API_KEY`, even if the key is present and valid. Both vars
were removed from `.env`, and explicit inline warnings pointing at this ADR were
added to both `.env` and `.env.example` next to `GOOGLE_API_KEY`, not just left as
prose in ADR 0001.

The legacy `GCLOUD_PROJECT` variable is intentionally different. It supplies the
generated Cloud Logging client with a project but is not read by `google-genai` for
model-auth selection. That separate decision is recorded in ADR 0004.

`google-genai` as an explicit `pyproject.toml` dependency (added via the same
`uv add`) was left in place — it's redundant (already pulled in transitively by
`google-adk[gcp,otel-gcp]`) but harmless, and not the cause of the failure.

## Alternatives considered
- **Use ADC plus these two variables for model calls.** Rejected — same reasoning as
  ADR 0001: model calls must retain the authorization-key path. ADC is used separately
  by the generated server's Cloud Logging client; see ADR 0004.
- **Leave the warning only in ADR 0001 / `.env.example` prose.** Rejected — that's
  exactly the state that led to this incident; a comment sitting right next to the
  two vars in `.env` itself is what actually stops a future `uv add`/quickstart-doc
  detour from reintroducing them silently.

## Consequences
- Any external Google quickstart for `google-genai` / Vertex AI that instructs
  setting `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` is describing the ADC
  path, not this project's path — treat those specific steps as not applicable here,
  even when the rest of the guide (e.g. `uv add google-genai`) is fine to follow.
- Do not confuse `GCLOUD_PROJECT` with `GOOGLE_CLOUD_PROJECT`; they have different
  effects in the installed libraries and serve different authentication boundaries.
