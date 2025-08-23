from db.manager import Database
from app_logging.config import setup_logger, get_ui
from InquirerPy import inquirer
from InquirerPy.base.control import Choice


def display_options() -> str:
    print("*" * 50)

    action = inquirer.select(
        message="Select an option",
        choices=[
            Choice(value="insert", name="Add new transaction"),
            Choice(value="view", name="View all transactions"),
            Choice(value="update", name="Update a transaction"),
            Choice(value="delete", name="Delete a transaction"),
        ],
    ).execute()

    return action


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
                    case "insert":
                        logger.info("User selected: Add transaction")
                        obj = db.add_transaction()
                        continue

                    case "view":
                        logger.info("User selected: Display transactions")
                        db.display_transaction_and_total_expenditure()
                        continue

                    case "delete":
                        logger.info("User selected: Delete transaction")
                        db.delete_transaction_menu()
                        continue

                    case "update":
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
