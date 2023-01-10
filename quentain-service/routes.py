from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_caching import Cache

import random
import string

import sys
sys.path.append('../')
import quentain

api = Blueprint('api', __name__)


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

from models import *

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@api.route('/new_game', methods=['POST'])
@cross_origin()
@limiter.limit("10 per minute")  # Limit to 10 requests per minute, returns 429 if too many requests from a client
def new_game():
    status = -1
    while status != 0:
        # Create a new game in the database
        token = generate_token()
        data = request.get_json()
        # Extract the level from the data
        level = data.get("level")
        # Initialize the game with the player's name
        game = quentain.Game(level=level, token=token)
        # Store the game in a database
        status = store_game(game)
    return jsonify({"token": token}), 200


def add_player_to_game(game, player_name=''):
    number = game.add_player(player_name)
    # cache.delete_memoized(get_player_game_state, game.token)
    update_game_player(game)
    return number


@api.route('/join_game/<token>', methods=['POST'])
@cross_origin()
def join_game(token):
    # Validate the token
    game = get_game(token)
    if game is None:
        return "Game not found", 404
    if game.token != token:
        return "Invalid token", 401

    # Add the player to the game in the database
    number = add_player_to_game(game)

    if number < 4:
        return jsonify({"player_number": number}), 200
    else:
        return "Room Full!", 401

@api.route('/get_game_state/<token>', methods=['GET'])
@cross_origin()
# @cache.memoize(20)  # cache for 20 seconds
def get_game_state(token):
    # Get the player's game from the database or cache
    game = get_game(token)
    if not game.finished:
        # Return the game state
        return jsonify({"current_player": game.current_player, "started": game.started,"game_state": game.get_game_state(game.current_player)}), 200
    else:
        return jsonify({"finished": game.finished, "rank": game.get_rank()}), 200


def gen_game_state(game, player):
    if not game.finished:
        return {
            'turn': game.current_player,
            'deck': None if not game.started else [c.json_encode() for c in game.player_cards[player]],
            'comp': [] if game.prev_comp is None else [c.json_encode() for c in game.prev_comp.cards],
            'started': game.started
        }
    else:
        return {
            "finished": game.finished,
            "rank": game.get_rank()
        }


# Yuanbiao: I added this cuz I want a JSON object returned
# instead of a string that needs to be parsed...
# Sherry: change this to get_player_game_state to make the name more explanable
@api.route('/get_player_game_state/<token>/<player_id>', methods=['GET'])
@cross_origin()
# @cache.memoize(20)  # cache for 20 seconds
def get_player_game_state(token, player_id):
    # Get the player's game from the database or cache
    game = get_game(token)
    return jsonify(gen_game_state(game, int(player_id))), 200


@api.route('/throw_cards/<token>', methods=['POST'])
@cross_origin()
def throw_cards(token):
    # cache.delete_memoized(get_player_game_state, token)
    data = request.get_json()
    player_number = data.get('player_number')
    choices = data.get('choices')
    choices = [int(x) for x in choices]
    
    game = get_game(token)

    if game.finished:
        return jsonify({"finished": True}), 401
    if not game.started:
        return 'Game has not started', 401
    if player_number != game.current_player:
        return 'Not your turn', 401

    succeed, explanation = game.throw_cards(choices)
    update_game(game)
    if succeed:
        if isinstance(explanation, quentain.Fold):
            return jsonify({"folded": True}), 200
        else:
            return jsonify({"thrown_cards": str(explanation)}), 200
    else:
        return jsonify({"error": explanation}), 401


# Again added this for the frontend
@api.route('/throw_comp/<token>', methods=['POST'])
@cross_origin()
def throw_comp(token):
    # cache.delete_memoized(get_player_game_state, token)
    data = request.get_json()
    player_number = data.get('player_number')
    choices = data.get('choices')
    choices = [int(x) for x in choices]
    game = get_game(token)

    if game.finished:
        return jsonify({"finished": True}), 401
    if not game.started:
        return 'Game has not started', 401
    if player_number != game.current_player:
        return 'Not your turn', 401

    succeed, explanation = game.throw_cards(choices)
    update_game(game)
    if succeed:
        return jsonify({
            "comp": [c.json_encode() for c in explanation.cards],
            "deck": [c.json_encode() for c in game.player_cards[player_number]],
            "turn": game.current_player
        }), 200
    else:
        return jsonify({"error": explanation}), 401
