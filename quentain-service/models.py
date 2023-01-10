import datetime
import sqlalchemy as sa
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
sys.path.append('../')
import quentain
from app import app, db

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "400 per minute"],
    storage_uri="memory://",
)
# A single game with four players

class Game(db.Model):
    '''
    A single game model for quentain
    '''
    id = sa.Column(sa.Integer, sa.Identity(start=0, cycle=True), primary_key=True)
    token = sa.Column(sa.String(8), index=True, unique=True)
    expiration_time = sa.Column(
        sa.DateTime, index=True, default=datetime.datetime.utcnow)
    level = sa.Column(sa.Integer)
    current_player = sa.Column(sa.Integer)
    prev_comp = sa.Column(sa.PickleType)
    fold_num = sa.Column(sa.Integer)
    winner = sa.Column(sa.Integer)
    started = sa.Column(sa.Integer)
    finished = sa.Column(sa.Integer)
    ongoing_players = sa.Column(sa.PickleType)
    player_names = sa.Column(sa.PickleType)
    finished_players = sa.Column(sa.PickleType)
    player_cards = sa.Column(sa.PickleType)

    def __repr__(self):
        return '<Game {}>'.format(self.token)


def store_game(game: quentain.Game):
    # Convert the ongoing_players, player_names, and player_cards attributes to strings
    game_model = Game(
        token=game.token, expiration_time=datetime.datetime.now() + datetime.timedelta(minutes=5), level=game.level, current_player=game.current_player, prev_comp=game.prev_comp,
        fold_num=game.fold_num, winner=game.winner, started=game.started, finished=game.finished, ongoing_players=game.ongoing_players,
        player_names=game.player_names, finished_players=game.finished_players, player_cards=game.player_cards
    )
    try:
        with app.app_context():
            db.session.add(game_model)
            db.session.commit()
        return 0
    except Exception as e:
        print(e)
        import time
        time.sleep(10)
        return -1


def get_game(token: str):
    game = None
    with app.app_context():
        game_model = db.session.execute(db.select(Game).where(Game.token==token)).scalar()

        game = quentain.Game(
            level=game_model.level,
            token=game_model.token
        )
        game.current_player = game_model.current_player
        game.prev_comp = game_model.prev_comp
        game.fold_num = game_model.fold_num
        game.winner = game_model.winner
        game.started = game_model.started
        game.finished = game_model.finished
        game.ongoing_players = game_model.ongoing_players
        game.player_names = game_model.player_names
        game.finished_players = game_model.finished_players
        game.player_cards = game_model.player_cards
    return game


def update_game(game: quentain.Game):
    with app.app_context():
        game_model = db.session.execute(db.select(Game).where(Game.token==game.token)).scalar()
        game_model.current_player = game.current_player
        game_model.prev_comp = game.prev_comp
        game_model.fold_num = game.fold_num
        game_model.player_cards = game.player_cards

        db.session.commit()


def update_game_player(game: quentain.Game):
    with app.app_context():
        game_model = db.session.execute(db.select(Game).where(Game.token==game.token)).scalar()
        game_model.player_names = game.player_names
        player_number = len(game.player_names)
        if (player_number == 4):
            game_model.started = True

        db.session.commit()


with app.app_context():
    db.create_all()