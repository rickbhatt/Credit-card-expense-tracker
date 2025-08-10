import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Transaction, Base
from .utils import (
    display_transactions_in_table,
    display_transactions_for_selection,
    display_single_transaction,
)
from app_logging.config import setup_logger


load_dotenv()


class Database:
    def __init__(self):
        self.logger = setup_logger("database")
        self.db_name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.password = os.getenv("DB_PASSWORD")
        self.is_create_table = os.getenv("CREATE_TABLES", "false").lower() == "true"
        self.engine = None
        self.Session = None
        self.session = None
        self.logger.info("Database instance initialized")

    def connect(self):
        """
        Connects to the database
        """
        self.logger.info("Attempting to connect to database")

        try:
            db_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            self.logger.debug(
                f"Database URL: postgresql://{self.user}:***@{self.host}:{self.port}/{self.db_name}"
            )

            self.engine = create_engine(db_url, echo=False)

            if self.is_create_table:
                self.logger.info("Creating database tables if they don't exist")
                Base.metadata.create_all(self.engine)

            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()

            self.logger.info("Successfully connected to database")

            return True

        except (SQLAlchemyError, Exception) as e:
            self.logger.error(f"Failed to connect to database: {e}")
            print("Unable to connect to the database:")
            print(e)
            return False

    def disconnect(self):
        self.logger.info("Disconnecting from database")
        if self.engine:
            self.session.close()
            self.session = None
            self.logger.debug("Database session closed")

        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.logger.debug("Database engine disposed")

        self.logger.info("Database connection closed")
        print("\nDatabase connection closed.")

    """
    Adding the enter and the exit methods makes the class a context manager.
    We can now use the class with 'with' block.
    """

    def __enter__(self):
        """Called automatically when entering 'with' block"""
        self.logger.debug("Entering database context manager")

        if self.connect():
            return self
        else:
            self.logger.error("Context manager failed to connect to database")
            raise ConnectionError("Failed to connect to the database")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called automatically when exiting 'with' block"""
        if exc_type:
            self.logger.error(
                f"Exception occurred in context manager: {exc_type.__name__}: {exc_val}"
            )
        self.logger.debug("Exiting database context manager")
        self.disconnect()
        return False

    def _insert_into_transaction_table(
        self, transaction_date_str, transaction_details, amount_str, remarks
    ):
        """
        Inserts a new transaction record into the transaction table.
        """
        self.logger.debug(
            f"Inserting transaction: {transaction_details}, amount: {amount_str}"
        )
        try:
            date = datetime.strptime(transaction_date_str, "%d-%m-%Y").date()

            amount = Decimal(amount_str)

            new_transaction = Transaction(
                date=date,
                transaction_details=transaction_details,
                amount=amount,
                remarks=remarks,
            )

            self.session.add(new_transaction)
            self.session.commit()

            self.logger.info(
                f"Successfully inserted transaction with ID: {new_transaction.id}"
            )
            return new_transaction.id

        except (SQLAlchemyError, Exception) as error:
            self.logger.error(f"Failed to insert transaction: {error}")
            self.session.rollback()
            print("Unable to insert data into the table:")
            print(error)
            return None

    def add_transaction(self):
        # Date validation with retry
        while True:
            transaction_date_str = input("Enter transaction date DD-MM-YYYY: ")
            try:
                datetime.strptime(transaction_date_str, "%d-%m-%Y")
                break  # Valid date, exit loop
            except ValueError:
                print(
                    "❌ Invalid date format. Please use DD-MM-YYYY format (e.g., 25-12-2024)"
                )

        transaction_details = input("Enter transaction details: ")

        # Amount validation with retry
        while True:
            amount_str = input("Enter amount: ")
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    print(
                        "❌ Amount cannot be negative. Please enter a positive value."
                    )
                    continue
                break  # Valid amount, exit loop
            except (ValueError, InvalidOperation):
                print("❌ Invalid amount format. Please enter a valid number.")

        remarks = input("Enter remarks (Optional): ")

        obj = self._insert_into_transaction_table(
            transaction_date_str=transaction_date_str,
            transaction_details=transaction_details,
            amount_str=amount_str,
            remarks=remarks,
        )

        if obj:
            self.logger.info(
                f"Transaction added successfully with details: {transaction_details}"
            )
            print("✅ Transaction added successfuly")

        else:
            self.logger.warning("Failed to add transaction - database operation failed")
            print("❌ Failed to insert transaction. Please check your input.")

    def _get_all_transactions(self):
        """
        Retrieve all transactions from the database using pandas
        Returns: pandas DataFrame or None if error
        """

        try:
            self.logger.debug("Retrieving all transactions from database")
            query = """
                SELECT id, date, transaction_details, amount, remarks 
                FROM transaction 
                ORDER BY date DESC, id DESC
            """

            df = pd.read_sql_query(query, self.engine)
            self.logger.info(f"Retrieved {len(df)} transactions from database")
            return df

        except (SQLAlchemyError, Exception) as error:
            self.logger.error(f"Failed to retrieve transactions: {error}")
            print(f"Unable to retrieve data from the transaction table: {error}")

            return None

    def _get_total_amount(self):
        """
        Calculate total amount of all transactions
        Returns: Decimal total or None if error
        """

        try:
            self.logger.debug("Calculating total amount of all transactions")
            total = self.session.query(func.sum(Transaction.amount)).scalar()
            result = total if total is not None else Decimal("0.00")
            self.logger.info(f"Total amount calculated: {result}")
            return result

        except (SQLAlchemyError, Exception) as error:
            self.logger.error(f"Failed to calculate total amount: {error}")
            print(f"Failed to calculate total: {error}")
            return None

    def display_transaction_and_total_expenditure(self):
        """
        Displays all the transactions and the total expenditure
        """
        try:
            df = self._get_all_transactions()

            if df is None or df.empty:
                print("No transactions found.")
                return

            total = self._get_total_amount()

            if total is None:
                total = Decimal("0.00")

            display_transactions_in_table(
                df=df,
                total=total,
                table_title="💳 Credit Card Transactions",
            )

        except Exception as e:
            print("Something went wrong, cannot display transaction and total: ", e)

    def _get_transaction_by_id(self, transaction_id):
        """
        Gets a transaction by id
        Args:
        transaction_id (int): The ID of the transaction
        Returns:
            dict: Transaction data or None if not found
        """

        try:
            transaction = self.session.get(Transaction, transaction_id)

            if not transaction:
                return None, None
            df = pd.DataFrame(
                [
                    {
                        "id": transaction.id,
                        "date": transaction.date,
                        "transaction_details": transaction.transaction_details,
                        "amount": transaction.amount,
                        "remarks": transaction.remarks,
                    }
                ]
            )

            return transaction, df

        except (SQLAlchemyError, Exception) as error:
            print(f"❌ Error fetching transaction: {error}")

            return None, None

    def delete_transaction_menu(self):
        """
        Menu interface for deleting transactions
        """
        try:
            # Show all transactions
            all_transactions = self._get_all_transactions()

            if all_transactions is None or all_transactions.empty:
                print("❌ No transactions found.")
                return False

            ID_map = display_transactions_for_selection(
                df=all_transactions, table_title="📑 Select Transaction to Delete"
            )

            # Get user selection
            try:
                serial_no = int(
                    input("Enter serial number of the record you want to delete: ")
                )
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                return False

            if serial_no not in ID_map:
                print("❌ Invalid transaction selection.")
                return False

            transaction_id = ID_map[serial_no]

            # Call the actual delete method
            return self._delete_transaction_by_id(transaction_id)

        except Exception as error:
            print(f"❌ Error in delete menu: {error}")
            return False

    def _delete_transaction_by_id(self, transaction_id):
        """
        Deletes a transaction by ID (pure business logic)
        """
        self.logger.info(f"Attempting to delete transaction with ID: {transaction_id}")
        try:
            transaction, df = self._get_transaction_by_id(transaction_id)

            if not transaction:
                self.logger.warning(
                    f"Transaction with ID {transaction_id} not found for deletion"
                )
                print("❌ Transaction not found.")
                return False

            # Show transaction to be deleted
            display_single_transaction(
                df=df,
                table_title="🚮 Transaction to be deleted",
            )

            confirm = input(
                "⚠️  Are you sure you want to delete this transaction? (y/N): "
            ).lower()

            if confirm not in ["y", "yes"]:
                print("❌ Deletion cancelled.")
                return False

            self.session.delete(transaction)
            self.session.commit()

            self.logger.info(
                f"Successfully deleted transaction with ID: {transaction_id}"
            )
            print("✅ Transaction deleted successfully.")
            return True

        except SQLAlchemyError as error:
            self.logger.error(
                f"Database error deleting transaction {transaction_id}: {error}"
            )
            print(f"❌ Database error deleting transaction: {error}")
            self.session.rollback()
            return False
        except Exception as error:
            self.logger.error(f"Error deleting transaction {transaction_id}: {error}")
            print(f"❌ Error deleting transaction: {error}")
            return False

    def _update_transaction_by_id(self, id):
        """
        Updates a transaction by ID (pure business logic)
        """
        self.logger.info(f"Attempting to update transaction with ID: {id}")

        try:
            transaction, df = self._get_transaction_by_id(id)

            if not transaction:
                self.logger.warning(f"Transaction with ID {id} not found for update")
                print("❌ Transaction not found.")
                return False

            # Show transaction to be updated
            display_single_transaction(
                df=df,
                table_title="💳 Transaction to be updated",
            )

            print("Enter the details below to update the transaction")
            while True:
                transaction_date_str = input("Enter transaction date DD-MM-YYYY: ")
                try:
                    datetime.strptime(transaction_date_str, "%d-%m-%Y")
                    break  # Valid date, exit loop
                except ValueError:
                    print(
                        "❌ Invalid date format. Please use DD-MM-YYYY format (e.g., 25-12-2024)"
                    )

            transaction_details = input("Enter transaction details: ")

            # Amount validation with retry
            while True:
                amount_str = input("Enter amount: ")
                try:
                    amount = Decimal(amount_str)
                    if amount <= 0:
                        print(
                            "❌ Amount cannot be negative. Please enter a positive value."
                        )
                        continue
                    break  # Valid amount, exit loop
                except (ValueError, InvalidOperation):
                    print("❌ Invalid amount format. Please enter a valid number.")

            remarks = input("Enter remarks (Optional): ")

            confirm = input(
                "⚠️  Are you sure you want to update this transaction? (y/N): "
            ).lower()

            if confirm not in ["y", "yes"]:
                print("❌ Update cancelled.")
                return False

            transaction.date = transaction_date_str
            transaction.transaction_details = transaction_details
            transaction.amount = amount
            transaction.remarks = remarks
            self.session.commit()

            self.logger.info(f"Successfully updated transaction with ID: {id}")
            return True

        except SQLAlchemyError as error:
            self.logger.error(f"Database error updating transaction {id}: {error}")
            print(f"❌ Database error updating transaction: {error}")
            self.session.rollback()
            return False
        except Exception as error:
            self.logger.error(f"Error updating transaction {id}: {error}")
            print(f"❌ Error updating transaction: {error}")
            return False

    def update_transaction_menu(self):
        """
        Menu interface for updating transactions
        """

        try:
            all_transactions = self._get_all_transactions()

            if all_transactions is None or all_transactions.empty:
                print("❌ No transactions found.")
                return False

            ID_map = display_transactions_for_selection(
                df=all_transactions, table_title="📑 Select Transaction to Update"
            )

            # Getting user selection
            try:
                serial_no = int(
                    input("Enter serial number of the record you want to update: ")
                )
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                return False

            if serial_no not in ID_map:
                print("❌ Invalid transaction selection.")
                return False

            transaction_id = ID_map[serial_no]

            # Call the actual update method
            result = self._update_transaction_by_id(transaction_id)

            if result:
                print("✅ Transaction updated successfully.")
            else:
                print("❌ Transaction update failed.")

        except Exception as error:
            print(f"❌ Error in delete menu: {error}")
            return False
