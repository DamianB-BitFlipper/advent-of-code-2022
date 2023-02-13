import re
import numpy
from dataclasses import dataclass
from enum import Enum

INPUT_FILE = "input.txt"

# Create a hashable dataclass with the extra arguments
@dataclass(frozen=True)
class Coordinates():
    x: int
    y: int

    def apply_direction(self, direction):
        return Coordinates(self.x + direction.value[0], self.y + direction.value[1])

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Coordinates(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return Coordinates(abs(self.x), abs(self.y))

class Direction(Enum):
    # One step vector in the respective directions
    Up    = Coordinates(0, -1)
    Down  = Coordinates(0, 1)
    Left  = Coordinates(-1, 0)
    Right = Coordinates(1, 0)

    @classmethod
    def from_string(cls, s):
        if s == 'U':
            return cls.Up
        elif s == 'D':
            return cls.Down
        elif s == 'L':
            return cls.Left
        elif s == 'R':
            return cls.Right
        else:
            raise ValueError(f"Unrecognized direction string: {s}")

@dataclass
class Movement():
    direction: Direction
    nsteps: int        
        
class UnboundedGrid():
    knots: list[Coordinates]

    t_visited: set[Coordinates]
    """A set of the coordinates where the rope tail has visited."""

    viz_min_x: int = 0
    viz_max_x: int = 0
    viz_min_y: int = 0
    viz_max_y: int = 0
    
    def __init__(self, nknots):
        # Assert that there are at least 2 knots, the head and tail
        assert nknots >= 2

        # Initialize the `knots` as `Coordinates`
        self.knots = [Coordinates(0, 0) for _ in range(nknots)]
        self.tail_visited = set()

        # Mark the starting position as visited by default
        self.mark_tail_visited()

    @property
    def n_visited(self):
        return len(self.tail_visited)

    @property
    def tail(self):
        """Return the tail which is the last knot."""
        return self.knots[-1]
    
    def mark_tail_visited(self):
        self.tail_visited.add(self.tail)

    def _apply_move_helper(self, knots, vector):
        # Apply the `vector` to the first knot
        new_head_pos = knots[0] + vector
        
        # Base case
        if len(knots) == 1:
            return [new_head_pos]

        # Trail the rope tail behind the head if needed
        diff = new_head_pos - knots[1]

        # Movement is needed only if any dimension of the `diff` is greater than 1
        if abs(diff.x) > 1 or abs(diff.y) > 1:
            # Compute the vector of movement for the trailing knot. It is
            # the diagonal of the respective signs of `diff`
            vector = Coordinates(numpy.sign(diff.x), numpy.sign(diff.y))

            # Recursively apply the `vector` with the trailing knot
            # being the head of this new movement
            return [new_head_pos] + self._apply_move_helper(knots[1:], vector)
        else:
            # The rest of the `knots` remain unmoved
            return [new_head_pos] + knots[1:]
        
    def apply_move(self, move):
        # Apply the `direction` a total of `nsteps` times
        for _ in range(move.nsteps):
            self.knots = self._apply_move_helper(self.knots, move.direction.value)

            # Mark wherever the tail is as visited
            self.mark_tail_visited()

    def visualize(self, tail_markings=True):
        # Find the range of the knots
        min_x = min(map(lambda k: k.x, self.knots))
        max_x = max(map(lambda k: k.x, self.knots))
        min_y = min(map(lambda k: k.y, self.knots))
        max_y = max(map(lambda k: k.y, self.knots))

        # Update the global min/max of the grid thus far
        self.viz_min_x = min(min_x, self.viz_min_x)
        self.viz_max_x = max(max_x, self.viz_max_x)
        self.viz_min_y = min(min_y, self.viz_min_y)
        self.viz_max_y = max(max_y, self.viz_max_y)
        
        x_size = self.viz_max_x - self.viz_min_x + 1
        y_size = self.viz_max_y - self.viz_min_y + 1
        grid = [['.' for _ in range(x_size)] for _ in range(y_size)]

        # First populate where the tail has visited with 'X'
        if tail_markings:
            for pos in self.tail_visited:
                grid[pos.y - self.viz_min_y][pos.x - self.viz_min_x] = 'X'
        
        # Populate the `grid` with the various knots
        for idx, knot in enumerate(self.knots):
            marker = 'H' if idx == 0 else str(idx)

            grid[knot.y - self.viz_min_y][knot.x - self.viz_min_x] = marker
            
        for line in grid:
            print(''.join(line))
        print()

            
def parse_line(line):
    ret = re.match(r'([UDLR]) (\d+)', line)
    return Movement(Direction.from_string(ret.group(1)), int(ret.group(2)))
    
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    # Materialize for parts 1 and 2
    moves = list(map(parse_line, lines))

    #
    # Part 1
    #
    grid = UnboundedGrid(2)
    
    for move in moves:
        grid.apply_move(move)
        
    print("Part 1: ", grid.n_visited)

    #
    # Part 2
    #
    grid = UnboundedGrid(10)
    
    for move in moves:
        grid.apply_move(move)

    print("Part 2: ", grid.n_visited)
        
if __name__ == "__main__":
    main()
