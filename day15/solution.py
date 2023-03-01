from typing import Iterable, TypeVar, Callable, Optional
from itertools import count
from more_itertools import interleave, peekable, make_decorator, consume, ilen
import re

from advent_support import Vector, Direction, Coordinate, LazyCoordinateSystem

T = TypeVar('T')

INPUT_FILE = "input.txt"

# Define a `peekable_function` decorator
peekable_function = make_decorator(peekable)

class Cave(LazyCoordinateSystem):

    def __init__(self, sensors_and_beacons: tuple[Coordinate, Coordinate]):
        super().__init__(fill='.')
        
        self.sensors_and_beacons = sensors_and_beacons
        
        for sensor, beacon in self.sensors_and_beacons:
            self[sensor] = 'S'
            self[beacon] = 'B'

    @staticmethod
    @peekable_function()
    def _walker(start: Coordinate, direction: Direction):
        """Walk from ``start`` heading in ``direction``."""
        yield start
        yield from Cave._walker(start + direction, direction)

    @staticmethod
    @peekable_function()
    def _biwalker(start: Coordinate, direction: Direction):
        """Walk from ``start`` heading in both ``direction`` and ``-1 * direction``."""
        yield from interleave(
            Cave._walker(start, direction), Cave._walker(start - direction, -1 * direction)
        )
        
    def map_flower(
            self,
            op: Callable[["Cave", Coordinate], T],
            origin: Coordinate,
            stop_pred: Callable[[Coordinate], bool] = lambda _: False,
            step: Vector = Direction.E.value,
    ) -> Iterable[T]:
        generators = []
        for i in count():
            # Special case for `i == 0`
            if i == 0:
                generators.append(Cave._biwalker(origin, step * Direction.E))
            else:
                generators.append(
                    Cave._biwalker(origin + i * Direction.N, step * Direction.E)
                )
                generators.append(
                    Cave._biwalker(origin + i * Direction.S, -1 * step * Direction.E)
                )

            # Yield all of the biwalker `generators` stepped twice, peeking and
            # filtering the `generators` before each step
            generators = [g for g in generators if not stop_pred(g.peek())]
            yield from map(lambda g: op(self, next(g)), generators)

            generators = [g for g in generators if not stop_pred(g.peek())]
            yield from map(lambda g: op(self, next(g)), generators)

            # Stop the iteration if all of the `generators` have been filtered
            if not generators:
                break                

    def apply_flower(
            self,
            op: Callable[["Cave", Coordinate], T],
            origin: Coordinate,
            stop_pred: Callable[[Coordinate], bool],            
            step: Vector = Direction.E.value,
    ):
        consume(self.map_flower(op, origin, stop_pred, step))
            
            
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    sensors_and_beacons = []
    for line in lines:
        res = re.fullmatch(r'Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)', line)
        # Sanity check
        assert res

        sensors_and_beacons.append((Coordinate.from_string(res.group(1), res.group(2)),
                                    Coordinate.from_string(res.group(3), res.group(4))))

    orig_cave = Cave(sensors_and_beacons)

    #
    # Part 1
    #
    cave_part1 = orig_cave.copy()
    
    def mark_non_beacon(cave, coord):
        if cave[coord] == '.':
            cave[coord] = '#'
    
    for sensor, beacon in cave_part1.sensors_and_beacons:
        manhattan_dist = (beacon - sensor).manhattan
        cave_part1.apply_flower(
            mark_non_beacon,
            sensor,
            lambda c: (c - sensor).manhattan > manhattan_dist
        )

    print("Part 1: ", ilen(filter(lambda v: v[0].y == -2000000 and v[1] == '#', cave_part1)))
    #print(cave_part1)
            
        
if __name__ == "__main__":
    main()
