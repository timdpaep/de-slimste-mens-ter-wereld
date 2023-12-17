from flask import Flask
from flask_socketio import SocketIO
from erik.dsmtw import DeSlimsteMens

socketio = SocketIO()

def create_app(questions_directory, player_names, debug=False):
	global global_questions_directory # it's bad but at least I know it's bad
	global global_player_names

	"""Create an application."""
	app = Flask(__name__)
	app.debug = debug
	app.config['SECRET_KEY'] = 'miep'
	app.config['questions_directory'] = questions_directory
	app.config['game'] = DeSlimsteMens(player_names, questions_directory)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint, url_prefix='')

	socketio.init_app(app)
	return app