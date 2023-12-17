import jsonpickle

class Gameshow():
	def __init__(self, name, rounds, no_players, best_position=1):
		# Basic information
		self.name = name
		self.running = False
		self.won = False

		# Round information
		self.current_round = 0
		# e.g. [ "3-6-9", "Open Deur", "Galerij" ]
		self.rounds = rounds
		self.current_round_text = self.rounds[self.current_round]
		
		self.current_subround = 0
		
		# Player information
		self.no_players = no_players
		self.players = []
		for i in range(self.no_players):
			self.players.append(Player(None))
		self.active_player = None
		self.active_player_index = None

		# Miscellaneous information
		self.best_position = best_position

	def advance_round(self):
		# Do not advance round beyond how many rounds there actually are
		if self.current_round + 1 > len(self.rounds):
			raise Exception("Cannot advance round beyond round bounds")
			return

		# Advance the round, reset the subround counter
		self.current_round += 1
		self.current_round_text = self.rounds[self.current_round]
		self.current_subround = 0

		print("Round advanced")

	def advance_subround(self):
		self.current_subround += 1

		print("Subround advanced")

	def set_active_player(self, player_index):
		self.active_player = self.players[player_index]
		self.active_player_index = player_index

	def player_award_points(self, player_index, awarded_points):
		self.players[player_index].points += awarded_points

		print("Awarded {} points to player {}".format(awarded_points, player_index))

	def player_advance_position(self, player_index, position_advancement):
		if self.players[player_index].position - position_advancement < self.best_position:
			self.players[player_index].position = self.best_position
			return

		self.players[player_index].position -= position_advancement

		print("Advanced player {}'s position by {} places".format(player_index, position_advancement))

	def start_game(self):
		self.running = True

		print("Game started")

	def end_game(self):
		self.running = False

		print("Game ended")

	def as_dict(self):
		gameshow_dict = { **self.__dict__ } # circumvent reference

		# Serialize the players as well
		players_array = []
		for player in self.players:
			player_dict = player.__dict__
			players_array.append(player_dict)

		gameshow_dict["players"] = players_array

		if gameshow_dict["active_player"] is not None:
			gameshow_dict["active_player"] = gameshow_dict["active_player"].__dict__

		return gameshow_dict

	def save(self, filename):
		with open(filename, "w") as writer:
			writer.write(jsonpickle.encode(self))

		print("Game saved to '{}'".format(filename))

	@staticmethod
	def load(filename):
		with open(filename, "r") as reader:
			game_raw = reader.read()

		print("Game loaded from '{}'".format(filename))

		return jsonpickle.decode(game_raw)

class Player():
	def __init__(self, name):
		self.name = name
		self.points = 0
		self.position = 0