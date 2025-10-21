"""A type-safe parsing-combinator library."""

from .combinators import (
    Combinator,
    build,
    regex,
    regex_groups,
    string,
    combinator,
)

from .err import (
    iserr
)

__all__ = [
    "Combinator",
    "build",
    "combinator",
    "regex",
    "regex_groups",
    "string",

    "iserr"
]