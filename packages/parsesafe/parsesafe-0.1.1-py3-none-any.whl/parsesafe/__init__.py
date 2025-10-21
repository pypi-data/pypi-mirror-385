"""A type-safe parsing-combinator library."""

from .combinators import (
    Combinator,
    regex,
    string,
)

from .err import (
    iserr
)

__all__ = [
    "Combinator",
    "regex",
    "string",

    "iserr"
]