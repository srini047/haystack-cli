from pathlib import Path

from rich.text import Text

from haystack_cli.adapters.pipeline import (
    PipelineLoadError,
    load,
    save_image,
    to_mermaid,
)
from haystack_cli.core.pipeline.inspector import PipelineInspector


class PipelineVisualizer:
    """
    Visualize Haystack Pipelines as Mermaid diagrams, ASCII diagram, or PNG
    """

    def mermaid(self, path: Path) -> str:
        """
        Return Mermaid diagram text

        Uses Haystack's native _to_mermaid_text if pipeline can be instantiated,
        falls back to a simple text representation from dict if not.
        """
        try:
            pipeline = load(path)
            return to_mermaid(pipeline)
        except PipelineLoadError:
            return self._mermaid_from_dict(path)

    def ascii(self, path: Path) -> Text:
        """Render pipeline as ASCII graph using Rich Text — no instantiation needed."""
        data = PipelineInspector().inspect(path)
        lines = Text()

        nodes = {c["name"]: c["type"] for c in data["components"]}

        # Build adjacency from connections
        adjacency: dict[str, list[str]] = {name: [] for name in nodes}
        for conn in data["connections"]:
            sender_component = conn["from"].split(".")[0]
            if sender_component in adjacency:
                adjacency[sender_component].append(conn["to"])

        for name, type_name in nodes.items():
            width = max(len(name), len(type_name)) + 4
            border = "─" * width
            lines.append(f"┌{border}┐\n", style="bold cyan")
            lines.append(f"│ {name.center(width - 2)} │\n", style="bold white")
            lines.append(f"│ {type_name.center(width - 2)} │\n", style="dim white")
            lines.append(f"└{border}┘\n", style="bold cyan")

            for target in adjacency[name]:
                lines.append(f"       │ → {target}\n", style="dim yellow")
                lines.append("       ▼\n", style="yellow")

        return lines

    def save(self, path: Path, output_dir: Path) -> Path:
        """Save a PNG diagram using Haystack's native draw(). Returns the saved path."""
        pipeline = load(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{path.stem}.png"
        save_image(pipeline, output_path)
        return output_path

    def _mermaid_from_dict(self, path: Path) -> str:
        """Minimal Mermaid output derived from YAML dict when instantiation fails."""
        data = PipelineInspector().inspect(path)
        lines = ["%%{ init: {} }%%", "", "graph TD;", ""]
        for conn in data["connections"]:
            sender = conn["from"].replace(".", "_")
            receiver = conn["to"].replace(".", "_")
            lines.append(f"{sender} --> {receiver}")
        return "\n".join(lines)
