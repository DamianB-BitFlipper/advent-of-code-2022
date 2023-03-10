from collections import deque
import re
from copy import deepcopy

INPUT_FILE = "input.txt"

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    columns_dict = {}
    for line in lines:
        # Test if this line is all numbers. If true, that is the
        # column index input line and column parsing is completed
        bare_line = line.replace(' ', '')
        if bare_line.isnumeric():
            break
        
        enum_line = enumerate(line)
        for idx, c in enum_line:
            if not c.isalpha():
                continue

            # Initialize an empty list for the first entry
            if idx not in columns_dict:
                columns_dict[idx] = list()
                
            columns_dict[idx].append(c)

    columns = []
    for col_key in sorted(columns_dict):
        columns.append(deque(columns_dict[col_key]))

    # Skip the empty line between the columns and instructions
    next(lines)

    commands = []
    for line in lines:
        digits = re.compile(r'\d+')
        commands.append([int(d) for d in digits.findall(line)])

    #
    # Part 1
    #
    columns_cpy = deepcopy(columns)
    for move_n, _move_from, _move_to in commands:
        # Make the `move_from` and `move_to` 0-indexed
        move_from = _move_from - 1
        move_to = _move_to - 1

        # Move the n crates from `move_from` left to `move_to` left
        for _ in range(move_n):
            crate = columns_cpy[move_from].popleft()
            columns_cpy[move_to].appendleft(crate)

    print("Part 1:", ''.join(col[0] for col in columns_cpy))

    #
    # Part 2
    #
    columns_cpy = deepcopy(columns)
    for move_n, _move_from, _move_to in commands:
        # Make the `move_from` and `move_to` 0-indexed
        move_from = _move_from - 1
        move_to = _move_to - 1

        # Move the n crates from `move_from` left to `move_to` left all at once
        crates = reversed([columns_cpy[move_from].popleft() for _ in range(move_n)])

        # The `extendleft` method results in the reversing of the iterable when placed in `columns_cpy`
        columns_cpy[move_to].extendleft(crates)

    print("Part 2:", ''.join(col[0] for col in columns_cpy))
        
if __name__ == "__main__":
    main()
