import bisect
from dataclasses import dataclass
import re
import typing as t
import math

from .err import Err, iserr
from .advancer import Advancer

class Addative(t.Protocol):
    def __add__(self, other: t.Self, /) -> t.Self: ...

_P = t.ParamSpec("_P")
_In = t.TypeVar("_In")
_Out = t.TypeVar("_Out")
_Out2 = t.TypeVar("_Out2")
_TOut = t.TypeVarTuple("_TOut")
_Addative = t.TypeVar("_Addative", bound=Addative)
_Err = t.TypeVar("_Err", bound=Err)
_Err2 = t.TypeVar("_Err2", bound=Err)
CombinatorResult: t.TypeAlias = tuple[Advancer[_In], _Out] | _Err
CombinatorFunction: t.TypeAlias = t.Callable[[Advancer[_In]], CombinatorResult[_In, _Out, _Err]]

_Car = t.TypeVar("_Car")
_Cdr = t.TypeVarTuple("_Cdr")
_Last = t.TypeVar("_Last")
_Init = t.TypeVarTuple("_Init")

@dataclass(frozen=True)
class Position:
    line: int
    char: int

@dataclass(frozen=True)
class Span():
    start: int
    end: int

@dataclass(frozen=True)
class Token[T]:
    obj: T
    span: Span

@dataclass(frozen=True)
class ErrProduction(Err):
    span: Span

@dataclass(frozen=True)
class ErrIncompleteParsing(Err, t.Generic[_In, _Out]):
    seq: Advancer[_In]
    obj: _Out

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
class Combinator(t.Generic[_In, _Out, _Err]):

    function: CombinatorFunction[_In, _Out, _Err]
    name: str
    _is_construct: bool = False
    

    def as_token(self) -> Combinator[_In, Token[_Out], _Err]:
        @combinator(f"with_token({self.name})")
        def comb(seq: Advancer[_In]):
            start = seq.pos
            res = self(seq)
            if iserr(res):
                return res
            return res[0], Token(res[1], span=Span(start=start, end=res[0].pos))
        return comb
    

    def map(self, function: t.Callable[[_Out], _Out2]) -> Combinator[_In, _Out2, _Err | ErrProduction]:
        return outmap(self, function)
    def ucmap(self, function: t.Callable[[_Out], _Out2]) -> Combinator[_In, _Out2, _Err]:
        return unchecked_outmap(self, function)
    def produce(self, production: _Out2) -> Combinator[_In, _Out2, _Err]:
        return produce(self, production)
    
    def postignore(self, post: Combinator[_In, t.Any, Err]) -> Combinator[_In, _Out, _Err]:
        return ignore_second(self, post)
    
    def preignore(self, pre: Combinator[_In, t.Any, Err]) -> Combinator[_In, _Out, _Err]:
        return ignore_first(pre, self)
    
    def parse(self, seq: t.Sequence[_In]) -> _Out | _Err | ErrIncompleteParsing[_In, _Out]:
        return parse(self, seq)
    

    def otherwise(self, *other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, _Out | _Out2, _Err | _Err2]:
        return alt(self, *other)
    
    def seq(self: Combinator[_In, _Addative, _Err], *others: Combinator[_In, _Addative, _Err2]):
        return seq(self, *others)
    
    def after(self, other: Combinator[_In, t.Any, _Err2]) -> Combinator[_In, _Out, _Err | _Err2]:
        return first(self, other)
    def before(self, other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, _Out2, _Err | _Err2]:
        return second(self, other)
    
    def times(self: Combinator[_In, _Out, Err], min: int = 0, max: t.Optional[int] = None) -> Combinator[_In, list[_Out], ErrIncompleteParsing[_In, list[_Out]]]:
        return times(self, min, max)
    
    def cons(self, other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[_Out, _Out2], _Err | _Err2]:
        return cons(self, other)
    
    def append(self: Combinator[_In, tuple[*_TOut], _Err], other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[*_TOut, _Out2], _Err | _Err2]:
        return append(self, other)
    
    def car(self: Combinator[_In, tuple[_Car, *_Cdr], _Err]) -> Combinator[_In, _Car, _Err]:
        return car(self)
    def cdr(self: Combinator[_In, tuple[_Car, *_Cdr], _Err]) -> Combinator[_In, tuple[*_Cdr], _Err]:
        return cdr(self)
    def last(self: Combinator[_In, tuple[*_Init, _Last], _Err]) -> Combinator[_In, _Last, _Err]:
        return last(self)
    def init(self: Combinator[_In, tuple[*_Init, _Last], _Err]) -> Combinator[_In, tuple[*_Init], _Err]:
        return init(self)
        
    def filter(self, *options: _Out):
        return outfilter(self, *options)
    
    def errmap(self, casting_function: t.Callable[[Advancer[_In], str, _Err], _Err2]):
        return errmap(self, casting_function)
    
    @property
    def lie(self) -> _Out:
        """Returns self, i.e. the combinator, but "lies" by claiming to return a value
        of the combinator's output. This is to satisfy type checkers when using
        `build`.
        """
        return t.cast(_Out, self)
    
    def __call__(self, seq: Advancer[_In]) -> CombinatorResult[_In, _Out, _Err]:
        return self.function(seq)
    def __or__(self: Combinator[_In, _Out, _Err], other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, _Out | _Out2, _Err | _Err2]:
        return alt(self, other)
    def __lshift__(self, other: Combinator[_In, t.Any, _Err2]):
        return first(self, other)
    def __rshift__(self, other: Combinator[_In, _Out2, _Err2]):
        return second(self, other)
    

    @t.overload
    def __and__(self: Combinator[_In, tuple[*_TOut], _Err], other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[*_TOut, _Out2], _Err | _Err2]: ...
    @t.overload
    def __and__(self: Combinator[_In, _Out, _Err], other: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[_Out, _Out2], _Err | _Err2]: ...
    @t.no_type_check
    def __and__(self: Combinator[_In, _Out], other: Combinator[_In, _Out2]):
        if self._is_construct:
            return append(self, other)
        return cons(self, other)
    def __add__(self: Combinator[_In, _Addative, _Err], other: Combinator[_In, _Addative, _Err2]):
        return seq(self, other)

