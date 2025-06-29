import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
import pandas as pd
from .utils import display_transactions_in_table


load_dotenv()


class Database:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.password = os.getenv("DB_PASSWORD")
        self.connection = None

    def connect(self):
        """
        Connects to the database
        """

        try:
            self.connection = psycopg2.connect(
                database=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            print("Connection to the database successful!")

            return True

        except (Exception, psycopg2.Error) as e:
            print("Unable to connect to the database:")
            print(e)
            return False

    def disconnect(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("\nDatabase connection closed.")

        self.connection = None

    """
    Adding the enter and the exit methods makes the class a context manager.
    We can now use the class with 'with' block.
    """

    def __enter__(self):
        """Called automatically when entering 'with' block"""

        if self.connect():
            return self
        else:
            raise ConnectionError("Failed to connect to the database")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called automatically when exiting 'with' block"""
        self.disconnect()
        return False

    def create_table(self, create_table_sql):
        """
        Creates a new table in the database.
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.connection.commit()
                print("Table created successfully.")
                return True

        except (Exception, psycopg2.Error) as error:
            print("Unable to create table:")
            print(error)
            return None

    def insert_into_transaction_table(
        self, transaction_date_str, transaction_details, amount_str, remarks
    ):
        """
        Inserts a new transaction record into the transaction table.
        """
        try:
            date = datetime.strptime(transaction_date_str, "%d-%m-%Y").date()

            amount = Decimal(amount_str)

            with self.connection.cursor() as cursor:
                insert_sql = """
                    INSERT INTO transaction (date, transaction_details, amount, remarks)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """
                cursor.execute(insert_sql, (date, transaction_details, amount, remarks))
                self.connection.commit()
                inserted_id = cursor.fetchone()[0]

                return inserted_id

        except (Exception, psycopg2.Error) as error:
            print("Unable to insert data into the table:")
            print(error)
            return None

    def _get_all_transactions(self):
        """
        Retrieve all transactions from the database using pandas
        Returns: pandas DataFrame or None if error
        """

        try:
            query = """
                SELECT id, date, transaction_details, amount, remarks 
                FROM transaction 
                ORDER BY date DESC, id DESC
            """

            df = pd.read_sql_query(query, self.connection)
            return df

        except (Exception, psycopg2.Error) as error:
            print(f"Unable to retrieve data from the transaction table: {error}")

            return None

    def _get_total_amount(self):
        """
        Calculate total amount of all transactions
        Returns: Decimal total or None if error
        """

        try:
            query = "SELECT SUM(amount) as total FROM transaction"

            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()[0]

            total = result if result is not None else Decimal("0.00")
            return total

        except (Exception, psycopg2.Error) as error:
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
            query = """
                SELECT id, date, transaction_details, amount, remarks 
                FROM transaction 
                WHERE id = %s
            """

            df = pd.read_sql_query(query, self.connection, params=(transaction_id,))

            return df

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Error fetching transaction: {error}")

            return pd.DataFrame()

    def delete_transaction_by_id(self, transaction_id):
        try:
            df = self._get_transaction_by_id(transaction_id)

            if df is None or df.empty:
                print("❌ Transaction not found.")
                return False

            display_transactions_in_table(
                df=df,
                table_title="🚮  Transaction to be deleted",
            )

            confirm = input(
                "⚠️  Are you sure you want to delete this transaction? (y/N): "
            ).lower()

            if confirm not in ["y", "yes"]:
                print("❌ Deletion cancelled.")
                return False

            with self.connection.cursor() as cursor:
                delete_query = "DELETE FROM transaction WHERE id = %s"
                cursor.execute(delete_query, (transaction_id,))
                self.connection.commit()

                if cursor.rowcount > 0:
                    print(
                        f"✅ Transaction with ID {transaction_id} deleted successfully."
                    )
                    return True
                else:
                    print(f"❌ Failed to delete transaction with ID {transaction_id}.")
                    return False

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Error deleting transaction: {error}")
            return False
