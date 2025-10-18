import bisect
from dataclasses import dataclass
import re
import typing as t
import math

from .err import Err, iserr
from .advancer import Advancer

    
@dataclass(frozen=True)
class Position:
    line: int
    char: int


@dataclass(frozen=True)
class Token[T]:
    obj: T
    span: Span


@dataclass(frozen=True)
class ErrLocation(Err):
    index: int


@dataclass(frozen=True)
class Span():
    start: int
    end: int


class Addative(t.Protocol):
    def __add__(self, other: t.Self, /) -> t.Self: ...

_In = t.TypeVar("_In")
_Addative = t.TypeVar("_Addative", bound=Addative)
type CombinatorResult[In, Out] =  tuple[Advancer[In], Out] | ErrLocation
type CombinatorFunction[In, Out] = t.Callable[[Advancer[In]], CombinatorResult[In, Out]]

class IndexToPositionConverter:
    def __init__(self, text: str):
        self._line_starts = [0]
        for i, char in enumerate(text):
            if char == "\n":
                self._line_starts.append(i + 1)
            elif char == "\r" and not (i + 1 < len(text) and text[i + 1] == "\n"):
                self._line_starts.append(i + 1)
    def get(self, index: int) -> Position:
        if index < 0:
            raise ValueError("Index cannot be negative.")
        line_index = bisect.bisect_right(self._line_starts, index) - 1
        line_start_index = self._line_starts[line_index]
        char_offset = index - line_start_index
        return Position(line=line_index + 1, char=char_offset)




@dataclass(frozen=True)
class Combinator[In, Out]():

    function: CombinatorFunction[In, Out]
    name: str
    _is_construct: bool = False
    

    def as_token(self) -> Combinator[In, Token[Out]]:
        @combinator(f"with_token({self.name})")
        def comb(seq: Advancer[In]):
            start = seq.pos
            res = self(seq)
            if iserr(res):
                return ErrLocation(res.index)
            return res[0], Token(res[1], span=Span(start=start, end=res[0].pos))
        return comb
    

    def map[T](self, function: t.Callable[[Out], T]) -> Combinator[In, T]:
        return outmap(self, function)
    
    def postignore(self, post: Combinator[In, t.Any]) -> Combinator[In, Out]:
        return ignore_second(self, post)
    
    def preignore(self, pre: Combinator[In, t.Any]) -> Combinator[In, Out]:
        return ignore_first(pre, self)
    
    def parse(self, seq: t.Sequence[In]) -> Out  | ErrLocation:
        return parse(self, seq)
    

    def otherwise[Out2](self, *other: Combinator[In, Out2]):
        return alt(self, *other)
    
    def seq(self: Combinator[In, _Addative], *others: Combinator[In, _Addative]):
        return seq(self, *others)
    
    def after(self, other: Combinator[In, t.Any]):
        return first(self, other)
    def before[Out2](self, other: Combinator[In, Out2]):
        return second(self, other)
    
    def times(self, min: int = 0, max: t.Optional[int] = None) -> Combinator[In, list[Out]]:
        return times(self, min, max)
    
    def cons[Out2](self, other: Combinator[In, Out2]) -> Combinator[In, tuple[Out, Out2]]:
        return cons(self, other)
    
    def append[*Out1, Out2](self: Combinator[In, tuple[*Out1]], other: Combinator[In, Out2]) -> Combinator[In, tuple[*Out1, Out2]]:
        return append(self, other)
        
    def filter(self, *options: Out) -> Combinator[In, Out]:
        return outfilter(self, *options)
    
    @property
    def lie(self) -> Out:
        """Returns self, i.e. the combinator, but "lies" by claiming to return a value
        of the combinator's output. This is to satisfy type checkers when using
        `build`.
        """
        return t.cast(Out, self)
    
    def __call__(self, seq: Advancer[In]) -> CombinatorResult[In, Out]:
        return self.function(seq)
    def __or__[Out2](self, other: Combinator[In, Out2]):
        return alt(self, other)
    def __lshift__(self, other: Combinator[In, t.Any]):
        return first(self, other)
    def __rshift__[Out2](self, other: Combinator[In, Out2]):
        return second(self, other)
    

    @t.overload
    def __and__[*Out1, Out2](self: Combinator[In, tuple[*Out1]], other: Combinator[In, Out2]) -> Combinator[In, tuple[*Out1, Out2]]: ...
    @t.overload
    def __and__[Out1, Out2](self: Combinator[In, Out1], other: Combinator[In, Out2]) -> Combinator[In, tuple[Out1, Out2]]: ...
    @t.no_type_check
    def __and__[Out1, Out2](self: Combinator[In, Out1], other: Combinator[In, Out2]):
        if self._is_construct:
            return append(self, other)
        return cons(self, other)
    def __add__(self: Combinator[In, _Addative], other: Combinator[In, _Addative]):
        return seq(self, other)
    
