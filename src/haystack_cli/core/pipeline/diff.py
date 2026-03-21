from pathlib import Path

from deepdiff import DeepDiff

from haystack_cli.adapters.pipeline import load_as_dict


class PipelineDiff:
    def diff(self, path_a: Path, path_b: Path) -> dict:
        """Return a structured semantic diff between two pipeline YAML files."""
        dict_a = load_as_dict(path_a)
        dict_b = load_as_dict(path_b)

        raw = DeepDiff(dict_a, dict_b, ignore_order=True, verbose_level=2)

        return {
            "added": self._extract(raw, "dictionary_item_added"),
            "removed": self._extract(raw, "dictionary_item_removed"),
            "changed": self._extract_changed(raw),
        }

    def _extract(self, diff: DeepDiff, key: str) -> list[str]:
        return [str(item) for item in diff.get(key, [])]

    def _extract_changed(self, diff: DeepDiff) -> list[dict]:
        changed = []
        for path, change in diff.get("values_changed", {}).items():
            changed.append(
                {
                    "path": str(path),
                    "before": change.get("old_value"),
                    "after": change.get("new_value"),
                }
            )

        for path, change in diff.get("type_changes", {}).items():
            changed.append(
                {
                    "path": str(path),
                    "before": str(change.get("old_value")),
                    "after": str(change.get("new_value")),
                }
            )
        return changed
