# ADR 0001: Authenticate via a Vertex AI / Gemini Enterprise Agent Platform API key, not an AI Studio key

## Status
Accepted

## Context
The project requirement was a Gemini API key obtained through a GCP account that
actually draws on the $300 Free Trial credit. The most commonly-documented and
easiest path to a "Gemini API key" is Google AI Studio
(https://aistudio.google.com) — one click, no billing setup.

Research established that, as of a March 2026 Google Cloud policy change, AI Studio
/ Gemini Developer API usage is explicitly excluded from Free Trial and Welcome
credit — it runs on its own separate free tier and, if billing is linked, its own
pay-as-you-go track. None of it touches the $300 credit. Only usage billed through
Vertex AI (rebranded "Gemini Enterprise Agent Platform") draws on it.

## Decision
Use a Vertex AI API key, backed by a service account (not Application Default
Credentials, not a bare service-account JSON key file), authenticated via
`GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` in `.env`. Documented in
`GCP_SETUP.md`.

## Alternatives considered
- **AI Studio key.** Rejected — does not draw on the $300 credit, which was an
  explicit, non-negotiable requirement.
- **Application Default Credentials (`gcloud auth application-default login`).**
  Rejected — out of scope for this prototype; adds a `gcloud` install/auth
  dependency the "API key only" requirement was meant to avoid.
- **Express Mode (`console.cloud.google.com/expressmode`).** Considered and
  documented as a footnote in `GCP_SETUP.md`'s troubleshooting section — it's the
  fastest path to *a* working key, but it's a separate no-billing quota that also
  does not draw on the $300 credit, so it doesn't satisfy the requirement either.

## Consequences
- Setup is more involved than the AI Studio path: enable the Vertex AI API, create
  a service account with the "Gemini Enterprise Agent Platform Express User (Beta)"
  role, then create a credential-authenticated-through-that-service-account API key.
  (The "Express" in that IAM role's name is unrelated to Express Mode billing — this
  tripped up an early draft of the guide; see the note in `GCP_SETUP.md` step 3.)
- `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` must stay unset in `.env` — if
  either is present alongside an API key, the `google-genai` SDK silently drops the
  key and requires ADC instead.
- This feature is Pre-GA/preview as of this writing; console screens may shift.
