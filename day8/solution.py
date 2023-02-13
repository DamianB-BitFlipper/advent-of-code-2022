from dataclasses import dataclass
from itertools import chain, count, repeat, starmap
from enum import Enum
from typing import Any
import copy

INPUT_FILE = "input.txt"

class Direction(Enum):
    """The visibility is coming from this direction."""
    North = 1
    East  = 2
    South = 3
    West  = 4

class Grid():
    """A convenient 2-d grid that can be iterated like any 1-d iterator."""
    _grid: list[list[Any]]

    @classmethod
    def from_list_grid(cls, list_grid):
        inst = cls()
        inst._grid = list_grid
        return inst

    @classmethod
    def from_fill(cls, len_x, len_y, fill):
        return cls.from_list_grid([[copy.copy(fill) for _ in range(len_x)] for _ in range(len_y)])

    @property
    def dimensions(self):
        """Return the x by y dimensions of this grid."""
        return len(self._grid[0]), len(self._grid)
        
    def __iter__(self):
        """Iterate over the grid rows by row, mimicking a 1-d iterable."""
        yield from chain.from_iterable(self._grid)

    def enumerate(self):
        """Iterate over the grid as a 1-d iterable, but include both (i, j) coordinates with every item."""
        yield from chain.from_iterable(starmap(lambda j, line: zip(line, count(), repeat(j)), enumerate(self._grid)))        

    def __getitem__(self, idx):
        return self._grid[idx]

    def is_edge(self, i, j):
        """Test if the coordinate (i, j) lays on an edge of the grid."""
        len_x, len_y = self.dimensions
        return i == 0 or i == len_x - 1 or j == 0 or j == len_y - 1
    
@dataclass
class TreeProperty():
    is_visible: bool
    scenic_score: int

    def apply_directional_property(self, dir_property):
        self.is_visible = self.is_visible or dir_property.is_visible
        self.scenic_score = self.scenic_score * dir_property.scenic_score
    
def calculate_tree_properties(grid, direction):
    len_x, len_y = grid.dimensions

    # Populate the `dir_properties_grid` with outer-edge trees at first
    dir_properties_grid = Grid.from_fill(len_x, len_y, TreeProperty(is_visible=True, scenic_score=0))

    for tree, i, j in grid.enumerate():
        # No need to iterate the outer layer of trees
        if grid.is_edge(i, j):
            continue

        if direction == Direction.North:
            # Get all trees above the current `tree`. The tree ordering
            # in `pre_trees` is from nearest to farthest
            pre_trees = [grid[vis_j][i] for vis_j in reversed(range(j))]
        elif direction == Direction.East:
            # Get all trees to the right of the current `tree`. The tree
            # ordering in `pre_trees` is from nearest to farthest
            pre_trees = [grid[j][vis_i] for vis_i in range(i + 1, len_x)]
        elif direction == Direction.South:
            # Get all trees below the current `tree`. The tree ordering
            # in `pre_trees` is from nearest to farthest
            pre_trees = [grid[vis_j][i] for vis_j in range(j + 1, len_y)]
        elif direction == Direction.West:
            # Get all trees to the left of the current `tree`. The tree
            # ordering in `pre_trees` is from nearest to farthest
            pre_trees = [grid[j][vis_i] for vis_i in reversed(range(i))]
        else:
            raise ValueError(f'Unknown direction {direction}')
            
        # A `tree` is visible only if its height is greater than
        # all of the trees before it.
        is_visible = max(pre_trees) < tree

        # The `scenic_score` of this `direction` are the number of trees before
        # one that is greater than or equal to in height from the current `tree`
        scenic_score = 0
        for pre_tree in pre_trees:
            scenic_score += 1
            if pre_tree >= tree:
                break
            
        # Populate the `dir_properties_grid` with a directional property
        dir_properties_grid[j][i] = \
            TreeProperty(
                is_visible=is_visible,
                scenic_score=scenic_score,
            )

    return dir_properties_grid

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    grid = Grid.from_list_grid([[int(c) for c in l] for l in lines])
    len_x, len_y = grid.dimensions
    
    # All trees begin as invisible until they are seen and have a neutral `scenic_score` of 1
    properties_grid = Grid.from_fill(*grid.dimensions, TreeProperty(is_visible=False, scenic_score=1))
    
    for direction in Direction:
        dir_properties_grid = calculate_tree_properties(grid, direction)

        # Element-wise apply the directional properties to the `properties_grid`
        for tree, dir_property in zip(properties_grid, dir_properties_grid):
            tree.apply_directional_property(dir_property)

    #
    # Part 1
    #
    n_invisible_trees = sum(map(lambda t: int(t.is_visible), properties_grid))
    print("Part 1: ", n_invisible_trees)

    #
    # Part 2
    #
    max_scenic_score = max(map(lambda t: t.scenic_score, properties_grid))
    print("Part 2: ", max_scenic_score)    
        
if __name__ == "__main__":
    main()
