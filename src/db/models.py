from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, Text


Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    transaction_details = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    remarks = Column(Text)

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount})>"

    def __str__(self):
        # For end users - human readable
        return f"Transaction: {self.transaction_details} - ${self.amount}"
