from collections import deque
import itertools

INPUT_FILE = "input.txt"

def all_unique(vals):
    seen = set()
    return not any(v in seen or seen.add(v) for v in vals)

def find_indicator_index(data, n_unique):
    # Turn the `data` into a generator to be consumed by `islice`
    data = (c for c in data)

    codes = deque(itertools.islice(data, n_unique))
    chars_processed = n_unique
    while not all_unique(codes):
        next_c = next(data, None)
        if next_c is None:
            raise ValueError("Reached end of stream without reading a start marker!")

        # Place `next_c` to the right and pop the left-most character
        codes.append(next_c)
        codes.popleft()

        # Increment the processed character counter
        chars_processed += 1

    return chars_processed
    
def main():
    with open(INPUT_FILE, 'r') as f:
        data = [c for c in f.read().rstrip()]

    print("Part 1:", find_indicator_index(data, 4))
    print("Part 2:", find_indicator_index(data, 14))
        
if __name__ == "__main__":
    main()
