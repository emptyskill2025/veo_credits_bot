from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    credits = Column(Integer, default=0)
    payments = relationship("PaymentRequest", back_populates="user")

class PaymentRequest(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    credits = Column(Integer)
    status = Column(Enum("pending", "approved", "rejected"))
    user = relationship("User", back_populates="payments")
