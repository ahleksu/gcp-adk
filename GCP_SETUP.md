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
instead, via an API key (not Application Default Credentials, not a service account key
file — those are out of scope for this prototype).

## Steps

### 1. Confirm your project and billing

1. Go to [console.cloud.google.com/projectselector2/home/dashboard](https://console.cloud.google.com/projectselector2/home/dashboard).
2. Select the project you want to use (or create a new one — "New Project" top right).
3. Confirm billing is attached: **☰ menu → Billing**. You should see your Free Trial
   account with remaining credit. If it says "No billing account," go back to
   [console.cloud.google.com/freetrial](https://console.cloud.google.com/freetrial) first.

### 2. Enable the Vertex AI API

1. Go to
   [console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com](https://console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com)
   (make sure the project selector at the top shows the project from step 1).
2. Click **Enable**.
3. Wait for the confirmation — this takes a few seconds.

### 3. Create a service account to back the API key

Vertex AI API keys on the billing-linked path are backed by a service account under the
hood, even though you'll only ever handle a plain key string — no JSON key file, no
`gcloud auth`.

1. Go to
   [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   (same project).
2. Click **Create Service Account**.
3. Give it any name, e.g. `adk-local-dev`. Click **Create and Continue**.
4. Under **Grant this service account access to project**, add the role
   **"Gemini Enterprise Agent Platform Express User (Beta)"** (search for "Gemini
   Enterprise" in the role picker — the exact label may shift slightly since it's beta).

   **Note the confusing name:** despite saying "Express," granting this role to a
   service account on *your billing-enabled project* is what makes the resulting API key
   draw on your $300 credit — it is not the same thing as using the separate
   [Express Mode](https://console.cloud.google.com/expressmode) signup flow described in
   Troubleshooting below, which skips billing entirely and does *not* touch your credit.
   "Express" here is just this IAM role's name, not a statement about which billing mode
   you're in.
5. Click **Continue**, then **Done**.

### 4. Create the API key

1. Go to [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials).
2. Click **+ Create Credentials → API key**.
3. In the dialog, check **"Authenticate API calls through a service account"** and select
   the service account you created in step 3.
4. Click **Create**.
5. On the resulting key details screen (or **Edit API key** later), check **"API
   restrictions"**. If it's set to "Restrict key," make sure **"Vertex AI API"**
   (may also show as "Gemini Enterprise Agent Platform API") is in the allowed list —
   or select **"Don't restrict key"** for simplicity in this prototype. Click **Save**.
   Skipping this step is the single most common cause of a working-looking key that
   still fails with `403 PERMISSION_DENIED` / `API_KEY_SERVICE_BLOCKED` once you try to
   actually use it.
6. Copy the key — you'll paste it into `.env` in [README.md](README.md)'s Milestone 2.
   You won't be able to see it again after leaving this screen (you can always generate a
   new one, but you'd have to update `.env` again).

**Expected result:** a dialog showing your new key. Note it will *not* look like an
AI Studio key (`AIzaSy...`) — a service-account-backed key from this flow has a
different-looking format (e.g. starting `AQ.`). That's expected; it's still a plain
string you paste straight into `GOOGLE_API_KEY` in Milestone 2, nothing else changes.

## Troubleshooting

- **`403 PERMISSION_DENIED` / `API_KEY_SERVICE_BLOCKED` when actually calling the
  model** (`Requests to this API aiplatform.googleapis.com ... are blocked.`). Your
  key already exists but its **API restrictions** setting doesn't allow the Vertex AI
  API. Go to
  [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials),
  click your key, and under "API restrictions" add "Vertex AI API" (or "Gemini
  Enterprise Agent Platform API") to the allowed list, or switch to "Don't restrict
  key." Save and wait ~1–2 minutes before retrying — this is the single most common
  failure once the key itself is created.
- **"Organization policy prevents this operation" when creating the API key.** Some GCP
  organizations block service-account-backed API key creation via the org policy
  `iam.managed.disableServiceAccountApiKeyCreation`. This is unlikely for an individual
  account created via the Free Trial (those aren't attached to a Cloud Organization,
  so there's no org policy to block you) — but if you see it, an Organization Policy
  Administrator needs to disable that constraint at
  [console.cloud.google.com/iam-admin/orgpolicies/list](https://console.cloud.google.com/iam-admin/orgpolicies/list).
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
inside it. If you instead get a `403`/`PERMISSION_DENIED`, re-check the service-account
role in step 3 above; a `404` on the model name means try a different `MODEL_ID` (model
availability varies by key/project); anything else, re-verify the key was copied
correctly with no extra whitespace.

## Next

Continue to [README.md](README.md) — Milestone 2: wiring this key into the repo.
