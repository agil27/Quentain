from flask import Flask, jsonify, render_template, redirect, request, url_for
import datetime
import pickle
import random
import sqlite3
import string
import threading
from quentain.game import Game
import quentain
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

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
        finished INTEGER NOT NULL,
        ongoing_players BLOB NOT NULL,
        player_names BLOB NOT NULL,
        finished_players BLOB NOT NULL,
        player_cards BLOB NOT NULL
    )
''')
conn.commit()


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route('/new_game', methods=['POST'])
@cross_origin()
def new_game():
    status = -1
    while status != 0:
        # Create a new game in the database
        token = generate_token()
        data = request.get_json()
        # Extract the level from the data
        level = data.get("level")
        # Initialize the game with the player's name
        game = Game(level=level, token=token)
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
        return "Game not found", 404
    if game.token != token:
        return "Invalid token", 401

    # Add the player to the game in the database
    number = add_player_to_game(game)

    if number < 4:
        return jsonify({"player_number": number}), 200
    else:
        return "Room Full!", 401


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
        return jsonify({"current_player": game.current_player, "started": game.started,"game_state": game.get_game_state(game.current_player)}), 200
    else:
        return jsonify({"finished": game.finished, "rank": game.get_rank()}), 200


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


def store_game(game):
    # Convert the ongoing_players, player_names, and player_cards attributes to strings
    ongoing_players_blob = sqlite3.Binary(pickle.dumps(game.ongoing_players))
    player_names_blob = sqlite3.Binary(pickle.dumps(game.player_names))
    finished_players_blob = sqlite3.Binary(pickle.dumps(game.finished_players))
    prev_comp_blob = sqlite3.Binary(pickle.dumps(game.prev_comp))
    player_cards_blob = sqlite3.Binary(pickle.dumps(game.player_cards))
    try:
        # Insert the game into the table
        cursor.execute('''
            INSERT INTO games (level, token, expiration_time, current_player, prev_comp, fold_num, winner, started, finished, ongoing_players, player_names, finished_players, player_cards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            game.level, game.token, game.expiration_time.strftime("%Y-%m-%d %H:%M:%S"), game.current_player, prev_comp_blob,
            game.fold_num, game.winner, game.started, game.finished, ongoing_players_blob,
            player_names_blob, finished_players_blob, player_cards_blob
        ))
    except sqlite3.IntegrityError:
        return -1
    conn.commit()
    return 0


def get_game(token):
    # Open the file in read binary mode
    cursor.execute('''
        SELECT * FROM games
        WHERE token = ?
    ''', (token,))
    row = cursor.fetchone()
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
            game.expiration_time = datetime.datetime.strptime(row[3][0], "%Y-%m-%d %H:%M:%S")
        else:
            game.expiration_time = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")

        game.current_player = row[4]
        game.prev_comp = pickle.loads(row[5])
        game.fold_num = row[6]
        game.winner = row[7]
        game.started = row[8]
        game.finished = row[9]
        game.ongoing_players = pickle.loads(row[10])
        game.player_names = pickle.loads(row[11])
        game.finished_players = pickle.loads(row[12])
        game.player_cards = pickle.loads(row[13])
        return game


def update_game(game):
    ongoing_players_blob = sqlite3.Binary(pickle.dumps(game.ongoing_players))
    player_names_blob = sqlite3.Binary(pickle.dumps(game.player_names))
    finished_players_blob = sqlite3.Binary(pickle.dumps(game.finished_players))
    prev_comp_blob = sqlite3.Binary(pickle.dumps(game.prev_comp))
    player_cards_blob = sqlite3.Binary(pickle.dumps(game.player_cards))

    cursor.execute(
        "UPDATE games SET level = ?, token = ?, expiration_time = ?, current_player = ?, prev_comp = ?, fold_num = ?, winner = ?, started = ?, finished = ?, ongoing_players = ?, player_names = ?, finished_players = ?, player_cards = ? WHERE token = ?",
        (game.level, game.token, game.expiration_time.strftime("%Y-%m-%d %H:%M:%S"), game.current_player, prev_comp_blob, game.fold_num,
         game.winner, game.started, game.finished, ongoing_players_blob, player_names_blob, finished_players_blob, player_cards_blob, game.token),
    )
    conn.commit()


def check_game_room_expiration():
    # Get the current timestamp
    now = datetime.datetime.now()

    # Execute the SELECT statement to retrieve the games with expired expiration times
    cursor.execute("SELECT * FROM games WHERE expiration_time < ?", (now.strftime("%Y-%m-%d %H:%M:%S"),))

    # Retrieve the rows from the cursor
    rows = cursor.fetchall()

    # Iterate over the rows and delete the expired games
    for row in rows:
        id = row[0]
        cursor.execute("DELETE FROM games WHERE id = ?", (id,))


if __name__ == "__main__":
    expiration_check_thread = threading.Thread(
        target=check_game_room_expiration)
    expiration_check_thread.daemon = True
    expiration_check_thread.start()

    # Run the Flask application
    app.run()
