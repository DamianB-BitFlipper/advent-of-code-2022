from functools import reduce

# The input file can be found here: https://adventofcode.com/2022/day/1/input
INPUT_FILE = "input.txt"

def to_groups(acc, val):
    if val != '':
        acc[-1].append(int(val))
    else:
        acc += [[]]

    return acc

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    groups = reduce(to_groups, lines, [[]])

    # Materialize the `calories_per_elf` to be used between Parts 1 and 2
    calories_per_elf = list(map(sum, groups))

    #
    # Part 1
    #
    max_elf = max(calories_per_elf)
    print("Part 1:", max_elf)

    #
    # Part 2
    #
    top_3_elves = sorted(calories_per_elf, reverse=True)[:3]
    calories_top_3 = sum(top_3_elves)
    print("Part 2:", calories_top_3)

if __name__ == "__main__":
    main()
