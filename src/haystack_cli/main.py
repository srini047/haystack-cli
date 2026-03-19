import importlib.metadata

import typer

from haystack_cli import __version__
from haystack_cli.commands import config as config_cmd
from haystack_cli.commands import init as init_cmd

app = typer.Typer(
    name="haystack",
    help="The CLI for Haystack Agentic AI Framework.",
    no_args_is_help=True,
)

app.add_typer(config_cmd.app, name="config")
app.add_typer(init_cmd.app, name="init")


def _get_haystack_version() -> str:
    """Get the installed haystack-ai version."""
    try:
        return importlib.metadata.version("haystack-ai")
    except importlib.metadata.PackageNotFoundError:
        return "Currently not installed"

def _get_haystack_cli_version() -> str:
    """Get the current haystack-cli version."""
    return __version__

@app.callback(invoke_without_command=True)
def root(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit.", is_eager=True
    ),
) -> None:
    if version:
        typer.echo(f"haystack-cli - {_get_haystack_cli_version()}")
        typer.echo(f"haystack-ai  - {_get_haystack_version()}")
        typer.echo("")

        raise typer.Exit()
