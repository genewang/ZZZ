# kits4kid

Company webpage for **kits4kid** — monthly Bible kits + supervised Create Studio — on a **Triple Zero** backend kernel.

## Frontend

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Backend (Triple Zero)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs) — see `backend/README.md`.