class UndefinedForwardCombinator(RuntimeError):
    def __init__(self):
        super().__init__("Attempted to parse with an undefined ForwardCombinator.")

class ForwardCombinator(Combinator[_In, _Out, _Err]):
    def __init__(self, name: str):
        def error(seq: Advancer[_In]) -> CombinatorResult[_In, _Out, _Err]:
            raise UndefinedForwardCombinator()
        super().__init__(function=error, name=name)
    def define(self, combinator: Combinator[_In, _Out, _Err]):
        object.__setattr__(self, "function", combinator.function)


def forward(type_in: t.Type[_In] = object, type_out: t.Type[_Out] = object, type_err: t.Type[_Err] = Err, name: str = "ForwardCombinator") -> ForwardCombinator[_In, _Out, _Err]:
    return ForwardCombinator[_In, _Out, _Err](name)


def sequence_to_advancer[T](seq: t.Sequence[T]) -> Advancer[T]:
    if isinstance(seq, Advancer):
        return seq
    else:
        return Advancer(seq)
    
def parse(combinator: Combinator[_In, _Out, _Err], seq: t.Sequence[_In]) -> _Out  | _Err | ErrIncompleteParsing[_In, _Out]:
    inp_advancer = sequence_to_advancer(seq)
    if iserr(v := combinator(inp_advancer)):
        return v
    if len(v[0]) > 0:
        return ErrIncompleteParsing(seq=v[0], obj=v[1])
    return v[1]

@t.overload
def combinator(name: str, /) -> t.Callable[[CombinatorFunction[_In, _Out, _Err]], Combinator[_In, _Out, _Err]]: ...
@t.overload
def combinator(function: CombinatorFunction[_In, _Out, _Err], /) -> Combinator[_In, _Out, _Err]: ...
def combinator(name_or_function: CombinatorFunction[_In, _Out, _Err] | str, /) -> Combinator[_In, _Out, _Err] | t.Callable[[CombinatorFunction[_In, _Out, _Err]], Combinator[_In, _Out, _Err]]:
    if isinstance(name_or_function, str):
        def wrapped(function: CombinatorFunction[_In, _Out, _Err]):
            return Combinator[_In, _Out, _Err](function=function, name=name_or_function)
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
        return Err()
    return c


def regex_groups(pattern: str, include_full: bool = False) -> Combinator[str, tuple[str, ...], Err]:
    if len(pattern) == 0:
        raise ValueError("pattern must be nonempty")
    compiled_pattern = re.compile(f"{pattern}")
    @combinator(f"r'{pattern}'")
    def c(seq: Advancer[str]):
        if not isinstance(seq.raw, str):
            raise ValueError(f"Cannot use Regex when the underlying data stream is not of type 'str': found type '{type(seq.raw).__name__}'")
        
        match = compiled_pattern.match(seq.raw, seq.pos)

        if not match:
            return Err()
        
        end = match.end() - seq.pos
        if include_full:
            groups = (t.cast(str, seq[:(end)]), *match.groups())
        else:
            groups = match.groups() or (match.group(0),)

        return seq.advance(end), groups
    return c

