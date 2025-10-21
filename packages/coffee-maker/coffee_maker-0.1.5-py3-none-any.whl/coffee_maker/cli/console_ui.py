"""Console UI utilities for rich, Claude-CLI quality terminal output.

This module provides centralized UI utilities for consistent, professional
terminal output across all CLI commands using the rich library.

US-036: Polish Console UI to Claude-CLI Quality Standard

Key Features:
    - Consistent color scheme (Info: blue, Success: green, Warning: yellow, Error: red)
    - Professional formatting (panels, tables, progress indicators)
    - Helpful error messages with suggestions
    - Clear visual separation between sections
    - Status indicators for real-time feedback

Example:
    >>> from coffee_maker.cli.console_ui import console, success, error, info
    >>> console.print("Hello world")
    >>> success("Task completed successfully!")
    >>> error("Something went wrong", suggestion="Try running with --debug")
"""

from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

# Shared console instance for consistent output
console = Console()

# Color scheme matching Claude CLI quality
COLORS = {
    "info": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim white",
    "highlight": "cyan",
    "accent": "magenta",
}

# Status symbols
SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "working": "⚙",
    "thinking": "🧠",
    "idle": "💤",
}


def success(message: str, details: Optional[str] = None) -> None:
    """Print success message with green checkmark.

    Args:
        message: Success message
        details: Optional additional details
    """
    text = f"[{COLORS['success']}]{SYMBOLS['success']}[/{COLORS['success']}] [bold]{message}[/bold]"
    if details:
        text += f"\n   [{COLORS['muted']}]{details}[/{COLORS['muted']}]"
    console.print(text)


def error(message: str, suggestion: Optional[str] = None, details: Optional[str] = None) -> None:
    """Print error message with red X and optional suggestion.

    Args:
        message: Error message
        suggestion: Optional suggestion for fixing the error
        details: Optional technical details
    """
    text = f"[{COLORS['error']}]{SYMBOLS['error']} Error:[/{COLORS['error']}] [bold]{message}[/bold]"

    if suggestion:
        text += f"\n   [{COLORS['info']}]💡 Suggestion:[/{COLORS['info']}] {suggestion}"

    if details:
        text += f"\n   [{COLORS['muted']}]Details: {details}[/{COLORS['muted']}]"

    console.print(text)


def warning(message: str, suggestion: Optional[str] = None) -> None:
    """Print warning message with yellow warning symbol.

    Args:
        message: Warning message
        suggestion: Optional suggestion for addressing the warning
    """
    text = f"[{COLORS['warning']}]{SYMBOLS['warning']} Warning:[/{COLORS['warning']}] {message}"

    if suggestion:
        text += f"\n   [{COLORS['info']}]💡 Suggestion:[/{COLORS['info']}] {suggestion}"

    console.print(text)


def info(message: str, details: Optional[str] = None) -> None:
    """Print info message with blue info symbol.

    Args:
        message: Info message
        details: Optional additional details
    """
    text = f"[{COLORS['info']}]{SYMBOLS['info']}[/{COLORS['info']}] {message}"

    if details:
        text += f"\n   [{COLORS['muted']}]{details}[/{COLORS['muted']}]"

    console.print(text)


def status(message: str, state: str = "working") -> None:
    """Print status message with appropriate symbol.

    Args:
        message: Status message
        state: State (working, thinking, idle, success, error, warning, info)
    """
    symbol = SYMBOLS.get(state, SYMBOLS["info"])
    color = COLORS.get(state, COLORS["info"])

    console.print(f"[{color}]{symbol}[/{color}] {message}")


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    """Print section header with visual separation.

    Args:
        title: Section title
        subtitle: Optional subtitle
    """
    console.print()
    console.rule(f"[bold {COLORS['highlight']}]{title}[/bold {COLORS['highlight']}]")

    if subtitle:
        console.print(f"[{COLORS['muted']}]{subtitle}[/{COLORS['muted']}]")

    console.print()


def create_table(
    title: Optional[str] = None,
    columns: Optional[List[str]] = None,
    show_header: bool = True,
) -> Table:
    """Create a formatted table with consistent styling.

    Args:
        title: Optional table title
        columns: Optional list of column headers
        show_header: Whether to show column headers

    Returns:
        Rich Table instance ready for adding rows
    """
    table = Table(
        show_header=show_header,
        header_style=f"bold {COLORS['highlight']}",
        border_style=COLORS["muted"],
        title=title,
        title_style=f"bold {COLORS['accent']}",
    )

    if columns:
        for col in columns:
            table.add_column(col)

    return table


def create_panel(
    content: Any,
    title: Optional[str] = None,
    border_style: str = "blue",
    padding: tuple = (1, 2),
) -> Panel:
    """Create a formatted panel with consistent styling.

    Args:
        content: Panel content (can be string, Table, or other Rich renderable)
        title: Optional panel title
        border_style: Border color style
        padding: Padding tuple (vertical, horizontal)

    Returns:
        Rich Panel instance
    """
    return Panel(content, title=title, border_style=border_style, padding=padding)


