import ast
from flask import Flask, request, jsonify
import pickle

from .game import Game
import quentain

app = Flask(__name__)

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    # Extract the level from the data
    level = data.get('level')
    # Initialize the game with the player's name
    game = Game(level)
    # Store the game in a database
    store_game(game)
    # Return a response to confirm that the game has been started

    return jsonify({'message': 'Game started!'})

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    # Get the player's game from the database or cache
    game = get_game()
    if not game.finished:
        # Return the game state
        return jsonify({'current_player': game.current_player, 'game_state': game.get_game_state(game.current_player)})
    else:
        rank = ''
        for i in range(4):
            rank += f'[{i + 1}] Player {game.finished_players[i]}'
        return jsonify({'finished': True, 'rank': game.finished_players})

@app.route('/throw_cards', methods=['POST'])
def throw_cards():
    data = request.get_json()
    choices = data.get('choices')
    choices = [int(x) for x in choices]
    game = get_game()

    if game.finished:
        return jsonify({'finished': True})

    succeed, explanation = game.throw_cards(choices)
    update_game(game)
    if succeed:
        if isinstance(explanation, quentain.Fold):
            return jsonify({'folded': True})
        else:
            return jsonify({'thrown_cards': str(explanation)})
    else:
        return jsonify({'error': explanation})

def store_game(game):
    # Open the file in write binary mode
    with open('game.bin', 'wb') as f:
        # Serialize the object and write it to the file
        pickle.dump(game, f)

def get_game():
    # Open the file in read binary mode
    with open('game.bin', 'rb') as f:
        # Load the object from the file
        game = pickle.load(f)
        return game

def update_game(game):
    # Open the file in write binary mode
    with open('game.bin', 'wb') as f:
        # Serialize the object and write it to the file
        pickle.dump(game, f)