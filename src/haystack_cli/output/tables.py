import json
from typing import Any

from rich import box
from rich.table import Table
from rich.text import Text

from haystack_cli.output.console import console


def print_config_table(rows: dict[str, tuple[Any, str]]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("Key", style="key", min_width=30)
    table.add_column("Value", min_width=20)
    table.add_column("Source", style="source")

    for key, (value, source) in rows.items():
        display = (
            "****"
            if "api_key" in key
            else str(value) if value is not None else "[muted]—[/muted]"
        )
        table.add_row(key, display, source)

    console.print(table)


def print_schema_table(rows: dict[str, list[str] | None]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("Key", style="key", min_width=30)
    table.add_column("Valid Values")

    for key, choices in rows.items():
        table.add_row(key, " | ".join(choices) if choices else "[muted]any[/muted]")

    console.print(table)


def print_validation_result(result: dict) -> None:
    if result["valid"]:
        console.print("  [success]✓[/success] Pipeline is valid.")
    else:
        console.print("  [error]✗[/error] Pipeline is invalid.\n")

    for error in result["errors"]:
        console.print(f"  [error]  • {error}[/error]")

    for warning in result["warnings"]:
        console.print(f"  [warning]  ⚠ {warning}[/warning]")


def print_inspect_result(data: dict) -> None:
    # Components
    comp_table = Table(box=box.SIMPLE, header_style="bold white", title="Components")
    comp_table.add_column("Name", style="key")
    comp_table.add_column("Type", style="bold white")
    comp_table.add_column("Full Type", style="muted")
    for c in data["components"]:
        comp_table.add_row(c["name"], c["type"], c.get("full_type", ""))
    console.print(comp_table)

    # Connections
    if data["connections"]:
        conn_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Connections"
        )
        conn_table.add_column("From", style="key")
        conn_table.add_column("To", style="key")
        for c in data["connections"]:
            conn_table.add_row(c["from"], c["to"])
        console.print(conn_table)

    # Inputs — YAML format: {socket_name: [component.socket, ...]} or {component: {socket: meta}}
    inputs = data.get("inputs", {})
    if inputs:
        inp_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Pipeline Inputs"
        )
        inp_table.add_column("Input", style="key")
        inp_table.add_column("Receives")
        for name, targets in inputs.items():
            targets_str = (
                ", ".join(targets) if isinstance(targets, list) else str(targets)
            )
            inp_table.add_row(name, targets_str)
        console.print(inp_table)

    # Outputs — YAML format: {output_name: component.socket}
    outputs = data.get("outputs", {})
    if outputs:
        out_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Pipeline Outputs"
        )
        out_table.add_column("Output", style="key")
        out_table.add_column("From")
        for name, source in outputs.items():
            out_table.add_row(name, str(source))
        console.print(out_table)


def print_diff_result(data: dict) -> None:
    if data["added"]:
        console.print("\n  [success]Added[/success]")
        for item in data["added"]:
            console.print(f"  [success]  + {item}[/success]")

    if data["removed"]:
        console.print("\n  [error]Removed[/error]")
        for item in data["removed"]:
            console.print(f"  [error]  - {item}[/error]")

    if data["changed"]:
        console.print("\n  [warning]Changed[/warning]")
        for item in data["changed"]:
            console.print(f"  [key]  ~ {item['path']}[/key]")
            console.print(f"    before: [error]{item['before']}[/error]")
            console.print(f"    after:  [success]{item['after']}[/success]")

    if not any([data["added"], data["removed"], data["changed"]]):
        console.print("  [success]✓[/success] Pipelines are identical.")


def print_run_result(data: dict) -> None:
    console.print("\n  [success]✓[/success] Pipeline completed.\n")
    for component, outputs in data.items():
        console.print(f"  [key]{component}[/key]")
        if isinstance(outputs, dict):
            for key, value in outputs.items():
                console.print(f"    [muted]{key}:[/muted] {value}")
        else:
            console.print(f"    {outputs}")


def print_component_list(grouped: dict[str, list[dict]]) -> None:
    for category, components in grouped.items():
        table = Table(box=box.SIMPLE, header_style="bold white", title=f"{category}")
        table.add_column("Component", style="key", min_width=35)
        table.add_column("Full Type", style="muted")
        for c in sorted(components, key=lambda x: x["name"]):
            table.add_row(c["name"], c["full_type"])
        console.print(table)


def print_component_info(data: dict) -> None:
    console.print(f"\n  [key]{data['name']}[/key]  [muted]{data['full_type']}[/muted]")
    console.print(f"  [muted]{data['doc']}[/muted]\n")

    if data["params"]:
        p_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Init Parameters"
        )
        p_table.add_column("Name", style="key")
        p_table.add_column("Type", style="muted")
        p_table.add_column("Required")
        p_table.add_column("Default", style="muted")
        for p in data["params"]:
            required = "[success]✓[/success]" if p["required"] else "[muted]—[/muted]"
            p_table.add_row(p["name"], p["type"], required, p["default"] or "")
        console.print(p_table)

    if data["inputs"]:
        i_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Input Sockets"
        )
        i_table.add_column("Name", style="key")
        i_table.add_column("Type", style="muted")
        for name, type_str in data["inputs"].items():
            i_table.add_row(name, type_str)
        console.print(i_table)

    if data["outputs"]:
        o_table = Table(
            box=box.SIMPLE, header_style="bold white", title="Output Sockets"
        )
        o_table.add_column("Name", style="key")
        o_table.add_column("Type", style="muted")
        for name, type_str in data["outputs"].items():
            o_table.add_row(name, type_str)
        console.print(o_table)
