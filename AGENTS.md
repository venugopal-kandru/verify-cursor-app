# AGENTS.md

## Cursor Cloud specific instructions

This is a single-service Flask URL shortener (`app.py`) backed by SQLite.

- Dependencies are installed into a local virtualenv at `.venv` (the system `python3.12-venv` package is required to create it and is pre-installed in the VM snapshot). The update script keeps `.venv` in sync with `requirements.txt`.
- Run the dev server with `.venv/bin/python app.py` (Flask debug mode + reloader, listens on `0.0.0.0:5000`). See `README.md` for API endpoints and env vars (`PORT`, `DATABASE_PATH`, `BASE_URL`).
- The SQLite DB (`urls.db`, gitignored) is created automatically on startup via `init_db()`; delete it to reset state.
- There is no lint config or automated test suite in this repo; verify changes by exercising the API (`/api/shorten`, `/api/stats/<code>`, `/api/urls`, `/<code>` redirect) or the web UI.
