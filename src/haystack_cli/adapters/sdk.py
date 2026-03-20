from importlib.metadata import PackageNotFoundError, version


class HaystackNotFoundError(RuntimeError):
    pass


def get_haystack_version() -> str:
    """Return the installed haystack-ai version string or raise HaystackNotFoundError."""
    try:
        return version("haystack-ai")
    except PackageNotFoundError:
        raise HaystackNotFoundError(
            "haystack-ai is not installed in the active environment.\n\n"
            "  pip install haystack-ai\n\n"
            "Make sure your project virtualenv is activated before running haystack-cli."
        )
