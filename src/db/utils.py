from rich.console import Console
from rich.table import Table
from rich.text import Text
import pandas as pd


def display_transactions_in_table(df, total=0.00, table_title=None):
    """
    Displays the transactions in a tabular form and also the total
    """
    try:
        # Create Rich console and table

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
        table.add_column(
            "Amount",
            style="green",
            justify="right",
            width=12,
        )
        table.add_column("Remarks", style="yellow", width=20)

        """
        mapped the ids to sl_no so that user does not need ids to do operations
        instead just mention the sl_no
        """
        ID_Map = dict(enumerate(df["id"], start=1))

        # Add rows from DataFrame
        for index, row in df.iterrows():
            # Format amount with currency symbol

            amount_str = f"₹{row['amount']:,.2f}"

            date_str = f"{row['date'].strftime('%d-%b-%Y')}"

            # Handle empty remarks
            remarks = (
                row["remarks"] if pd.notna(row["remarks"]) and row["remarks"] else "-"
            )

            table.add_row(
                str(index + 1),
                date_str,
                str(row["transaction_details"]),
                amount_str,
                remarks,
            )

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

        return ID_Map

    except Exception as e:
        raise Exception(f"An error occurred in display_transactions_and_total: {e}")
