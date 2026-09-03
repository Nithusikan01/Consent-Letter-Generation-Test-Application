# Consent Letter Generator - Test Backend

A minimal, standalone FastAPI app for testing/tuning the consent letter generator
(prompt, glossary, post-processing) without touching the main `medicube_backend` repo.
No database, no auth — just the generator library and one endpoint.

Contains:
- `app/libraries/consent_letter_generator/` — copied as-is from
  `medicube_backend/backend/app/libraries/consent_letter_generator`
- `app/test_letter_generator.py` — the `/generate-patient-letter` endpoint, copied as-is
  from `medicube_backend/backend/app/api/api_v2/endpoints/test_letter_generator.py`
  (imports adjusted to this app's flat layout)
- `app/utils.py` — the two small helper functions
  (`_remove_invalid_placeholders`, `_normalize_unicode_chars`) the endpoint depends on,
  extracted from `consent_bundle.py` so the rest of that file doesn't need to be pulled in

## Setup

```bash
cd "Test Backend"
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# .venv\Scripts\Activate.ps1       # Windows (PowerShell)
# source .venv/bin/activate        # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file (copy `.env.example`) with a Groq or OpenAI-compatible key:

```env
OPENAPI_API_KEY=your-groq-or-openai-compatible-key
```

## Run

```bash
uvicorn main:app --app-dir app --host 0.0.0.0 --port 8001 --reload
```

Runs on port **8001** so it can sit alongside the main backend (port 8000) without conflict.

## Test

Swagger UI: http://localhost:8001/docs

Or via curl/Postman:

```
POST http://localhost:8001/test/generate-patient-letter
Content-Type: application/json

{
  "patient_name": "John Smith",
  "clinician_name": "Dr. Brown",
  "treatment_plan_items": ["Composite restoration LR6", "Hygienist referral"],
  "patient_notes": "Patient presents with mild gingivitis around the lower anterior teeth. Small carious lesion noted on LR6. Discussed composite restoration and referred to hygienist for scale and polish."
}
```

Response:

```json
{
  "html": "<p>Dear John Smith,</p>...",
  "full_letter": "..."
}
```

Nothing is persisted — no database involved — so you can freely edit
`app/libraries/consent_letter_generator/generator.py` (the prompt) and resend requests to
iterate.

## Keeping this in sync with the main repo

This is a copy, not a symlink or package reference — if the prompt or the endpoint changes in
`medicube_backend`, re-copy the relevant files here manually.
