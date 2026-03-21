from haystack_cli.adapters.document_store import get_document_store


class DocumentLister:
    def list(
        self,
        limit: int = 5,
        filter_field: str | None = None,
        filter_value: str | None = None,
    ) -> dict:
        store = get_document_store()
        total = store.count_documents()

        filters = None
        if filter_field and filter_value:
            filters = {"field": filter_field, "operator": "==", "value": filter_value}

        documents = store.filter_documents(filters=filters)
        sampled = documents[:limit]

        return {
            "total": total,
            "showing": len(sampled),
            "documents": [
                {
                    "id": d.id,
                    "content_preview": (d.content or "")[:100],
                    "meta": d.meta,
                }
                for d in sampled
            ],
        }
