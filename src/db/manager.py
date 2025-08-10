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
from app_logging.config import setup_logger, get_ui


load_dotenv()


class Database:
    def __init__(self):
        self.logger = setup_logger("database")
        self.ui = get_ui()
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
        self.ui.process_start("Connecting to database")

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
            self.ui.success(
                message="Database connection establised successfully", title="Connected"
            )

            return True

        except (SQLAlchemyError, Exception) as e:
            self.logger.error(f"Failed to connect to database: {e}")
            self.ui.error(
                message=f"Unable to connect to the database: {str(e)}",
                title="Connection Failed",
            )
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
        self.ui.info("Database connection closed safely")

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
            self.ui.error(
                message=f"Unable to insert transaction: {str(error)}",
                title="Database Error",
            )
            return None

    def add_transaction(self):
        self.ui.separator("Add New Transaction")

        # Date validation with retry
        while True:
            transaction_date_str = self.ui.input_prompt(
                "Enter transaction date (DD-MM-YYYY)"
            )
            try:
                datetime.strptime(transaction_date_str, "%d-%m-%Y")
                break  # Valid date, exit loop
            except ValueError:
                self.ui.validation_error(
                    "Invalid date format. Please use DD-MM-YYYY format (e.g., 25-12-2024)"
                )

        transaction_details = self.ui.input_prompt("Enter transaction details")

        # Amount validation with retry
        while True:
            amount_str = self.ui.input_prompt("Enter amount")
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    self.ui.validation_error(
                        "Amount cannot be negative. Please enter a positive value"
                    )
                    continue
                break  # Valid amount, exit loop
            except (ValueError, InvalidOperation):
                self.ui.validation_error(
                    "Invalid amount format. Please enter a valid number"
                )

        remarks = self.ui.input_prompt("Enter remarks (Optional)")

        self.ui.process_start("Adding transaction to database")

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
            self.ui.success(
                f"Transaction added successfully! ID: {obj}", "Transaction Added"
            )
        else:
            self.logger.warning("Failed to add transaction - database operation failed")
            # Error already shown by _insert_into_transaction_table

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
            self.ui.error(
                f"Unable to retrieve transactions: {str(error)}", "Database Error"
            )
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
            self.ui.error(
                f"Failed to calculate total: {str(error)}", "Calculation Error"
            )
            return None

    def display_transaction_and_total_expenditure(self):
        """
        Displays all the transactions and the total expenditure
        """
        self.ui.process_start("Loading transactions")

        try:
            df = self._get_all_transactions()

            if df is None or df.empty:
                self.ui.warning(
                    "No transactions found in the database", "Empty Database"
                )
                return

            total = self._get_total_amount()

            if total is None:
                total = Decimal("0.00")

            # Show summary first
            summary = {
                "Total Transactions": len(df),
                "Total Amount": f"₹{total:,.2f}",
                "Latest Transaction": df.iloc[0]["date"].strftime("%d-%m-%Y")
                if len(df) > 0
                else "N/A",
            }
            self.ui.status_panel("Transaction Summary", summary)

            display_transactions_in_table(
                df=df,
                total=total,
                table_title="💳 Credit Card Transactions",
            )

        except Exception as e:
            self.logger.error(f"Error displaying transactions: {e}")
            self.ui.error(
                f"Something went wrong while displaying transactions: {str(e)}",
                "Display Error",
            )

    def _get_transaction_by_id(self, transaction_id):
        """
        Gets a transaction by id
        Args:
        transaction_id (int): The ID of the transaction
        Returns:
            tuple: (Transaction object, DataFrame) or (None, None) if not found
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
            self.logger.error(f"Error fetching transaction {transaction_id}: {error}")
            self.ui.error(f"Error fetching transaction: {str(error)}", "Database Error")
            return None, None

    def delete_transaction_menu(self):
        """
        Menu interface for deleting transactions
        """
        self.ui.separator("Delete Transaction")

        try:
            # Show all transactions
            all_transactions = self._get_all_transactions()

            if all_transactions is None or all_transactions.empty:
                self.ui.warning("No transactions found to delete", "Empty Database")
                return False

            ID_map = display_transactions_for_selection(
                df=all_transactions, table_title="📑 Select Transaction to Delete"
            )

            # Get user selection
            try:
                serial_no_str = self.ui.input_prompt(
                    "Enter serial number of the record you want to delete"
                )
                serial_no = int(serial_no_str)
            except ValueError:
                self.ui.validation_error("Invalid input. Please enter a number")
                return False

            if serial_no not in ID_map:
                self.ui.validation_error("Invalid transaction selection")
                return False

            transaction_id = ID_map[serial_no]

            # Call the actual delete method
            return self._delete_transaction_by_id(transaction_id)

        except Exception as error:
            self.logger.error(f"Error in delete menu: {error}")
            self.ui.error(f"Error in delete menu: {str(error)}", "Menu Error")
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
                self.ui.warning("Transaction not found", "Not Found")
                return False

            # Show transaction to be deleted
            display_single_transaction(
                df=df,
                table_title="🚮 Transaction to be deleted",
            )

            confirm = self.ui.confirmation_prompt(
                "Are you sure you want to delete this transaction?"
            ).lower()

            if confirm not in ["y", "yes"]:
                self.ui.info("Deletion cancelled by user", "Cancelled")
                return False

            self.ui.process_start("Deleting transaction")

            self.session.delete(transaction)
            self.session.commit()

            self.logger.info(
                f"Successfully deleted transaction with ID: {transaction_id}"
            )
            self.ui.success(
                f"Transaction {transaction_id} deleted successfully", "Deleted"
            )
            return True

        except SQLAlchemyError as error:
            self.logger.error(
                f"Database error deleting transaction {transaction_id}: {error}"
            )
            self.ui.error(
                f"Database error deleting transaction: {str(error)}", "Database Error"
            )
            self.session.rollback()
            return False
        except Exception as error:
            self.logger.error(f"Error deleting transaction {transaction_id}: {error}")
            self.ui.error(f"Error deleting transaction: {str(error)}", "Delete Error")
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
                self.ui.warning("Transaction not found", "Not Found")
                return False

            # Show transaction to be updated
            display_single_transaction(
                df=df,
                table_title="💳 Transaction to be updated",
            )

            self.ui.info("Enter the new details below to update the transaction")

            # Date validation with retry
            while True:
                transaction_date_str = self.ui.input_prompt(
                    "Enter transaction date (DD-MM-YYYY)"
                )
                try:
                    datetime.strptime(transaction_date_str, "%d-%m-%Y")
                    break  # Valid date, exit loop
                except ValueError:
                    self.ui.validation_error(
                        "Invalid date format. Please use DD-MM-YYYY format (e.g., 25-12-2024)"
                    )

            transaction_details = self.ui.input_prompt("Enter transaction details")

            # Amount validation with retry
            while True:
                amount_str = self.ui.input_prompt("Enter amount")
                try:
                    amount = Decimal(amount_str)
                    if amount <= 0:
                        self.ui.validation_error(
                            "Amount cannot be negative. Please enter a positive value"
                        )
                        continue
                    break  # Valid amount, exit loop
                except (ValueError, InvalidOperation):
                    self.ui.validation_error(
                        "Invalid amount format. Please enter a valid number"
                    )

            remarks = self.ui.input_prompt("Enter remarks (Optional)")

            confirm = self.ui.confirmation_prompt(
                "Are you sure you want to update this transaction?"
            ).lower()

            if confirm not in ["y", "yes"]:
                self.ui.info("Update cancelled by user", "Cancelled")
                return False

            self.ui.process_start("Updating transaction")

            transaction.date = datetime.strptime(
                transaction_date_str, "%d-%m-%Y"
            ).date()
            transaction.transaction_details = transaction_details
            transaction.amount = amount
            transaction.remarks = remarks
            self.session.commit()

            self.logger.info(f"Successfully updated transaction with ID: {id}")
            self.ui.success(f"Transaction {id} updated successfully", "Updated")
            return True

        except SQLAlchemyError as error:
            self.logger.error(f"Database error updating transaction {id}: {error}")
            self.ui.error(
                f"Database error updating transaction: {str(error)}", "Database Error"
            )
            self.session.rollback()
            return False
        except Exception as error:
            self.logger.error(f"Error updating transaction {id}: {error}")
            self.ui.error(f"Error updating transaction: {str(error)}", "Update Error")
            return False

    def update_transaction_menu(self):
        """
        Menu interface for updating transactions
        """
        self.ui.separator("Update Transaction")

        try:
            all_transactions = self._get_all_transactions()

            if all_transactions is None or all_transactions.empty:
                self.ui.warning("No transactions found to update", "Empty Database")
                return False

            ID_map = display_transactions_for_selection(
                df=all_transactions, table_title="📑 Select Transaction to Update"
            )

            # Getting user selection
            try:
                serial_no_str = self.ui.input_prompt(
                    "Enter serial number of the record you want to update"
                )
                serial_no = int(serial_no_str)
            except ValueError:
                self.ui.validation_error("Invalid input. Please enter a number")
                return False

            if serial_no not in ID_map:
                self.ui.validation_error("Invalid transaction selection")
                return False

            transaction_id = ID_map[serial_no]

            # Call the actual update method
            result = self._update_transaction_by_id(transaction_id)
            return result

        except Exception as error:
            self.logger.error(f"Error in update menu: {error}")
            self.ui.error(f"Error in update menu: {str(error)}", "Menu Error")
            return False
