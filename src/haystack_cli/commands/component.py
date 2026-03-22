import json
from typing import Annotated

import typer

from haystack_cli.core.component.inspector import (
    ComponentInspector,
    ComponentNotFoundError,
)
from haystack_cli.core.component.registry import ComponentRegistry
from haystack_cli.output.errors import abort
from haystack_cli.output.tables import print_component_info, print_component_list

app = typer.Typer(help="Browse and inspect Haystack components.")


@app.command("list")
def list_components(
    type_filter: Annotated[
        str | None, typer.Option("--type", "-t", help="Filter by category.")
    ] = None,
    search: Annotated[str | None, typer.Option("--search", "-s", help="Search by keyword.")] = None,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """List all available Haystack components, grouped by type."""
    registry = ComponentRegistry()

    if search:
        results = registry.search(search)
        if not results:
            abort(f"No components found matching '{search}'.")
            return

        if as_json:
            typer.echo(json.dumps(results, indent=2))
            return

        print_component_list({"search results": results})

        return

    if type_filter:
        components = registry.list_by_category(type_filter)
        if not components:
            categories = ", ".join(registry.available_categories())
            abort(
                f"Unknown category: '{type_filter}'",
                hint=f"Available: {categories}",
            )
        data = {type_filter: components}
    else:
        data = registry.list_all()

    if as_json:
        typer.echo(json.dumps(data, indent=2))
        return

    print_component_list(data)


@app.command()
def info(
    name: str,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Show full schema, init params, and sockets for a component."""
    try:
        data = ComponentInspector().info(name)
    except ComponentNotFoundError as e:
        abort(str(e))

    if as_json:
        typer.echo(json.dumps(data, indent=2))
        return

    print_component_info(data)
