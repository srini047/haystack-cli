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


@app.callback(invoke_without_command=True)
def root(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit.", is_eager=True
    ),
) -> None:
    if version:
        typer.echo(f"haystack-cli {__version__}")
        raise typer.Exit()
