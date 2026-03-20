from importlib import resources
from pathlib import Path


class TemplateNotFoundError(FileNotFoundError):
    pass


class ProjectExistsError(FileExistsError):
    pass


_STORE_TYPE_MAP: dict[str, str] = {
    "inmemory": "haystack.document_stores.in_memory.document_store.InMemoryDocumentStore",
    "elasticsearch": "haystack_integrations.document_stores.elasticsearch.document_store.ElasticsearchDocumentStore",
    "opensearch": "haystack_integrations.document_stores.opensearch.document_store.OpenSearchDocumentStore",
    "weaviate": "haystack_integrations.document_stores.weaviate.document_store.WeaviateDocumentStore",
    "qdrant": "haystack_integrations.document_stores.qdrant.document_store.QdrantDocumentStore",
    "pgvector": "haystack_integrations.document_stores.pgvector.document_store.PgvectorDocumentStore",
}

_RETRIEVER_TYPE_MAP: dict[str, str] = {
    "inmemory": "haystack.components.retrievers.in_memory.bm25_retriever.InMemoryBM25Retriever",
    "elasticsearch": "haystack_integrations.components.retrievers.elasticsearch.bm25_retriever.ElasticsearchBM25Retriever",
    "opensearch": "haystack_integrations.components.retrievers.opensearch.bm25_retriever.OpenSearchBM25Retriever",
    "weaviate": "haystack_integrations.components.retrievers.weaviate.embedding_retriever.WeaviateEmbeddingRetriever",
    "qdrant": "haystack_integrations.components.retrievers.qdrant.retriever.QdrantEmbeddingRetriever",
    "pgvector": "haystack_integrations.components.retrievers.pgvector.pgvector_embedding_retriever.PgvectorEmbeddingRetriever",
}

_GENERATOR_TYPE_MAP: dict[str, str] = {
    "openai": "haystack.components.generators.openai.OpenAIGenerator",
    "anthropic": "haystack_integrations.components.generators.anthropic.generator.AnthropicGenerator",
    "cohere": "haystack_integrations.components.generators.cohere.generator.CohereGenerator",
    "ollama": "haystack_integrations.components.generators.ollama.generator.OllamaGenerator",
    "huggingface": "haystack.components.generators.hugging_face_api.HuggingFaceAPIGenerator",
}

_EMBEDDER_TYPE_MAP: dict[str, str] = {
    "openai": "haystack.components.embedders.openai_document_embedder.OpenAIDocumentEmbedder",
    "anthropic": "haystack.components.embedders.openai_document_embedder.OpenAIDocumentEmbedder",
    "cohere": "haystack_integrations.components.embedders.cohere.document_embedder.CohereDocumentEmbedder",
    "ollama": "haystack_integrations.components.embedders.ollama.document_embedder.OllamaDocumentEmbedder",
    "huggingface": "haystack.components.embedders.hugging_face_api_document_embedder.HuggingFaceAPIDocumentEmbedder",
}

_ENV_VAR_MAP: dict[str, str] = {
    "openai": "OPENAI_API_KEY=sk-...",
    "anthropic": "ANTHROPIC_API_KEY=sk-ant-...",
    "cohere": "COHERE_API_KEY=...",
    "ollama": "# No API key required for Ollama",
    "huggingface": "HUGGINGFACE_API_KEY=hf_...",
}


class PipelineScaffold:
    """Locates packaged templates and writes them into a project directory."""

    _TEMPLATES_PACKAGE = "haystack_cli.templates"

    def list_templates(self) -> list[str]:
        pkg = resources.files(self._TEMPLATES_PACKAGE)
        return sorted(
            item.name.removesuffix(".yaml")
            for item in pkg.iterdir()
            if item.name.endswith(".yaml")
        )

    def read_template(self, name: str) -> str:
        try:
            ref = resources.files(self._TEMPLATES_PACKAGE).joinpath(f"{name}.yaml")
            return ref.read_text(encoding="utf-8")
        except (FileNotFoundError, TypeError):
            raise TemplateNotFoundError(f"Template '{name}' not found.")

    def build_context(self, document_store: str, llm_provider: str) -> dict[str, str]:
        return {
            "document_store": document_store,
            "llm_provider": llm_provider,
            "document_store_type": _STORE_TYPE_MAP[document_store],
            "retriever_type": _RETRIEVER_TYPE_MAP[document_store],
            "generator_type": _GENERATOR_TYPE_MAP[llm_provider],
            "embedder_type": _EMBEDDER_TYPE_MAP[llm_provider],
        }

    def write_project(
        self,
        project_dir: Path,
        context: dict[str, str],
    ) -> list[Path]:
        if project_dir.exists():
            raise ProjectExistsError(f"Directory already exists: {project_dir}")

        retrieval_yaml = self._interpolate(self.read_template("retrieval"), context)
        indexing_yaml = self._interpolate(self.read_template("indexing"), context)

        files: dict[Path, str] = {
            project_dir / "retrieval.yaml": retrieval_yaml,
            project_dir / "indexing.yaml": indexing_yaml,
            project_dir / ".env.example": self._build_env_example(context),
            project_dir
            / ".haystack"
            / "config.toml": self._build_project_toml(context),
            project_dir / "README.md": self._build_readme(project_dir.name),
        }

        created: list[Path] = []
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(path)

        return created

    def _interpolate(self, template: str, context: dict[str, str]) -> str:
        for key, value in context.items():
            template = template.replace(f"{{{{ {key} }}}}", value)
        return template

    def _build_env_example(self, context: dict[str, str]) -> str:
        provider = context.get("llm_provider", "openai")
        return f"# Copy to .env and fill in your credentials\n{_ENV_VAR_MAP.get(provider, '')}\n"

    def _build_project_toml(self, context: dict[str, str]) -> str:
        return (
            "[document_store]\n"
            f'backend = "{context.get("document_store", "inmemory")}"\n\n'
            "[llm]\n"
            f'provider = "{context.get("llm_provider", "openai")}"\n'
        )

    def _build_readme(self, project_name: str) -> str:
        return (
            f"# {project_name}\n\n"
            "Generated by haystack-cli.\n\n"
            "## Quickstart\n\n"
            "```bash\n"
            "cp .env.example .env  # add your credentials\n"
            "haystack pipeline validate indexing.yaml\n"
            "haystack pipeline run indexing.yaml\n"
            "```\n"
        )
