from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from operator import attrgetter
import requests

##app and local db config
app = Flask(__name__)

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

## external api chess endpoints
external_endpoints = {
        'create_game': 'http://chess-api-chess.herokuapp.com/api/v1/chess/one',
        'possible_moves': 'http://chess-api-chess.herokuapp.com/api/v1/chess/one/moves',
        'check_game': 'http://chess-api-chess.herokuapp.com/api/v1/chess/one/check',
        'current_status': 'http://chess-api-chess.herokuapp.com/api/v1/chess/one/fen',
        'make_move':'http://chess-api-chess.herokuapp.com/api/v1/chess/one/move/player',
        'ask_ai_to_move': 'http://chess-api-chess.herokuapp.com/api/v1/chess/one/move/ai'
}


##models
class ChessGame(db.Model):
    id = db.Column(db.Unicode, primary_key=True)
    players = db.relationship('Player',backref='player')
    moves = db.relationship('Move',backref='moves')
    possible_moves = db.relationship('PossibleMoves', backref='ref_possible_moves_list')
    votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<ChessGame: {}>, CurrentPlayers: {}'.format(self.id,self.players)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj


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
        return obj


class PossibleMoves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moves = db.relationship('Move',backref='ref_possible_moves')
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    game_id = db.Column(db.Unicode, db.ForeignKey(ChessGame.id))
    votes = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<ListOfPossibleMoves: {}>'.format(self.id)

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
    list_id = db.Column(db.Integer, db.ForeignKey(PossibleMoves.id))
    
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
        fields = ('id', 'game_id','source_position','target_position')

move_schema = MoveSchema()
moves_schema = MoveSchema(many=True)

class PossibleMovesSchema(ma.Schema):
    moves = ma.Nested(moves_schema, many=True)
    class Meta:
        fields = ('id','player_id', 'moves', 'votes')

possible_moves_schema = PossibleMovesSchema()
possible_movess_schema = PossibleMovesSchema(many=True)


class ChessGameSchema(ma.Schema):
    players = ma.Nested(players_schema, many=True)
    moves = ma.Nested(moves_schema, many=True)
    possible_moves = ma.Nested(possible_movess_schema, many=True)
    class Meta:
        fields = ('id','players', 'moves', 'possible_moves', 'votes')

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
        new_game = ChessGame.create(id=remote_request['game_id'])
        return jsonify(chess_game_schema.dump(new_game))

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
        moves = PossibleMoves.query.filter_by(game_id=game_id).all()
        return jsonify(possible_movess_schema.dump(moves))

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
        game = ChessGame.query.filter_by(id=player.game_id).first()
        player.game_id = ""
        db.session.commit()
        if len(game.players) == 0:
            db.session.delete(game)
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
                'list_id' : request.args.get('list_id',''),
                'source_position': request.args.get('source_position',''),
                'target_position': request.args.get('target_position','')
        }
        new_move = Move.create(list_id=data['list_id'], player_id=data['player_id'], source_position=data['source_position'], target_position=data['target_position'])
        return jsonify(move_schema.dump(new_move))

@app.route('/make_possible_move_list', methods=['POST'])
def make_possible_move_list():
        data = {
                'game_id': request.args.get('game_id',''),
                'player_id': request.args.get('player_id',''),
        }
        new_list = PossibleMoves.create(game_id=data['game_id'], player_id=data['player_id'])
        return jsonify(possible_moves_schema.dump(new_list))

@app.route('/vote', methods = ['POST'])
def vote():
        data = {
                'list_id': request.args.get('list_id'),
                'game_id': request.args.get('game_id')    
        }
        list_to_vote = PossibleMoves.query.filter_by(id=data['list_id']).first()
        list_to_vote.votes += 1
        current_game = ChessGame.query.filter_by(id=data['game_id']).first()
        current_game.votes += 1

        if current_game.votes == len(current_game.players):
            winner_list = max(current_game.possible_moves, key=attrgetter('votes'))
            current_game.moves += winner_list.moves
            current_game.votes = 0

            # now we have to send the winner list moves to remote api chess, and get the new move by the AI 

            move_data = {
                'game_id': current_game.id,
                'from': winner_list.moves[0].source_position,
                'to': winner_list.moves[0].target_position
            }
            db.session.delete(winner_list)
            remote_request = requests.post(external_endpoints['make_move'], move_data)
            ai_data = {
                'game_id': current_game.id,
            }
            if remote_request.status_code == 200:
                remote_request = requests.post(external_endpoints['ask_ai_to_move'], ai_data).json()
                new_ai_move = Move.create(game_id=current_game.id, source_position=remote_request['from'],\
                 target_position=remote_request['to'])
        db.session.commit()
        return

if __name__ == '__main__':
        app.run(host='0.0.0.0')
