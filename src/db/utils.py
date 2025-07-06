from rich.console import Console
from rich.table import Table
from rich.text import Text
import pandas as pd


def _create_transaction_table(df, table_title=None):
    """
    Private helper method to create a Rich table from DataFrame
    Returns: (table, ID_map)
    """
    console = Console()

    table = Table(
        title=table_title,
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    # Add columns
    table.add_column("Sl No.", style="dim", width=6)
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Transaction Details", style="white", width=40)
    table.add_column("Amount", style="green", justify="right", width=12)
    table.add_column("Remarks", style="yellow", width=20)

    # Create ID mapping
    ID_map = dict(enumerate(df["id"], start=1))

    # Add rows from DataFrame
    for index, row in df.iterrows():
        # Format amount with currency symbol
        amount_str = f"₹{row['amount']:,.2f}"
        date_str = f"{row['date'].strftime('%d-%b-%Y')}"

        # Handle empty remarks
        remarks = row["remarks"] if pd.notna(row["remarks"]) and row["remarks"] else "-"

        table.add_row(
            str(index + 1),
            date_str,
            str(row["transaction_details"]),
            amount_str,
            remarks,
        )

    return table, ID_map, console


def display_transactions_in_table(df, total=0.00, table_title=None):
    """
    Displays transactions in a table format (pure display, no return value)

    Args:
        df (pandas.DataFrame): DataFrame containing transaction data
        total (float): Total amount to display at bottom
        table_title (str): Title for the table
    """
    try:
        if df is None or df.empty:
            console = Console()
            console.print("📭 No transactions found.", style="yellow")
            return

        # Create table
        table, _, console = _create_transaction_table(df, table_title)

        # Display the table
        console.print(table)

        # Display total with styling
        if total > 0.00:
            console.print()
            total_text = Text(
                f"💰 Total Expenditure: ₹{total:,.2f}", style="bold green"
            )
            console.print(total_text)
            console.print()

    except Exception as e:
        raise Exception(f"An error occurred in display_transactions_in_table: {e}")


def display_transactions_for_selection(df, table_title=None):
    """
    Displays transactions in a table and returns ID mapping for user selection

    Args:
        df (pandas.DataFrame): DataFrame containing transaction data
        table_title (str): Title for the table

    Returns:
        dict: Mapping of serial numbers to transaction IDs {1: id1, 2: id2, ...}
              Returns empty dict if no transactions
    """
    try:
        if df is None or df.empty:
            console = Console()
            console.print("📭 No transactions found.", style="yellow")
            return {}

        # Create table
        table, ID_map, console = _create_transaction_table(df, table_title)

        # Display the table
        console.print(table)

        # Add instruction for user
        console.print()
        instruction_text = Text(
            f"📝 Select a transaction by entering its serial number (1-{len(ID_map)})",
            style="bold blue",
        )
        console.print(instruction_text)
        console.print()

        return ID_map

    except Exception as e:
        raise Exception(f"An error occurred in display_transactions_for_selection: {e}")


def display_single_transaction(df, table_title=None):
    """
    Display a single transaction (used for confirmations)

    Args:
        df (pandas.DataFrame): DataFrame containing single transaction
        table_title (str): Title for the table
    """
    try:
        if df is None or df.empty:
            console = Console()
            console.print("❌ No transaction data to display.", style="red")
            return

        # For single transaction, we don't need ID mapping
        table, _, console = _create_transaction_table(df, table_title)
        console.print(table)

    except Exception as e:
        raise Exception(f"An error occurred in display_single_transaction: {e}")
