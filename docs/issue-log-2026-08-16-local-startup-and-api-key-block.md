# Issue Log: Local startup failure and Agent Platform API-key block

## Status

Resolved on 2026-08-16 (Asia/Manila).

## Date observed

2026-08-16 (Asia/Manila)

## Impact

`agents-cli run` cannot return an agent response. Without a project hint, the local
server crashes during import. With that startup problem bypassed, Google rejects the
configured key before the model is invoked.

## Reproduction

From the repository root:

```bash
agents-cli run "What's the weather in San Francisco?"
```

The CLI reports that its local server did not start within 30 seconds. The server log
ends at `app/fast_api_app.py` while constructing `google_cloud_logging.Client()`:

```text
OSError: Project was not passed and could not be determined from the environment.
```

A minimal local reproduction is:

```bash
uv run python -c 'import app.fast_api_app'
```

## Verified findings

### 1. The generated serving layer requires a project

`app/fast_api_app.py` creates a Cloud Logging client at module import time. The current
`.env` intentionally leaves `GOOGLE_CLOUD_PROJECT` unset to preserve the API-key auth
path, so Google Auth cannot infer the project and aborts startup.

A process-only test with the legacy Google Auth project variable succeeds:

```bash
GCLOUD_PROJECT="YOUR_PROJECT_ID" \
  uv run python -c 'import app.fast_api_app; print("startup_import=ok")'
```

The installed `google-auth` package recognizes `GCLOUD_PROJECT`, while the installed
`google-genai` API client reads `GOOGLE_CLOUD_PROJECT` and
`GOOGLE_CLOUD_LOCATION`—not `GCLOUD_PROJECT`. This makes `GCLOUD_PROJECT` the narrow
configuration option that supplies the logging client with a project without selecting
the ADC model-auth path described in ADR 0003.

This workaround was verified only for local server startup. A Cloud Logging write was
not performed.

### 2. The configured key is blocked from Vertex AI

After supplying `GCLOUD_PROJECT` for the process, the server starts and the request
reaches Google. Both `agents-cli run` and a direct REST request using the key currently
in `.env` return:

```text
403 PERMISSION_DENIED
reason: API_KEY_SERVICE_BLOCKED
service: aiplatform.googleapis.com
consumer: projects/<PROJECT_NUMBER>
```

The direct REST reproduction rules out the ADK agent, the Agents CLI, and the
repository's model/tool code as the source of this 403.

A read-only Service Usage query confirmed that `aiplatform.googleapis.com` is
`ENABLED` on the key's consumer project. Therefore, enabling the API again is not the
remedy: the exact API key used by `.env` is not currently permitted to call that
service.

The API Keys metadata lookup returned 403 for the locally authenticated user, so the
original key's allowlist could not be independently read from the API. At diagnosis
time, the remaining external possibilities were:

- the exact key in `.env` does not include Agent Platform API in its API restrictions;
- a different key was edited in Cloud Console than the key stored in `.env`; or
- the correct restriction was saved but has not propagated yet.

### 3. Repository structure is otherwise healthy

```text
uv run pytest tests/unit -q
3 passed
```

The installed Agents CLI is version 1.3.1 and resolves this directory as a valid
prototype project. The dependency changes are not responsible for either verified
failure.

## Resolution applied

1. Added the following non-secret value to local `.env`, using the actual project ID
   shown in Cloud Console:

   ```env
   GCLOUD_PROJECT="YOUR_PROJECT_ID"
   ```

   Keep `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` unset.

2. Granted the backing service account **Agent Platform User**
   (`roles/aiplatform.user`). The earlier **Agent Platform Express User (Beta)**
   guidance was not used for this standard billing-project path.

3. Created a new authorization key bound to that service account and restricted it to
   **Agent Platform API** (`aiplatform.googleapis.com`). Application restrictions were
   left as **None** for the local prototype.

4. Replaced only `GOOGLE_API_KEY` in local `.env`; the key was not printed, logged, or
   committed.

5. Ran the direct `google-genai` verification from `README.md`. It returned `OK`,
   proving the key, service-account role, API restriction, and model endpoint worked
   independently of ADK.

6. Re-ran the original end-to-end command:

   ```bash
   agents-cli run "What's the weather in San Francisco?"
   ```

   The agent called `get_weather` and returned:

   ```text
   The weather in San Francisco is currently 60°F and foggy.
   ```

## Resolution verification

This issue is resolved when all of the following are true:

- `uv run python -c 'import app.fast_api_app'` succeeds with `.env` loaded.
- The direct Agent Platform request returns a generated response.
- `agents-cli run` starts locally, invokes `get_weather`, and prints a response.
- `uv run pytest tests/unit -q` reports `3 passed`.

The issue was not caused by the agent implementation, its model constant, or the
dependency update. It was the combination of a generated Cloud Logging startup
requirement and an authorization key that did not allow `aiplatform.googleapis.com`.
