# a CLI version of Quentain
# for single machine test only
import quentain
import ast
import math
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--exp',
        help='whether to turn on the experimental mode (7 cards for each player only)',
        action='store_true'
    )
    args = parser.parse_args()

    level = int(input('Please input a level(2-13):'))
    game = quentain.Game(level, first_player=0, experimental=args.exp)

    print('============<Game Started>==============')
    while not game.finished:
        print(f'\n============player {game.current_player + 1} cards============')
        player_cards = game.player_cards[game.current_player]
        num_lines = math.ceil(len(player_cards) / 9.0)
        for j in range(num_lines):
            print(', '.join(f'{9 * j + i}: {c}' for i, c in enumerate(player_cards[9 * j: 9 * (j + 1)])))
        print()
        succeed = False
        explanation = None
        while not succeed:
            if explanation is not None:
                print('Illegal Operation:', explanation)
            choices = input('Input your choices, splitting with comma: ')
            choices = ast.literal_eval('[' + choices.strip() + ']')
            succeed, explanation = game.throw_cards(choices)
        if isinstance(explanation, quentain.Fold):
            print('You folded!\n')
        else:
            print('You throw', explanation)

    print('============<Game Over; Ranks>==============')
    for i in range(4):
        print(f'[{i + 1}] Player {game.finished_players[i]}')
