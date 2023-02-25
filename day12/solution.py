from typing import Iterable, Optional
from dataclasses import dataclass
from enum import Enum
from itertools import chain
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

    def __init__(self, *, initial: Optional[Iterable[tuple[Coordinate, int]]] = None):
        # Create two dictionaries, each keyed with each
        # other to implement a 2-way mapping
        self.frontier_keyed: dict[int, set[Coordinate]] = {}
        self.location_keyed: dict[Coordinate, int] = {}

        # Populate the dictionaries with any initial frontiers
        if initial is not None:
            for location, frontier in initial:
                self.location_keyed[location] = frontier
                
                # There may be no values yet at this `frontier_keyed_entry`
                frontier_keyed_entry = self.frontier_keyed.get(frontier, set())
                self.frontier_keyed[frontier] = frontier_keyed_entry | {location}

    @singledispatchmethod
    def __contains__(self, val):
        ...

    @__contains__.register
    def _(self, val: int):
        """Probe by frontier."""
        return val in self.frontier_keyed

    @__contains__.register
    def _(self, val: Coordinate):
        """Probe by location."""
        return val in self.location_keyed

    @singledispatchmethod
    def __getitem__(self, idx):
        ...

    @__getitem__.register
    def _(self, idx: int):
        """Query by frontier."""
        return self.frontier_keyed[val]

    @__getitem__.register
    def _(self, val: Coordinate):
        """Query by location."""
        return self.location_keyed[val]

    def __iter__(self):
        """Iterate as location keyed."""
        return iter(self.location_keyed.items())

    def __or__(self, other):
        """Create a new ``FrontiersSet`` combining ``self`` with ``other``."""
        return FrontiersSet(initial=chain(self, other))

    def __str__(self):
        return "FrontiersSet(" + ", ".join(f"{loc} @ {f}" for f, loc in self.frontier_keyed.items()) + "}"

    def __repr__(self):
        return str(self)
    
class Grid:

    def __init__(self, lines):
        self._grid = [[ord(c) for c in l] for l in lines]

        self.nrows = len(self._grid)
        self.ncols = len(self._grid[0])
        
        for r in range(self.nrows):
            for c in range(self.ncols):
                if self._grid[r][c] == ord('E'):
                    # The end has the height `z`
                    self._grid[r][c] = ord('z')
                    self.e_loc = Coordinate(r, c)
                elif self._grid[r][c] == ord('S'):
                    # The start has the height `a`
                    self._grid[r][c] = ord('a')                    
                    self.s_loc = Coordinate(r, c)

    def __str__(self):
        return str(self._grid)

    def __getitem__(self, coord):
        return self._grid[coord.r][coord.c]
                    
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

    def _solve_helper(self, *, frontiers_set, frontier):
        """This is a frontier based algorithm and records all newly discovered locations 
        during ``frontier`` until the end is located.
        """
        # Base case
        if self.e_loc in frontiers_set:
            return frontiers_set[self.e_loc]

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

                # Record the `next_loc` only if is has not been discovered yet
                if next_loc not in frontiers_set:
                    next_locs.add(next_loc)
        
        if not next_locs:
            raise RuntimeError(f"The frontier {frontier} found no new locations, but the end location was never discovered.")

        # Since each location in `next_locs` was newly discovered during `frontier`, record them as such
        new_frontiers_set = frontiers_set | FrontiersSet(initial=map(lambda loc: (loc, frontier), next_locs))
        
        # Continue on the recursion, solving the next `frontier`
        return self._solve_helper(frontiers_set=new_frontiers_set, frontier=frontier+1)
    
    def solve(self):
        return self._solve_helper(frontiers_set=FrontiersSet(initial=[(self.s_loc, 0)]), frontier=1)
                    
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    grid = Grid(lines)

    print(grid.solve())

if __name__ == "__main__":
    main()
