class Gameshow
{
	constructor(name)
	{
		this.name = name
		this.websocket = io("/", { path: "/socket.io", transports: ["websocket", "polling"], reconnection: true });
		this.websocket.on('connect', (event) => { console.log("Connected"); });
		this.websocket.on('disconnect', (event) => { console.log("Disconnected"); });
		this.websocket.on('error', (event) => { console.log("Error"); });
		this.websocket.on('state', (event) => { this.renderState(event); });
		this.websocket.on('event', (event) => { this.handleMessage(event); });

		this.websocket.connect();
	}

	advanceRound()
	{
		this.websocket.emit("advance_round");
	}

	advanceSubround()
	{
		this.websocket.emit("advance_subround");
	}

	playerAwardPoints(playerIndex, awardedPoints)
	{
		this.websocket.emit("player_award_points", playerIndex, playerAwardPoints);
	}

	playerAdvancePosition(playerIndex, positionAdvancement)
	{
		this.websocket.emit("player_advance_position", playerIndex, positionAdvancement);
	}

	startGame()
	{
		this.websocket.emit("start_game");
	}

	endGame()
	{
		this.websocket.emit("end_game");
	}

	renderState(event)
	{
		console.log("Received state");
		console.log(event);
	}
}