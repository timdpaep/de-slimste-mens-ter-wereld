import os
import random

from flask import session, redirect, url_for, render_template, request, send_file
from . import main

from flask import current_app

@main.route('/')
def landing():
	return render_template('landing.html', global_questions_directory=current_app.config["questions_directory"])

@main.route('/host')
def host(callback=None):
	return render_template('game.html', host=True)

@main.route('/player')
def player(callback=None):
	return render_template('game.html', host=False)

@main.route('/resources/<string:filename>')
def display_label_image(filename):
	global_questions_directory = current_app.config["questions_directory"]

	if not os.path.isabs(global_questions_directory):
		path = os.path.join("..", global_questions_directory, filename)
	else:
		path = os.path.join(global_questions_directory, filename)

	return send_file(path)