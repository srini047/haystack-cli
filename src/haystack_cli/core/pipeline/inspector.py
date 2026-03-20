from pathlib import Path

from haystack_cli.adapters.pipeline import load_as_dict


class PipelineInspector:

    def inspect(self, path: Path) -> dict:
        """
        Return a structured summary of a pipeline's components,
        connections, and input/output sockets — from YAML dict only,
        no component instantiation required.
        """
        data = load_as_dict(path)

        components = [
            {
                "name": name,
                "type": defn.get("type", "").split(".")[-1],
                "full_type": defn.get("type", ""),
            }
            for name, defn in data.get("components", {}).items()
        ]

        connections = [
            {
                "from": c.get("sender", ""),
                "to": c.get("receiver", ""),
            }
            for c in data.get("connections", [])
        ]

        # Pipeline-level inputs/outputs from YAML (if declared)
        inputs = data.get("inputs", {})
        outputs = data.get("outputs", {})

        return {
            "components": components,
            "connections": connections,
            "inputs": inputs,
            "outputs": outputs,
        }
