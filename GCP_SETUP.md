# Milestone 1: Get a Gemini API key that uses your $300 Free Trial credit

This is the first of three milestones (see [README.md](README.md) for the other two). By
the end of this doc you'll have one thing: an API key in your clipboard, ready to paste
into `.env`.

**Prerequisite:** an existing Google account with access to the
[Google Cloud Console](https://console.cloud.google.com) and an active $300 Free Trial
(a project with a Cloud Billing account in trial status). If you don't have that yet,
start it at [console.cloud.google.com/freetrial](https://console.cloud.google.com/freetrial)
before continuing.

## Why not the simple route?

The most commonly-Googled way to get a "Gemini API key" is
[Google AI Studio](https://aistudio.google.com) — click a button, get a key, done. That
key **does not draw on your $300 Free Trial credit.** As of a March 2026 Google Cloud
policy change, Gemini API / AI Studio usage is explicitly excluded from Free Trial and
Welcome credit — it runs on its own separate free tier and, if you link billing, its own
pay-as-you-go track. None of it touches the $300.

The credit only applies to Gemini usage billed through **Vertex AI**, now branded
**Gemini Enterprise Agent Platform** in the console and docs (same underlying service —
`aiplatform.googleapis.com` — just a renamed product). So this guide uses that path
instead, via an authorization key rather than ADC for model calls. The generated local
server has a separate Cloud Logging ADC requirement documented in [README.md](README.md);
no service-account JSON key file is used.

## Steps

### 1. Confirm your project and billing

1. Go to [console.cloud.google.com/projectselector2/home/dashboard](https://console.cloud.google.com/projectselector2/home/dashboard).
2. Select the project you want to use (or create a new one — "New Project" top right).
3. Confirm billing is attached: **☰ menu → Billing**. You should see your Free Trial
   account with remaining credit. If it says "No billing account," go back to
   [console.cloud.google.com/freetrial](https://console.cloud.google.com/freetrial) first.

### 2. Enable Agent Platform API

1. Go to
   [console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com](https://console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com)
   (make sure the project selector at the top shows the project from step 1).
2. Click **Enable**.
3. Wait for the confirmation — this takes a few seconds.

### 3. Create a service account to back the API key

Authorization keys for Agent Platform on the billing-linked path are backed by a
service account, even though the application only handles a key string — no service
account JSON key file is created or downloaded. Model calls do not use the local ADC
credential configured later for the generated Cloud Logging client.

1. Go to
   [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   (same project).
2. Click **Create Service Account**.
3. Give it any name, e.g. `adk-local-dev`. Click **Create and Continue**.
4. Under **Grant this service account access to project**, add the role
   **Agent Platform User** (`roles/aiplatform.user`). Search for the exact phrase
   `Agent Platform User`; the role picker can show only Administrator, Express, and
   Sessions roles when searching broadly for `Agent Platform`, but the exact role is
   available under the product-role list.

   Do not select **Agent Platform Express User (Beta)** for this standard,
   billing-linked project flow. The current role definition is documented in Google's
   [Agent Platform IAM reference](https://docs.cloud.google.com/iam/docs/roles-permissions/aiplatform#gemini-enterprise-agent-platform-roles).
5. Click **Continue**, then **Done**.

### 4. Create the API key

1. Go to [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials).
2. Click **+ Create Credentials → API key**.
3. Give the key a descriptive name, e.g. `gcp-adk-key`.
4. Under **Select API restrictions**, select **Agent Platform API**. Its underlying
   service identifier is `aiplatform.googleapis.com`. Selecting it makes the service
   account selector appear automatically.
5. Under **Service account**, select the account from step 3. This binds the key to the
   service account and makes it an authorization key.
6. For this local prototype, leave **Application restrictions** set to **None**. Add an
   IP restriction later only if the development machine has a stable outbound IP.
7. Click **Create**, copy the key, and store it securely. The current Console flow and
   authorization-key behavior are described in Google's
   [API-key authentication guide](https://docs.cloud.google.com/docs/authentication/api-keys).

   **If "Agent Platform API" doesn't appear in that dropdown at all:** this list only
   shows APIs enabled on the *project this key belongs to*. That means step 2 above
   (enabling Agent Platform API) either didn't complete or ran against a different
   project than this key/service account ended up in. Go back to
   `console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com&project=YOUR_PROJECT_ID`
   (use the project ID from your service account's email, e.g.
   `name@YOUR_PROJECT_ID.iam.gserviceaccount.com`) to confirm/enable it there, then
   return to this step — the option should then appear.

   Skipping this step is the single most common cause of a working-looking key that
   still fails with `403 PERMISSION_DENIED` / `API_KEY_SERVICE_BLOCKED` once you try to
   actually use it.
Paste the key into `.env` in [README.md](README.md)'s Milestone 2. Never commit the key.

**Expected result:** a dialog showing your new key. Note it will *not* look like an
AI Studio key (`AIzaSy...`) — a service-account-backed key from this flow has a
different-looking format (e.g. starting `AQ.`). That's expected; it's still a plain
string you paste straight into `GOOGLE_API_KEY` in Milestone 2, nothing else changes.

## Troubleshooting

- **`403 PERMISSION_DENIED` / `API_KEY_SERVICE_BLOCKED` when actually calling the
  model** (`Requests to this API aiplatform.googleapis.com ... are blocked.`). Your
  key already exists but its **API restrictions** setting doesn't allow Agent Platform
  API. Go to
  [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials),
  click your key, and under "Select API restrictions" add **Agent Platform API**
  (`aiplatform.googleapis.com`) to the allowed list. If it isn't in the
  dropdown at all, that list only shows APIs enabled on the key's own project — go
  re-run step 2's enable-API link against that specific project ID first. Save and
  wait up to 5 minutes before retrying — this is the single most common
  failure once the key itself is created.
- **"Organization policy prevents this operation" when creating the API key.** Some GCP
  projects block service-account-backed API key creation via the org policy
  `iam.managed.disableServiceAccountApiKeyCreation` (shown in the Console as "Block
  service account API key bindings"). This can happen even on a Free Trial project if
  it's attached to a Cloud Identity/Workspace organization — check by opening the
  constraint at
  [console.cloud.google.com/iam-admin/orgpolicies/list](https://console.cloud.google.com/iam-admin/orgpolicies/list)
  and seeing whether your project inherits it.

  Don't disable the constraint outright — scope it to allow just Agent Platform instead:
  1. Open the `disableServiceAccountApiKeyCreation` constraint and click **Manage
     policy** for your project.
  2. Set **Policy source** to **"Override parent's policy"**.
  3. Add a rule with **Enforcement: On**.
  4. Under **Parameters**, click the pencil on `allowedServices`, set **Value type**
     to **"User-defined"**, and add `aiplatform.googleapis.com` as Value 1.
  5. Save (you'll see a "Updated policy for the constraint..." confirmation toast).

  This keeps the org-wide block in place for every other service and only allows
  service-account-bound keys for Agent Platform — narrower and safer than fully disabling
  the constraint. Requires Organization Policy Administrator permissions on the
  project. Allow a couple minutes for the change to propagate before retrying key
  creation.
- **You just want to try something immediately, credit usage aside.** Google Cloud
  offers a separate, zero-setup "Express Mode" at
  [console.cloud.google.com/expressmode](https://console.cloud.google.com/expressmode)
  that auto-generates a key for you with no billing account needed. It's genuinely the
  fastest path to a working key — but per the note above, it explicitly does **not** draw
  on your $300 Free Trial credit (Express Mode is its own separate no-billing quota), so
  it doesn't satisfy this guide's goal. Only use it if you've decided credit usage
  doesn't matter for your case.
- **Billing shows no usage after running the agent.** Small local runs may take a few
  hours to appear in Cloud Billing reports — check
  [console.cloud.google.com/billing](https://console.cloud.google.com/billing) the next
  day if you want to confirm the credit is actually being drawn down.
- **This whole API-key-for-Vertex-AI feature is in Pre-GA/preview** as of this writing —
  Google's own docs carry a "Pre-GA Offerings Terms" notice. If the console screens above
  have moved by the time you read this, search the Cloud Console for "API keys" under
  "Gemini Enterprise Agent Platform" or "Vertex AI" — the underlying flow (project →
  enable API → service account → credential) tends to stay stable even when menu labels
  change.

## Verify the key works (optional, before Milestone 2)

You don't need `uv`, this repo, or anything else installed for this — just a terminal
and `curl`. It isolates one question: *is this key valid and able to call a model at
all*, before wiring it into the agent scaffold. Run it yourself; this is a live call
against your key, so it's not something to hand off.

```bash
GOOGLE_API_KEY="paste-your-key-here"
curl -X POST \
  -H "Content-Type: application/json" \
  "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-2.5-flash:generateContent?key=${GOOGLE_API_KEY}" \
  -d '{
    "contents": {
      "role": "user",
      "parts": { "text": "Explain how AI works in a few words" }
    }
  }'
```

Notes on this specific call:
- The API-key auth path never needs a project or location in the URL — no
  `projects/{id}/locations/{loc}/` segment, unlike the ADC/service-account-key REST
  examples you may see elsewhere in Google's docs. That's expected here, not a mistake.
- The key goes in the `?key=` query parameter, not an `Authorization` header.
- This example deliberately uses `gemini-2.5-flash` (Google's own documented example
  model for this exact call), not this repo's `gemini-3.6-flash` — the point here is
  testing the key/auth, not the specific model the agent will use later. If this curl
  call works but the actual agent doesn't, that's a model-availability question, not an
  auth problem — see README.md's Troubleshooting.

**Expected result:** a JSON body containing a `candidates` array with generated text
inside it. If you get `API_KEY_SERVICE_BLOCKED`, re-check the **Agent Platform API**
restriction in step 4. For another `403`/`PERMISSION_DENIED`, re-check that the backing
service account has **Agent Platform User** (`roles/aiplatform.user`). A `404` on the
model name means try a different `MODEL_ID`; anything else, re-verify the key was copied
correctly with no extra whitespace.

## Next

Continue to [README.md](README.md) — Milestone 2: wiring this key into the repo.
