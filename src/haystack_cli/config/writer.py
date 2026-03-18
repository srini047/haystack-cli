from typing import Any

import tomlkit

from haystack_cli.config.loader import GLOBAL_CONFIG_PATH, PROJECT_CONFIG_PATH
from haystack_cli.config.schema import FIELD_CHOICES


class InvalidConfigKeyError(ValueError):
    pass


class InvalidConfigValueError(ValueError):
    pass


class ConfigWriter:
    """Reads, validates, and writes config values — preserving TOML comments."""

    def __init__(self, global_scope: bool = False) -> None:
        self._path = GLOBAL_CONFIG_PATH if global_scope else PROJECT_CONFIG_PATH

    def _load_document(self) -> tomlkit.TOMLDocument:
        if self._path.exists():
            return tomlkit.parse(self._path.read_text())
        return tomlkit.document()

    def _save_document(self, doc: tomlkit.TOMLDocument) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(tomlkit.dumps(doc))

    def set(self, key: str, value: str) -> None:
        self._validate_key(key)
        self._validate_value(key, value)

        section_name, field = key.split(".", 1)
        coerced = self._coerce(key, value)
        doc = self._load_document()

        if section_name not in doc:
            table = tomlkit.table()
            table.append(field, coerced)
            doc.append(section_name, table)
        else:
            section = doc[section_name]
            if field in section:
                section[field] = coerced  # update existing key in-place
            else:
                section.append(field, coerced)  # tomlkit append for new key in existing section

        self._save_document(doc)

    def _validate_key(self, key: str) -> None:
        if key not in FIELD_CHOICES:
            valid = "\n  ".join(FIELD_CHOICES.keys())
            raise InvalidConfigKeyError(f"Unknown config key: '{key}'\n\nValid keys:\n  {valid}")

    def _validate_value(self, key: str, value: str) -> None:
        choices = FIELD_CHOICES.get(key)
        if choices and value not in choices:
            raise InvalidConfigValueError(
                f"Invalid value for '{key}': '{value}'\n\nValid choices: {' | '.join(choices)}"
            )

    def _coerce(self, key: str, value: str) -> Any:
        if key == "document_store.port":
            return int(value)
        return value
