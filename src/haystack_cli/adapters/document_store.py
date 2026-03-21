from pathlib import Path
from typing import Any

from haystack_cli.config.loader import load as load_config
from haystack_cli.config.schema import DocumentStoreBackend


class DocumentStoreConnectionError(RuntimeError):
    pass


class UnsupportedBackendError(RuntimeError):
    pass


def _build_store(backend: str, host: str, port: int, index: str | None) -> Any:
    """Instantiate the correct document store from config values."""
    if backend == "inmemory":
        from haystack.document_stores.in_memory import InMemoryDocumentStore

        store_path = Path(".haystack") / "document_store.db"
        if store_path.exists():
            return InMemoryDocumentStore.load_from_disk(str(store_path))
        return InMemoryDocumentStore()

    if backend == "elasticsearch":
        try:
            from haystack_integrations.document_stores.elasticsearch import (
                ElasticsearchDocumentStore,
            )

            return ElasticsearchDocumentStore(
                hosts=f"http://{host}:{port}", index=index or "default"
            )
        except ImportError:
            raise UnsupportedBackendError(
                "Elasticsearch integration not installed.\n\n  pip install elasticsearch-haystack"
            )

    if backend == "opensearch":
        try:
            from haystack_integrations.document_stores.opensearch import (
                OpenSearchDocumentStore,
            )

            return OpenSearchDocumentStore(hosts=f"http://{host}:{port}", index=index or "default")
        except ImportError:
            raise UnsupportedBackendError(
                "OpenSearch integration not installed.\n\n  pip install opensearch-haystack"
            )

    if backend == "weaviate":
        try:
            from haystack_integrations.document_stores.weaviate import (
                WeaviateDocumentStore,
            )

            return WeaviateDocumentStore(url=f"http://{host}:{port}", index=index or "default")
        except ImportError:
            raise UnsupportedBackendError(
                "Weaviate integration not installed.\n\n  pip install weaviate-haystack"
            )

    if backend == "qdrant":
        try:
            from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

            return QdrantDocumentStore(host=host, port=port, index=index or "default")
        except ImportError:
            raise UnsupportedBackendError(
                "Qdrant integration not installed.\n\n  pip install qdrant-haystack"
            )

    if backend == "pgvector":
        try:
            from haystack_integrations.document_stores.pgvector import (
                PgvectorDocumentStore,
            )

            return PgvectorDocumentStore(
                connection_string=f"postgresql://localhost/{index or 'haystack'}"
            )
        except ImportError:
            raise UnsupportedBackendError(
                "PgVector integration not installed.\n\n  pip install pgvector-haystack"
            )

    raise UnsupportedBackendError(f"Unknown backend: '{backend}'")


def get_document_store() -> Any:
    """
    Resolve and return the document store from project config.
    Raises DocumentStoreConnectionError or UnsupportedBackendError.
    """
    cfg = load_config()
    backend = cfg.document_store.backend

    if backend is None:
        raise DocumentStoreConnectionError(
            "No document store configured.\n\n"
            "  Run: haystack config set document_store.backend <backend>"
        )

    try:
        return _build_store(
            backend=backend,
            host=cfg.document_store.host,
            port=cfg.document_store.port,
            index=cfg.document_store.index,
        )
    except UnsupportedBackendError:
        raise
    except Exception as e:
        raise DocumentStoreConnectionError(
            f"Failed to connect to {backend} at {cfg.document_store.host}:{cfg.document_store.port}\n\n"
            f"  {e}\n\n"
            "  Run: haystack connect  to diagnose connection issues."
        )
