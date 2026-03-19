from pathlib import Path
from typing import Any

import tomlkit

from haystack_cli.config.schema import (
    HaystackConfig,
    DocumentStoreConfig,
    LLMConfig,
    OutputConfig,
    PipelineConfig,
)

GLOBAL_CONFIG_PATH = Path.home() / ".haystack" / "config.toml"
PROJECT_CONFIG_PATH = Path(".haystack") / "config.toml"

# Maps HAYSTACK_* env var names to dotted config keys.
HAYSTACK_ENV_VAR_MAP: dict[str, str] = {
    "HAYSTACK_OUTPUT_FORMAT": "output.format",
    "HAYSTACK_LOG_LEVEL": "output.log_level",
    "HAYSTACK_STORE_BACKEND": "document_store.backend",
    "HAYSTACK_STORE_HOST": "document_store.host",
    "HAYSTACK_STORE_PORT": "document_store.port",
    "HAYSTACK_STORE_INDEX": "document_store.index",
    "HAYSTACK_LLM_PROVIDER": "llm.provider",
    "HAYSTACK_LLM_MODEL": "llm.model",
    "HAYSTACK_TEMPLATES_DIR": "pipeline.templates_dir",
}


class ConfigSource:
    """Tracks where each resolved value originated."""

    DEFAULT = "default"
    GLOBAL = "global config"
    PROJECT = "config.toml"
    ENV = "environment variable"


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return dict(tomlkit.parse(path.read_text()))


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    import os

    for env_key, dotted_key in HAYSTACK_ENV_VAR_MAP.items():
        value = os.environ.get(env_key)
        if value is None:
            continue
        section, field = dotted_key.split(".", 1)
        data.setdefault(section, {})[field] = value

    return data


def load() -> HaystackConfig:
    """Merge global → project → env vars into a validated HaystackConfig."""
    global_data = _read_toml(GLOBAL_CONFIG_PATH)
    project_data = _read_toml(PROJECT_CONFIG_PATH)
    merged = _deep_merge(global_data, project_data)
    merged = _apply_env_overrides(merged)

    return HaystackConfig(
        output=OutputConfig(**merged.get("output", {})),
        document_store=DocumentStoreConfig(**merged.get("document_store", {})),
        llm=LLMConfig(**merged.get("llm", {})),
        pipeline=PipelineConfig(**merged.get("pipeline", {})),
    )


def load_with_sources() -> dict[str, tuple[Any, str]]:
    """
    Returns every config key with its resolved value and the source it came from.
    Used exclusively by `haystack config show`.
    """
    import os

    global_data = _read_toml(GLOBAL_CONFIG_PATH)
    project_data = _read_toml(PROJECT_CONFIG_PATH)

    resolved: dict[str, tuple[Any, str]] = {}

    config = HaystackConfig()  # defaults
    for section_name, section in {
        "output": config.output,
        "document_store": config.document_store,
        "llm": config.llm,
        "pipeline": config.pipeline,
    }.items():
        for field, value in vars(section).items():
            resolved[f"{section_name}.{field}"] = (value, ConfigSource.DEFAULT)

    # global config overrides
    for section, fields in global_data.items():
        if isinstance(fields, dict):
            for field, value in fields.items():
                resolved[f"{section}.{field}"] = (value, ConfigSource.GLOBAL)

    # project config overrides
    for section, fields in project_data.items():
        if isinstance(fields, dict):
            for field, value in fields.items():
                resolved[f"{section}.{field}"] = (value, ConfigSource.PROJECT)

    # env var overrides
    for env_key, dotted_key in HAYSTACK_ENV_VAR_MAP.items():
        value = os.environ.get(env_key)
        if value is not None:
            resolved[dotted_key] = (value, f"${env_key}")

    return resolved
