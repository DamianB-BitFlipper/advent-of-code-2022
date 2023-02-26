import re
from enum import Enum, auto
from more_itertools import chunked, locate

INPUT_FILE = "input.txt"

# Make the Integrity also a monad
class Integrity(Enum):
    Correct = auto()
    Wrong = auto()
    Inconclusive = auto()

    def __or__(self, other):
        # Always propagate whatever `self` is if it is conclusive, otherwise propagate `other`
        if self in {Integrity.Correct, Integrity.Wrong}:
            return self
        else:
            return other

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

    def to_list(self):
        if self._accumulator is None:
            raise RuntimeError("Cannot create list from non-existent token accumulator.")

        ret = []
        for val in self._accumulator:
            # Recurse the `to_list` operation
            if isinstance(val, TokenAccumulator):
                ret.append(val.to_list())
            else:
                ret.append(val)

        return ret
    
    def __str__(self):
        if self._accumulator is None:
            return "Empty"
        else:
            return str(self.to_list())

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
        
        return self.resolution.to_list()
    
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

def packets_pair_walker(left_packet, right_packet):
    # Integer comparisons are well defined
    if type(left_packet) is int and type(right_packet) is int:
        if left_packet < right_packet:
            return Integrity.Correct
        elif left_packet > right_packet:
            return Integrity.Wrong
        else:
            return Integrity.Inconclusive
    
    # Fix any typing mismatch first
    if type(left_packet) is not type(right_packet):
        if type(left_packet) is int:
            left_packet = [left_packet]
        else:
            right_packet = [right_packet]    

    # Type sanity check
    assert type(left_packet) is list
    assert type(right_packet) is list    
            
    # Rule set if any one of the packets have been exhausted
    if len(left_packet) == 0 and len(right_packet) != 0:
        return Integrity.Correct
    elif len(left_packet) != 0 and len(right_packet) == 0:
        return Integrity.Wrong
    elif len(left_packet) == 0 and len(right_packet) == 0:
        return Integrity.Inconclusive

    lval, lrest = left_packet[0], left_packet[1:]
    rval, rrest = right_packet[0], right_packet[1:]

    # Recurse on the first elements and the rest elements
    return packets_pair_walker(lval, rval) | packets_pair_walker(lrest, rrest)
    
            
def main():
    with open(INPUT_FILE, 'r') as f:
        lines = chunked(filter(lambda l: l != '', map(lambda s: s.rstrip('\n'), f.readlines())), n=2)

    encoding_integrities = []
    for left_line, right_line in lines:
        left_packet, right_packet = ListParser.from_string(left_line).resolve(), ListParser.from_string(right_line).resolve()

        encoding_integrities.append(packets_pair_walker(left_packet, right_packet))
        
    # Sanity check that there is no inconclusive encoding integrity
    assert not any(map(lambda integrity: integrity is Integrity.Inconclusive, encoding_integrities))

    correct_indices = locate(encoding_integrities, lambda integrity: integrity is Integrity.Correct)

    # Convert the `correct_indices` to 1-indexed
    print("Part 1: ", sum(map(lambda i: i + 1, correct_indices)))

if __name__ == "__main__":
    main()
