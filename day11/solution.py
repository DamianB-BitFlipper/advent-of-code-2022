import operator
import re
from itertools import islice
import time

INPUT_FILE = "input.txt"

class Monkey():

    def __init__(self, identifier, items, worry_fn, test_fn, true_recipient, false_recipient):
        self.identifier = identifier
        self.items = items
        self.worry_fn = worry_fn
        self.test_fn = test_fn
        self.true_recipient = true_recipient
        self.false_recipient = false_recipient

        # Initialize the inspection counter
        self.n_inspections = 0

    @staticmethod
    def match(regex, val, group_ids):
        ret = re.match(regex, val)
        if ret is None:
            raise ValueError(f"Failed to match '{val}' to '{regex}'")
        return tuple(ret.group(i) for i in group_ids)
        
    @classmethod
    def from_description(cls, desc):
        lines = map(lambda s: s.strip(), desc.split('\n'))

        # The description has specific values at different lines
        m_monkey_id, = Monkey.match(r'Monkey (\d+):', next(lines), [1])
        m_monkey_items, = Monkey.match(r'Starting items: ((?:\d+(?:, )?)+)', next(lines), [1])
        m_worry_op, m_worry_op_val = Monkey.match(r'Operation: new = old ([+*]) (\d+|(?:old))', next(lines), [1, 2])
        m_test, = Monkey.match(r'Test: divisible by (\d+)', next(lines), [1])
        m_true_recipient, = Monkey.match(r'If true: throw to monkey (\d+)', next(lines), [1])
        m_false_recipient, = Monkey.match(r'If false: throw to monkey (\d+)', next(lines), [1])

        # Finish parsing the respective values
        monkey_id = int(m_monkey_id)
        monkey_items = [int(v) for v in m_monkey_items.split(', ')]
        get_worry_op_val = lambda v: v if m_worry_op_val == "old" else int(m_worry_op_val)
        worry_op = operator.add if m_worry_op == '+' else operator.mul
        test = int(m_test)
        true_recipient = int(m_true_recipient)
        false_recipient = int(m_false_recipient)

        return cls(
            identifier=monkey_id,
            items=monkey_items,
            worry_fn=lambda v: worry_op(v, get_worry_op_val(v)),
            test_fn=lambda v: v % test == 0,
            true_recipient=true_recipient,
            false_recipient=false_recipient,
        )

    def throw_items(self):
        """Iterate through the monkey logic."""
        for item in self.items:
            # Increment the inspection counter
            self.n_inspections += 1
        
            worry = self.worry_fn(item) // 3
            should_thow = self.test_fn(worry)
            
            if should_thow:
                yield self.true_recipient, worry
            else:
                yield self.false_recipient, worry

        # All of the items have been thrown, so clear them from our inventory
        self.items = []
    
class MonkeyGang():

    def __init__(self, monkeys):
        self.monkeys = monkeys

    def __iter__(self):
        # Define an infinite iterator
        while True:
            # Perform a round of monkey business
            for monkey in self.monkeys:
                # Transfer the `item`s to `recipient`s
                for recipient, item in monkey.throw_items():
                    self.monkeys[recipient].items.append(item)

            # Yield after a round of monkey business
            yield

    def __str__(self):
        ret = ''
        for monkey in self.monkeys:
            ret += 'Monkey {}: {}\n'.format(monkey.identifier, ', '.join(map(str, monkey.items)))

        return ret
            
def main():
    with open(INPUT_FILE, 'r') as f:
        monkey_descs = f.read().split('\n\n')

    monkey_gang = MonkeyGang([Monkey.from_description(md) for md in monkey_descs])

    #
    # Part 1
    #
    # Play 20 rounds of monkey business using `islice`
    #islice(monkey_gang, 20, None)
    for _ in range(20):
        next(iter(monkey_gang))
        print(monkey_gang)
    top_trouble_makers = sorted(map(lambda m: m.n_inspections, monkey_gang.monkeys), reverse=True)

    print("Part 1: ", top_trouble_makers[0] * top_trouble_makers[1])
        
if __name__ == "__main__":
    main()
