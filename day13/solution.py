import re
from more_itertools import chunked

INPUT_FILE = "input.txt"

# TODO: Use a real monad MaybeList for the accumulator!
class TokenAccumulator():

    def __init__(self, *, default=None):
        self._accumulator = default
        
    def append(self, value):
        # No operation
        if value is None or self._accumulator is None:
            return

        self._accumulator.append(value)

    def hasvalue(self):
        return self._accumulator is not None

    def __str__(self):
        if self._accumulator is None:
            return "Empty"
        else:
            vals = ', '.join(map(str, self._accumulator))
            return f'[{vals}]'

class ListParser():

    def __init__(self, *, parent=None):
        self.parent = parent
        
        self.forward_to = None
        self.accumulator = TokenAccumulator()
        self.resolution = None

    @classmethod
    def from_string(cls, line):
        parser = ListParser()

        # Match all of the relevant tokens in `line`
        match_str = r"\[|\]|(?:\d+)"
        tokens = re.findall(match_str, line)

        # Push each `token` to the `parser`
        for token in tokens:
            parser.push(token)

        return parser
        
    def _resolve(self):
        # A `None` value in the `self.accumulator` means that too many close brackets were received
        if not self.accumulator.hasvalue():
            raise ValueError("Too many close brackets received.")

        # Move the `self.accumulator` to the  `self.resolution`
        self.resolution = self.accumulator
        self.accumulator = TokenAccumulator()
        
        return self.resolution

    def resolve(self):
        """User-facing resolve function simply returns the ``resolution``."""
        # Any open `self.accumulator` means that not all close brackets were received
        if self.accumulator.hasvalue():
            raise ValueError("Not all open brackets were closed.")
        
        return self.resolution
    
    def push(self, token):
        # If there is a forwarding parser, simply pass the `token` along
        if self.forward_to:
            self.forward_to.push(token)
            return

        if token == "[":
            # If we already have an `self.accumulator`, then this open bracket spawns
            # a child parser and let it handle the `token`
            if self.accumulator.hasvalue():
                self.forward_to = ListParser(parent=self)
                self.forward_to.push(token)
            else:
                self.accumulator = TokenAccumulator(default=[])
        elif token == "]":
            # A close bracket resolves and removes this parser
            res = self._resolve()      

            # Add to the `parent.accumulator` if `parent` exists, then close ourselves
            if self.parent:
                self.parent.accumulator.append(res)
                self.parent.forward_to = None
        else:
            # The `token` should be an integer
            val = int(token)            
            self.accumulator.append(val)

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = chunked(filter(lambda l: l != '', map(lambda s: s.rstrip('\n'), f.readlines())), n=2)

    for left_line, right_line in lines:
        print(left_line)
        print(ListParser.from_string(left_line).resolve())
        print()

if __name__ == "__main__":
    main()
