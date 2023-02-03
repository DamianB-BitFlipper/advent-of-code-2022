
INPUT_FILE = "input.txt"

def parse_to_compartments(s):
    len_s = len(s)
    first_s, second_s = s[:len_s//2], s[len_s//2:]
    
    return set(first_s), set(second_s)

def get_priority(c):
    ord_c = ord(c)

    # For 'A'-'Z'
    if 65 <= ord_c <= 90:
        # The value 'A' has 27
        return ord_c - 65 + 27
    elif 97 <= ord_c <= 122:
        # The value `a` has 1
        return ord_c - 97 + 1
    else:
        raise ValueError(f"The character {c=} is out of range.")

def main():
    with open(INPUT_FILE, 'r') as f:
        # Materialize to share between parts 1 and 2
        lines = list(map(lambda s: s.rstrip('\n'), f.readlines()))

    compartments = map(parse_to_compartments, lines)
    overlaps = map(lambda c: c[0].intersection(c[1]), compartments)
    priorities = map(lambda c: sum(map(get_priority, c)), overlaps)

    #
    # Part 1
    #
    print("Part 1:", sum(priorities))

    #
    # Part 2
    #
    groups = [(lines[3 * i], lines[3 * i + 1], lines[3 * i + 2]) for i in range(len(lines) // 3)]
    badges = map(lambda g: set(g[0]).intersection(*g[1:]), groups)
    priorities = map(lambda c: sum(map(get_priority, c)), badges)
    print("Part 2:", sum(priorities))
    
if __name__ == "__main__":
    main()
