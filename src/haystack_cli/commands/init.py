from pathlib import Path

import questionary
import typer

from haystack_cli.config.schema import FIELD_CHOICES
from haystack_cli.core.pipeline.scaffold import PipelineScaffold, ProjectExistsError
from haystack_cli.output.console import console
from haystack_cli.output.errors import abort

app = typer.Typer(help="Scaffold a new Haystack project.")


@app.callback(invoke_without_command=True)
def init(project_name: str = typer.Argument(default="")) -> None:
    """Scaffold a new Haystack project. Runs interactively if no name is given."""
    if not project_name:
        project_name = questionary.text(
            "Project name:",
            validate=lambda v: True if v.strip() else "Project name cannot be empty.",
        ).ask()
        if not project_name:
            raise typer.Exit()

    project_name = project_name.strip()

    document_store = questionary.select(
        "Document store backend:",
        choices=FIELD_CHOICES["document_store.backend"] or [],
    ).ask()

    llm_provider = questionary.select(
        "LLM provider:",
        choices=FIELD_CHOICES["llm.provider"] or [],
    ).ask()

    scaffold = PipelineScaffold()
    context = scaffold.build_context(
        document_store=document_store,
        llm_provider=llm_provider,
    )

    project_dir = Path.cwd() / project_name

    try:
        created = scaffold.write_project(project_dir, context)
    except ProjectExistsError as e:
        abort(str(e), hint="Choose a different name or remove the existing directory.")

    console.print(f"\n  [success]✓[/success] Created [key]{project_name}/[/key]\n")
    for path in created:
        console.print(f"    [muted]{path.relative_to(Path.cwd())}[/muted]")

    console.print(f"\n  [info]Next steps:[/info]")
    console.print(f"    cd {project_name}")
    console.print(f"    cp .env.example .env")
    console.print(f"    haystack pipeline validate retrieval.yaml")
    console.print(f"    haystack pipeline run retrieval.yaml\n")
