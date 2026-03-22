import json
from pathlib import Path
from typing import Annotated

import questionary
import typer

from haystack_cli.adapters.pipeline import PipelineLoadError, load
from haystack_cli.config.schema import FIELD_CHOICES
from haystack_cli.core.pipeline.benchmark import PipelineBenchmark
from haystack_cli.core.pipeline.diff import PipelineDiff
from haystack_cli.core.pipeline.inspector import PipelineInspector
from haystack_cli.core.pipeline.runner import PipelineRunner
from haystack_cli.core.pipeline.scaffold import PipelineScaffold, TemplateNotFoundError
from haystack_cli.core.pipeline.validator import PipelineValidator
from haystack_cli.core.pipeline.visualizer import PipelineVisualizer
from haystack_cli.output.console import console
from haystack_cli.output.errors import abort
from haystack_cli.output.tables import (
    print_benchmark_result,
    print_diff_result,
    print_inspect_result,
    print_run_result,
    print_validation_result,
)

app = typer.Typer(help="Manage and run Haystack pipelines.")
template_app = typer.Typer(help="Work with pipeline templates.")
app.add_typer(template_app, name="template")

_DEFAULT_PIPELINES_DIR = Path("pipelines")
_PIPELINES_ASSESTS_DIR = Path("assets") / "pipelines"


