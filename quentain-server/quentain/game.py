# A single game with four players
from .card import Card, colors, name_map
from .comp import CardComp, IllegalComp
import math
import names
import random
import datetime

class Player:
    '''
    A player
    '''
    def __init__(self, name):
        self.name = name

class Game:
    '''
    A single game with a certain level value

    If modify Game, then modify Game in ../quentain-service/models.py
    '''

    def __init__(self, level, first_player=0, experimental=False, token=''):
        self.token = token
        self.expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        self.level = level
        self.distribute_cards(experimental)
        self.current_player = first_player
        self.prev_comp = None
        self.fold_num = 0
        self.winner = None
        self.started = False
        self.paused = False
        self.finished = False
        self.ongoing_players = [0, 1, 2, 3]
        self.player_names = {}
        self.finished_players = []
        self.player_comps = [None, None, None, None]

    def add_player(self, player_name: str = None):
        res = len(self.player_names)
        if player_name is None:
            self.player_names[res] = names.get_full_name()
        else:
            self.player_names[res] = player_name
        return res
            
    def distribute_cards(self, experimental=False):
        deck = []
        for color in colors:
            for number in range(1, 14):
                deck.extend([Card(number, color, self.level),
                             Card(number, color, self.level)])
        deck.extend([Card(15, 'Joker', self.level), Card(15, 'Joker', self.level),
                     Card(16, 'Joker', self.level), Card(16, 'Joker', self.level)])
        random.seed(datetime.datetime.now().timestamp())
        random.shuffle(deck)
        num_cards_per_player = 27 if not experimental else 4
        self.player_cards = [
            deck[i * num_cards_per_player : (i + 1) * num_cards_per_player]
            for i in range(4)
        ]
        for i in range(4):
            self.player_cards[i] = sorted(self.player_cards[i])

    def throw_cards(self, card_indices):
        '''
        execute a move of throwing a card composition
        :param card_indices: indices of cards from the current player's cards, empty list for folding
        :return:
            1. a boolean value indicating whether this throw is successful
            2. a CardComp object if successful or a string indicating the failure
        '''
        if len(card_indices) == 0:
            # fold
            if self.prev_comp is None:
                return False, 'The starter cannot fold!'
            self.fold_num += 1

            # if there are x - 1 consecutive players folding
            # where x is the number of ongoing players
            if self.fold_num == len(self.ongoing_players) - 1:
                # the next player is now free to
                # throw any types of composition
                self.prev_comp = None

            self.player_comps[self.current_player] = CardComp.from_card_list([])
            current_player_index = self.ongoing_players.index(self.current_player)
            self.current_player = self.ongoing_players[
                (current_player_index + 1) % len(self.ongoing_players)
                ]
            return True, CardComp.from_card_list([])
        else:
            # try to throw a comp
            current_player_cards = self.player_cards[self.current_player]
            selected_cards = [current_player_cards[i] for i in card_indices]
            comp = CardComp.from_card_list(selected_cards, self.prev_comp)
            if isinstance(comp, IllegalComp):
                return False, 'Illegal Composition!'
            if self.prev_comp is None or comp.greater_than(self.prev_comp):
                self.prev_comp = comp
                cards_after_throw = [
                    current_player_cards[i]
                    for i in range(len(current_player_cards))
                    if i not in card_indices
                ]
                self.player_cards[self.current_player] = cards_after_throw

                # reset the fold num
                self.fold_num = 0
            else:
                return False, 'This composition cannot beat the previous!'

            # find next player
            current_player_index = self.ongoing_players.index(self.current_player)
            next_player = self.ongoing_players[(current_player_index + 1) % len(self.ongoing_players)]

            # if this player uses up all his/her cards
            if len(self.player_cards[self.current_player]) == 0:
                self.finished_players.append(self.current_player)
                self.ongoing_players.remove(self.current_player)
                # only one player unfinished
                # the game is over
                if len(self.ongoing_players) == 1:
                    self.finished_players.append(self.ongoing_players[0])
                    self.ongoing_players = []
                    self.finished = True

            # go to next player
            self.player_comps[self.current_player] = comp
            self.current_player = next_player
            return True, comp

    def get_game_state(self, player):
        message = ''
        player_cards = self.player_cards[player]
            
        num_lines = math.ceil(len(player_cards) / 9.0)
        for j in range(num_lines):
            message += ', '.join(f'{9 * j + i}: {c}' for i, c in enumerate(player_cards[9 * j: 9 * (j + 1)]))
            message += '\n'
        return message

    def get_rank_str(self):
        assert self.finished
        rank = ''
        for i in range(4):
            rank += f'[{i + 1}] Player {self.player_names[self.finished_players[i]]}\n'
        return rank

    def get_rank(self):
        assert self.finished
        rank = [-1, -1, -1, -1]
        for i in range(4):
            rank[self.finished_players[i]] = i + 1
        return rank