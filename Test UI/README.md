# Patient Letter Tester

A lightweight internal tool for dentists to generate Meditude patient consent
letters from clinical notes, read them against the original notes, and give
feedback on clinical accuracy, readability and completeness.

This is **not** production Meditube UI — it's an evaluation tool for the
consent letter generator.

## Stack

React + TypeScript + Vite + Material UI + Axios. No state management library,
no router, no backend of its own — it just calls one FastAPI endpoint.

## How it talks to the backend

The app calls a single endpoint on the Meditube backend:

```
POST /api/v2/test/generate-patient-letter
```

Request body:

```json
{
  "patient_name": "Jane Doe",
  "clinician_name": "Dr. Smith",
  "treatment_plan_items": ["Composite filling"],
  "patient_notes": "Routine dental examination..."
}
```

Response body:

```json
{
  "html": "<p>Dear Jane...</p>...",
  "full_letter": "Dear Jane...\n\n..."
}
```

The `html` field is rendered directly (via the existing
`ConsentLetterGenerator` → `markdown` pipeline the backend already uses) in a
styled, document-like card. This endpoint is separate from the production
`PUT /{consent_bundle_id}/generate_patient_letter` route, which is tied to a
saved `ConsentBundle`/`Patient`/`Clinician`/`Treatment` and returns a boolean
rather than the letter content — unsuitable for a standalone tester. The new
route reuses the same `ConsentLetterGenerator`/`LetterRequest` library and
placeholder/Unicode cleanup logic; it does not duplicate the generation logic
or touch the database.

All API calls go through `src/api/client.ts` (an Axios instance) and
`src/api/letterApi.ts`. The base URL comes from `VITE_API_BASE_URL` — no URL
or key is hard-coded.

## Running locally

Requires Node 18+.

```bash
npm install
cp .env.example .env   # then edit VITE_API_BASE_URL if needed
npm run dev
```

The app runs at `http://localhost:5173`. By default `.env.example` points at
`http://localhost:8000`, matching the backend's default local port.

You also need the backend running locally with the
`generate-patient-letter` test route available (see "Backend setup" below).

### Building

```bash
npm run build   # type-checks with tsc, then builds to dist/
npm run preview # serve the production build locally
```

## Environment variables

| Variable              | Description                                             |
| --------------------- | -------------------------------------------------------- |
| `VITE_API_BASE_URL`   | Base URL of the FastAPI backend, e.g. `http://localhost:8000` or a deployed backend URL. Required. |

Never commit a real `.env` file — only `.env.example` is tracked. No API
keys (OpenAI/Groq or otherwise) are used or stored in this frontend; the LLM
key lives only on the backend.

## Deploying to Vercel

1. Push this directory to a Git repository (or import it directly).
2. In Vercel, "Add New Project" → import the repo. Vercel auto-detects Vite
   (a `vercel.json` is included with the build command/output dir as a
   fallback).
3. Set the environment variable `VITE_API_BASE_URL` in the Vercel project
   settings to the URL of your deployed backend (e.g.
   `https://api.yourdomain.com`). Set it for Production/Preview/Development
   as needed.
4. Deploy. Vercel runs `npm run build` and serves `dist/`.

## Backend / CORS notes

- The backend already enables CORS for all origins
  (`allow_origins=["*"]` in `backend/app/main.py`). Once the frontend is
  deployed, requests from its Vercel origin will work without further
  backend changes.
- This app does not send cookies or use `withCredentials`, so the existing
  `allow_origins=["*"]` configuration is safe to use as-is even though
  `allow_credentials=True` is also set backend-wide. If the backend is ever
  tightened to an explicit origin allowlist, add the deployed frontend's
  Vercel URL to it.
- The test endpoint (`/api/v2/test/generate-patient-letter`) does not
  require authentication, matching the pattern of the existing
  `/api/v2/template_generator/generate-template` endpoint. Treat its URL as
  something you don't want to advertise publicly if the backend is deployed
  without further access control — it triggers a real LLM call.

## Test cases

Eight predefined, fictional test cases are defined in `src/data/testCases.ts`
covering: routine examination, caries/fillings, periodontal treatment,
extraction, crown treatment, multiple treatments, minimal notes, and
jargon-heavy notes. Selecting one auto-fills the form; all fields stay
editable afterwards. No real patient data is used anywhere in the app.

## Feedback

Feedback (star rating, understandability, accuracy, missing/unnecessary
content, comments) is captured in `src/api/letterApi.ts`'s `submitFeedback`
function, which currently only logs to the console — there's no feedback
storage on the backend yet. Swap that function's body for a real API call if
a feedback endpoint is added later.