@template_app.command("list")
def template_list(
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """List all available built-in pipeline templates"""

    templates = PipelineScaffold().list_templates()

    if as_json:
        typer.echo(json.dumps(templates, indent=2))
        return

    console.print("\n  [info]Available templates:[/info]\n")
    for name in templates:
        console.print(f"    [key]{name}[/key]")
    console.print()


@template_app.command("use")
def template_use(
    name: str,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output directory.")] = None,
) -> None:
    """Copy a pipeline template into the project (default: pipelines/)"""

    scaffold = PipelineScaffold()

    try:
        scaffold.read_template(name)  # validate name exists before prompting
    except TemplateNotFoundError as e:
        abort(str(e), hint="Run: haystack pipeline template list")

    document_store = questionary.select(
        "Document store:",
        choices=FIELD_CHOICES["document_store.backend"] or [],
    ).ask()

    llm_provider = questionary.select(
        "LLM provider:",
        choices=FIELD_CHOICES["llm.provider"] or [],
    ).ask()

    context = scaffold.build_context(document_store=document_store, llm_provider=llm_provider)
    content = scaffold._interpolate(scaffold.read_template(name), context)

    out_dir = output or _DEFAULT_PIPELINES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{name}.yaml"

    if dest.exists():
        console.print(f"\n  [warning]⚠[/warning]  {dest} already exists.\n")
        if not questionary.confirm("Overwrite?", default=False).ask():
            raise typer.Exit()

    dest.write_text(content, encoding="utf-8")
    console.print(f"  [success]✓[/success] Copied template to [key]{dest}[/key]")


@app.command()
def create() -> None:
    """Guided wizard to create a new pipeline YAML from a template"""

    name = questionary.text(
        "Pipeline name:",
        validate=lambda v: True if v.strip() else "Name cannot be empty.",
    ).ask()
    if not name:
        raise typer.Exit()

    template = questionary.select(
        "Template:",
        choices=PipelineScaffold().list_templates(),
    ).ask()

    document_store = questionary.select(
        "Document store:",
        choices=FIELD_CHOICES["document_store.backend"] or [],
    ).ask()

    llm_provider = questionary.select(
        "LLM provider:",
        choices=FIELD_CHOICES["llm.provider"] or [],
    ).ask()

    default_dest = str(_DEFAULT_PIPELINES_DIR / f"{name.strip().replace(' ', '-')}.yaml")
    dest_str = questionary.text("Save to:", default=default_dest).ask()
    if not dest_str:
        raise typer.Exit()

    dest = Path(dest_str)
    dest.parent.mkdir(parents=True, exist_ok=True)

    scaffold = PipelineScaffold()
    context = scaffold.build_context(
        document_store=document_store,
        llm_provider=llm_provider,
    )

    content = scaffold._interpolate(scaffold.read_template(template), context)
    dest.write_text(content, encoding="utf-8")

    console.print(f"\n  [success]✓[/success] Created [key]{dest}[/key]")
    console.print(f"  [muted]Run: haystack pipeline validate {dest}[/muted]\n")


@app.command()
def validate(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
) -> None:
    """Validate a pipeline YAML — checks structure and component types"""

    result = PipelineValidator().validate(file)

    print_validation_result(result.to_dict())
    if not result.valid:
        raise typer.Exit(code=1)


@app.command()
def inspect(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Show components, connections, and input/output sockets of a pipeline"""

    data = PipelineInspector().inspect(file)

    if as_json:
        typer.echo(json.dumps(data, indent=2))
        return

    print_inspect_result(data)


@app.command()
def show(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: ascii | mermaid.")
    ] = "ascii",
    as_json: Annotated[
        bool, typer.Option("--json", help="Output graph as JSON adjacency list.")
    ] = False,
) -> None:
    """Visualize a pipeline as ASCII (default), Mermaid text, or JSON adjacency"""

    viz = PipelineVisualizer()

    if as_json:
        data = PipelineInspector().inspect(file)
        typer.echo(
            json.dumps(
                {"components": data["components"], "connections": data["connections"]},
                indent=2,
            )
        )
        return

    if format == "mermaid":
        typer.echo(viz.mermaid(file))
        return

    console.print(viz.ascii(file))


@app.command()
def save(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
) -> None:
    """Save a PNG diagram of the pipeline to assets/pipelines/<name>.png"""
    try:
        load(file)
    except PipelineLoadError as e:
        abort(str(e), hint="Fix the pipeline YAML before saving a diagram.")

    console.print("  [muted]Rendering pipeline diagram via mermaid.ink...[/muted]")
    try:
        output_path = PipelineVisualizer().save(file, _PIPELINES_ASSESTS_DIR)
        console.print(f"  [success]\u2713[/success] Saved to [key]{output_path}[/key]")
    except Exception as e:
        abort(
            str(e),
            hint=(
                "mermaid.ink requires an internet connection. "
                "For offline use: haystack pipeline show --format mermaid"
            ),
        )
    except Exception as e:
        abort(str(e))


@app.command()
def benchmark(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
    input: Annotated[
        str | None,
        typer.Option("--input", "-i", help="Pipeline inputs as JSON string."),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file", help="Path to JSON file with inputs."),
    ] = None,
    runs: Annotated[int, typer.Option("--runs", "-n", help="Number of benchmark runs.")] = 10,
    warmup: Annotated[int, typer.Option("--warmup", help="Warmup runs excluded from stats.")] = 1,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Run a benchmark on the pipeline and print results"""

    try:
        pipeline = load(file)
    except PipelineLoadError as e:
        abort(str(e))

    inputs: dict = {}
    if input_file:
        try:
            inputs = json.loads(input_file.read_text(encoding="utf-8"))
        except Exception as e:
            abort(f"Failed to read input file: {e}")
    elif input:
        try:
            inputs = json.loads(input)
        except json.JSONDecodeError as e:
            abort(f"Invalid JSON in --input: {e}")
    else:
        inputs = _prompt_for_inputs(file)

    if runs < 1:
        abort("--runs must be at least 1.")

    result = PipelineBenchmark().run(
        pipeline=pipeline,
        inputs=inputs,
        pipeline_file=str(file),
        runs=runs,
        warmup=warmup,
    )
    results = result.to_dict()

    if as_json:
        typer.echo(json.dumps(results, indent=2))
        return

    print_benchmark_result(results)


@app.command()
def diff(
    file_a: Annotated[Path, typer.Argument(help="First pipeline YAML.")],
    file_b: Annotated[Path, typer.Argument(help="Second pipeline YAML.")],
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Semantically diff two pipeline YAML files"""

    data = PipelineDiff().diff(file_a, file_b)

    if as_json:
        typer.echo(json.dumps(data, indent=2))
        return

    print_diff_result(data)


@app.command()
def run(
    file: Annotated[Path, typer.Argument(help="Path to pipeline YAML.")],
    input: Annotated[
        str | None,
        typer.Option("--input", "-i", help="Pipeline inputs as JSON string."),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file", help="Path to JSON file with inputs."),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Validate and load only — do not execute.")
    ] = False,
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Execute a pipeline. Pass inputs via --input JSON or --input-file"""

    if dry_run:
        result = PipelineValidator().validate(file)
        msg = {"dry_run": True, "valid": result.valid, "errors": result.errors}
        if as_json:
            typer.echo(json.dumps(msg, indent=2))
        else:
            if result.valid:
                console.print(
                    "  [success]✓[/success] Dry run complete — pipeline loaded successfully."
                )
            else:
                console.print("  [error]✗[/error] Dry run failed.")
                for e in result.errors:
                    console.print(f"  [error]  • {e}[/error]")
        return

    inputs: dict = {}
    if input_file:
        try:
            inputs = json.loads(input_file.read_text(encoding="utf-8"))
        except Exception as e:
            abort(f"Failed to read input file: {e}")
    elif input:
        try:
            inputs = json.loads(input)
        except json.JSONDecodeError as e:
            abort(f"Invalid JSON in --input: {e}")
    else:
        inputs = _prompt_for_inputs(file)

    try:
        result_data = PipelineRunner().run(file, inputs)
    except Exception as e:
        abort(str(e))

    if as_json:
        typer.echo(json.dumps(result_data, indent=2, default=str))
        return

    print_run_result(result_data)


def _prompt_for_inputs(file: Path) -> dict:
    """Interactively prompt for mandatory pipeline inputs"""

    data = PipelineInspector().inspect(file)
    inputs_map = data.get("inputs", {})

    if not inputs_map:
        return {}

    console.print("\n  [info]Pipeline inputs required:[/info]\n")
    inputs: dict = {}

    for input_name, targets in inputs_map.items():
        value = questionary.text(f"  {input_name}:").ask()
        if not value:
            continue

        target_list = targets if isinstance(targets, list) else [targets]
        for target in target_list:
            if "." in str(target):
                component, socket = str(target).split(".", 1)
                inputs.setdefault(component, {})[socket] = value

    return inputs