def progress_context(description: str = "Processing..."):
    """Create a progress context manager for long operations.

    Args:
        description: Progress description

    Returns:
        Progress context manager

    Example:
        >>> with progress_context("Loading data...") as progress:
        ...     task = progress.add_task(description, total=100)
        ...     for i in range(100):
        ...         progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )


def format_key_value(key: str, value: Any, key_style: str = "bold cyan") -> Text:
    """Format key-value pair for display.

    Args:
        key: Key text
        value: Value text
        key_style: Style for key (default: bold cyan)

    Returns:
        Rich Text instance
    """
    text = Text()
    text.append(f"{key}: ", style=key_style)
    text.append(str(value))
    return text


def format_metric(label: str, value: Any, unit: str = "", good_threshold: Optional[float] = None) -> str:
    """Format metric with color coding based on threshold.

    Args:
        label: Metric label
        value: Metric value
        unit: Optional unit suffix
        good_threshold: Optional threshold for color coding (above = green, below = yellow)

    Returns:
        Formatted metric string
    """
    # Determine color
    color = COLORS["muted"]
    if good_threshold is not None and isinstance(value, (int, float)):
        color = COLORS["success"] if value >= good_threshold else COLORS["warning"]

    value_str = f"{value}{unit}" if unit else str(value)
    return f"[{color}]{label}:[/{color}] [bold]{value_str}[/bold]"


def format_list(items: List[str], bullet: str = "•", indent: int = 2) -> str:
    """Format list with bullets and consistent indentation.

    Args:
        items: List of items
        bullet: Bullet character
        indent: Indentation spaces

    Returns:
        Formatted list string
    """
    spaces = " " * indent
    lines = [f"{spaces}[{COLORS['highlight']}]{bullet}[/{COLORS['highlight']}] {item}" for item in items]
    return "\n".join(lines)


def format_error_with_suggestions(
    error_message: str, suggestions: List[str], error_details: Optional[str] = None
) -> Panel:
    """Format error with helpful suggestions in a panel.

    Args:
        error_message: Main error message
        suggestions: List of suggestions for fixing the error
        error_details: Optional technical error details

    Returns:
        Rich Panel with formatted error and suggestions
    """
    content = []

    # Error message
    content.append(f"[bold {COLORS['error']}]{SYMBOLS['error']} {error_message}[/bold {COLORS['error']}]")
    content.append("")

    # Error details if provided
    if error_details:
        content.append(f"[{COLORS['muted']}]{error_details}[/{COLORS['muted']}]")
        content.append("")

    # Suggestions
    if suggestions:
        content.append(f"[{COLORS['info']}]💡 Suggestions:[/{COLORS['info']}]")
        content.append(format_list(suggestions))

    return Panel(
        "\n".join(content),
        title=f"[bold {COLORS['error']}]Error[/bold {COLORS['error']}]",
        border_style=COLORS["error"],
        padding=(1, 2),
    )


def format_notification(
    notif_type: str,
    title: str,
    message: str,
    priority: str = "normal",
    created_at: Optional[str] = None,
) -> Panel:
    """Format notification with appropriate styling based on type and priority.

    Args:
        notif_type: Notification type (question, info, warning, error, completion)
        title: Notification title
        message: Notification message
        priority: Priority level (critical, high, normal, low)
        created_at: Optional creation timestamp

    Returns:
        Rich Panel with formatted notification
    """
    # Determine color and symbol
    type_map = {
        "question": (COLORS["info"], "❓"),
        "info": (COLORS["info"], SYMBOLS["info"]),
        "warning": (COLORS["warning"], SYMBOLS["warning"]),
        "error": (COLORS["error"], SYMBOLS["error"]),
        "completion": (COLORS["success"], SYMBOLS["success"]),
    }

    color, symbol = type_map.get(notif_type, (COLORS["info"], SYMBOLS["info"]))

    # Adjust for priority
    if priority == "critical":
        color = COLORS["error"]
        symbol = "🚨"
    elif priority == "high":
        symbol = "‼️"

    # Build content
    content = []
    content.append(f"[bold {color}]{symbol} {title}[/bold {color}]")
    content.append("")
    content.append(message)

    if created_at:
        content.append("")
        content.append(f"[{COLORS['muted']}]Created: {created_at}[/{COLORS['muted']}]")

    border_style = color if priority in ["critical", "high"] else "white"

    return Panel(
        "\n".join(content),
        title=f"[bold]{notif_type.upper()}[/bold]",
        border_style=border_style,
        padding=(1, 2),
    )


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask user for confirmation with consistent styling.

    Args:
        prompt: Confirmation prompt
        default: Default value if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    default_str = "[Y/n]" if default else "[y/N]"
    full_prompt = f"[{COLORS['info']}]{prompt} {default_str}:[/{COLORS['info']}] "

    console.print(full_prompt, end="")
    response = input().strip().lower()

    if not response:
        return default

    return response in ["y", "yes"]


def print_separator(char: str = "─", style: str = "dim white") -> None:
    """Print a visual separator line.

    Args:
        char: Character to use for separator
        style: Rich style for the separator
    """
    console.rule(style=style, characters=char)
