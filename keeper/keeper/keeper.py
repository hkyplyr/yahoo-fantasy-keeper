import os
import sqlite3

from flask import Flask, render_template,g
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'draft.db'),
    SECRET_KEY='secret!',
    USERNAME='admin',
    PASSWORD='default'
))
socketio = SocketIO(app, async_mode=async_mode)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.cli.command('initdb')
def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Initialized the database.')


@app.cli.command('keepers')
def update_keepers():
    """Updates the `draft` database with `keeper` information."""
    db = get_db()
    cur = db.execute('select pick, player from keeper')
    keepers = cur.fetchall()
    for keeper in keepers:
        db.execute('insert into draft (pick, player) values (?, ?)', [keeper['pick'], keeper['player']])
    db.commit()
    print('Updated the keepers.')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


def check_pick_used(pick):
    db = get_db()
    cur = db.execute('select * from draft where pick=?', [pick])
    return cur.fetchone() is None


def increment_pick(pick):
    db = get_db()
    cur_pick = pick
    while check_pick_used(cur_pick) is False:
        cur_pick += 1
    db.execute('update current_pick set pick=? where id=1', [cur_pick])
    db.commit()


def get_current_pick():
    db = get_db()
    cur = db.execute('select pick from current_pick')
    return cur.fetchone()['pick']


def add_player_to_db(pick, player):
    db = get_db()
    db.execute('insert into draft (pick, player) values (?,?)', [pick, player])
    db.commit()


@socketio.on('draft_event')
def draft_event(player):
    # Get the current pick, where to insert the new player.
    current_pick = get_current_pick()
    # Insert the player into the given pick.
    add_player_to_db(current_pick, player['data'])
    # Increment the pick to the next open.
    increment_pick(current_pick)
    # Add the player to every client's draft board.
    emit('draft_player', {'player': player, 'pick': current_pick}, broadcast=True)


def convert_to_draft_map(draft_data):
    draft_map = {}
    for row in draft_data:
        draft_map[row['pick']] = row['player']
    return draft_map


def update_draft_board():
    db = get_db()
    cur = db.execute('select pick, player from draft')
    picks = cur.fetchall()
    # Convert the result to a serializable format.
    draft_map = convert_to_draft_map(picks)
    # Update every client's draft board.
    emit('update_board', draft_map)


@socketio.on('connect')
def connect():
    update_draft_board()


if __name__ == '__main__':
    socketio.run(app, debug=True)
