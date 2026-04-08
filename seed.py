from datetime import date, timedelta

from sqlalchemy.orm import Session

from .models import Client, Invoice, InvoiceStatus, Payment, User


def seed_demo_data(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    user = User(email="demo@exporter.com", name="Demo Exporter")
    db.add(user)
    db.flush()

    client_fast = Client(
        user_id=user.id, name="Northwind Retail", country="US", default_currency="USD", risk_level="low"
    )
    client_delayed = Client(
        user_id=user.id, name="LatePay GmbH", country="DE", default_currency="EUR", risk_level="high"
    )
    db.add_all([client_fast, client_delayed])
    db.flush()

    today = date.today()
    invoices = [
        Invoice(
            user_id=user.id,
            client_id=client_fast.id,
            invoice_number="INV-1001",
            issue_date=today - timedelta(days=30),
            due_date=today - timedelta(days=10),
            amount=250000,
            currency="INR",
            status=InvoiceStatus.pending,
        ),
        Invoice(
            user_id=user.id,
            client_id=client_fast.id,
            invoice_number="INV-1002",
            issue_date=today - timedelta(days=20),
            due_date=today + timedelta(days=3),
            amount=180000,
            currency="INR",
            status=InvoiceStatus.pending,
        ),
        Invoice(
            user_id=user.id,
            client_id=client_delayed.id,
            invoice_number="INV-2001",
            issue_date=today - timedelta(days=45),
            due_date=today - timedelta(days=15),
            amount=325000,
            currency="INR",
            status=InvoiceStatus.pending,
        ),
    ]
    db.add_all(invoices)
    db.flush()

    historical_paid_invoice = Invoice(
        user_id=user.id,
        client_id=client_delayed.id,
        invoice_number="INV-1999",
        issue_date=today - timedelta(days=90),
        due_date=today - timedelta(days=60),
        amount=210000,
        currency="INR",
        amount_paid_base=210000,
        status=InvoiceStatus.paid,
        last_payment_date=today - timedelta(days=40),
    )
    db.add(historical_paid_invoice)

    payments = [
        Payment(
            user_id=user.id,
            client_id=client_fast.id,
            payment_reference="PAY-EXACT-001",
            payment_date=today - timedelta(days=8),
            amount_received=3000,
            source_currency="USD",
            target_currency="INR",
            fx_rate_applied=83.33,
            fx_fee=0,
            platform_fee=0,
            net_amount_base=250000,
            raw_reference_text="Payment for INV-1001",
        ),
        Payment(
            user_id=user.id,
            client_id=client_fast.id,
            payment_reference="PAY-PARTIAL-001",
            payment_date=today - timedelta(days=1),
            amount_received=1200,
            source_currency="USD",
            target_currency="INR",
            fx_rate_applied=83.00,
            fx_fee=500,
            platform_fee=500,
            net_amount_base=99000,
            raw_reference_text="Part settlement INV-1002",
        ),
    ]
    db.add_all(payments)
    db.commit()
