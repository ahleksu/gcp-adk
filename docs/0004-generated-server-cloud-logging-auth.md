# ADR 0004: Use ADC and GCLOUD_PROJECT for generated local Cloud Logging

## Status
Accepted

## Context
The project deliberately uses a service-account-bound Agent Platform authorization
key for Gemini model calls, as recorded in ADR 0001. ADR 0003 keeps
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` unset because the installed
`google-genai` client treats those variables as a request to use ADC instead of
`GOOGLE_API_KEY`.

The generated Agents CLI server introduces a separate requirement. At module import,
`app/fast_api_app.py` calls `google.auth.default()` and constructs
`google_cloud_logging.Client()`. Without local ADC and a project hint,
`agents-cli run` fails before loading the agent:

```text
OSError: Project was not passed and could not be determined from the environment.
```

The installed `google-auth` package accepts the legacy `GCLOUD_PROJECT` variable as a
project hint, while the installed `google-genai` client does not use that variable for
model-auth selection.

## Decision
Keep the generated serving files unchanged. On a fresh machine, install the Google
Cloud CLI and establish local ADC with `gcloud auth application-default login`. Set
`GCLOUD_PROJECT` in `.env` to the same project that owns the authorization key.
Continue to leave `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` unset.

This creates two explicit authentication boundaries:

- Gemini model calls: `GOOGLE_API_KEY` plus `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`.
- Generated Cloud Logging client: local ADC plus `GCLOUD_PROJECT`.

## Alternatives considered
- **Modify `app/fast_api_app.py` to disable Cloud Logging locally.** Rejected because
  the repository treats generated serving and A2A wiring as read-only.
- **Set `GOOGLE_CLOUD_PROJECT` and use ADC for everything.** Rejected because it changes
  the model-auth and billing path selected in ADR 0001.
- **Use only `uv run adk run app`.** Rejected as the primary workflow because this
  project intentionally validates the Agents CLI scaffold and its serving path.

## Consequences
- A fresh local setup needs the Google Cloud CLI and an interactive ADC login even
  though model calls use an API key.
- `agents-cli login -i` is not an adequate substitute after `GOOGLE_API_KEY` is set:
  Agents CLI can consider the API key sufficient and return without establishing ADC.
- `.env.example` must include the non-secret `GCLOUD_PROJECT` placeholder and explain
  why the similarly named `GOOGLE_CLOUD_PROJECT` remains unset.
- A direct `google-genai` request can validate the authorization key independently of
  the generated server, which keeps authentication failures diagnosable.
- This is a local-prototype accommodation, not a production credential design.
