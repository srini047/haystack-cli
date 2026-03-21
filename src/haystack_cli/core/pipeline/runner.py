from pathlib import Path

from haystack_cli.adapters.pipeline import PipelineRunError, load, run


class PipelineRunner:
    def run(self, path: Path, inputs: dict) -> dict:
        """Load and execute a pipeline, returning its outputs."""
        pipeline = load(path)
        try:
            return run(pipeline, inputs)
        except PipelineRunError as e:
            raise PipelineRunError(f"Failed to run pipeline: {e}")
