
# The input file can be found here: https://adventofcode.com/2022/day/2/input
INPUT_FILE = "input.txt"

def calculate_score_part1(game):
    # Query the score as `score_table[opp_move][our_move]`
    score_table = {
        # Rock: 1pt
        'A': {
            'X': 1 + 3, # Rock, draw
            'Y': 2 + 6, # Paper, win
            'Z': 3 + 0, # Scissors: loss
        },
        # Paper: 2pt
        'B': {
            'X': 1 + 0, # Rock, loss
            'Y': 2 + 3, # Paper, draw
            'Z': 3 + 6, # Scissors: win
        },
        # Scissors: 3p
        'C': {
            'X': 1 + 6, # Rock, win
            'Y': 2 + 0, # Paper, loss
            'Z': 3 + 3, # Scissors: draw
        },
    }

    return score_table[game[0]][game[1]]

def calculate_score_part2(game):
    # Query the score as `score_table[opp_move][our_move]`
    score_table = {
        # Rock: 1pt
        'A': {
            'X': 0 + 3, # loss, scissors
            'Y': 3 + 1, # draw, rock
            'Z': 6 + 2, # win, paper
        },
        # Paper: 2pt
        'B': {
            'X': 0 + 1, # loss, rock
            'Y': 3 + 2, # draw, paper
            'Z': 6 + 3, # win, scissors
        },
        # Scissors: 3p
        'C': {
            'X': 0 + 2, # loss, paper
            'Y': 3 + 3, # draw, scissors
            'Z': 6 + 1, # win, rock
        },
    }

    return score_table[game[0]][game[1]]

def main():
    with open(INPUT_FILE, 'r') as f:
        lines = map(lambda s: s.rstrip('\n'), f.readlines())

    # Materialize for both parts 1 and 2 
    games = list(map(lambda l: l.split(), lines))

    #
    # Part 1
    #
    scores = map(calculate_score_part1, games)    
    total_score = sum(scores)    
    print(total_score)

    #
    # Part 2
    #
    scores = map(calculate_score_part2, games)    
    total_score = sum(scores)    
    print(total_score)
    
if __name__ == "__main__":
    main()
