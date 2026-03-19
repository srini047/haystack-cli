from pathlib import Path

import questionary
import typer

from haystack_cli.config.schema import FIELD_CHOICES
from haystack_cli.core.pipeline.scaffold import PipelineScaffold, ProjectExistsError
from haystack_cli.output.console import console
from haystack_cli.output.errors import abort

app = typer.Typer(help="Scaffold a new Haystack project.")

# Maps pipeline type choice → (pipeline template, indexing template)
_PIPELINE_TEMPLATES: dict[str, tuple[str, str]] = {
    "RAG": ("rag-basic", "indexing-basic"),
    "Hybrid retrieval": ("hybrid-retrieval", "indexing-basic"),
}

SAMPLE_DOCUMENT_CONTENT = """
"Haystack is an open-source framework for building LLM pipelines.\n"
"It supports RAG, agents, and custom pipeline topologies.\n"
"""


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

    pipeline_type = questionary.select(
        "Pipeline type:", choices=list(_PIPELINE_TEMPLATES.keys())
    ).ask()

    document_store = questionary.select(
        "Document store backend:",
        choices=FIELD_CHOICES["document_store.backend"] or [],
    ).ask()

    llm_provider = questionary.select(
        "LLM provider:",
        choices=FIELD_CHOICES["llm.provider"] or [],
    ).ask()

    include_examples = questionary.confirm("Include example documents?", default=True).ask()

    # All prompts answered — resolve templates and write project
    pipeline_tmpl, indexing_tmpl = _PIPELINE_TEMPLATES[pipeline_type]
    context = {
        "llm_provider": llm_provider,
        "document_store": document_store,
    }

    scaffold = PipelineScaffold()
    project_dir = Path.cwd() / project_name

    try:
        created = scaffold.write_project(project_dir, pipeline_tmpl, indexing_tmpl, context)
    except ProjectExistsError as e:
        abort(
            str(e),
            hint="Choose a different project name or remove the existing directory.",
        )

    if include_examples:
        _write_example_doc(project_dir)

    console.print(f"\n  [success]✓[/success] Created [key]{project_name}/[/key]\n")
    for path in created:
        console.print(f"    [muted]{path.relative_to(Path.cwd())}[/muted]")

    console.print(f"\n  [info]Next steps:[/info]")
    console.print(f"    cd {project_name}")
    console.print(f"    cp .env.example .env")
    console.print(f"    haystack pipeline validate pipeline.yaml")
    console.print(f"    haystack pipeline run pipeline.yaml\n")


def _write_example_doc(project_dir: Path) -> None:
    docs_dir = project_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "example.txt").write_text(SAMPLE_DOCUMENT_CONTENT)
