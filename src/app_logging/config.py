import logging
import logging.handlers
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from typing import Optional


# Global Rich console instance for user-facing messages
console = Console()


def setup_logger(name: str = "credit_card_tracker", level: str = "INFO"):
    """
    Set up logging configuration for the credit card tracker application.
    All logs go to file only. No console handler.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """

    # Create logs directory if it doesn't exist
    project_root = Path(__file__).resolve().parent.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    log_file = logs_dir / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)

    return logger


class UserInterfaceLogger:
    """
    Rich-based user interface for beautiful console output.
    Handles all user-facing messages with proper styling.
    """

    def __init__(self):
        self.console = console

        self.symbols = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "💡",
            "process": "🔄",
        }

    def success(self, message: str, title: Optional[str] = None):
        """Display success message with green styling."""

        if title:
            panel = Panel(
                f"[green]{self.symbols['success']} {message}[/green]",
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
            )

            self.console.print(panel)

        else:
            rprint(f"[green]{self.symbols['success']} {message}[/green]")

    def error(self, message: str, title: Optional[str] = None):
        """Display error message with red styling."""

        if title:
            panel = Panel(
                f"[red]{self.symbols['error']} {message}[/red]",
                title=f"[bold red]{title}[/bold red]",
                border_style="red",
            )
            self.console.print(panel)
        else:
            rprint(f"[red]{self.symbols['error']} {message}[/red]")

    def warning(self, message: str, title: Optional[str] = None):
        """Display warning message with yellow styling."""

        if title:
            panel = Panel(
                f"[yellow]{self.symbols['warning']} {message}[/yellow]",
                title=f"[bold yellow]{title}[/bold yellow]",
                border_style="yellow",
            )
            self.console.print(panel)
        else:
            rprint(f"[yellow]{self.symbols['warning']} {message}[/yellow]")

    def info(self, message: str, title: Optional[str] = None):
        """Display info message with blue styling."""

        if title:
            panel = Panel(
                f"[blue]{self.symbols['info']} {message}[/blue]",
                title=f"[bold blue]{title}[/bold blue]",
                border_style="blue",
            )
            self.console.print(panel)
        else:
            rprint(f"[blue]{self.symbols['info']} {message}[/blue]")

    def process_start(self, message: str):
        """Indicate start of a process."""

        symbol = self.symbols["process"]

        rprint(f"[cyan]{symbol} {message}...[/cyan]")

    def process_complete(self, message: str):
        """Indicate completion of a process."""

        rprint(f"[green]{self.symbols['success']} {message}[/green]")

    def input_prompt(self, prompt: str) -> str:
        """Styled input prompt."""
        return self.console.input(f"[bold cyan]{prompt}:[/bold cyan] ")

    def confirmation_prompt(self, message: str) -> str:
        """Styled confirmation prompt."""
        return self.console.input(
            f"[bold yellow]{self.symbols['warning']} {message} (y/N):[/bold yellow] "
        )

    def validation_error(self, message: str):
        """Display validation error."""

        rprint(f"[red]{self.symbols['error']} {message}[/red]")

    def separator(self, title: Optional[str] = None):
        """Print a separator line."""
        if title:
            self.console.rule(f"[bold blue]{title}[/bold blue]", style="blue")
        else:
            self.console.rule(style="dim")

    def status_panel(self, title: str, content: dict):
        """Display a status panel with key-value pairs."""
        text = Text()
        for key, value in content.items():
            text.append(f"{key}: ", style="cyan")
            text.append(f"{value}\n", style="white")

        panel = Panel(
            text,
            title=f"[bold blue]{title}[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(panel)


ui = UserInterfaceLogger()


def get_console() -> Console:
    """Get the global Rich console instance."""
    return console


def get_ui() -> UserInterfaceLogger:
    """Get the global user interface instance."""
    return ui
