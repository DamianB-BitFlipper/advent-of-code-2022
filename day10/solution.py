import re
from typing import Any
from enum import Enum, auto
from dataclasses import dataclass
from itertools import count

INPUT_FILE = "input.txt"

class Command(Enum):
    addx = auto()
    noop = auto()

@dataclass
class Instruction():
    cmd: Command
    
    params: list[Any]
    """A list of any parameters passed to the instruction."""
    
    @classmethod
    def from_string(cls, val):
        ret = re.match(r'([a-z]+)\s*(.*)', val)
        if ret is None:
            raise ValueError(f"Invalid instruction: {val}")

        # The command is the first group
        cmd = ret.group(1)

        if cmd == "addx":
            arg = int(ret.group(2))
            return cls(Command.addx, [arg])
        elif cmd == "noop":
            return cls(Command.noop, [])
        else:
            raise ValueError(f"Unrecognized command: {cmd}")

class CPU:
    CRT_WIDTH: int = 40
    
    def __init__(self, instructions):
        # Initialize the initial state of the CPU
        self.X = 1
        self.crt = ''
        self.counter = 0
        
        self.instructions = iter(instructions)
    
    def __iter__(self):
        for cur_instr in self.instructions:
            if cur_instr.cmd is Command.addx:
                yield from self.addx(*cur_instr.params)
            elif cur_instr.cmd is Command.noop:
                yield from self.noop()
            else:
                raise ValueError(f"Unknown instruction: {cur_instr}")
            
    @property
    def current_state(self):
        return {'X': self.X, 'counter': self.counter, 'crt': self.crt}

    def _perform_cycle(self):
        # Increment the cycle counter first
        self.counter += 1

        # Get the position where the character will be placed on the `self.crt`. The position
        # is reset to the beginning and the crt cleared every `CRT_WIDTH` pixels
        char_pos = len(self.crt)
        if char_pos == CPU.CRT_WIDTH:
            char_pos = 0
            self.crt = ''
        
        # Append to the `self.crt` string
        char = '#' if self.X - 1 <= char_pos <= self.X + 1 else '.'
        self.crt += char
        
        yield self.current_state        

    def states_at(self, iterator):
        """Step the CPU a number of cycles forward defined in `iterator` and yield the `current_state`."""
        yield_cycle = next(iterator)
        for state in self:
            if state['counter'] == yield_cycle:
                yield state

                # Fetch the next `yield_cycle`
                yield_cycle = next(iterator)
        
    def addx(self, V):
        # Perform two cycles
        yield from self._perform_cycle()
        yield from self._perform_cycle()        

        # Add `V` to `X` after the 2 cycles
        self.X += V
        
    def noop(self):
        # Increment the counter with no other operation.        
        yield from self._perform_cycle()


def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    # Materialize for parts 1 and 2
    instructions = list(map(Instruction.from_string, lines))
    
    #
    # Part 1
    #
    cycles_of_interest = count(20, step=40)
    cpu1 = CPU(instructions)
    
    # Iterate the `cpu` taking the elements at `cycles_of_interest`
    signal_strength = sum(map(lambda s: s['counter'] * s['X'], cpu1.states_at(cycles_of_interest)))
    print("Part 1: ", signal_strength)

    #
    # Part 2
    #
    # Print the CRT every `CRT_WIDTH` of cycles    
    cycles_of_interest = count(CPU.CRT_WIDTH, step=CPU.CRT_WIDTH)
    cpu2 = CPU(instructions)

    crt = '\n'.join(map(lambda s: s['crt'], cpu2.states_at(cycles_of_interest)))
    print(f"Part 2:\n{crt}")
                
if __name__ == "__main__":
    main()
