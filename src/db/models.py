from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class BillingPeriod(Base):
    __tablename__ = "billing_period"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month_name = Column(String(20), nullable=False)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Reverse relationship to transactions
    transactions = relationship("Transaction", back_populates="billing_period")

    def __repr__(self):
        return f"<BillingPeriod(id={self.id}, month_name={self.month_name}, start={self.period_start_date}, end={self.period_end_date})>"

    def __str__(self):
        return f"Billing Period: {self.month_name} ({self.period_start_date} to {self.period_end_date})"


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    transaction_details = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    remarks = Column(Text)
    billing_period_id = Column(Integer, ForeignKey("billing_period.id", ondelete="CASCADE"), nullable=True)

    # Relationship to billing period
    billing_period = relationship("BillingPeriod", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount})>"

    def __str__(self):
        # For end users - human readable
        return f"Transaction: {self.transaction_details} - ${self.amount}"
