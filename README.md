# Cash Flow Intelligence for Exporters

Interview-focused fintech MVP built with FastAPI, React, and Tailwind CSS.

## Approach

This MVP is designed to look and behave like a real product while staying manageable for a fresher timeline.

- Backend stores invoices, payments, and reconciliation records in SQLite (local) or PostgreSQL (production).
- When a payment is recorded, a deterministic reconciliation engine matches it against pending invoices.
- A rule-based prediction layer computes expected inflow (next 7 days) using each client's average historical delay.
- Dashboard API returns table-ready data and summary KPIs to keep frontend simple and responsive.

## Folder Structure

```text
cash-flow-intelligence-mvp/
  backend/
    app/
      database.py
      models.py
      schemas.py
      seed.py
      main.py
      services/
        reconciliation.py
        prediction.py
    requirements.txt
    .env.example
  frontend/
    src/
      App.tsx
      api.ts
      types.ts
      main.tsx
      index.css
    index.html
    package.json
    tailwind.config.js
    postcss.config.js
    vite.config.ts
```

## Backend Highlights

- `POST /api/invoices`: create invoice
- `POST /api/payments`: record payment and immediately reconcile
- `GET /api/reconciliation`: reconciliation records
- `GET /api/dashboard/summary`: KPIs + invoices + payments + reconciliation overview

Reconciliation outcomes:
- `matched`
- `partially_matched`
- `unmatched`

Prediction logic:
- Average delay per client from paid invoices
- Predicted date for pending invoices
- Expected inflow for next 7 days
- Risk tags for overdue and delayed clients

## Frontend Highlights

- Stripe-like clean dashboard layout
- Top summary cards:
  - Total received
  - Expected inflow (7 days)
  - Overdue amount
- Main sections:
  - Invoices table with status color chips
  - Payments table
  - Reconciliation status cards
- Loading and error states included

## Demo Seed Data

Startup auto-seeds:
- Exact match (`PAY-EXACT-001` -> `INV-1001`)
- Partial payment (`PAY-PARTIAL-001` -> `INV-1002`)
- Delayed client behavior via `LatePay GmbH` historical paid invoice

## How to Run

## 1) Run backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## 2) Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173` and calls backend at `http://127.0.0.1:8000`.

## Deploy (Vercel + Render)

### Backend on Render

1. Push this repo to GitHub.
2. In Render, create from blueprint using `render.yaml` (or create web service + Postgres manually).
3. Confirm service:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `ALLOWED_ORIGINS` to your frontend domain, e.g.:
   - `https://your-app.vercel.app`

### Frontend on Vercel

1. Import the same GitHub repo in Vercel.
2. Set root directory to `frontend`.
3. Add environment variable:
   - `VITE_API_URL=https://<your-render-service>.onrender.com`
4. Deploy.

### Smoke test

- Open frontend URL from Vercel.
- Confirm data loads in dashboard.
- Check backend health at:
  - `https://<your-render-service>.onrender.com/health`

## Suggested Interview Demo Flow

1. Open dashboard summary and explain the 3 KPIs.
2. Show reconciliation records for exact and partial match.
3. Show overdue invoice and delayed client risk surfacing.
4. Explain deterministic prediction logic and practical next improvements.
