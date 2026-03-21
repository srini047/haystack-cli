import json
from typing import Annotated, Optional

import typer

from haystack_cli.adapters.document_store import (
    DocumentStoreConnectionError,
    UnsupportedBackendError,
)
from haystack_cli.core.document.lister import DocumentLister
from haystack_cli.core.document.searcher import DocumentSearcher
from haystack_cli.output.errors import abort
from haystack_cli.output.tables import print_document_list, print_document_search

app = typer.Typer(help="Inspect documents in the configured document store.")


@app.command("list")
def list_documents(
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="Max documents to show.")
    ] = 20,
    filter_field: Annotated[
        Optional[str], typer.Option("--filter-field", help="Meta field to filter on.")
    ] = None,
    filter_value: Annotated[
        Optional[str], typer.Option("--filter-value", help="Value to match.")
    ] = None,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """List documents in the configured document store."""
    try:
        data = DocumentLister().list(
            limit=limit, filter_field=filter_field, filter_value=filter_value
        )
    except (DocumentStoreConnectionError, UnsupportedBackendError) as e:
        abort(str(e))

    if as_json:
        typer.echo(json.dumps(data, indent=2, default=str))
        return

    print_document_list(data)


@app.command()
def search(
    query: str,
    top_k: Annotated[int, typer.Option("--top-k", "-k", help="Number of results.")] = 5,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Search documents in the configured document store."""
    try:
        data = DocumentSearcher().search(query=query, top_k=top_k)
    except (DocumentStoreConnectionError, UnsupportedBackendError) as e:
        abort(str(e))

    if as_json:
        typer.echo(json.dumps(data, indent=2, default=str))
        return

    print_document_search(data)
