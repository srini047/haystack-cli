from collections import defaultdict

from haystack_cli.adapters.component import get_registry, _category


class ComponentRegistry:

    def list_all(self) -> dict[str, list[dict]]:
        """Return all components grouped by category."""
        registry = get_registry()
        grouped: dict[str, list[dict]] = defaultdict(list)

        seen_names: set[str] = set()
        for fqn, cls in registry.items():
            if cls.__name__ in seen_names:
                continue
            seen_names.add(cls.__name__)
            grouped[_category(cls)].append({
                "name": cls.__name__,
                "full_type": fqn,
            })

        return dict(sorted(grouped.items()))

    def list_by_category(self, category: str) -> list[dict]:
        """Return components filtered to a specific category."""
        all_grouped = self.list_all()
        return all_grouped.get(category, [])

    def search(self, keyword: str) -> list[dict]:
        """Return components whose name or category contains the keyword."""
        keyword_lower = keyword.lower()
        results = []
        seen: set[str] = set()
        for category, components in self.list_all().items():
            for comp in components:
                if keyword_lower in comp["name"].lower() or keyword_lower in category:
                    if comp["name"] not in seen:
                        seen.add(comp["name"])
                        results.append({**comp, "category": category})
        return results

    def available_categories(self) -> list[str]:
        return list(self.list_all().keys())
