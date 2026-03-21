from pathlib import Path

import yaml
from haystack import Pipeline
from haystack.core.errors import DeserializationError, PipelineError
from haystack.core.pipeline.draw import _to_mermaid_text


class PipelineLoadError(RuntimeError):
    pass


class PipelineRunError(RuntimeError):
    pass


class PipelineSaveError(RuntimeError):
    pass


def load(path: Path) -> Pipeline:
    """Load and instantiate a Pipeline from a YAML file."""
    try:
        return Pipeline.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PipelineLoadError(f"Pipeline file not found: {path}")
    except DeserializationError as e:
        raise PipelineLoadError(f"Failed to deserialize pipeline: {e}")
    except Exception as e:
        raise PipelineLoadError(f"Failed to load pipeline: {e}")


def load_as_dict(path: Path) -> dict:
    """Parse a pipeline YAML into a raw dict without instantiating components."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise PipelineLoadError(f"Pipeline file not found: {path}")
    except yaml.YAMLError as e:
        raise PipelineLoadError(f"Invalid YAML: {e}")


def to_mermaid(pipeline: Pipeline) -> str:
    """Return the Mermaid diagram text for a pipeline using Haystack's internal renderer."""
    return _to_mermaid_text(pipeline.graph, init_params="{}")


def run(pipeline: Pipeline, inputs: dict) -> dict:
    """Execute a pipeline and return its outputs."""
    try:
        return pipeline.run(inputs)
    except PipelineError as e:
        raise PipelineRunError(f"Pipeline execution failed: {e}")
    except Exception as e:
        raise PipelineRunError(f"Unexpected error during pipeline run: {e}")


def save_image(pipeline: Pipeline, output_path: Path) -> None:
    """Save a PNG diagram of the pipeline using Haystack's native draw() method."""
    try:
        pipeline.draw(path=output_path, params={"type": "png"})
    except Exception as e:
        raise PipelineSaveError(f"Failed to save pipeline image: {e}")
