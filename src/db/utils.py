from rich.console import Console
from rich.table import Table
from rich.text import Text
import pandas as pd


def display_transactions_and_total(df, total):
    """
    Displays the transactions in a tabular form and also the total
    """
    try:
        # Create Rich console and table

        console = Console()

        table = Table(
            title="💳 Credit Card Transactions",
            show_header=True,
            header_style="bold magenta",
        )

        # Add columns
        table.add_column("ID", style="dim", width=6)
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Transaction Details", style="white", width=40)
        table.add_column("Amount", style="green", justify="right", width=12)
        table.add_column("Remarks", style="yellow", width=20)

        # Add rows from DataFrame
        for _, row in df.iterrows():
            # Format amount with currency symbol
            amount_str = f"₹{row['amount']:,.2f}"

            date_str = f"{row['date'].strftime('%d-%b-%Y')}"

            # Handle empty remarks
            remarks = (
                row["remarks"] if pd.notna(row["remarks"]) and row["remarks"] else "-"
            )

            table.add_row(
                str(row["id"]),
                date_str,
                str(row["transaction_details"]),
                amount_str,
                remarks,
            )

        # Display the table
        console.print(table)

        # Display total with styling
        console.print()
        total_text = Text(f"💰 Total Amount: ₹{total:,.2f}", style="bold green")
        console.print(total_text)
        console.print()

    except Exception as e:
        raise Exception(f"An error occurred in display_transactions_and_total: {e}")
