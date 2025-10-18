import typing as t

_T = t.TypeVar("_T")
_E = t.TypeVar("_E", bound="Err")

Result: t.TypeAlias = t.Union[_T, _E]

def iserr(res: t.Any) -> t.TypeIs[Err]:
    if isinstance(res, Err):
        return True
    return False

@t.overload
def has_no_err(seq: tuple[Result[_T, _E]] | tuple[_T]) -> t.TypeGuard[tuple[_T]]: ...
@t.overload
def has_no_err(seq: tuple[Result[_T, _E], Result[_T, _E]] | tuple[_T, _T]) -> t.TypeGuard[tuple[_T, _T]]: ...
@t.overload
def has_no_err(seq: tuple[Result[_T, _E], Result[_T, _E], Result[_T, _E]] | tuple[_T, _T, _T]) -> t.TypeGuard[tuple[_T, _T, _T]]: ...
@t.overload
def has_no_err(seq: list[Result[_T, _E]] | list[_T]) -> t.TypeGuard[list[_T]]: ...
@t.overload
def has_no_err(seq: t.Sequence[Result[_T, _E]] | t.Sequence[_T]) -> t.TypeGuard[t.Sequence[_T]]: ...
@t.overload
def has_no_err(seq: t.Iterable[Result[_T, _E]] | t.Iterable[_T]) -> t.TypeGuard[t.Iterable[_T]]: ...
def has_no_err(seq: t.Iterable[Result[_T, _E]] | t.Iterable[_T]) -> t.TypeGuard[t.Iterable[_T]]:
    return not any(map(iserr, seq))


def expect(res: Result[_T, _E], reason: t.Optional[str] = None) -> _T:
    """Casts a Result to the non-:class:`Err` value.
    
    :throws ExpectationError: If the result is an object that inherits form :class:`Err`.
    """
    if iserr(res):
        raise ExpectationError(res, reason)
    return res

class ExpectationError(ValueError):
    def __init__(self, err: Err, reason: t.Optional[str] = None):
        if reason is None:
            super().__init__(f"Expectation violated: found {type(err).__name__}: {err}")
        else:
            super().__init__(f"Expectation violated: {reason}: found {type(err).__name__}: {err}")

class Err: pass