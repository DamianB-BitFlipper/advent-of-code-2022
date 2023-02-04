from functools import reduce

INPUT_FILE = "input.txt"

def parse_pairings(line):
    pairs = line.split(',')

    ret = []
    for pair in pairs:
        s, e = map(int, pair.split('-'))
        ret.append(range(s, e + 1))

    return ret

def has_full_containment(pairing):
    r1, r2 = pairing
    
    def range_is_contained(inner_r, outer_r):
        return inner_r[0] in outer_r and inner_r[-1] in outer_r

    return range_is_contained(r1, r2) or range_is_contained(r2, r1)

def has_overlap(pairing):
    r1, r2 = pairing
    return r2[0] <= r1[0] <= r2[-1] or r1[0] <= r2[0] <= r1[-1]

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    # Materialize for parts 1 and 2
    pairings = list(map(parse_pairings, lines))
    
    #
    # Part 1
    #
    containments = map(has_full_containment, pairings)    
    n_containments = reduce(lambda acc, b: acc + 1 if b else acc, containments, 0)
    print("Part 1:", n_containments)

    #
    # Part 2
    #
    overlaps = map(has_overlap, pairings)
    n_overlaps = reduce(lambda acc, b: acc + 1 if b else acc, overlaps, 0)
    print("Part 2:", n_overlaps)

if __name__ == "__main__":
    main()
