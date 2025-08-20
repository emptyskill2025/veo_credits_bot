# payments.py
from db_setup import Session
from models import PaymentRequest, User

GCASH_NUMBER = "09215958284 - HJS"  # Your GCASH recipient

def payment_instructions():
    """Return GCASH payment instructions."""
    msg = (
        f"💰 To buy credits, send payment to:\n"
        f"{GCASH_NUMBER}\n\n"
        "After payment, submit your GCASH reference in the bot using:\n"
        "/pay <credits> <GCASH Reference>\n\n"
        "1 credit = 1 video generate, Php 20.00 per credit."
    )
    return msg

def request_payment(user_id: int, amount: int, reference: str) -> str:
    """User submits a payment request."""
    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return "❌ User not found. Start the bot first."
        existing = session.query(PaymentRequest).filter_by(reference=reference).first()
        if existing:
            return "❌ This reference was already used."
        payment = PaymentRequest(user_id=user_id, credits=amount, reference=reference, status="pending")
        session.add(payment)
        session.commit()
    return "✅ Payment request submitted. Waiting for admin approval."

def approve_payment(payment_id: int) -> str:
    """Admin approves a payment request."""
    with Session() as session:
        payment = session.query(PaymentRequest).filter_by(id=payment_id, status="pending").first()
        if not payment:
            return "❌ Payment not found or already approved."
        payment.status = "approved"
        session.commit()
    return f"✅ Payment #{payment_id} approved. {payment.credits} credits added."

def reject_payment(payment_id: int) -> str:
    """Admin rejects a payment request."""
    with Session() as session:
        payment = session.query(PaymentRequest).filter_by(id=payment_id, status="pending").first()
        if not payment:
            return "❌ Payment not found or already processed."
        payment.status = "rejected"
        session.commit()
    return f"❌ Payment #{payment_id} has been rejected."

def list_pending_payments() -> list:
    """Return all pending payments."""
    with Session() as session:
        return session.query(PaymentRequest).filter_by(status="pending").all()
