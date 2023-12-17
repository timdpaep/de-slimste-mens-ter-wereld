import json
import time

# Flask stuff
from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio

from flask import current_app

from threading import Event

thread_event = Event()
thread = None

namespace = ""

@socketio.on('connect', namespace=namespace)
def io_connect():
	print("Client connected")
	broadcast_state()
	
def broadcast_state():
	global thread

	game = current_app.config["game"]

	# Stop countdown-to-zero timer if it changed automatically
	if not game.timer_running:
		if thread is not None:
			thread_event.clear()

	socketio.emit("state", game.as_dict())

def broadcast_video(video_filename):
	socketio.emit("video", video_filename)

@socketio.on('start_game', namespace=namespace)
def io_start_game():
	game = current_app.config["game"]

	game.start_game()
	broadcast_state()

@socketio.on('advance', namespace=namespace)
def io_advance():
	game = current_app.config["game"]
	
	game.advance()
	broadcast_state()

@socketio.on('advance_round', namespace=namespace)
def io_advance_round():
	game = current_app.config["game"]
	
	game.advance_round()
	broadcast_state()

@socketio.on('advance_subround', namespace=namespace)
def io_advance_subround():
	game = current_app.config["game"]
	
	game.advance_subround()
	broadcast_state()

@socketio.on('release_advance', namespace=namespace)
def io_release_advance():
	game = current_app.config["game"]
	
	to_release = game.release_advance()

	if to_release == "video":
		broadcast_video(game.current_question["video"])

	broadcast_state()

@socketio.on('answer_correct', namespace=namespace)
def io_answer_correct(answer_value):
	game = current_app.config["game"]
	
	print("Received answer:", answer_value)
	points_awarded = game.answer_correct(answer_value)
	socketio.emit("points_awarded", points_awarded)
	broadcast_state()

@socketio.on('answer_pass', namespace=namespace)
def io_answer_pass():
	game = current_app.config["game"]
	
	print("Received answer pass")
	game.answer_pass()
	broadcast_state()

@socketio.on('clock_start', namespace=namespace)
def io_clock_start():
	global thread

	game = current_app.config["game"]
	socketio.emit("clock_start")

	# Add a socket IO background task in the Finale round
	# Yes, I have to do this outside the game logic because socket io is stupid
	# Don't ask, I spent way too much time getting this to work
	if thread is None and game.current_round_text == "Finale":
		thread_event.set()
		# We start a background task which will run continuously while the clock is running
		thread = socketio.start_background_task(timeout, thread_event, game)

	game.clock_start()
	broadcast_state()

def timeout(event, game):
	global thread

	# How long should we wait until the game ends?
	seconds_loop = game.active_player.points

	try:
		# Keep alive while seconds are positive and timer is running
		while seconds_loop > 0 and event.is_set():
			socketio.sleep(1)

			# State can have changed during sleep
			if not event.is_set():
				break

			# Sleep tick
			seconds_loop -= 1
			print("Tick", seconds_loop)
	
		# Do not end game if event is cancelled prematurely
		if seconds_loop > 0:
			thread = None
			event.clear()
			return

		# Else, declare a winner
		game.timeout()
		socketio.emit("state", game.as_dict())
		event.clear()
		thread = None
	except:
		pass

@socketio.on('clock_stop', namespace=namespace)
def io_clock_stop():
	game = current_app.config["game"]
	socketio.emit("clock_stop")

	# Cancel Finale timer if there is one
	global thread
	if thread is not None:
		thread_event.clear()

	game.clock_stop()
	broadcast_state()

@socketio.on('clock_toggle', namespace=namespace)
def io_clock_toggle():
	game = current_app.config["game"]
	
	if not game.timer_running:
		io_clock_start()
	else:
		io_clock_stop()

@socketio.on('open_deur_choose', namespace=namespace)
def io_open_deur_choose(questioneer_index):
	game = current_app.config["game"]
	
	print("Received Open deur choice:", questioneer_index)
	video_filename = game.open_deur_choose(questioneer_index)

	broadcast_state()

	if video_filename:
		broadcast_video(video_filename)