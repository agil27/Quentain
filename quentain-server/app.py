from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import datetime
import pickle
import random
import sqlite3
import string
import threading
from quentain.game import Game
import quentain


# Initiate flask app
app = Flask(__name__)
CORS(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per minute"],
    storage_uri="memory://",
)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initiate db connections
conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

# Create the game_rooms table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expiration_time DATETIME NOT NULL,
            current_player INTEGER NOT NULL,
            prev_comp BLOB,
            fold_num INTEGER NOT NULL,
            winner INTEGER,
            started INTEGER NOT NULL,
            paused INTEGER NOT NULL,
            finished INTEGER NOT NULL,
            ongoing_players BLOB NOT NULL,
            player_names BLOB NOT NULL,
            finished_players BLOB NOT NULL,
            player_cards BLOB NOT NULL,
            player_comps BLOB NOT NULL
    )
''')

# Create the game_series table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            player_names BLOB NOT NULL,
            current_turn INTEGER NOT NULL,
            levels BLOB NOT NULL,
            started INTEGER NOT NULL,
            game_tokens BLOB NOT NULL,
            finished INTEGER NOT NULL,
            winning_turn INTEGER NOT NULL
    )
''')

conn.commit()
cursor.close()


@app.route('/new_series', methods=['POST'])
@cross_origin()
@limiter.limit("10 per minute")
def new_series():
    status = -1


@app.route('/new_game', methods=['POST'])
@cross_origin()
# Limit to 10 requests per minute, returns 429 if too many requests from a client
@limiter.limit("10 per minute")
def new_game():
    status = -1
    while status != 0:
        # Create a new game in the database
        token = generate_token()
        data = request.get_json()
        # Extract the level from the data
        level = data.get("level")
        experimental = data.get("experimental")
        # Initialize the game with the player's name
        game = Game(level=level, token=token, experimental=experimental)
        # Store the game in a database
        status = store_game(game)

    return jsonify({"token": token}), 200


def add_player_to_game(game, player_name=''):
    number = game.add_player(player_name)
    update_game(game)
    return number


@app.route('/join_game/<token>', methods=['POST'])
@cross_origin()
def join_game(token):
    # Validate the token
    game = get_game(token)
    if game is None:
        return jsonify({'reason': "Game not found"}), 404
    if game.token != token:
        return jsonify({'reason': "Invalid token"}), 401

    # Add the player to the game in the database
    number = add_player_to_game(game)
    if (number == 3):
        game.started = True
        update_game(game)
    if number < 4:
        return jsonify({"player_number": number}), 200
    else:
        return jsonify({'reason': "Room Full!"}), 401


@app.route('/start_game/<token>', methods=['POST'])
@cross_origin()
def start_game(token):
    # Retrieve the game from the database
    game = get_game(token)
    if game is None:
        return "Game not found", 404

    # Check if all players have joined
    if len(game.player_names) < len(game.ongoing_players):
        return "Not all players have joined", 400

    # Start the game
    game.started = True
    update_game(game)
    return "Game started!", 204


@app.route('/get_game_state/<token>', methods=['GET'])
@cross_origin()
def get_game_state(token):
    # Get the player's game from the database or cache
    game = get_game(token)
    if not game.finished:
        # Return the game state
        return jsonify({"current_player": game.current_player, "started": game.started, "game_state": game.get_game_state(game.current_player)}), 200
    else:
        return jsonify({"finished": game.finished, "rank": game.get_rank_str()}), 200


def gen_game_state(game, player):
    if not game.finished and not game.paused:
        return {
            'turn': game.current_player,
            'deck': None if not game.started else [c.json_encode() for c in game.player_cards[player]],
            'comp': [] if game.prev_comp is None else [c.json_encode() for c in game.prev_comp.cards],
            'started': game.started,
            'player_comp': [[c.json_encode() for c in comp.cards] if comp is not None else None for comp in game.player_comps],
            'finished_players': game.finished_players,
            'finished': game.finished,
            'paused': game.paused
        }
    elif game.paused:
        return {
            'started': game.started,
            "paused": game.paused,
            'player_comp': [[c.json_encode() for c in comp.cards] if comp is not None else None for comp in game.player_comps],
        }
    else:
        return {
            "finished": game.finished,
            "rank": game.get_rank()
        }


