from enum import Enum

INPUT_FILE = "input.txt"

class Direction(Enum):
    """The visibility is coming from this direction."""
    North = 1
    East  = 2
    South = 3
    West  = 4

def calc_dir_visibility_grid(grid, direction):
    len_x = len(grid[0])
    len_y = len(grid)
    visibility_grid = [[True] * len_x for _ in range(len_y)]

    # No need to iterate the outer layer of trees
    for i in range(1, len_x - 1):
        for j in range(1, len_y - 1):
            # Get the current tree
            tree = grid[j][i]            
            if direction == Direction.North:
                # Get all trees above the current `tree`
                pre_trees = [grid[vis_j][i] for vis_j in range(j)]
            elif direction == Direction.East:
                # Get all trees to the right of the current `tree`
                pre_trees = [grid[j][vis_i] for vis_i in range(i + 1, len_x)]
            elif direction == Direction.South:
                # Get all trees below the current `tree`
                pre_trees = [grid[vis_j][i] for vis_j in range(j + 1, len_y)]
            elif direction == Direction.West:
                # Get all trees to the left of the current `tree`
                pre_trees = [grid[j][vis_i] for vis_i in range(i)]
            else:
                raise ValueError(f'Unknown direction {direction}')
            
            # A `tree` is visible only if its height is greater than
            # all of the trees before it.
            visibility_grid[j][i] = max(pre_trees) < tree

    return visibility_grid

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    grid = [[int(c) for c in l] for l in lines]
    len_x = len(grid[0])
    len_y = len(grid)

    # All trees begin as invisible until they are seen
    visibility_grid = [[False] * len_x for _ in range(len_y)]
    
    for direction in Direction:
        dir_visibility_grid = calc_dir_visibility_grid(grid, direction)

        # Perform a logical OR of both visibility grids to retrieve the new `visibility_grid`
        visibility_grid = [[visibility_grid[j][i] | dir_visibility_grid[j][i] for i in range(len_x)] for j in range(len_y)]

    # Sum all of the trees that are visible, `True`
    n_invisible_trees = sum(1 if visibility_grid[j][i] else 0 for i in range(len_x) for j in range(len_y))

    print("Part 1: ", n_invisible_trees)
        
if __name__ == "__main__":
    main()
