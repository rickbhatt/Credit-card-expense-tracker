from db.manager import Database
import warnings
from datetime import datetime
from decimal import Decimal, InvalidOperation


def display_options():
    print("*" * 50, end="\n")

    print("1. Press 1 to insert transaction details")
    print("2. Press 2 to see all transactions and total expenditure")
    print("3. Press 3 to exit the program")

    option_input = input("Enter your option: ")

    print("*" * 50, end="\n")

    return option_input


def insert(db):
    print("Inserting into transaction table")

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
                print("❌ Amount cannot be negative. Please enter a positive value.")
                continue
            break  # Valid amount, exit loop
        except (ValueError, InvalidOperation):
            print("❌ Invalid amount format. Please enter a valid number.")

    remarks = input("Enter remarks (Optional): ")

    return db.insert_into_transaction_table(
        transaction_date_str=transaction_date_str,
        transaction_details=transaction_details,
        amount_str=amount_str,
        remarks=remarks,
    )


if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
    try:
        with Database() as db:
            while True:
                option_input = display_options()

                match option_input:
                    case "1":
                        try:
                            obj = insert(db)
                            if obj:
                                print(f"Transaction inserted with id: {obj}")
                            else:
                                print(
                                    "Failed to insert transaction. Please check your input."
                                )
                        except Exception as e:
                            print(f"Error inserting transaction: {e}")
                        continue

                    case "2":
                        db.display_transaction_and_total_expenditure()
                        continue

                    case "3":
                        print("Exiting program...")

                        break

                    case _:
                        print("Invalid option. Please try again.")
                        continue
    except ConnectionError as e:
        print(f"Failed to connect to database: {e}")
        print("Please check your database configuration.")

    except KeyboardInterrupt:
        print("\n⚠️ Program exited.")

    except Exception as e:
        print("Something went wrong: ", e)