def regex(pattern: str) -> Combinator[str, str, Err]:
    return regex_groups(pattern, include_full=True).map(lambda x: x[0])

def seq(first_combinator: Combinator[_In, _Addative, _Err], *combinators: Combinator[_In, _Addative, _Err2]):
    @combinator(f"({" + ".join([c.name for c in combinators])})")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Addative, _Err | _Err2]:
        res = first_combinator(seq)
        if iserr(res):
            return res
        joined_obj = res[1]
        for combinator in combinators:
            res = combinator(res[0])
            if iserr(res):
                return res
            joined_obj += res[1]
        return res[0], joined_obj
    return comb

def times(com: Combinator[_In, _Out, Err], min: int = 0, max: t.Optional[int] = None) -> Combinator[_In, list[_Out], ErrIncompleteParsing[_In, list[_Out]]]:
    maximum = max or math.inf
    @combinator(f"{min} to {maximum} of {com.name}")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, list[_Out], ErrIncompleteParsing[_In, list[_Out]]]:
        outputs: list[_Out] = []
        while len(outputs) < maximum and not iserr(res := com(seq)):
            outputs.append(res[1])
            seq = res[0]
        if len(outputs) < min:
            return ErrIncompleteParsing(seq, outputs)
        return seq, outputs
    return comb

def first(first: Combinator[_In, _Out, _Err], second: Combinator[_In, t.Any, _Err2]) -> Combinator[_In, _Out, _Err | _Err2]:
    @combinator(f"({first.name} << {second.name})")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Out, _Err | _Err2]:
        res1 = first(seq)
        if iserr(res1):
            return res1
        obj = res1[1]
        res2 = second(res1[0])
        if iserr(res2):
            return res2
        return res2[0], obj
    return comb

def second(first: Combinator[_In, t.Any, _Err], second: Combinator[_In, _Out, _Err2]) -> Combinator[_In, _Out, _Err | _Err2]:
    @combinator(f"({first.name} >> {second.name})")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Out, _Err | _Err2]:
        res = first(seq)
        if iserr(res):
            return res
        res = second(res[0])
        if iserr(res):
            return res
        return res[0], res[1]
    return comb

def alt(first: Combinator[_In, _Out, _Err], *others: Combinator[_In, _Out2, _Err2], name: t.Optional[str] = None):
    @combinator(name or f"{" | ".join([c.name for c in (first, *others)])}")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Out | _Out2, _Err | _Err2]:
        res = first(seq)
        for other in others:
            if iserr(res):
                res = other(seq)
            else:
                break
        return res
    return comb

def build(builder: t.Callable[_P, _Out], input_type: t.Type[_In], *arg_combinators: _P.args, **kwarg_combinators: _P.kwargs) -> Combinator[_In, _Out, Err]:
    for i, arg in enumerate(arg_combinators, 1):
        if not isinstance(arg, Combinator):
            raise ValueError(f"Argument {i} must be of type '{Combinator.__name__}', but got '{arg}' of type '{type(arg).__name__}'")
    for key, value in kwarg_combinators.items():
        if not isinstance(value, Combinator):
            raise ValueError(f"Keyword argument '{key}' must be type '{Combinator.__name__}', but got '{value}' of type '{type(value).__name__}'")
        if len(arg_combinators) + len(kwarg_combinators) == 0:
            raise ValueError("At least one combinator must be passed in as an argument")
    positional_combinators = t.cast(tuple[Combinator[_In, t.Any, Err], ...], arg_combinators)
    named_combinators = t.cast(t.Mapping[str, Combinator[_In, t.Any, Err]], kwarg_combinators)
    @combinator
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Out, Err]:
        args: list[t.Any] = []
        for combinator in positional_combinators:
            res = combinator(seq)
            if iserr(res):
                return Err()
            seq, arg = res
            args.append(arg)
        
        kwargs: dict[str, t.Any] = dict()
        for name, combinator in named_combinators.items():
            res = combinator(seq)
            if iserr(res):
                return Err()
            seq, value = res
            kwargs[name] = value

        try:
            obj = builder(*args, **kwargs) # type: ignore
        except:
            return Err()

        return seq, obj
    return comb


def cons(first: Combinator[_In, _Out, _Err], second: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[_Out, _Out2], _Err | _Err2]:
    @combinator(f"{first.name} & {second.name}")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, tuple[_Out, _Out2], _Err | _Err2]:
        res1 = first(seq)
        if iserr(res1):
            return res1
        res2 = second(res1[0])
        if iserr(res2):
            return res2
        return res2[0], (res1[1], res2[1])
    object.__setattr__(comb, "_is_construct", True)
    return comb

