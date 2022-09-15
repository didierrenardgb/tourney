# Copyright 2022 The people
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from time import sleep
from typing import List
from random import randint, shuffle
from argparse import ArgumentParser, Namespace


def dramatic_delay(delay: float, config: Namespace):
    """Introduces a wait of `delay` seconds.
    
    Args:
        delay: Amount of seconds to delay.
        config: Parsed arguments from the command line. The value for `speed` will be read, which
            acts as a multiplier for the delay values.
    """
    if delay > 0 and config.speed > 0:  # skip the call if the effective delay would be 0 or less
        sleep(config.speed * delay)


def build_matches(with_players: List[str]) -> List[List[str]]:
    """It produces a random matches list after shuffling the provided player list.

    Args:
        with_players: A list of player names to build the matches with.

    Returns:
        List[List[str]]: A list of matches (list of player names) that should play between against.
    """
    for _ in range(10):  # shuffle 10 times to make a good scramble of the player list
        shuffle(with_players)
    matches = []
    current_match = -1  # starts in -1 so it gets increased to 0 in the first iteration
    for i in range(len(with_players)):
        # We need to push a new match to the list if there are none or if the previous one is full
        if len(matches) == 0 or len(matches[current_match]) >= 2:
            matches.append([])
            current_match += 1
        matches[current_match].append(with_players[i])
    return matches


def kick_penalty(player: str, config: Namespace) -> bool:
    """Have a player take a penalty.

    Args:
        player: The player taking the penalty. It's only used to display proper messages.

    Returns:
        bool: `True` if the penatly was scored, `False` otherwise.
    """
    print(f'{player} steps up... ', end='')
    dramatic_delay(0.6, config)
    print(f'{player} kicks... ', end='')
    dramatic_delay(1.0, config)
    if randint(0, 1) == 1:
        print('Scored \\O/')
        return True
    print('Missed <O>')
    return False


def determine_winner(scores: List[int], match: List[str], config: Namespace) -> str:
    """Small routine that determines who the winner is based on the provided scores.

    In case of a tie, it'll be decided by a sudden death. This means each player takes a penalty
    until someone scores while the other misses.

    Args:
        scores: 
    """
    winner = None
    if scores[0] > scores[1]:
        winner = match[0]
    elif scores[0] < scores[1]:
        winner = match[1]
    else:
        print('Draw! Sudden death...')
        dramatic_delay(0.3, config)
        while scores[0] == scores[1]:
            scores[0] += (1 if kick_penalty(match[0], config) else 0)
            scores[1] += (1 if kick_penalty(match[1], config) else 0)
        dramatic_delay(1.5, config)
        return determine_winner(scores, match, config)
    print(f'{winner} is the winner!')
    return winner

def play_match(match: List[str], config: Namespace) -> str:
    """Runs a match among two players.

    Args:
        match: A match consists of a list of players playing that match. It is expected for them
            to be 2.
        config: Parsed command line arguments. It'll be used to define the speed of the match and
            the total amount of penalties that the players will take.

    Returns:
        str: Name of the winning player
    """
    print(f'Next up: {match[0]} vs {match[1]}')
    print('-----------------------------------------')
    dramatic_delay(1.0, config)
    current_turn = True  # Flags who's current's turn. If True, first player; second otherwise.
    scores = [0, 0]
    for _ in range(config.penalty_count):
        player_index = 0 if current_turn else 1
        scores[player_index] += (1 if kick_penalty(match[player_index], config) else 0)
        print(f'\t{match[0]} {scores[0]} - {scores[1]} {match[1]}')
        print()
        current_turn = not current_turn
    dramatic_delay(0.5, config)
    print('-----------------------------------------')
    return determine_winner(scores, match, config)


def run_brackets(matches: List[List[str]], config: Namespace) -> List[str]:
    """Runs a list of matches, considered brackets from a play-off styled tourney.

    Args:
        matches: A list of matches (lists of strings representing players playing that match) to
            simulate.
        config: Parsed command line arguments. It'll be used to define the speed of the match and
            the total amount of penalties that the players will take.

    Returns:
        List[str]: List of winning players for the supplied matches.
    """
    print('*****************************************')
    winners = []
    for match in matches:
        if len(match) == 2:
            winners.append(play_match(match, config))
        else:
            print(f'No contendants for {match[0]}, advances to next round')
            winners.append(match[0])
    print('*****************************************')
    return winners


def parse_config(args: List[str]) -> Namespace:
    """Parse command line arguments to establish the configurations for the tourney.

    Args:
        args: Arguments for the program, typically taken from `sys.argv`.

    Return:
        Namespace: The parsed arguments.
    """
    parser = ArgumentParser()
    parser.add_argument('-pc', '--penalty-count', type=int, required=False, default=6,
                        help='Total amount of shots to be made by players; defaults to 6'
                             '(3 penalties each player)')
    parser.add_argument('-s', '--speed', type=float, required=False, default=1.0,
                        help='Modifier for simulation run speed; defaults to 1.0')
    parser.add_argument('players', nargs='*',
                        help='A space-separated list of participants for the tourney')
    if len(args) == 0:
        parser.print_help()
        exit(1)
    return parser.parse_args(args)


def main(args: List[str]):
    """Main routine fro the program.

    Args:
        args: List of profram arguments, typically aken from `sys.argv`
    """
    config = parse_config(args)
    matches = build_matches(config.players)
    while len(matches) > 1 or len(matches[0]) > 1:
        matches = build_matches(run_brackets(matches, config))
    print(f'{matches[0][0]} is the champion!')


# Just in case it's being executed as main script
if __name__ == '__main__':
    from sys import argv
    main(argv[1:])  # exclude script name
