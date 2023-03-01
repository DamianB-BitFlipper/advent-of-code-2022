import typing
from typing import Generic, TypeVar, Callable

from dataclasses import dataclass
from enum import Enum
import copy
import operator
from itertools import starmap

from math import sqrt

T = TypeVar('T', int, float, covariant=True)

@dataclass(frozen=True)
class Vector(Generic[T]):
    x: T
    y: T

    @staticmethod
    def dunder_broadcastable(func):
        def wrapper(self_: "Vector[T]", other: "T | Vector[T]") -> "Vector[T]":
            op = func()
            
            if isinstance(other, T.__constraints__):
                return op(self_, Vector(other, other))
            elif isinstance(other, Vector):
                return self_.__class__(op(self_.x, other.x), op(self_.y, other.y))
            else:
                return NotImplemented
        
        return wrapper

    @dunder_broadcastable
    @staticmethod
    def __add__() -> Callable[[T, T], T]:
        return operator.add
    __radd__ = __add__

    
    @dunder_broadcastable
    @staticmethod
    def __sub__() -> Callable[[T, T], T]:
        return operator.sub
    __rsub__ = __sub__

    @dunder_broadcastable
    @staticmethod
    def __mul__() -> Callable[[T, T], T]:
        return operator.mul
    __rmul__ = __mul__

    @dunder_broadcastable
    @staticmethod
    def __truediv__() -> Callable[[T, T], T]:
        return operator.truediv
    
    def __iter__(self) -> tuple[T, T]:
        return iter((self.x, self.y))
    
    @property
    def length(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    @property
    def manhattan(self) -> int:
        return abs(self.x) + abs(self.y)

    @property
    def norm(self) -> "Vector[float]":
        return self / self.length

    @property
    def orthogonal(self) -> "Vector[T]":
        return self.__class__(-1 * self.y, self.x)
    
    def dot(self, other) -> T:
        return self.x * other.x + self.y * other.y

class Coordinate(Vector[int]):
    
    @classmethod
    def from_string(cls, x, y):
        # String inputs of `y` are inverted in the problem, flip it back over
        return cls(int(x), -1 * int(y))

class Direction(Enum):
    N = Vector(0, 1)
    NE = Vector(1, 1)
    E = Vector(1, 0)
    SE = Vector(1, -1)
    S = Vector(0, -1)    
    SW = Vector(-1, -1)
    W = Vector(-1, 0)
    NW = Vector(-1, 1)
    STOP = Vector(0, 0)

    def __mul__(self, other: T | Vector[T]) -> Vector[T]:
        return self.value * other
    __rmul__ = __mul__
    
class LazyCoordinateSystem():

    def __init__(self, *, fill=None):
        self.fill = fill
        self.data = {}

        # Record the min and max values encountered for nice pretty-printing
        self.min_x = self.max_x = self.min_y = self.max_y = None

    def __getitem__(self, coord):
        if isinstance(coord, slice):
            vector = coord.stop - coord.start
            norm_vector = vector.norm
            
            ret = []
            c = coord.start
            # While the iterations are still progressing in the `norm_vector` direction
            while (coord.stop - c).dot(norm_vector) > 0:
                ret.append(self[c])
                c += coord.step or norm_vector
            return ret
        else:
            return self.data.get(tuple(coord), self.fill)

    def __setitem__(self, coord, value):
        if isinstance(coord, slice):
            vector = coord.stop - coord.start
            norm_vector = vector.norm

            c = coord.start
            # While the iterations are still progressing in the `norm_vector` direction
            while (coord.stop - c).dot(norm_vector) > 0:
                self[c] = value
                c += coord.step or norm_vector
        else:
            self.data[tuple(coord)] = value

            # Update the min/max values encountered if warranted
            self.min_x = min(filter(lambda c: c is not None, [self.min_x, coord.x]), default=None)
            self.min_y = min(filter(lambda c: c is not None, [self.min_y, coord.y]), default=None)
            self.max_x = max(filter(lambda c: c is not None, [self.max_x, coord.x]), default=None)
            self.max_y = max(filter(lambda c: c is not None, [self.max_y, coord.y]), default=None)        

    def __str__(self):
        if self.min_x is None:
            # Sanity check, the other coordinates must also be `None`
            assert all(map(lambda c: c is None, (self.min_y, self.max_x, self.max_y)))
            return "Empty"

        # Sanity check, all coordinates are non-`None`
        assert all(map(lambda c: c is not None, (self.min_x, self.min_y, self.max_x, self.max_y)))
        
        # Iterate from (min_x, max_y) -> (max_x, min_y) inclusive
        ret = ""
        for y in range(self.max_y, self.min_y - 1, -1):        
            for x in range(self.min_x, self.max_x + 1):
                coord = Coordinate(x, y)
                ret += str(self[coord])

            # Add a newline only if it is not the last iteration
            if y > self.min_y:
                ret += "\n"
                
        return ret

    def __repr__(self):
        return str(self)

    def __iter__(self):
        # Convert all of the keys to `Coordinate`s
        yield from starmap(lambda k, v: (Coordinate(*k), v), self.data.items())

    def copy(self):
        return copy.deepcopy(self)
