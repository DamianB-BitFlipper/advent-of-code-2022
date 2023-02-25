from typing import Iterable, Optional, Any
from dataclasses import dataclass
from enum import Enum
from itertools import starmap
from functools import singledispatchmethod

INPUT_FILE = "input.txt"

# Create a hashable dataclass
@dataclass(frozen=True)
class Coordinate():
    r: int
    c: int

    def __str__(self):
        return f"({self.r}, {self.c})"

    def __repr__(self):
        return f"Coord({self.r}, {self.c})"

    def __add__(self, other):
        return Coordinate(self.r + other.r, self.c + other.c)
    
class Directions(Enum):
    # One step vector in the respective directions
    Up    = Coordinate(-1, 0)
    Down  = Coordinate(1, 0)
    Left  = Coordinate(0, -1)
    Right = Coordinate(0, 1)

class FrontiersSet():

    def __init__(self, *, initial: Optional[Iterable[tuple[Coordinate, Coordinate, int]]] = None):
        """Implements a bidirectional mapping of locations and frontiers.

        Initial values take an iterable of tuples consisting of: (location, parent_location, frontier).
        """
        # Create two dictionaries, each keyed with each
        # other to implement a 2-way mapping
        self.frontier_to_location: dict[int, set[Coordinate]] = {}
        self.location_to_frontier: dict[Coordinate, int] = {}
        self.location_to_parent: dict[Coordinate, Coordinate] = {}

        # Populate the dictionaries with any initial frontiers
        if initial is not None:
            for location, parent_location, frontier in initial:
                self.location_to_frontier[location] = frontier
                self.location_to_parent[location] = parent_location
                
                # There may be no values yet at this `frontier_to_location_entry`
                frontier_to_location_entry = self.frontier_to_location.get(frontier, set())
                self.frontier_to_location[frontier] = frontier_to_location_entry | {location}

    @singledispatchmethod
    def __contains__(self, val):
        ...

    @__contains__.register
    def _(self, val: int):
        """Probe by frontier."""
        return val in self.frontier_to_location

    @__contains__.register
    def _(self, val: Coordinate):
        """Probe by location."""
        return val in self.location_to_frontier

    @singledispatchmethod
    def __getitem__(self, idx):
        ...

    @__getitem__.register
    def _(self, idx: int):
        """Query by frontier."""
        return self.frontier_to_location[val]

    @__getitem__.register
    def _(self, val: Coordinate):
        """Query by location."""
        return self.location_to_frontier[val]

    def __iter__(self):
        """Iterate as location keyed."""
        return iter(self.location_to_frontier.items())

    def __or__(self, other):
        """Create a new ``FrontiersSet`` combining ``self`` with ``other``."""
        self_initial = [(loc, self.location_to_parent[loc], f) for loc, f in self]
        other_initial = [(loc, other.location_to_parent[loc], f) for loc, f in other]
        return FrontiersSet(initial=self_initial + other_initial)

    def __str__(self):
        return "FrontiersSet(" + ", ".join(f"{loc} @ {f}" for loc, f in self) + "}"

    def __repr__(self):
        return str(self)

    def retrieve_path(self, start, end):
        path = [end]
        
        # Work our way backswards since we only have parent information
        while parent := self.location_to_parent.get(path[-1]):
            # Add the parent to the path, which will further the loop upon the next iteration
            path.append(parent)            
            if parent == start:
                break
        else:
            # There exists no path
            raise ValueError(f"There exists no path between: {start} -> {end}")

        # The `path` is in reverse order, simply reverse and return
        return reversed(path)
    
class Grid:
    def __init__(self, matrix: Iterable[Iterable[Any]]):
        self._grid = [[val for val in row] for row in matrix]

        self.nrows = len(self._grid)
        self.ncols = len(self._grid[0])        
    
    def __str__(self):
        return str(self._grid)

    def __getitem__(self, coord):
        return self._grid[coord.r][coord.c]

    def __setitem__(self, coord, value):
        self._grid[coord.r][coord.c] = value

    def __iter__(self):
        for r in range(self.nrows):
            for c in range(self.ncols):
                coord = Coordinate(r, c)
                yield coord, self[coord]