class ForwardCombinator[In, Out](Combinator[In, Out]):
    def __init__(self, name: str):
        def error(seq: Advancer[In]) -> CombinatorResult[In, Out]:
            return ErrLocation(seq.pos)
        super().__init__(function=error, name=name)
    def define(self, combinator: Combinator[In, Out]):
        object.__setattr__(self, "function", combinator.function)

def forward[In, Out](type_in: t.Type[In], type_out: t.Type[Out], name: str = "ForwardCombinator") -> ForwardCombinator[In, Out]:
    return ForwardCombinator[In, Out](name)


def sequence_to_advancer[T](seq: t.Sequence[T]) -> Advancer[T]:
    if isinstance(seq, Advancer):
        return seq
    else:
        return Advancer(seq)
    
def parse[In, Out](combinator: Combinator[In, Out], seq: t.Sequence[In]) -> Out  | ErrLocation:
    inp_advancer = sequence_to_advancer(seq)
    if iserr(v := combinator(inp_advancer)):
        return v
    if len(v[0]) > 0:
        return ErrLocation(v[0].pos)
    return v[1]

@t.overload
def combinator[In, Out](name: str, /) -> t.Callable[[CombinatorFunction[In, Out]], Combinator[In, Out]]: ...
@t.overload
def combinator[In, Out](function: CombinatorFunction[In, Out], /) -> Combinator[In, Out]: ...
def combinator[In, Out](name_or_function: CombinatorFunction[In, Out] | str, /) -> Combinator[In, Out] | t.Callable[[CombinatorFunction[In, Out]], Combinator[In, Out]]:
    if isinstance(name_or_function, str):
        def wrapped(function: CombinatorFunction[In, Out]):
            return Combinator[In, Out](function=function, name=name_or_function)
        return wrapped
    return Combinator(function=name_or_function, name=name_or_function.__name__)


def _start_match(t1: Advancer[t.Any], t2: t.Sequence[t.Any], ) -> bool:
    return len(t1) >= len(t2) and all([e1 == e2 for e1, e2 in zip(t1, t2)])

def string(string: str):
    if len(string) == 0:
        raise ValueError("string must be nonempty")
    @combinator(f"'{string}'")
    def c(seq: Advancer[str]):
        if _start_match(seq, string):
            return seq.advance(len(string)), string
        return ErrLocation(seq.pos)
    return c


def regex_groups(pattern: str, include_full: bool = False):
    if len(pattern) == 0:
        raise ValueError("pattern must be nonempty")
    compiled_pattern = re.compile(f"{pattern}")
    @combinator(f"r'{pattern}'")
    def c(seq: Advancer[str]):
        if not isinstance(seq.raw, str):
            raise ValueError(f"Cannot use Regex when the underlying data stream is not of type 'str': found type '{type(seq.raw).__name__}'")
        
        match = compiled_pattern.match(seq.raw, seq.pos)

        if not match:
            return ErrLocation(seq.pos)
        
        end = match.end() - seq.pos
        if include_full:
            groups = (t.cast(str, seq[:(end)]), *match.groups())
        else:
            groups = match.groups() or (match.group(0),)

        return seq.advance(end), groups
    return c

