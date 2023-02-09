from functools import cached_property, total_ordering
from itertools import chain
import re

INPUT_FILE = "input.txt"

class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size

@total_ordering        
class Directory:
    def __init__(self, name, parentdir):
        self.name = name
        self.parentdir = parentdir
        self.subdirs = []
        self.files = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Directory(name={self.name}, parentdir={self.parentdir})"

    def __eq__(self, other):
        return self.name == other.name and self.parentdir == other.parentdir

    def __lt__(self, other):
        return self.size < other.size
    
    @cached_property
    def size(self):
        return (
            sum(map(lambda f: f.size, self.files)) +
            sum(map(lambda d: d.size, self.subdirs))
        )
                    
    def add_fs_entry(self, entry):
        if entry.startswith("dir"):
            self.subdirs.append(Directory(name=entry[4:], parentdir=self))
        elif (res := re.search('^([0-9]+) (.*)', entry)) is not None:
            self.files.append(File(name=res.group(2), size=int(res.group(1))))
        else:
            raise ValueError(f"Unrecognized filesystem entry: {entry}")

    def search_for_directory(self, directory):
        if directory == "..":
            ret = self.parentdir
        else:
            ret = next(filter(lambda d: d.name == directory, self.subdirs), None)

        if ret is not None:
            return ret
        else:
            raise ValueError(f"Directory not found: {directory}")

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    # Create a root directory
    ROOT_DIR = Directory("/", parentdir=None)
    
    cwd = None    
    while line := next(lines, False):
        # Each line encountered must be a command
        assert line[0] == "$"
        
        cmd = line[2:4]
        if cmd == "cd":
            directory = line[5:]
            print("CD", directory)            

            # Special case for non-relative `cd` to root
            if directory == "/":
                cwd = ROOT_DIR
            else:
                cwd = cwd.search_for_directory(directory)
        elif cmd == "ls":
            entries = []
            while entry := next(lines, None):
                if entry.startswith("$"):
                    break
                entries.append(entry)
            print("LS", entries)
                
            # Return the consumed `entry` back to `lines`, if any value was read
            if entry is not None:
                lines = chain([entry], lines)

            for entry in entries:
                cwd.add_fs_entry(entry)
        else:
            raise ValueError(f"Unrecognized command: {cmd}")

    #
    # Part 1
    #

    # Traverse all directories from `ROOT_DIR` down and keep a running sum
    # of the sizes of all directories smaller than `THRESHOLD`
    THRESHOLD = 100_000
    def traverse(d):
        rest = sum(map(lambda d: traverse(d), d.subdirs))
        return rest + (d.size if d.size <= THRESHOLD else 0)

    print("Part 1: ", traverse(ROOT_DIR))

    #
    # Part 2
    #
    CUR_FREE_SPACE = 70_000_000 - ROOT_DIR.size
    SPACE_NEEDED = 30_000_000 - CUR_FREE_SPACE

    assert SPACE_NEEDED > 0

    # Find the smallest directory greater than `SPACE_NEEDED`
    def traverse(d):
        # Base case
        if d.size < SPACE_NEEDED:
            return []

        return chain([d], chain.from_iterable(traverse(sd) for sd in d.subdirs))

    min_dir = min(traverse(ROOT_DIR))    
    print("Part 2: ", min_dir.size)
    
if __name__ == "__main__":
    main()