def append(first: Combinator[_In, tuple[*_TOut], _Err], second: Combinator[_In, _Out2, _Err2]) -> Combinator[_In, tuple[*_TOut, _Out2], _Err | _Err2]:
    @combinator(f"{first} & {second}")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, tuple[*_TOut, _Out2], _Err | _Err2]:
        res1 = first(seq)
        if iserr(res1):
            return res1
        res2 = second(res1[0])
        if iserr(res2):
            return res2        
        return res2[0], (*res1[1], res2[1])
    object.__setattr__(comb, "_is_construct", True)
    return comb


def car(combinator: Combinator[_In, tuple[_Car, *_Cdr], _Err]) -> Combinator[_In, _Car, _Err]:
    comb = unchecked_outmap(combinator, lambda c: c[0])
    return comb
def cdr(combinator: Combinator[_In, tuple[_Car, *_Cdr], _Err]) -> Combinator[_In, tuple[*_Cdr], _Err]:
    comb = unchecked_outmap(combinator, lambda c: c[1:])
    object.__setattr__(comb, "_is_construct", True)
    return comb
def last(combinator: Combinator[_In, tuple[*_Init, _Last], _Err]) -> Combinator[_In, _Last, _Err]:
    return unchecked_outmap(combinator, lambda c: c[-1])
def init(combinator: Combinator[_In, tuple[*_Init, _Last], _Err]) -> Combinator[_In, tuple[*_Init], _Err]:
    comb = unchecked_outmap(combinator, lambda c: c[:-1])
    object.__setattr__(comb, "_is_construct", True)
    return comb


def outfilter(com: Combinator[_In, _Out, _Err], *options: _Out) -> Combinator[_In, _Out, _Err | ErrProduction]:
    @combinator(f"({' | '.join(map(lambda x: f"{x}", options))})")
    def comb(seq: Advancer[_In]) -> CombinatorResult[_In, _Out, _Err | ErrProduction]:
        res1 = com(seq)
        if iserr(res1):
            return res1
        return next(map(lambda x: (res1[0], x), filter(lambda x: x == res1[1], options)), ErrProduction(Span(seq.pos, res1[0].pos)))
    return comb
    
    
def outmap(com: Combinator[_In, _Out, _Err], function: t.Callable[[_Out], _Out2]) -> Combinator[_In, _Out2, _Err | ErrProduction]:
    unckeded_comb = unchecked_outmap(com, function)
    @combinator(com.name)
    def comb(seq: Advancer[_In]):
        try:
            return unckeded_comb(seq)
        except RuntimeError:
            return ErrProduction(Span(seq.pos, seq.pos))
    return comb

def unchecked_outmap(com: Combinator[_In, _Out, _Err], function: t.Callable[[_Out], _Out2]) -> Combinator[_In, _Out2, _Err]:
    @combinator(com.name)
    def comb(seq: Advancer[_In]):
        res = com(seq)
        if iserr(res):
            return res
        obj = function(res[1])
        return res[0], obj
    return comb

def ignore_second(first: Combinator[_In, _Out, _Err], second: Combinator[_In, t.Any, Err]) -> Combinator[_In, _Out, _Err]:
    @combinator(first.name)
    def comb(seq: Advancer[_In]):
        res = first(seq)
        if iserr(res):
            return res
        obj = res[1]
        seq = res[0]
        if not iserr(res := second(seq)):
            seq = res[0]
        return seq, obj
    return comb

def ignore_first(first: Combinator[_In, t.Any, Err], second: Combinator[_In, _Out, _Err]) -> Combinator[_In, _Out, _Err]:
    @combinator(second.name)
    def comb(seq: Advancer[_In]):
        if not iserr(res := first(seq)):
            seq = res[0]
        res = second(seq)
        return res
    return comb

def errmap(com: Combinator[_In, _Out, _Err], casting_function: t.Callable[[Advancer[_In], str, _Err], _Err2]) -> Combinator[_In, _Out, _Err2]:
    @combinator(com.name)
    def c(seq: Advancer[_In]):
        res = com(seq)
        if iserr(res):
            return casting_function(seq, com.name, res)
        return res
    return c

def produce(com: Combinator[_In, _Out, _Err], production: _Out2) -> Combinator[_In, _Out2, _Err]:
    @combinator(com.name)
    def c(seq: Advancer[_In]):
        res = com(seq)
        if iserr(res):
            return res
        return res[0], production
    return c