def regex(pattern: str) -> Combinator[str, str]:
    return regex_groups(pattern, include_full=True).map(lambda x: x[0])

def seq(first_combinator: Combinator[_In, _Addative], *combinators: Combinator[_In, _Addative]):
    @combinator(f"({" + ".join([c.name for c in combinators])})")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Addative]:
        res = first_combinator(seq)
        if iserr(res):
            return ErrLocation(seq.pos)
        joined_obj = res[1]
        for combinator in combinators:
            res = combinator(res[0])
            if iserr(res):
                return res
            joined_obj += res[1]
        return res[0], joined_obj
    return comb

def times[In, Out](com: Combinator[In, Out], min: int = 0, max: t.Optional[int] = None) -> Combinator[In, list[Out]]:
    maximum = max or math.inf
    @combinator(f"{min} to {maximum} of {com.name}")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, list[Out]]:
        outputs: list[Out] = []
        while len(outputs) < maximum and not iserr(res := com(seq)):
            outputs.append(res[1])
            seq = res[0]
        if len(outputs) < min:
            return ErrLocation(seq.pos)
        return seq, outputs
    return comb

def first[In, Out](first: Combinator[In, Out], second: Combinator[In, t.Any]) -> Combinator[In, Out]:
    @combinator(f"({first.name} << {second.name})")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, Out]:
        res = first(seq)
        if iserr(res):
            return res
        obj = res[1]
        res = second(res[0])
        if iserr(res):
            return res
        return res[0], obj
    return comb

def second[In, Out](first: Combinator[In, t.Any], second: Combinator[In, Out]) -> Combinator[In, Out]:
    @combinator(f"({first.name} >> {second.name})")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, Out]:
        res = first(seq)
        if iserr(res):
            return res
        res = second(res[0])
        if iserr(res):
            return res
        return res[0], res[1]
    return comb

def alt[In, Out1, Out2](first: Combinator[In, Out1], *others: Combinator[In, Out2], name: t.Optional[str] = None):
    @combinator(name or f"{" | ".join([c.name for c in (first, *others)])}")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, Out1 | Out2]:
        res = first(seq)
        for other in others:
            if iserr(res):
                res = other(seq)
            else:
                break
        return res
    return comb

def build[**P, In, Out](builder: t.Callable[P, Out], input_type: t.Type[In], *arg_combinators: P.args, **kwarg_combinators: P.kwargs) -> Combinator[In, Out]:
    for i, arg in enumerate(arg_combinators, 1):
        if not isinstance(arg, Combinator):
            raise ValueError(f"Argument {i} must be of type '{Combinator.__name__}', but got '{arg}' of type '{type(arg).__name__}'")
    for key, value in kwarg_combinators.items():
        if not isinstance(value, Combinator):
            raise ValueError(f"Keyword argument '{key}' must be type '{Combinator.__name__}', but got '{value}' of type '{type(value).__name__}'")
        if len(arg_combinators) + len(kwarg_combinators) == 0:
            raise ValueError("At least one combinator must be passed in as an argument")
    positional_combinators = t.cast(tuple[Combinator[In, t.Any], ...], arg_combinators)
    named_combinators = t.cast(t.Mapping[str, Combinator[In, t.Any]], kwarg_combinators)
    @combinator
    def comb(seq: Advancer[In]) -> CombinatorResult[In, Out]:
        args: list[t.Any] = []
        for combinator in positional_combinators:
            res = combinator(seq)
            if iserr(res):
                return ErrLocation(seq.pos)
            seq, arg = res
            args.append(arg)
        
        kwargs: dict[str, t.Any] = dict()
        for name, combinator in named_combinators.items():
            res = combinator(seq)
            if iserr(res):
                return ErrLocation(seq.pos)
            seq, value = res
            kwargs[name] = value

        return seq, builder(*args, **kwargs) # type: ignore
    return comb


