class Scores {
	constructor() {
		this.scoreDomBuilt = false;
	}

	// Create the DOM for the scores of the players
	// Cannot be hardcoded anymore, since here in the future, 
	// we have variable player counts
	buildScoreDom(state) {
		for (let i = 0; i < state.players.length; i++) {
			let player = state.players[i];

			let circleBox = document.createElement("div");
			circleBox.className = "circlebox";
			circleBox.id = this.getCircleBoxElementName(i);

			let playerName = document.createElement("div")
			playerName.className = "name";
			playerName.innerHTML = player.name;

			let innerCircle = document.createElement("div");
			innerCircle.className = "circle";
			innerCircle.id = this.getCircleElementName(i);

			let score = document.createElement("p");
			score.className = "score";
			score.id = this.getScoreElementName(i);

			let background = document.createElement("div");
			background.className = "background";

			circleBox.appendChild(playerName);
			circleBox.appendChild(innerCircle);
			innerCircle.appendChild(score);
			innerCircle.appendChild(background);

			document.getElementById("scores").appendChild(circleBox);
		}

		this.scoreDomBuilt = true;
	}

	renderState(state, updatePoints=true) {
		// We only build the score badges ONCE
		if (!this.scoreDomBuilt) {
			this.buildScoreDom(state);
		}

		let playerIndex = 0;
		state.players.forEach(player => {
			if (updatePoints || playerIndex != state.active_player_index) {
				this.adjustPlayerPoints(playerIndex, player.points);
			}

			let circle = document.getElementById(this.getCircleElementName(playerIndex));
			circle.classList.remove("turn");
			circle.classList.remove("spin");

			if (playerIndex == state.active_player_index) {
				circle.classList.add("turn");

				if (state.timer_running) {
					circle.classList.add("spin");
				}
			}

			playerIndex++;
		});

		/* Hide non finalists in Finale ronde */
		if (state.current_round_text == "Finale") {
			let playerIndex = 0;
			state.players.forEach(player => {
				if (!player.finalist) {
					document.getElementById(this.getCircleBoxElementName(playerIndex)).classList.add("d-none");
				}

				playerIndex++
			});
		}
	}

	adjustPlayerPoints(playerIndex, points) {
		document.getElementById(this.getScoreElementName(playerIndex)).innerHTML = 
				points;
	}

	getCircleBoxElementName(playerIndex) {
		return `circlebox_player_${playerIndex}`;
	}

	getCircleElementName(playerIndex) {
		return `circle_player_${playerIndex}`;
	}

	getScoreElementName(playerIndex) {
		return `score_player_${playerIndex}`;
	}
}