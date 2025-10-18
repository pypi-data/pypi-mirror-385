import typing as t

class Advancer[T](t.Sequence[T]):
    def __init__(self, sequence: t.Sequence[T], _pos: int = 0):
        self._sequence = sequence
        self._pos = _pos
    @property
    def pos(self):
        """The index of the beginning of this sequence in the original sequence"""
        return self._pos
    @property
    def raw(self) -> t.Sequence[T]:
        return self._sequence
    
    def advance(self, number: int) -> t.Self:
        """Gets a slice self[number:] without copying any memory"""
        return self.__class__(self._sequence, _pos = number + self._pos)
    def __len__(self):
        return max(len(self._sequence) - self._pos, 0)
    @t.overload
    def __getitem__(self, index: int) -> T: ...
    @t.overload
    def __getitem__(self, index: slice) -> t.Sequence[T]: ...
    def __getitem__(self, index: int | slice) -> T | t.Sequence[T]:
        if isinstance(index, slice):
            return self._sequence[self.pos:][index]
        return self._sequence[self.pos + index]
    def __str__(self):
        return f"{self.__class__.__name__}({self._sequence[self.pos:]})"
    def __repr__(self):
        return str(self)