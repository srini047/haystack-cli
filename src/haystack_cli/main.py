import typer

from haystack_cli import __version__
from haystack_cli.adapters.sdk import get_haystack_version, HaystackNotFoundError
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
    try:
        return get_haystack_version()
    except HaystackNotFoundError:
        return """`haystack-ai` not installed. Please install using 
                  `pip install haystack-ai` to access all features
               """

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

        raise typer.Exit()
