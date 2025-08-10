from db.manager import Database
from app_logging.config import setup_logger, get_ui


def display_options():
    print("*" * 50)

    print("1. Press 1 to insert transaction details")
    print("2. Press 2 to see all transactions and total expenditure")
    print("3. Press 3 to delete a transaction")
    print("4. Press 4 to update a transaction")
    print("🚪 Press Ctrl+C to exit the program")

    option_input = input("Enter your option: ")

    print("*" * 50)

    return option_input


if __name__ == "__main__":
    logger = setup_logger("main")
    ui = get_ui()
    logger.info("Starting Credit Card Tracker application")

    try:
        with Database() as db:
            logger.info("Entering main application loop")
            while True:
                option_input = display_options()
                logger.debug(f"User selected option: {option_input}")

                match option_input:
                    case "1":
                        logger.info("User selected: Add transaction")
                        obj = db.add_transaction()
                        continue

                    case "2":
                        logger.info("User selected: Display transactions")
                        db.display_transaction_and_total_expenditure()
                        continue

                    case "3":
                        logger.info("User selected: Delete transaction")
                        db.delete_transaction_menu()
                        continue

                    case "4":
                        logger.info("User selected: Update transaction")
                        db.update_transaction_menu()
                        continue

                    case _:
                        logger.warning(f"Invalid option selected: {option_input}")
                        print("Invalid option. Please try again.")
                        continue

    except ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        ui.error("Database connection failed", "Connection Error")

    except KeyboardInterrupt:
        logger.info("Application terminated by user (Ctrl+C)")
        ui.info("Application terminated by user (Ctrl+C)")

    except Exception as e:
        logger.critical(f"Unexpected error occurred: {e}", exc_info=True)
        ui.error("Unexpected error occurred", "Error")

    finally:
        logger.info("Credit Card Tracker application ended")
