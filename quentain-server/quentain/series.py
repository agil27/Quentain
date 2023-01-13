from .game import Game
import names
import random
import string


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Series:
    '''
    A game series that starting at level 2, ending at level 13.
    '''

    def __init__(self, token=''):
        self.token = token
        self.players = [0, 1, 2, 3]
        self.player_names = {}
        self.current_game = None
        self.current_turn = 0
        self.levels = {0: 2, 1: 2}  # turn: level
        self.started = False
        self.game_tokens = []
        self.finished = False
        self.winning_turn = -1

    def add_player(self, player_name: str = None):
        res = len(self.player_names)
        if player_name is None:
            self.player_names[res] = names.get_full_name()
        else:
            self.player_names[res] = player_name
        return res

    def start(self):
        '''
        Start a new game series if all four players join, return the first game which is also started
        '''
        if len(self.player_names) < 4:
            return None
        else:
            token = generate_token()
            self.game_tokens.append(token)
            self.current_game = Game(level=self.levels[self.current_turn], token=token)
            self.current_game.player_names = self.player_names
            self.current_game.started = True
            return self.current_game

    def next_game(self):
        '''
        Based on the rank of current_game, start the next game
        '''
        finished_players = self.current_game.finished_players

        winner = finished_players[0]
        turn = winner % 2

        # For playing 'A', only if two players from the same side are both not the last can they win the game
        if self.levels[turn] == 13:
            if finished_players[3] % 2 != turn:
                self.finished = True
                self.winning_turn = turn
                return None

        else:
            self.levels[turn] += 1

            if finished_players[1] % 2 == turn:
                self.levels[turn] = min(self.levels[turn]+2, 13)
            elif finished_players[2] % 2 == turn:
                self.levels[turn] = min(self.levels[turn]+1, 13)
            else:
                self.levels[turn] += 0

        self.current_turn = turn
        token = generate_token()
        self.game_tokens.append(token)
        self.current_game = Game(
            level=self.levels[turn], first_player=winner, token=token)
        return self.current_game
