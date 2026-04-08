from datetime import date, datetime
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Invoice, InvoiceStatus, Payment, ReconciliationRecord
from .schemas import DashboardSummary, InvoiceCreate, PaymentCreate, ReconciliationResponse
from .seed import seed_demo_data
from .services.prediction import build_dashboard_summary
from .services.reconciliation import reconcile_payment

app = FastAPI(title="Cash Flow Intelligence API", version="0.1.0")

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5173,http://localhost:5173",
).split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as db:
        seed_demo_data(db)
        # Reconcile seed payments once to keep demo deterministic.
        seeded = db.execute(select(Payment)).scalars().all()
        if seeded and db.query(ReconciliationRecord).count() == 0:
            for p in seeded:
                reconcile_payment(db, p)


@app.get("/health")
def health():
    return {"ok": True, "timestamp": datetime.utcnow()}


@app.post("/api/invoices")
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = Invoice(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return {"id": invoice.id, "invoice_number": invoice.invoice_number, "status": invoice.status.value}


@app.post("/api/payments", response_model=ReconciliationResponse)
def record_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    net_amount_base = payload.amount_received * payload.fx_rate_applied - payload.fx_fee - payload.platform_fee
    payment = Payment(**payload.model_dump(), net_amount_base=net_amount_base)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return reconcile_payment(db, payment)


@app.get("/api/reconciliation")
def get_reconciliation(db: Session = Depends(get_db)):
    rows = db.execute(select(ReconciliationRecord).order_by(ReconciliationRecord.created_at.desc())).scalars().all()
    return [
        {
            "id": row.id,
            "payment_id": row.payment_id,
            "invoice_id": row.invoice_id,
            "status": row.status.value,
            "matched_amount_base": float(row.matched_amount_base),
            "delta_amount_base": float(row.delta_amount_base),
            "match_reason": row.match_reason,
        }
        for row in rows
    ]


@app.get("/api/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    summary = build_dashboard_summary(db)

    today = date.today()
    for row in summary["invoices"]:
        if row["status"] in [InvoiceStatus.pending.value, InvoiceStatus.partially_paid.value] and row["due_date"] < today:
            row["status"] = InvoiceStatus.overdue.value
    return summary
