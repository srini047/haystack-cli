from rich.console import Console
from haystack_cli.output.themes import HAYSTACK_THEME

console = Console(theme=HAYSTACK_THEME)
err_console = Console(stderr=True, theme=HAYSTACK_THEME)
