from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

DocumentStoreBackend = Literal[
    "inmemory", "elasticsearch", "opensearch", "weaviate", "qdrant", "pgvector"
]

LLMProvider = Literal["openai", "anthropic", "cohere", "ollama", "huggingface"]

OutputFormat = Literal["rich", "json", "plain"]

LogLevel = Literal["debug", "info", "warning", "error"]


@dataclass
class OutputConfig:
    format: OutputFormat = "rich"
    log_level: LogLevel = "error"


@dataclass
class DocumentStoreConfig:
    backend: DocumentStoreBackend | None = None
    host: str = "localhost"
    port: int = Field(default=8080, gt=0, lt=65536)
    index: str | None = None


@dataclass
class LLMConfig:
    provider: LLMProvider | None = None
    model: str | None = None


@dataclass
class PipelineConfig:
    templates_dir: str = "pipelines/"


@dataclass
class HaystackConfig:
    output: OutputConfig = Field(default_factory=OutputConfig)
    document_store: DocumentStoreConfig = Field(default_factory=DocumentStoreConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)


# Derived from Literal types above — single source of truth for valid choices.
FIELD_CHOICES: dict[str, list[str] | None] = {
    "output.format": list(OutputFormat.__args__),  # type: ignore[attr-defined]
    "output.log_level": list(LogLevel.__args__),  # type: ignore[attr-defined]
    "document_store.backend": list(DocumentStoreBackend.__args__),  # type: ignore[attr-defined]
    "document_store.host": None,
    "document_store.port": None,
    "document_store.index": None,
    "llm.provider": list(LLMProvider.__args__),  # type: ignore[attr-defined]
    "llm.model": None,
}
