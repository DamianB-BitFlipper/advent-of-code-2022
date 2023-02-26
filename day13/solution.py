import re
from enum import Enum, auto
from itertools import starmap, combinations, pairwise
from more_itertools import chunked, locate
from functools import reduce
from operator import mul, lt

INPUT_FILE = "input.txt"

# Make the Integrity also a monad
class Integrity(Enum):
    Correct = auto()
    Wrong = auto()
    Inconclusive = auto()

    def __or__(self, other):
        """Return a ``self`` if it is a conclusive value. Otherwise return ``other``."""
        if self in {Integrity.Correct, Integrity.Wrong}:
            return self
        else:
            return other
    
class Packet():

    def __init__(self, contents):
        self._contents = contents

    @staticmethod
    def pair_walker(left_packet, right_packet):
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

        # Recurse on the first values. If they are inconclusive, as defined by
        # the OR, the result of the rest values is returned
        return Packet.pair_walker(lval, rval) | Packet.pair_walker(lrest, rrest)

    def __lt__(self, other):
        # Correct integrity signifies an ordering where `self` is before `other` (ie: `self < other`)
        return Packet.pair_walker(self._contents, other._contents) is Integrity.Correct

    def __eq__(self, other):
        # Inconclusive integrity signifies equality between two packets
        return Packet.pair_walker(self._contents, other._contents) is Integrity.Inconclusive

    def __str__(self):
        return str(self._contents)
    
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

    def _to_list(self):
        if self._accumulator is None:
            raise RuntimeError("Cannot create list from non-existent token accumulator.")

        ret = []
        for val in self._accumulator:
            # Recurse the `_to_list` operation
            if isinstance(val, TokenAccumulator):
                ret.append(val._to_list())
            else:
                ret.append(val)

        return ret

    def to_packet(self):
        return Packet(self._to_list())
    
    def __str__(self):
        if self._accumulator is None:
            return "Empty"
        else:
            return str(self._to_list())

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
        
        return self.resolution.to_packet()
    
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
        lines = filter(lambda l: l != '', map(lambda s: s.rstrip('\n'), f.readlines()))
    packets = list(map(lambda line: ListParser.from_string(line).resolve(), lines))

    #
    # Part 1
    #
    # Packets in the correct order will respond positively to `left_packet < right_packet`
    correct_integrities = starmap(lt, chunked(packets, n=2))

    # Convert the correct integrity indices to 1-indexed
    print("Part 1: ", sum(map(lambda i: i + 1, locate(correct_integrities))))

    #
    # Part 2
    #
    DIVIDER_PACKETS = [Packet([[2]]), Packet([[6]])]
    ordered_packets = sorted(packets + DIVIDER_PACKETS)

    # Find the `divider_locations` on a 1-index
    divider_locations = map(lambda idx: idx + 1, locate(ordered_packets, lambda packet: packet in DIVIDER_PACKETS))

    # Multiple all of the divider locations together
    print("Part 2: ", reduce(mul, divider_locations, 1))
    
if __name__ == "__main__":
    main()
