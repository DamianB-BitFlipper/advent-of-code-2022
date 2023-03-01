from typing import Iterable, TypeVar, Callable, Optional
from itertools import count
from more_itertools import peekable, make_decorator, consume, ilen, filter_except
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
    def _walker(start: Coordinate, direction: Direction) -> Iterable[Coordinate]:
        """Walk from ``start`` heading in ``direction``."""
        point = start
        while True:
            yield point
            point += direction

    @peekable_function()
    def map_linear(
            self,
            op: Callable[["Cave", Coordinate], T],
            origin: Coordinate,
            stop_pred: Callable[[Coordinate], bool] = lambda _: False,
            step: Vector = Direction.E.value,            
    ) -> Iterable[T]:
        generators = [Cave._walker(origin, step), Cave._walker(origin - step, -1 * step)]
        while generators:
            # Yield all `generators`, peeking and filtering them before stepping
            generators = [g for g in generators if not stop_pred(g.peek())]
            yield from map(lambda g: op(self, next(g)), generators)

    def apply_linear(
            self,
            op: Callable[["Cave", Coordinate], T],
            origin: Coordinate,
            stop_pred: Callable[[Coordinate], bool],            
            step: Vector = Direction.E.value,
    ):
        consume(self.map_linear(op, origin, stop_pred, step))
        
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
                generators.append(self.map_linear(op, origin, stop_pred, step))
            else:
                generators.append(
                    self.map_linear(op, origin + i * step.orthogonal, stop_pred, step)
                )
                generators.append(
                    self.map_linear(op, origin - i * step.orthogonal, stop_pred, -1 * step)
                )

            # Yield each bidirectional generator two for each direction. Filter
            # any generators not producing anymore in between each step
            generators = list(filter_except(lambda g: g.peek(), generators, StopIteration))
            yield from map(next, generators)

            generators = list(filter_except(lambda g: g.peek(), generators, StopIteration))
            yield from map(next, generators)            
            
            # If no `generators` are left, stop yielding
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
    row_of_interest = -2_000_000
    
    def mark_non_beacon(cave, coord):
        if cave[coord] == '.':
            cave[coord] = '#'
    
    for sensor, beacon in cave_part1.sensors_and_beacons:
        manhattan_dist = (beacon - sensor).manhattan

        # Find the point on the `row_of_interest`
        point = Vector(sensor.x, row_of_interest)

        # Apply a horizontal linear map, marking only this row
        cave_part1.apply_linear(
            mark_non_beacon,
            point,
            lambda c: (c - sensor).manhattan > manhattan_dist
        )

    print("Part 1: ", ilen(filter(lambda v: v[0].y == row_of_interest and v[1] == '#', cave_part1)))
            
        
if __name__ == "__main__":
    main()
