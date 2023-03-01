from typing import Generic, TypeVar
from dataclasses import dataclass
from enum import Enum
import copy

from math import sqrt

T = TypeVar('T', int, float, covariant=True)

@dataclass(frozen=True)
class Vector(Generic[T]):
    x: T
    y: T

    def __add__(self, other: "Vector[T]") -> "Vector[T]":
        return self.__class__(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: "Vector[T]") -> "Vector[T]":
        return self.__class__(self.x - other.x, self.y - other.y)
    
    def __iter__(self) -> tuple[T, T]:
        return iter((self.x, self.y))

    def __truediv__(self, other: "Vector[T]") -> "Vector[T]":
        return self.__class__(self.x / other, self.y / other)
    
    @property
    def length(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    @property
    def norm(self) -> "Vector[float]":
        return self / self.length

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

    def copy(self):
        return copy.deepcopy(self)
