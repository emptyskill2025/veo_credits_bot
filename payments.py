# payments.py
from db_setup import Session as DBSession
from models import PaymentRequest, User

# -----------------------------
# User Payment Functions
# -----------------------------

def request_payment(user_id: int, amount: int, reference: str) -> str:
    """
    Create a new payment request for a user.
    - user_id: Telegram user ID
    - amount: Credits requested (1 credit = 1 video)
    - reference: GCASH payment reference manually provided by user
    """
    with DBSession() as session:
        # Ensure user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return "❌ User not found. Please start the bot first."

        # Check if reference already exists
        existing = session.query(PaymentRequest).filter_by(reference=reference).first()
        if existing:
            return "❌ This payment reference was already used."

        # Create new payment request
        payment = PaymentRequest(
            user_id=user_id,
            credits=amount,
            reference=reference,
            status="pending"  # Admin must approve manually
        )
        session.add(payment)
        session.commit()

    return "✅ Payment request submitted. Waiting for admin approval."


# -----------------------------
# Admin Functions
# -----------------------------

def approve_payment(payment_id: int) -> str:
    """
    Approve a pending payment and add credits to the user's account.
    """
    with DBSession() as session:
        payment = session.query(PaymentRequest).filter_by(id=payment_id, status="pending").first()
        if not payment:
            return "❌ Payment not found or already approved."

        payment.status = "approved"
        session.commit()

    return f"✅ Payment #{payment_id} approved. {payment.credits} credits added to user."


def reject_payment(payment_id: int) -> str:
    """
    Reject a payment request.
    """
    with DBSession() as session:
        payment = session.query(PaymentRequest).filter_by(id=payment_id, status="pending").first()
        if not payment:
            return "❌ Payment not found or already processed."

        payment.status = "rejected"
        session.commit()

    return f"❌ Payment #{payment_id} has been rejected."


def list_pending_payments() -> list:
    """
    Return all pending payments for admin review.
    """
    with DBSession() as session:
        pending = session.query(PaymentRequest).filter_by(status="pending").all()
        return pending  # List of PaymentRequest objects
