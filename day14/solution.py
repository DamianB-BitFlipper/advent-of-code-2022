import re
from itertools import starmap, pairwise
from more_itertools import ilen

from advent_support import Coordinate, Direction, LazyCoordinateSystem

INPUT_FILE = "input.txt"    
    
class Cave(LazyCoordinateSystem):

    def __init__(self):
        super().__init__(fill='.')
        
        # Insert the `sand_source`
        self.sand_source = Coordinate(500, 0)
        self[self.sand_source] = '+'
        
    def insert_rock_path(self, start, end):
        """Insert a straight rock path from ``start`` to ``end`` inclusive."""
        vector = end - start

        # Sanity check that the path is either horizontal or vertical
        assert any(map(lambda p: p == 0, vector))

        # Normalize the vector
        norm_vector = vector.norm
        self[start:end+norm_vector] = '#'

    @staticmethod
    def sand_move(spots):
        """Simulate the sand give the 3 spots directly below it."""
        # Sanity check
        assert len(spots) == 3

        if spots[1] == '.':
            return Direction.S
        elif spots[0] == '.':
            return Direction.SW
        elif spots[2] == '.':
            return Direction.SE
        else:
            return Direction.STOP
        
    def pour_sand_part1(self):
        # Save the current minimum before we have added any sand
        min_y = self.min_y

        while True:
            sand_loc = self.sand_source
        
            # The sand must be above the lowest level of rocks,
            # otherwise it will fall indefinitely
            while sand_loc.y > min_y:
                below = self[slice(sand_loc + Direction.SW.value, sand_loc + Direction.SE.value + Direction.E.value)]
                sand_move = self.sand_move(below)

                # Mark the sand down as it has settled
                if sand_move is Direction.STOP:
                    # Yield and mark this sand particle
                    yield sand_loc                    
                    self[sand_loc] = 'o'
                    
                    break
                else:
                    sand_loc += sand_move.value
            else:
                # The sand never settled and fell off indefinitely
                break

    def pour_sand_part2(self):
        # The floor is 2 units below the lowest rock path
        min_y = self.min_y - 2
        
        source_blocked = False
        while not source_blocked:
            sand_loc = self.sand_source
        
            while True:
                below = self[slice(sand_loc + Direction.SW.value, sand_loc + Direction.SE.value + Direction.E.value)]
                sand_move = self.sand_move(below)

                # Mark the sand down as it has settled. This is if it is stopped or directly above the floor
                if sand_move is Direction.STOP or sand_loc.y == min_y + 1:
                    # If the `sand_loc` is at the `self.sand_source`, it blocks it
                    if sand_loc == self.sand_source:
                        source_blocked = True
                    
                    # Yield and mark this sand particle
                    yield sand_loc                    
                    self[sand_loc] = 'o'
                    
                    break
                else:
                    sand_loc += sand_move.value           
            
    
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())
    line_coords = [list(starmap(Coordinate.from_string, re.findall(r'(\d+),(\d+)', l))) for l in lines]

    orig_cave = Cave()
    
    for coords in line_coords:
        for start_coord, end_coord in pairwise(coords):
            orig_cave.insert_rock_path(start_coord, end_coord)
            
    cave_part1 = orig_cave.copy()        
    print("Part 1: ", ilen(cave_part1.pour_sand_part1()))
    
    cave_part2 = orig_cave.copy()
    print("Part 2: ", ilen(cave_part2.pour_sand_part2()))
    
if __name__ == "__main__":
    main()
