# models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # Telegram user ID
    username = Column(String)
    payments = relationship("PaymentRequest", back_populates="user")

class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    credits = Column(Integer)
    reference = Column(String, unique=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    user = relationship("User", back_populates="payments")
