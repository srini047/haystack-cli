import typer

from haystack_cli.output.console import err_console


def abort(message: str, hint: str | None = None) -> None:
    """Print a formatted error and exit."""
    err_console.print(f"\n  [error]✗[/error] {message}")
    if hint:
        err_console.print(f"  [muted]{hint}[/muted]\n")
    raise typer.Exit(code=1)