# Yuanbiao: I added this cuz I want a JSON object returned
# instead of a string that needs to be parsed...
# Sherry: change this to get_player_game_state to make the name more explanable
@app.route('/get_player_game_state/<token>/<player_id>', methods=['GET'])
@cross_origin()
def get_player_game_state(token, player_id):
    # Get the player's game from the database or cache
    game = get_game(token)
    return jsonify(gen_game_state(game, int(player_id))), 200


@app.route('/throw_cards/<token>', methods=['POST'])
@cross_origin()
def throw_cards(token):
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
@app.route('/throw_comp/<token>', methods=['POST'])
@cross_origin()
def throw_comp(token):
    data = request.get_json()
    player_number = data.get('player_number')
    choices = data.get('choices')
    choices = [int(x) for x in choices]
    game = get_game(token)

    if game.finished:
        return jsonify({"error": 'game finished'}), 401
    if not game.started:
        return jsonify({'error': 'Game has not started'}), 401
    if player_number != game.current_player:
        return jsonify({'error': 'Not your turn'}), 401

    succeed, explanation = game.throw_cards(choices)
    update_game(game)
    if succeed:
        return jsonify({
            "player_comp": [[c.json_encode() for c in comp.cards] if comp is not None else None for comp in game.player_comps],
            "comp": [c.json_encode() for c in explanation.cards],
            "deck": [c.json_encode() for c in game.player_cards[player_number]],
            "turn": game.current_player
        }), 200
    else:
        return jsonify({"error": explanation}), 401


def store_game(game):
    # Convert the ongoing_players, player_names, and player_cards attributes to strings
    ongoing_players_blob = sqlite3.Binary(pickle.dumps(game.ongoing_players))
    player_names_blob = sqlite3.Binary(pickle.dumps(game.player_names))
    finished_players_blob = sqlite3.Binary(pickle.dumps(game.finished_players))
    prev_comp_blob = sqlite3.Binary(pickle.dumps(game.prev_comp))
    player_cards_blob = sqlite3.Binary(pickle.dumps(game.player_cards))
    player_comps_blob = sqlite3.Binary(pickle.dumps(game.player_comps))
    try:
        cursor = conn.cursor()
        # Insert the game into the table
        cursor.execute('''
            INSERT INTO games (level, token, expiration_time, current_player, prev_comp, fold_num, winner, started, paused, finished, ongoing_players, player_names, finished_players, player_cards, player_comps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            game.level, game.token, game.expiration_time.strftime(
                "%Y-%m-%d %H:%M:%S"), game.current_player, prev_comp_blob,
            game.fold_num, game.winner, game.started, game.paused, game.finished, ongoing_players_blob,
            player_names_blob, finished_players_blob, player_cards_blob, player_comps_blob
        ))
        conn.commit()
        cursor.close()
    except sqlite3.IntegrityError:
        return -1

    return 0


def get_series(token):
    # Open the file in read binary mode
    fetch_cursor.execute('''
        SELECT * FROM series
        WHERE token = ?
    ''', (token,))
    row = fetch_cursor.fetchone()

    if row is None:
        return None
    else:
        series = quentain.Series(
            token=row[1]
        )
        series.player_names = pickle.loads(row[2])
        series.current_turn = row[3]
        series.levels = pickle.loads(row[4])
        series.started = row[5]
        if series.started:
            series.current_game = get_game(token=token)
        series.game_tokens = pickle.loads(row[6])
        series.finished = row[7]
        series.winning_turn = row[8]


def update_series(series):
    player_names_blob = sqlite3.Binary(pickle.dumps(series.player_names))
    levels_blob = sqlite3.Binary(pickle.dumps(series.finished_players))
    game_tokens_blob = sqlite3.Binary(pickle.dumps(series.prev_comp))

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE games SET token = ?, player_names = ?, current_turn = ?, levels = ?, started = ?, game_tokens = ?, finished = ?, winning_turn = ? WHERE token = ?",
        (series.token, player_names_blob, series.current_turn, levels_blob, series.started,
         game_tokens_blob, series.finished, series.winning_turn, series.token),
    )
    conn.commit()
    cursor.close()


def store_series(series):
    player_names_blob = sqlite3.Binary(pickle.dumps(series.player_names))
    levels_blob = sqlite3.Binary(pickle.dumps(series.finished_players))
    game_tokens_blob = sqlite3.Binary(pickle.dumps(series.prev_comp))
    try:
        cursor = conn.cursor()
        # Insert the game into the table
        cursor.execute('''
            INSERT INTO series (token, player_names, current_turn, levels, started, game_tokens, finished, winning_turn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            series.token, player_names_blob, series.current_turn, levels_blob, series.started,
            game_tokens_blob, series.finished, series.winning_turn))
        conn.commit()
        cursor.close()
    except sqlite3.IntegrityError:
        return -1

    return 0