def cons[In, Out, Out2](first: Combinator[In, Out], second: Combinator[In, Out2]) -> Combinator[In, tuple[Out, Out2]]:
    @combinator(f"{first.name} & {second.name}")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, tuple[Out, Out2]]:
        res1 = first(seq)
        if iserr(res1):
            return res1
        res2 = second(res1[0])
        if iserr(res2):
            return res2
        return res2[0], (res1[1], res2[1])
    object.__setattr__(comb, "_is_construct", True)
    return comb

def append[In, *Out1, Out2](first: Combinator[In, tuple[*Out1]], second: Combinator[In, Out2]) -> Combinator[In, tuple[*Out1, Out2]]:
    @combinator(f"{first} & {second}")
    def comb(seq: Advancer[In]) -> CombinatorResult[In, tuple[*Out1, Out2]]:
        res1 = first(seq)
        if iserr(res1):
            return res1
        res2 = second(res1[0])
        if iserr(res2):
            return res2        
        return res2[0], (*res1[1], res2[1])
    object.__setattr__(comb, "_is_construct", True)
    return comb

def car[In, Car, *Cdr](combinator: Combinator[In, tuple[Car, *Cdr]]) -> Combinator[In, Car]:
    return outmap(combinator, lambda c: c[0])
def cdr[In, Car, *Cdr](combinator: Combinator[In, tuple[Car, *Cdr]]) -> Combinator[In, tuple[*Cdr]]:
    comb = outmap(combinator, lambda c: c[1:])
    object.__setattr__(comb, "_is_construct", True)
    return comb
def last[In, *Init, Last](combinator: Combinator[In, tuple[*Init, Last]]) -> Combinator[In, Last]:
    return outmap(combinator, lambda c: c[-1])
def init[In, *Init, Last](combinator: Combinator[In, tuple[*Init, Last]]) -> Combinator[In, tuple[*Init]]:
    comb = outmap(combinator, lambda c: c[:-1])
    object.__setattr__(comb, "_is_construct", True)
    return comb


def outfilter[In, Out](com: Combinator[In, Out], *options: Out) -> Combinator[In, Out]:
    @combinator(f"({' | '.join(map(lambda x: f"{x}", options))})")
    def comb(seq: Advancer[In]) -> CombinatorResult[In,Out]:
        res1 = com(seq)
        if iserr(res1):
            return res1
        return next(map(lambda x: (res1[0], x), filter(lambda x: x == res1[1], options)), ErrLocation(res1[0].pos))
    return comb
    
    
def outmap[In, Out, T](com: Combinator[In, Out], function: t.Callable[[Out], T]) -> Combinator[In, T]:
    @combinator(com.name)
    def comb(seq: Advancer[In]):
        res = com(seq)
        if iserr(res):
            return ErrLocation(res.index)
        try:
            obj = function(res[1])
        except RuntimeError:
            return ErrLocation(res[0].pos)
        return res[0], obj
    return comb

def ignore_second[In, Out](first: Combinator[In, Out], second: Combinator[In, t.Any]) -> Combinator[In, Out]:
    @combinator(first.name)
    def comb(seq: Advancer[In]):
        res = first(seq)
        if iserr(res):
            return res
        obj = res[1]
        seq = res[0]
        if not iserr(res := second(seq)):
            seq = res[0]
        return seq, obj
    return comb

def ignore_first[In, Out](first: Combinator[In, t.Any], second: Combinator[In, Out]) -> Combinator[In, Out]:
    @combinator(second.name)
    def comb(seq: Advancer[In]):
        if not iserr(res := first(seq)):
            seq = res[0]
        res = second(seq)
        return res
    return comb