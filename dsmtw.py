# dsmtw
# by Anthe Sevenants
# started on 2022-12-03
# 100% functional on 2022-12-13
# based on the 2016 version in PHP


from flask_socketio import SocketIO
import argparse

from app import create_app, socketio


#
# Arguments
#

parser = argparse.ArgumentParser(description='Play De Slimste Mens Ter Wereld')
parser.add_argument('function', type=str,
					help='listen')
parser.add_argument('questions_directory', type=str,
					help='tafelquiz')
parser.add_argument('player_names', type=str,
					help='list of the player names, separated by commas')

args = parser.parse_args();

if args.function == "listen":
	player_names = args.player_names.split(",")

	app = create_app(args.questions_directory, player_names, debug=True)
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True

	socketio.run(app, port=10965, debug=True)