from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
import requests

##app and local db config
app = Flask(__name__)

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

## external api chess endpoints
external_endpoints = {
	'create_game': 'http://chess-api-chess.herokuapp.com/api/v1/chess/two',
	'possible_moves': 'http://chess-api-chess.herokuapp.com/api/v1/chess/two/moves',
	'check_game': 'http://chess-api-chess.herokuapp.com/api/v1/chess/two/check',
	'current_status': 'http://chess-api-chess.herokuapp.com/api/v1/chess/two/fen'
}


##models
class ChessGame(db.Model):
    id = db.Column(db.Unicode, primary_key=True)
    players = db.relationship('Player',backref='player')
    moves = db.relationship('Move',backref='moves')
    possible_moves = db.relationship('PossibleMove', backref='possible_moves')

    def __repr__(self):
        return '<ChessGame: {}>, CurrentPlayers: {}'.format(self.id,self.players)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    game_id = db.Column(db.Unicode, db.ForeignKey(ChessGame.id))
    password = db.Column(db.String)

    def __repr__(self):
        return '<Player: {}, CurrentGame: {}>'.format(self.name,self.game_id)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

class PossibleMove(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    game_id = db.Column(db.Unicode, db.ForeignKey(ChessGame.id))
    source_position = db.Column(db.String)
    target_position = db.Column(db.String)
    
    def __repr__(self):
        return '<PossibleMove: {}>'.format(self.id)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    game_id = db.Column(db.Unicode, db.ForeignKey(ChessGame.id))
    source_position = db.Column(db.String)
    target_position = db.Column(db.String)
    
    def __repr__(self):
        return '<Move: {}>'.format(self.id)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj


## serialize schemes

class PlayerSchema(ma.Schema):
    class Meta:
        fields = ('id','name','game_id')

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)

class MoveSchema(ma.Schema):
    class Meta:
        fields = ('id', 'player_id', 'game_id','source_position','target_position')

move_schema = MoveSchema()
moves_schema = MoveSchema(many=True)

class PossibleMoveSchema(ma.Schema):
    class Meta:
        fields = ('id', 'player_id', 'game_id','source_position','target_position')

possible_move_schema = PossibleMoveSchema()
possible_moves_schema = PossibleMoveSchema(many=True)

class ChessGameSchema(ma.Schema):
    players = ma.Nested(players_schema, many=True)
    moves = ma.Nested(moves_schema, many=True)
    possible_moves = ma.Nested(possible_moves_schema, many=True)
    class Meta:
        fields = ('id','players', 'moves', 'possible_moves')

chess_game_schema = ChessGameSchema()
chess_games_schema = ChessGameSchema(many=True)





######### game endpoints ########

@app.route('/')
def index():
    return 'Welcome'

@app.route('/authenticate', methods=['POST'])
def authenticate():	
	username = request.args.get('username','')
	password = request.args.get('password','')
	if username != '' and password != '':
		player = Player.query.filter_by(name = username, password = password).first()
		return jsonify(player_schema.dump(player))

@app.route('/create-game', methods=['GET'])
def create_game():
	remote_request = requests.get(external_endpoints['create_game']).json()
	ChessGame.create(id=remote_request['game_id'])
	return jsonify(remote_request)

@app.route('/list-games', methods=['GET'])
def list_games():
	games = ChessGame.query.all()
	return jsonify(chess_games_schema.dump(games))

@app.route('/list-moves/<game_id>', methods=['GET'])
def list_moves(game_id):
	moves = Move.query.filter_by(game_id=game_id).all()
	return jsonify(moves_schema.dump(moves))

@app.route('/list-possible-moves/<game_id>', methods=['GET'])
def list_possible_moves(game_id):
	moves = PossibleMove.query.filter_by(game_id=game_id).group_by(PossibleMove.player_id).all()
	return jsonify(possible_moves_schema(moves))



@app.route('/clear_moves/<game_id>', methods=['GET'])
def clear_moves(game_id):
        game = ChessGame.query.filter_by(id=game_id).first()
        game.moves = []
        db.session.commit()
        return jsonify(chess_game_schema.dump(game))

@app.route('/game_status', methods=['POST'])
def game_status():
	data = {
		'game_id': request.args.get('game_id',''),
	}
	remote_request = requests.post(external_endpoints['current_status'],data).json()
	return jsonify(remote_request)

@app.route('/check_status', methods=['POST'])
def check_game():
	data = {
		'game_id': request.args.get('game_id',''),
	}
	remote_request = requests.post(external_endpoints['check_game'],data).json()
	return jsonify(remote_request)


######### player endpoints ########
@app.route('/players', methods=['GET'])
def player():
	players = Player.query.all()
	return jsonify(players_schema.dump(players))

@app.route('/enter_game', methods=['POST'])
def enter_game():
	game = ChessGame.query.filter_by(id=request.args.get('game_id','')).first()
	player = Player.query.filter_by(id=request.args.get('player_id','')).first()
	player.game_id = game.id
	db.session.commit()
	return jsonify(player_schema.dump(player))

@app.route('/exit_game', methods=['POST'])
def exit_game():
        player = Player.query.filter_by(id=request.args.get('player_id','')).first()
        player.game_id = ""
        db.session.commit()
        return jsonify(player_schema.dump(player))

@app.route('/possible_moves', methods=['POST'])
def possible_moves():
	data = {
		'game_id': request.args.get('game_id',''),
		'position': request.args.get('position','')
	}
	remote_request = requests.post(external_endpoints['possible_moves'], data)
	return jsonify(remote_request.json())

@app.route('/make_move', methods=['POST'])
def make_move():
	data = {
		'game_id': request.args.get('game_id',''),
		'player_id': request.args.get('player_id',''),
		'source_position': request.args.get('source_position',''),
		'target_position': request.args.get('target_position','')
	}
	new_move = Move.create(game_id=data['game_id'], player_id=data['player_id'], source_position=data['source_position'], target_position=data['target_position'])
	return jsonify(move_schema.dump(new_move))

@app.route('/make_possible_move', methods=['POST'])
def make_possible_move():
	data = {
		'game_id': request.args.get('game_id',''),
		'player_id': request.args.get('player_id',''),
		'source_position': request.args.get('source_position',''),
		'target_position': request.args.get('target_position','')
	}
	new_move = PossibleMove.create(game_id=data['game_id'], player_id=data['player_id'], source_position=data['source_position'], target_position=data['target_position'])
	return jsonify(possible_move_schema.dump(new_move))


if __name__ == '__main__':
	app.run(host='0.0.0.0')
