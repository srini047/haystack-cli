import json
import json
import os
import subprocess
from typing import Annotated

import typer

from haystack_cli.config.loader import (
    PROJECT_CONFIG_PATH,
    GLOBAL_CONFIG_PATH,
    load_with_sources,
)
from haystack_cli.config.schema import FIELD_CHOICES
from haystack_cli.config.writer import (
    ConfigWriter,
    InvalidConfigKeyError,
    InvalidConfigValueError,
)
from haystack_cli.output.console import console
from haystack_cli.output.errors import abort
from haystack_cli.output.tables import print_config_table, print_schema_table

app = typer.Typer(help="Manage Haystack CLI configuration.")


@app.command()
def show(
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Print all resolved config values, annotated with their source."""
    rows = load_with_sources()

    if as_json:
        typer.echo(
            json.dumps({k: {"value": v, "source": s} for k, (v, s) in rows.items()}, indent=2)
        )
        return

    print_config_table(rows)


@app.command()
def get(key: str) -> None:
    """Read a single config value"""
    rows = load_with_sources()
    if key not in rows:
        abort(f"Unknown config key: '{key}'", hint="Run: haystack config schema")

    value, source = rows[key]
    console.print(f"[key]{key}[/key]  {value}  [source]({source})[/source]")


@app.command()
def set(
    key: str,
    value: str,
    global_: Annotated[bool, typer.Option("--global", help="Write to global config.")] = False,
) -> None:
    """Set a config key to a value"""
    try:
        scope = "global config" if global_ else "project.toml"
        console.print(
            f"  [success]✓[/success] Set [key]{key}[/key] = {value}  [source]({scope})[/source]"
        )
    except (InvalidConfigKeyError, InvalidConfigValueError, ValueError) as e:
        abort(str(e))


@app.command()
def schema(
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Show all valid config keys and their accepted values"""
    if as_json:
        typer.echo(json.dumps({k: v for k, v in FIELD_CHOICES.items()}, indent=2))
        return

    print_schema_table(FIELD_CHOICES)


@app.command()
def edit(
    global_: Annotated[bool, typer.Option("--global", help="Edit global config.")] = False,
) -> None:
    """Open the config file in $EDITOR or default to `nano`."""
    path = GLOBAL_CONFIG_PATH if global_ else PROJECT_CONFIG_PATH

    if not path.exists():
        abort(
            f"Config file not found: {path}",
            hint="Run: haystack config init",
        )

    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(path)], check=True)


@app.command()
def init(
    global_: Annotated[bool, typer.Option("--global", help="Initialise global config.")] = False,
) -> None:
    """Interactively create a project or global config file."""
    import questionary

    path = GLOBAL_CONFIG_PATH if global_ else PROJECT_CONFIG_PATH

    if path.exists():
        overwrite = questionary.confirm(f"{path} already exists. Overwrite?").ask()
        if not overwrite:
            raise typer.Exit()

    backend = questionary.select(
        "Document store backend:",
        choices=FIELD_CHOICES["document_store.backend"] or [],
    ).ask()

    host = questionary.text("Document store host:", default="localhost").ask()
    port = questionary.text("Document store port:", default="8080").ask()

    provider = questionary.select(
        "LLM provider:",
        choices=FIELD_CHOICES["llm.provider"] or [],
    ).ask()

    writer = ConfigWriter(global_scope=global_)
    writer.set("document_store.backend", backend)
    writer.set("document_store.host", host)
    writer.set("document_store.port", port)
    writer.set("llm.provider", provider)

    console.print(f"\n  [success]✓[/success] Config written to {path}")
    console.print(f"  [muted]Run [key]haystack config show[/key] to verify.[/muted]")
