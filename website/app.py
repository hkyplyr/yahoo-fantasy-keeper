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

class Draft(db.Model):
    __tablename__ = 'draft'

    player_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    team_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))
    pick = db.Column(db.Integer)
    round = db.Column(db.Integer)

db.create_all()
db.session.commit()

@app.route('/')
def index():
    teams = Team.query.all()
    return render_template('index.html', teams=teams)

@app.route('/draft')
def draft():
    players = Draft.query.order_by(Draft.pick.asc()).all()
    teams = Team.query.all()
    return render_template('draft.html', teams=teams, players=players)

if __name__ == '__main__':
    app.run(debug=True)