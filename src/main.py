from db.manager import Database
import warnings


if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
    try:
        with Database() as db:
            while True:
                print("*" * 50, end="\n")

                print("1. Press 1 to insert transaction details")
                print("2. Press 2 to see all transactions and total expenditure")
                print("3. Press 3 to exit the program")

                option_input = input("Enter your option: ")

                print("*" * 50, end="\n")

                match option_input:
                    case "1":
                        print("Inserting into transaction table")

                        transaction_date_str = input(
                            "Enter transaction date DD-MM-YYYY: "
                        )
                        transaction_details = input("Enter transaction details: ")
                        amount_str = input("Enter amount: ")
                        remarks = input("Enter remarks (Optional): ")

                        obj = db.insert_into_transaction_table(
                            transaction_date_str=transaction_date_str,
                            transaction_details=transaction_details,
                            amount_str=amount_str,
                            remarks=remarks,
                        )
                        if obj:
                            print(f"Transaction inserted with id: {obj}")

                            continue
                        break

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

    except Exception as e:
        print("Something went wrong: ", e)