class GridSolver(Grid):
    def __init__(self, lines):
        super().__init__(lines)

        # Convert the underlying `self._grid` to `ord`
        for r in range(self.nrows):
            for c in range(self.ncols):
                self._grid[r][c] = ord(self._grid[r][c])
                
                if self._grid[r][c] == ord('E'):
                    # The end has the height `z`
                    self._grid[r][c] = ord('z')
                    self.e_loc = Coordinate(r, c)
                elif self._grid[r][c] == ord('S'):
                    # The start has the height `a`
                    self._grid[r][c] = ord('a')                    
                    self.s_loc = Coordinate(r, c)
                    
    def _solve_helper_reverse(self, loc, acc_path):
        """Find the shortest distance from ``self.s_loc`` to ``loc``. It starts backwards
        from the end until it gets to the starting position. In effect, this algorithm tries
        all possible paths between the end and any point which makes it rather inefficient.
        """
        # Base case `loc` is the `self.s_loc`
        if loc == self.s_loc:
            return 0

        preceding_locs = []
        for direction in Directions:
            preceding_loc = loc + direction.value

            # Skip this location if it is out-of-bounds
            if not (0 <= preceding_loc.r < self.nrows and 0 <= preceding_loc.c < self.ncols):
                continue

            # Skip this location if the move `preceding_loc` -> `loc` exceeds the climbing restrictions
            climbing_diff = self[loc] - self[preceding_loc]
            if climbing_diff > 1:
                continue

            # Consider `preceding_loc` as a possible new location to explore
            preceding_locs.append(preceding_loc)

        # The preceding locations must be non-empty, otherwise `loc` is unreachable
        if not preceding_loc:
            raise RuntimeError(f"The location {loc} is unreachable.")
            
        recurse_locs = []
        for preceding_loc in preceding_locs:
            # Skip this location if it has already been visited in `acc_path`
            if preceding_loc in acc_path:
                continue
            
            # Consider the `preceding_loc` for further recursion
            recurse_locs.append(preceding_loc)

        # Recurse the solver on all `recurse_locs`, marking that we have already been to `loc`.
        # If no non-`None` distances are found, then we got to a dead end where there is a better
        # way to get to `self.s_loc` than this recursive branch
        dists = list(
            filter(lambda d: d is not None, 
                   map(lambda rec_loc: self._solve_helper_reverse(rec_loc, acc_path | {loc}), recurse_locs)
            )
        )

        # Return the best possible distance. If none exists, propagate the dead end `None`
        if dists:
            return 1 + min(dists)
        else:
            return None
            
    def solve_reverse(self):
        return self._solve_helper_reverse(self.e_loc, set())

    def _solve_frontiers_set_helper(self, *, frontiers_set, frontier):
        """This is a frontier based algorithm and records all newly discovered locations 
        during ``frontier`` until the end is located.
        """
        # Base case
        if self.e_loc in frontiers_set:
            return frontiers_set

        prev_frontier = frontier - 1
        
        # Fetch all of the coordinates that were reachable within `prev_frontier` steps
        prev_frontier_locs = [loc for loc, f in frontiers_set if f == prev_frontier]
        
        next_locs = set()
        for prev_frontier_loc in prev_frontier_locs:
            for direction in Directions:
                next_loc = prev_frontier_loc + direction.value
                
                # Skip this location if it is out-of-bounds
                if not (0 <= next_loc.r < self.nrows and 0 <= next_loc.c < self.ncols):
                    continue

                # Skip this location if the move `next_loc` -> `prev_frontier_loc` exceeds the climbing restrictions
                climbing_diff = self[next_loc] - self[prev_frontier_loc]
                if climbing_diff > 1:
                    continue

                # Record the `next_loc` and its parent `prev_frontier_loc` only if is has not been discovered yet
                if next_loc not in frontiers_set:
                    next_locs.add((next_loc, prev_frontier_loc))

        # The frontier found no new locations, but the end location was never discovered
        if not next_locs:
            return None

        # Since each location in `next_locs` was newly discovered during `frontier`, record them as such
        new_frontiers_set = frontiers_set | FrontiersSet(initial=starmap(lambda loc, parent_loc: (loc, parent_loc, frontier), next_locs))
        
        # Continue on the recursion, solving the next `frontier`
        return self._solve_frontiers_set_helper(frontiers_set=new_frontiers_set, frontier=frontier+1)
    
    def _solve_frontiers_set(self, start):
        return self._solve_frontiers_set_helper(frontiers_set=FrontiersSet(initial=[(start, None, 0)]), frontier=1)

    def solve(self):
        frontiers_set = self._solve_frontiers_set(self.s_loc)
        return frontiers_set[self.e_loc]

    def solve_all_starts(self):
        solutions_grid = Grid([[None] * self.ncols] * self.nrows)

        # Iterate over ourselves, solving every starting point
        for loc, altitude in self:
            # Skip any irrelevant `altitude`
            if altitude != ord('a'):
                continue

            # Skip if we have already solved `loc` from a previous solution's path
            if solutions_grid[loc] is not None:
                continue

            # Solve the frontiers starting from `loc` until the end location
            frontiers_set = self._solve_frontiers_set(loc)

            # Ignore `loc` if no solution is found. This means that there is no path from `loc` -> `self.e_loc`
            if frontiers_set is None:
                continue

            # Retrieve the path from `loc` -> `self.e_loc`
            solution_path = list(frontiers_set.retrieve_path(loc, self.e_loc))

            # Iterate through the `solution_path`, if any points along it are of altitude 'a', record their solution too
            for i, solution_loc in enumerate(solution_path):
                if self[solution_loc] == ord('a'):
                    dist_to_e = len(solution_path) - i - 1
                    
                    # Sanity check that if a solution is already marked, the result should be identical with what we calculated
                    if solutions_grid[solution_loc] is not None:
                        assert solutions_grid[solution_loc] == dist_to_e

                    # Assign the distance to the end at `solution_loc`
                    solutions_grid[solution_loc] = dist_to_e

        # The result is all locations of non-`None` values and the values themselves
        yield from filter(lambda pair: pair[1] is not None, solutions_grid)
        
    
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    grid_solver = GridSolver(lines)
    
    #
    # Part 1
    #   
    print("Part 1: ", grid_solver.solve())

    #
    # Part 2
    #
    solutions = grid_solver.solve_all_starts()
    print("Part 2: ", min(starmap(lambda _, dist: dist, solutions)))

if __name__ == "__main__":
    main()
