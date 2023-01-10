from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


# Initiate flask app
app = Flask(__name__)

import datetime
import os
import threading
from flask import Flask
import sqlite3
import sys
sys.path.append('../')
import quentain

# Initiate db connections
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
db.app = app

def check_game_room_expiration(cursor):
    # Get the current timestamp
    now = datetime.datetime.now()
    
    # Execute the SELECT statement to retrieve the games with expired expiration times
    cursor.execute("SELECT * FROM game WHERE expiration_time < ?", (now.strftime("%Y-%m-%d %H:%M:%S"),))

    # Retrieve the rows from the cursor
    rows = cursor.fetchall()

    # Iterate over the rows and delete the expired games
    for row in rows:
        id = row[0]
        cursor.execute("DELETE FROM game WHERE id = ?", (id,))

if __name__ == "__main__":
    from models import Game
    from routes import api
    with app.app_context():
        app.register_blueprint(api)
        CORS(app)
    # Run the Flask application
    app.run(port=5050)

    conn = sqlite3.connect("games.db", check_same_thread=False)
    daemon_cursor = conn.cursor()
    expiration_check_thread = threading.Thread(
        target=check_game_room_expiration, args=(daemon_cursor,))
    expiration_check_thread.daemon = True
    expiration_check_thread.start()


