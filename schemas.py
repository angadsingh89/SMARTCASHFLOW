from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    user_id: int
    client_id: int
    invoice_number: str
    issue_date: date
    due_date: date
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=8)
    base_currency: str = Field(default="INR", min_length=3, max_length=8)


class PaymentCreate(BaseModel):
    user_id: int
    client_id: int
    payment_reference: str
    payment_date: date
    amount_received: float = Field(gt=0)
    source_currency: str = Field(min_length=3, max_length=8)
    target_currency: str = Field(default="INR", min_length=3, max_length=8)
    fx_rate_applied: float = Field(gt=0)
    fx_fee: float = 0
    platform_fee: float = 0
    raw_reference_text: str | None = None


class ReconciliationResponse(BaseModel):
    payment_id: int
    status: Literal["matched", "partially_matched", "unmatched"]
    matched_invoices: list[dict]
    unmatched_amount_base: float


class InvoiceRow(BaseModel):
    id: int
    invoice_number: str
    client_name: str
    due_date: date
    amount: float
    amount_paid_base: float
    status: str
    predicted_payment_date: date | None = None
    risk_flag: str | None = None


class PaymentRow(BaseModel):
    id: int
    payment_reference: str
    client_name: str
    payment_date: date
    amount_received: float
    net_amount_base: float
    source_currency: str


class DashboardSummary(BaseModel):
    total_received: float
    expected_inflow_next_7_days: float
    overdue_amount: float
    risky_clients: list[str]
    invoices: list[InvoiceRow]
    payments: list[PaymentRow]
    reconciliation: list[dict]
    generated_at: datetime
