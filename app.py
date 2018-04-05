from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://paquette@localhost/paquette')
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

class Team(db.Model):
    __tablename__ = 'teams'

    team_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(30))
    manager = db.Column(db.String(30))

class Player(db.Model):
    __tablename__ = 'players'

    player_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    status = db.Column(db.String(4))
    nhl_team = db.Column(db.String(3))
    number = db.Column(db.Integer)
    position = db.Column(db.String(7))

class Draft(db.Model):
    __tablename__ = 'draft'

    player_id = db.Column(db.Integer, db.ForeignKey(Player.player_id), primary_key=True, autoincrement=False)
    team_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))
    pick = db.Column(db.Integer)
    round = db.Column(db.Integer)

class Ownership(db.Model):
    __tablename__ = 'ownership'

    player_id = db.Column(db.Integer, db.ForeignKey(Player.player_id), primary_key=True, autoincrement=False)
    team_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))

class Pick(db.Model):
    __tablename__ = 'picks'

    original_id = db.Column(db.Integer, db.ForeignKey(Team.team_id), primary_key=True, autoincrement=False)
    draft_round = db.Column(db.Integer, primary_key=True, autoincrement=False)
    owner_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))

db.create_all()
db.session.commit()

@app.route('/')
def index():
    teams = Team.query.all()
    return render_template('index.html', teams=teams)

@app.route('/draft/<clazz>')
def draft(clazz):
    players = Player.query.join(Draft).add_columns(Player.player_id, Player.first_name, Player.last_name, Draft.team_id, Player.position, Player.nhl_team).order_by(Draft.pick.asc())
    teams = Team.query.all()
    return render_template('draft.html', teams=teams, players=players, clazz=clazz)

@app.route('/teams/<team_id>')
def team(team_id):
    team_id = int(team_id)
    if team_id > 10:
        abort(404)
    players = Player.query.join(Ownership).join(Draft).add_columns(Player.position, Player.first_name, Player.last_name, Player.nhl_team, Player.number, Draft.round).filter(Ownership.team_id == team_id).order_by(Draft.pick.asc())
    teams = Team.query.all()
    picks = Pick.query.filter(Pick.owner_id == team_id).order_by(Pick.draft_round.asc())
    return render_template('team.html', players=players, teams=teams, team_id=team_id-1, picks=picks)

if __name__ == '__main__':
    app.run(debug=True)