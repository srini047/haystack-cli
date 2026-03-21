from haystack_cli.adapters.document_store import get_document_store


class DocumentSearcher:

    def search(self, query: str, top_k: int = 5) -> dict:
        store = get_document_store()

        # Use BM25 if available
        if hasattr(store, "bm25_retrieval"):
            results = store.bm25_retrieval(query=query, top_k=top_k)
        else:
            # For other backends fall back to semantic search if available
            if hasattr(store, "embedding_retrieval"):
                results = store.embedding_retrieval(query_embedding=[], top_k=top_k)
            else:
                results = store.filter_documents()[:top_k]

        return {
            "query": query,
            "top_k": top_k,
            "results": [
                {
                    "id": d.id,
                    "score": d.score,
                    "content_preview": (d.content or "")[:200],
                    "meta": d.meta,
                }
                for d in results
            ],
        }
