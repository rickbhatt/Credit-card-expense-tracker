from db.manager import Database


def display_options():
    print("*" * 50)

    print("1. Press 1 to insert transaction details")
    print("2. Press 2 to see all transactions and total expenditure")
    print("3. Press 3 to delete a transaction")
    print("🚪 Press Ctrl+C to exit the program")

    option_input = input("Enter your option: ")

    print("*" * 50)

    return option_input


if __name__ == "__main__":
    try:
        with Database() as db:
            while True:
                option_input = display_options()

                match option_input:
                    case "1":
                        obj = db.add_transaction()

                        continue

                    case "2":
                        db.display_transaction_and_total_expenditure()
                        continue

                    case "3":
                        db.delete_transaction_menu()
                        continue

                    case _:
                        print("Invalid option. Please try again.")
                        continue
    except ConnectionError as e:
        print(f"❌ Failed to connect to database: {e}")
        print("❌ Please check your database configuration.")

    except KeyboardInterrupt:
        print("⚠️ Program exited.")

    except Exception as e:
        print("❌ Something went wrong: ", e)
