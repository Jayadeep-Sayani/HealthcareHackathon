# Setup & Spinup

## Prerequisites

- Node.js >= 18
- Python >= 3.11
- npm

---

## Backend

```bash
cd backend

# Copy env
cp .env.example .env

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load demo doctors/patients (required for login)
python seed.py

# Start dev server (auto-reloads on save)
python -m uvicorn main:app --reload
```

Runs at: http://localhost:8000
API docs: http://localhost:8000/docs

---

## Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Runs at: http://localhost:5173

---

## Build for Production

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

---

## Notes

- The Vite dev server proxies `/api/*` to `localhost:8000` — no CORS issues during development.
- The SQLite database file is created under `backend/data/` (see `DATABASE_URL` in `.env`) on first run.
- To reset the database, delete that file and restart the backend.
