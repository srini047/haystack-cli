from haystack_cli.adapters.component import get_component_class, get_component_info


class ComponentNotFoundError(ValueError):
    pass


class ComponentInspector:

    def info(self, name: str) -> dict:
        cls = get_component_class(name)
        if cls is None:
            raise ComponentNotFoundError(
                f"Component '{name}' not found.\n\n"
                "  Run: haystack component list  to browse available components."
            )
        return get_component_info(cls)
