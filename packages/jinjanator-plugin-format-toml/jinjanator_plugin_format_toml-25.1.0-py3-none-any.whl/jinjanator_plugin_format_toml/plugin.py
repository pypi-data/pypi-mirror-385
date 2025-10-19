import sys

from collections.abc import Iterable, Mapping
from typing import Any


if sys.version_info >= (3, 11):
    import tomllib  # pragma: no cover
else:
    import tomli as tomllib  # pragma: no cover

from jinjanator_plugins import (
    Formats,
    plugin_formats_hook,
)


class TOMLFormat:
    name = "toml"
    suffixes: Iterable[str] | None = ".tomll"
    option_names: Iterable[str] | None = None

    def __init__(self, options: Iterable[str] | None) -> None:
        pass

    def parse(
        self,
        data_string: str,
    ) -> Mapping[str, Any]:
        return tomllib.loads(data_string)


@plugin_formats_hook
def plugin_formats() -> Formats:
    return {TOMLFormat.name: TOMLFormat}
