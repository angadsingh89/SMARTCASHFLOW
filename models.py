import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    partially_paid = "partially_paid"


class MatchStatus(str, enum.Enum):
    matched = "matched"
    partially_matched = "partially_matched"
    unmatched = "unmatched"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    clients: Mapped[list["Client"]] = relationship(back_populates="user")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    default_currency: Mapped[str] = mapped_column(String(8), default="USD")
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="clients")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client")
    payments: Mapped[list["Payment"]] = relationship(back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.pending, nullable=False
    )
    amount_paid_base: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    base_currency: Mapped[str] = mapped_column(String(8), default="INR")
    last_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    client: Mapped["Client"] = relationship(back_populates="invoices")
    reconciliations: Mapped[list["ReconciliationRecord"]] = relationship(
        back_populates="invoice"
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    payment_reference: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_received: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(8), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(8), default="INR")
    fx_rate_applied: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    fx_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    platform_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_amount_base: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    raw_reference_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    client: Mapped["Client"] = relationship(back_populates="payments")
    reconciliations: Mapped[list["ReconciliationRecord"]] = relationship(
        back_populates="payment"
    )


class ReconciliationRecord(Base):
    __tablename__ = "reconciliation_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"), nullable=False, index=True
    )
    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"), nullable=True, index=True
    )
    matched_amount_base: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    match_confidence: Mapped[float] = mapped_column(Numeric(4, 2), default=0)
    match_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), nullable=False)
    delta_amount_base: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    payment: Mapped["Payment"] = relationship(back_populates="reconciliations")
    invoice: Mapped["Invoice"] = relationship(back_populates="reconciliations")
