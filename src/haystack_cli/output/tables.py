from typing import Any
from rich.table import Table
from rich import box
from haystack_cli.output.console import console


def print_config_table(rows: dict[str, tuple[Any, str]]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("Key", style="key", min_width=30)
    table.add_column("Value", min_width=20)
    table.add_column("Source", style="source")

    for key, (value, source) in rows.items():
        display_value = (
            "****" if "api_key" in key else str(value) if value is not None else "[muted]—[/muted]"
        )
        table.add_row(key, display_value, source)

    console.print(table)


def print_schema_table(rows: dict[str, list[str] | None]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("Key", style="key", min_width=30)
    table.add_column("Valid Values")

    for key, choices in rows.items():
        table.add_row(key, " | ".join(choices) if choices else "[muted]any[/muted]")

    console.print(table)
