import importlib
import inspect
import pkgutil
from typing import Any

import haystack.components
from haystack.core.component import component as component_registry


def _import_all_components() -> None:
    """Walk haystack.components and import every submodule to populate the registry."""
    for _, modname, _ in pkgutil.walk_packages(
        path=haystack.components.__path__,
        prefix=haystack.components.__name__ + ".",
        onerror=lambda _: None,
    ):
        try:
            importlib.import_module(modname)
        except Exception:
            pass


def get_registry() -> dict[str, type]:
    """Return fully populated {fqn: class} registry of all Haystack components."""
    _import_all_components()
    return dict(component_registry.registry)


def get_component_class(name: str) -> type | None:
    """Look up a component class by short name or fully qualified name."""
    registry = get_registry()

    if name in registry:
        return registry[name]

    for cls in registry.values():
        if cls.__name__ == name:
            return cls
    return None


def get_component_info(cls: type) -> dict[str, Any]:
    """Extract init params, input sockets, and output sockets from a component class."""
    sig = inspect.signature(cls.__init__)
    params = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        annotation = param.annotation
        type_str = (
            annotation.__name__
            if hasattr(annotation, "__name__")
            else str(annotation)
            if annotation != inspect.Parameter.empty
            else "Any"
        )
        params.append(
            {
                "name": param_name,
                "type": type_str,
                "required": param.default is inspect.Parameter.empty,
                "default": (None if param.default is inspect.Parameter.empty else repr(param.default)),
            }
        )

    inputs: dict[str, str] = {}
    outputs: dict[str, str] = {}
    required_params = [p for p in params if p["required"]]
    if not required_params:
        try:
            instance = cls()
            if hasattr(instance, "__haystack_input__"):
                inputs = {k: str(v.type) for k, v in instance.__haystack_input__._sockets_dict.items()}
            if hasattr(instance, "__haystack_output__"):
                outputs = {k: str(v.type) for k, v in instance.__haystack_output__._sockets_dict.items()}
        except Exception:
            pass
    else:
        # Fall back to run() signature for inputs
        if hasattr(cls, "run"):
            run_sig = inspect.signature(cls.run)  # ty:ignore[invalid-argument-type]
            inputs = {
                n: (p.annotation.__name__ if hasattr(p.annotation, "__name__") else str(p.annotation))
                for n, p in run_sig.parameters.items()
                if n != "self" and p.annotation != inspect.Parameter.empty
            }

    return {
        "name": cls.__name__,
        "full_type": f"{cls.__module__}.{cls.__name__}",
        "category": _category(cls),
        "doc": (inspect.getdoc(cls) or "").split("\n")[0],
        "params": params,
        "inputs": inputs,
        "outputs": outputs,
    }


def _category(cls: type) -> str:
    parts = cls.__module__.split(".")
    if len(parts) >= 3 and parts[0] == "haystack" and parts[1] == "components":
        return parts[2]
    return "other"
