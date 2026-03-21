from pathlib import Path

from haystack_cli.adapters.pipeline import PipelineLoadError, load, load_as_dict


class PipelineResultValidation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


_WARNING_HINTS = (
    "environment variables are not set",
    "api_key",
    "API_KEY",
    "authentication",
    "credential",
    "not imported",
    "Please check that the package is installed",
    "failed to import the optional dependency",
    "Run 'pip install",
)


class PipelineValidator:
    """
    Validates the structure of a pipeline YAML file and checks for any issues
    """

    def validate(self, path: Path) -> PipelineResultValidation:
        result = PipelineResultValidation()

        try:
            data = load_as_dict(path)
        except PipelineLoadError as e:
            result.errors.append(str(e))
            return result

        self._check_structure(data, result)
        if not result.valid:
            return result

        try:
            load(path)
        except PipelineLoadError as e:
            error_str = str(e)
            if any(hint in error_str for hint in _WARNING_HINTS):
                result.warnings.append(
                    f"Component requires credentials not set in environment: {error_str}\n"
                    "  Pipeline structure is valid — set the required env vars before running."
                )
            else:
                result.errors.append(error_str)

        return result

    def _check_structure(self, data: dict, result: PipelineResultValidation) -> None:
        if not isinstance(data, dict):
            result.errors.append("Pipeline YAML must be a mapping at the top level.")
            return

        if "components" not in data:
            result.errors.append("Missing required key: 'components'")

        if "connections" not in data:
            result.warnings.append(
                "No 'connections' defined — pipeline has a single component or is incomplete."
            )

        components = data.get("components", {})
        if not isinstance(components, dict):
            result.errors.append("'components' must be a mapping.")
            return

        for name, definition in components.items():
            if not isinstance(definition, dict):
                result.errors.append(f"Component '{name}' must be a mapping.")
                continue
            if "type" not in definition:
                result.errors.append(f"Component '{name}' is missing required key: 'type'")
