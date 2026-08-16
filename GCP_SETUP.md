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
5. Copy the key — you'll paste it into `.env` in [README.md](README.md)'s Milestone 2.
   You won't be able to see it again after leaving this screen (you can always generate a
   new one, but you'd have to update `.env` again).

**Expected result:** a dialog showing a string that looks like `AIzaSy...`. That's your
key for Milestone 2.

## Troubleshooting

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

## Next

Continue to [README.md](README.md) — Milestone 2: wiring this key into the repo.
