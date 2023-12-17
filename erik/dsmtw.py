import json
import os.path
import random
import time

from gameshow.gameshow import Gameshow

class DeSlimsteMens(Gameshow):
	def __init__(self, players, questions_directory, finale_rules=True):
		rounds = [ "3-6-9", "Open deur", "Puzzel", "Galerij", "Collectief geheugen",
				   "Finale" ]

		no_players = len(players)

		super().__init__("De Slimste Mens Ter Wereld", rounds, no_players)

		self.settings = { "369_round_no": 15,
						  "Galerij_round_no": 10 }

		self.questions = [ [] for round_text in rounds ]

		self.load_questions(questions_directory)

		# Start off by setting the current question to the first question
		# This, of course, assumes we're starting in 3-6-9
		self.set_current_question(0)
		# Available questions will be used for Open deur, since there, a player
		# is free to choose whichever question they want
		self.available_questions = []

		# Used to signal whether it's time to answer a specific question
		self.answer_time = False

		# The leftmost player should start
		self.set_active_player(0)
		self.reset_turn_history(save_latest_player=False)

		# Let's award 60 seconds to every player, which they'll need in the game
		# ...and maybe also in the finals!
		for i, player in enumerate(players):
			self.players[i].name = player
			self.players[i].points = 60
			self.players[i].finalist = False

		# Keep track of whether we're playing with the finale episode rules
		self.finale_rules = finale_rules

		# Seconds clock
		self.timer_running = False

		# Keep track of what state the game should advance in
		# Instead of immediately advancing the game when all answers have been
		# given / no turns are left / there are no more subrounds, we hold the current
		# screen for a little longer so the host can still review the answers.
		self.to_advance = None

		# Only show the clock toggle on the client when necessary
		self.clock_visible = False

		# Player with last turn
		# Important for ex aequo scores in the Finale round
		self.last_player_index = 1

	# 
	# Turn taking
	# 

	# We use the turn history to keep track of which players have already had a guess
	# in this specific subround. This allows game-crucial mechanics such as keeping track
	# of who can complement an answer first
	def reset_turn_history(self, save_latest_player=True):
		if save_latest_player:
			if len(self.turn_history) > 0:
				self.last_player_index = self.turn_history[-1]

		self.turn_history = []

	# The same as above, but for EXTERNAL turns
	def reset_player_history(self):
		self.player_history = []

	# Add the index of the current player to the turn history
	def add_current_player_to_turn_history(self):
		self.turn_history.append(self.active_player_index)

	# Which answers have already been found?
	# Saves the indices!
	def reset_answers_found(self):
		self.answers_found = []

	# Do simple turn advancement which is not based on seconds
	# Only used in 3-6-9
	# Turns will advance "simply" from 1 -> 2 -> 3 etc.
	def advance_turn_simply(self):
		if len(self.turn_history) == self.no_players:
			# Give the turn back to the first player if this turn
			self.set_active_player(self.turn_history[0])
			# Then advance the subround
			# This must be done *after* setting the active player, because
			# advancing the subround empties the turn history
			self.to_advance = "subround"
			return

		# If we need to advance the turn, but we need to "wrap" to the first player
		if self.turn_history[-1] == self.no_players - 1:
			self.set_active_player(0)
		# We get the last player, and we add 1 to get the "next" player
		else:
			self.set_active_player(self.turn_history[-1] + 1)

	# Do logical turn advancement based on seconds
	# The player with the fewest seconds who did not already have a go takes the turn
	def advance_turn_logically(self, history=None):
		# "history" can either be the EXTERNAL turn history or the INTERNAL turn history
		if history is None:
			history = self.turn_history

		current_lowest_score = float('inf')
		next_player_index = None
		# Loop over all players and find out which player conforms to our conditions
		for player_index, player in enumerate(self.players):
			# Ignore player if Finale and not a finalist
			if self.current_round_text == "Finale" and not player.finalist:
				continue

			# Both finalist scores are equal
			if self.current_round_text == "Finale" and player.points == current_lowest_score \
				and self.current_subround != 0:
				# Give the turn to the player who had the turn last
				next_player_index = self.last_player_index
				print("Special Finale turn logic")
				break

			if player.points < current_lowest_score and player_index not in history:
				current_lowest_score = player.points
				next_player_index = player_index

		# Set this player as the current active player, and add them to the history
		self.set_active_player(next_player_index)
		history.append(next_player_index)

	# 
	# Round flow
	# 

	# Advance round
	def advance_round(self):
		super().advance_round()
		
		# Player history 
		self.reset_player_history()
		self.reset_turn_history()

		# Show client clock for all rounds except 3-6-9
		if self.current_round_text != "3-6-9":
			self.clock_visible = True

		# Finale
		# Needs to come before general advance, else no finalists will be found
		if self.current_round_text == "Finale":
			self.prepare_finale()

		self.general_advance()

		# Open deur only
		if self.current_round_text == "Open deur":
			# Broadcast the available questioneers
			self.set_available_questions()
	# Advance the subround, and clear the turn history
	def advance_subround(self):
		self.reset_turn_history()

		if self.current_round_text == "Finale":
			# Player history is reset over subrounds in the Finale round as well
			self.reset_player_history()

		if self.current_round_text == "Galerij" and self.overview == False:
			self.reset_galerij_index()
			self.overview = True
			return

		# Find the end of a round
		# The conditions differ based on the current round
		if self.current_round_text == "3-6-9":
			if self.current_subround == self.settings["369_round_no"] - 1:
				self.advance_round()
				return
		elif self.current_round_text in [ "Open deur", "Puzzel", "Galerij",
										  "Collectief geheugen" ]:
			if self.current_subround == self.no_players - 1:
				self.advance_round()
				return

			# We have to reset the current question, else the questioneer face will
			# remain visible on the screen
			self.current_question = None

		super().advance_subround()

		self.general_advance()

		# If answer time is True, the question has been asked and answering is allowed
		self.answer_time = False

	# Logic shared by round advance and subround advance
	def general_advance(self):
		# We reset the found answers
		self.reset_answers_found()

		# Does NOT apply to Open deur, because the question order is free for this round
		if self.current_round_text in [ "3-6-9", "Puzzel", "Galerij", "Collectief geheugen",
										"Finale" ]:
			# We prepare the question corresponding to the index of the 
			# current subround. E.g. subround 0 <=> question 0 etc.
			self.set_current_question(self.current_subround)

		# The following rounds use second-based logic to determine whose turn it is
		if self.current_round_text in [ "Open deur", "Puzzel", "Galerij", "Collectief geheugen",
										"Finale" ]:
			# Player with the least seconds can start
			# We decide on the GLOBAL turn first (*not* complement turns)
			self.advance_turn_logically(history=self.player_history)
			# Then, we set the INTERNAL turn (= same turn used for complement turns)
			# We cannot ask to advance the turn logically for the turn history, 
			# because we will get a different result and it'll ruin our day
			self.turn_history.append(self.active_player_index)

		# Galerij only
		if self.current_round_text == "Galerij":
			# Galerij always has an overview part to each subround
			# In this overview part, all images are reviewed
			# At the start of the round, set the overview to False
			self.overview = False

			# Keep track of what image we're currently looking at
			self.reset_galerij_index()

		# Collectief geheugen only
		if self.current_round_text == "Collectief geheugen":
			# Make a "wait" state so the video can start
			self.to_advance = "video"
			# Keep track of in what order seconds were awarded
			self.awarded_seconds = []

	def set_current_question(self, question_no):
		# Puzzel round has specific question logic
		if self.current_round_text == "Puzzel":
			self.set_current_question_puzzle(self.current_subround)
			return

		self.current_question = self.questions[self.current_round][question_no]

	# Used only in Open deur because question order is free there
	def set_available_questions(self):
		self.available_questions = self.questions[self.current_round]
		self.question_history = []

	# Used to *actually* advance after host review
	def release_advance(self):
		to_return = False

		if self.to_advance == "subround":
			self.to_advance = None
			self.advance_subround()
		elif self.to_advance == "round":
			self.to_advance = None
			self.advance_round()
		elif self.to_advance == "video":
			self.to_advance = None
			to_return = "video"

		return to_return

	# 
	# Clock
	#

	def clock_start(self):
		print("Timer started")
		self.timer_start = time.time()
		self.timer_running = True

	def clock_stop(self, pass_turn=True):
		print("Timer halted")
		# Deduct the amount of seconds that have passed since timer was started
		self.active_player.points -= round(time.time() - self.timer_start)
		self.timer_running = False

		if pass_turn:
			self.answer_pass()

	#
	# Answering
	# 

	def answer_correct(self, answer_value):
		if self.current_round_text == "3-6-9":
			points_awarded = self.handle_369_answer_correct()
			return points_awarded
		elif self.current_round_text == "Open deur":
			points_awarded = 20
			self.handle_list_answer_correct(answer_value, points_awarded)
		elif self.current_round_text == "Puzzel":
			points_awarded = 30
			self.handle_list_answer_correct(answer_value, points_awarded)
		elif self.current_round_text == "Galerij":
			points_awarded = 10
			self.handle_list_answer_correct(answer_value, points_awarded)

			# Only advance if the primary player is answering
			if len(self.turn_history) == 1:
				self.advance_galerij()
		elif self.current_round_text == "Collectief geheugen":
			# Point allocation for Collectief geheugen is dynamic
			# Offset by one is needed because the answer still needs to be registered
			points_awarded = 10 * (len(self.answers_found) + 1)

			self.awarded_seconds.append(points_awarded)
			self.handle_list_answer_correct(answer_value, points_awarded)
		elif self.current_round_text == "Finale":
			points_awarded = 20
			self.handle_list_answer_correct(answer_value, points_awarded)

		return points_awarded

	def answer_pass(self):
		if self.current_round_text == "3-6-9":
			self.handle_369_answer_pass()
			return
		elif self.current_round_text in [ "Open deur", "Puzzel", "Collectief geheugen", "Finale" ]:
			self.handle_list_answer_pass()
			return
		elif self.current_round_text == "Galerij":
			# Only advance if the primary player is answering
			# If we're in the overview stage, "pass" should just mean skip
			if len(self.turn_history) == 1 or self.overview:
				self.advance_galerij()
			else:
				self.handle_list_answer_pass()
			return

	def award_seconds(self, seconds):
		self.active_player.points += seconds

	def deduct_seconds(self, seconds):
		# We get the index of the target player by...
		# - getting the index of the current player
		# - then getting the index of the only other player in that list
		target_player_index = abs(self.finalist_player_indices.index(self.active_player_index) - 1)
		target_player_index = self.finalist_player_indices[target_player_index]

		self.players[target_player_index].points -= seconds

		if self.players[target_player_index].points <= 0:
			self.clock_stop()
			self.players[target_player_index].points = 0
			self.end_game()

	def handle_list_answer_correct(self, answer_index, awarded_seconds):
		if answer_index in self.answers_found:
			print("Could not register answer; answer already found")
			return False

		# Add answer to found answer list
		self.answers_found.append(answer_index)

		if self.current_round_text != "Finale":
			self.award_seconds(awarded_seconds)
		# In Finale, we remove seconds
		else:
			self.deduct_seconds(awarded_seconds)

		if len(self.answers_found) == len(self.current_question["answers"]):
			self.clock_stop(pass_turn=False)
			self.to_advance = "subround"

	def handle_list_answer_pass(self):
		print("Turn history", self.turn_history)

		# If no one is left to guess, move on to the next questioneer choice
		if (len(self.turn_history) == self.no_players) or \
			(self.current_round_text == "Finale" and len(self.turn_history) == 2):
			print("Player count", self.no_players)

			self.to_advance = "subround"
			return

		self.advance_turn_logically()

	# 
	# 3-6-9
	#

	def handle_369_answer_correct(self):
		points_awarded = None

		# If this is the third question in 3-6-9, award 10 seconds
		if (self.current_subround + 1) % 3 == 0:
			points_awarded = 10
			self.award_seconds(points_awarded)

		# Then, move on to the next question
		self.to_advance = "subround"

		return points_awarded

	def handle_369_answer_pass(self):
		self.add_current_player_to_turn_history()
		self.advance_turn_simply()


	# 
	# Open deur
	#

	def open_deur_choose(self, questioneer_index):
		if questioneer_index in self.question_history:
			print("Could not choose Open deur question; question was already asked")
			return False

		self.set_current_question(questioneer_index)
		self.question_history.append(questioneer_index)
		self.answer_time = True

		return self.current_question["video"]

	#
	# Puzzel
	# 

	def set_current_question_puzzle(self, puzzle_index):
		# Always three questions for each puzzle
		start_index = puzzle_index * 3
		end_index = start_index + 3

		# We get the questions
		picked_questions = self.questions[self.current_round][start_index:end_index]

		picked_keywords = []
		picked_answer_indices = []
		picked_answers = []
		for index, picked_question in enumerate(picked_questions):
			# Extract the keywords
			picked_keywords += picked_question["keywords"]
			# Repeat four times, because each keyword corresponds to the same answer
			# We save the answer indices, not the answers themselves
			picked_answer_indices += [ index ] * 4

			# Also save the answers themselves (to display them)
			picked_answers.append(picked_question["answer"])

		keywords_with_indices = list(zip(picked_keywords, picked_answer_indices))
		random.shuffle(keywords_with_indices)

		picked_keywords, picked_answer_indices = zip(*keywords_with_indices)

		self.current_question = { "keywords": picked_keywords,
								  "answer_indices": picked_answer_indices,
								  "answers": picked_answers }

	#
	# Galerij
	#

	def reset_galerij_index(self):
		self.galerij_index = 0
		self.infer_galerij_image()

	def infer_galerij_image(self):
		self.current_question["image"] = self.current_question["images"][self.galerij_index]

	def advance_galerij(self):
		# If we reached the end of a gallery
		if self.galerij_index == self.settings["Galerij_round_no"] - 1:
			print("Galerij done for primary player. Complementing starts now")

			# If we're still in the answering stage, pass the turn to another player
			if not self.overview:
				self.handle_list_answer_pass()
				# Hide last image
				self.current_question["image"] = None

				self.clock_stop(pass_turn=False)
			# If we're in the review stage, advance the subround
			else:
				self.advance_subround()
			return

		self.galerij_index += 1
		self.infer_galerij_image()

	#
	# Collectief geheugen
	# 

	# 
	# Finale
	# 

	def prepare_finale(self):
		# Get all scores
		scores = list(map(lambda player: player.points, self.players))

		# Get all indices
		indices = list(range(0, self.no_players))

		# Combine them into tuples
		scores_with_indices = list(zip(scores, indices))

		# Sort the tuples
		# If we're playing with regular rules, the worst two players play the Finale round
		# If we're playing with final episode rules, the best two players play the Finale round
		scores_with_indices.sort(reverse=self.finale_rules)

		self.finalist_player_indices = [ scores_with_indices[0][1],
										 scores_with_indices[1][1] ]

		# Get the two first players from the array and make them finalists
		self.players[self.finalist_player_indices[0]].finalist = True
		self.players[self.finalist_player_indices[1]].finalist = True

	# When player lets the timer run out
	def timeout(self):
		# Stop the clock
		self.clock_stop(pass_turn=False)
		# Make the points equal zero
		self.active_player.points = 0
		# Victory!
		self.end_game()

	# 
	# Question loading
	# 

	def load_questions(self, questions_directory):
		# Load the questions for each round
		for i, round_text in enumerate(self.rounds):
			# Each question set should be named "round.json"
			questions_json_path = os.path.join(questions_directory, f"{round_text}.json")
			if os.path.exists(questions_json_path):
				with open(questions_json_path, "rt", encoding="utf-8") as reader:
					self.questions[i] = json.loads(reader.read())
					question_count = len(self.questions[i])
					
					# Different checks for finale
					if round_text == "Finale":
						if question_count < 10:
							print(f"{round_text}: {question_count} questions might be too few")
						continue

					if round_text == "3-6-9":
						if question_count < 15:
							print(f"{round_text}: 15 questions are required for this round")
						continue

					if question_count < self.no_players:
						print(f"{round_text}: not enough questions ({question_count}) for the number of players ({self.no_players})")
			else:
				print(f"Questions for round {round_text} not found!")