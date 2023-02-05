from collections import deque
import re

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
        commands.append(int(d) for d in digits.findall(line))

    for move_n, _move_from, _move_to in commands:
        # Make the `move_from` and `move_to` 0-indexed
        move_from = _move_from - 1
        move_to = _move_to - 1

        # Move the n creates from `move_from` left to `move_to` left
        for _ in range(move_n):
            crate = columns[move_from].popleft()
            columns[move_to].appendleft(crate)

    print(''.join(col[0] for col in columns))
        
if __name__ == "__main__":
    main()
