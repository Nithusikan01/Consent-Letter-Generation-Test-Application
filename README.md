# Consent Letter Generation - Test Application

A standalone pair of apps for testing and tuning the AI-generated dental consent
letter: a FastAPI backend (`Test Backend/`) that wraps the letter generator, and
a React/Vite frontend (`Test UI/`) for trying it out and giving feedback.

- `Test Backend/` — FastAPI app exposing `POST /test/generate-patient-letter`.
  No database, no auth.
- `Test UI/` — React + TypeScript + Vite + MUI tool that calls the backend and
  renders the generated letter.

See each folder's own README for details (prompt structure, deployment, etc.).
This file only covers running both locally from a terminal.

## Prerequisites

- Python 3.11+ and `pip`
- Node 18+ and `npm`
- A Groq (or other OpenAI-compatible) API key

## 1. Run Test Backend

```bash
cd "Test Backend"
python -m venv .venv

# Activate the virtual environment
source .venv/Scripts/activate      # Windows (Git Bash)
# .venv\Scripts\Activate.ps1       # Windows (PowerShell)
# source .venv/bin/activate        # macOS/Linux

pip install -r requirements.txt
```

Create `Test Backend/.env` (copy `.env.example`) with:

```env
OPENAPI_API_KEY=your-groq-or-openai-compatible-key
```

Start the server:

```bash
uvicorn main:app --app-dir app --host 0.0.0.0 --port 8001 --reload
```

- Runs on **http://localhost:8001** (kept off port 8000 so it doesn't clash
  with the main `medicube_backend`, if you run that too).
- Health check: `GET http://localhost:8001/health`
- Swagger UI: http://localhost:8001/docs

## 2. Run Test UI

In a separate terminal:

```bash
cd "Test UI"
npm install
```

Create `Test UI/.env` (copy `.env.example`) pointing at the backend you just
started:

```env
VITE_API_BASE_URL=http://localhost:8001
```

Start the dev server:

```bash
npm run dev
```

- Runs on **http://localhost:5173** (or the next free port, e.g. 5174, if
  5173 is already in use).
- Open it in a browser, pick or fill in a test case, and click **Generate
  Letter** — it calls the Test Backend at `VITE_API_BASE_URL` under
  `/test/generate-patient-letter`.

## Notes

- Both `.env` files are git-ignored — never commit real API keys.
- The two apps must be started separately (two terminals); neither starts the
  other.
- `Test Backend/.env.example` and `Test UI/.env.example` show the required
  variables.

## Troubleshooting

**`npm install`/`npm run dev` fails in Git Bash with
`Cannot find module '...npm-cli.js'`, and the path in the error looks
mangled (e.g. `anaconda3\Library\c\Users\...`):**

This happens when Anaconda's `base` environment is active in that shell
(look for `(base)` in the prompt). Anaconda ships its own `cygpath`, which
sits ahead of Git's real one on PATH and mis-resolves npm's own install
path. Fix with either:

```bash
conda deactivate      # then re-run npm as normal
```

or, without touching the environment:

```bash
PATH="/usr/bin:$PATH" npm install
```

Alternatively, run the `Test UI` commands from PowerShell/cmd instead of
Git Bash — npm isn't affected there.