fetch_cursor = conn.cursor()


@cache.memoize(20)  # cache for 20 seconds
def get_game(token):
    # Open the file in read binary mode
    fetch_cursor.execute('''
        SELECT * FROM games
        WHERE token = ?
    ''', (token,))
    row = fetch_cursor.fetchone()

    if row is None:
        return None
    else:
        game = Game(
            level=row[1],
            token=row[2]
        )
        # Make sure that now is not a tuple
        if isinstance(row[3], tuple):
            # If now is a tuple, get the first element (which should be a datetime object)
            game.expiration_time = datetime.datetime.strptime(
                row[3][0], "%Y-%m-%d %H:%M:%S")
        else:
            game.expiration_time = datetime.datetime.strptime(
                row[3], "%Y-%m-%d %H:%M:%S")

        game.current_player = row[4]
        game.prev_comp = pickle.loads(row[5])
        game.fold_num = row[6]
        game.winner = row[7]
        game.started = row[8]
        game.paused = row[9]
        game.finished = row[10]
        game.ongoing_players = pickle.loads(row[11])
        game.player_names = pickle.loads(row[12])
        game.finished_players = pickle.loads(row[13])
        game.player_cards = pickle.loads(row[14])
        game.player_comps = pickle.loads(row[15])
        return game


def update_game(game):
    cache.delete_memoized(get_game, game.token)
    ongoing_players_blob = sqlite3.Binary(pickle.dumps(game.ongoing_players))
    player_names_blob = sqlite3.Binary(pickle.dumps(game.player_names))
    finished_players_blob = sqlite3.Binary(pickle.dumps(game.finished_players))
    prev_comp_blob = sqlite3.Binary(pickle.dumps(game.prev_comp))
    player_cards_blob = sqlite3.Binary(pickle.dumps(game.player_cards))
    player_comps_blob = sqlite3.Binary(pickle.dumps(game.player_comps))
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE games SET level = ?, token = ?, expiration_time = ?, current_player = ?, prev_comp = ?, fold_num = ?, winner = ?, started = ?, paused = ?, finished = ?, ongoing_players = ?, player_names = ?, finished_players = ?, player_cards = ?, player_comps = ? WHERE token = ?",
        (game.level, game.token, game.expiration_time.strftime("%Y-%m-%d %H:%M:%S"), game.current_player, prev_comp_blob, game.fold_num,
         game.winner, game.started, game.paused, game.finished, ongoing_players_blob, player_names_blob, finished_players_blob, player_cards_blob, player_comps_blob, game.token),
    )
    conn.commit()
    cursor.close()


@app.route('/end_game/<token>', methods=['POST'])
@cross_origin()
def end_game(token):
    n_game = fetch_cursor.execute(
        "select count(token) from games where token = ?", (token, ))
    n_game = fetch_cursor.fetchone()[0]
    if int(n_game) > 0:
        fetch_cursor.execute(
            "UPDATE games SET paused = ? WHERE token = ?",
            (1, token))
        conn.commit()
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "No game with token" + token}), 400


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def check_game_room_expiration(cursor):
    # Get the current timestamp
    now = datetime.datetime.now()

    # Execute the SELECT statement to retrieve the games with expired expiration times
    cursor.execute("SELECT * FROM games WHERE expiration_time < ?",
                   (now.strftime("%Y-%m-%d %H:%M:%S"),))

    # Retrieve the rows from the cursor
    rows = cursor.fetchall()

    # Iterate over the rows and delete the expired games
    for row in rows:
        id = row[0]
        cursor.execute("DELETE FROM games WHERE id = ?", (id,))


if __name__ == "__main__":
    expiration_check_thread = threading.Thread(
        target=check_game_room_expiration, args=(conn.cursor(),))
    expiration_check_thread.daemon = True
    expiration_check_thread.start()

    # Run the Flask application
    app.run()
