import operator
import re
import time

INPUT_FILE = "input.txt"

class MonkeyBase():

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
        m_monkey_id, = cls.match(r'Monkey (\d+):', next(lines), [1])
        m_monkey_items, = cls.match(r'Starting items: ((?:\d+(?:, )?)+)', next(lines), [1])
        m_worry_op, m_worry_op_val = cls.match(r'Operation: new = old ([+*]) (\d+|(?:old))', next(lines), [1, 2])
        m_test, = cls.match(r'Test: divisible by (\d+)', next(lines), [1])
        m_true_recipient, = cls.match(r'If true: throw to monkey (\d+)', next(lines), [1])
        m_false_recipient, = cls.match(r'If false: throw to monkey (\d+)', next(lines), [1])

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
        
            worry = self.worry_fn(item)
            should_thow = self.test_fn(worry)
            
            if should_thow:
                yield self.true_recipient, worry
            else:
                yield self.false_recipient, worry

        # All of the items have been thrown, so clear them from our inventory
        self.items = []
    
class Part1Monkey(MonkeyBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The result of the worry function is divided by 3
        self._orig_worry_fn = self.worry_fn
        self.worry_fn = lambda item: self._orig_worry_fn(item) // 3
    
class MonkeyGang():

    def __init__(self, monkeys):
        self.monkeys = monkeys

    def __iter__(self):
        return self
        
    def __next__(self):
        # Perform a round of monkey business
        for monkey in self.monkeys:
            # Transfer the `item`s to `recipient`s
            for recipient, item in monkey.throw_items():
                self.monkeys[recipient].items.append(item)

    def __str__(self):
        ret = ''
        for monkey in self.monkeys:
            ret += 'Monkey {}: {}\n'.format(monkey.identifier, ', '.join(map(str, monkey.items)))

        return ret

    @property
    def monkey_business(self):
        top_trouble_makers = sorted(map(lambda m: m.n_inspections, self.monkeys), reverse=True)
        return top_trouble_makers[0] * top_trouble_makers[1]
    
def main():
    with open(INPUT_FILE, 'r') as f:
        monkey_descs = f.read().split('\n\n')

    monkey_gang = MonkeyGang([Part1Monkey.from_description(md) for md in monkey_descs])

    #
    # Part 1
    #
    # Play 20 rounds of monkey business
    for _ in range(20):
        next(monkey_gang)

    print("Part 1: ", monkey_gang.monkey_business)
        
if __name__ == "__main__":
    main()
