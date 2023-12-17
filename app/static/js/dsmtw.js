class DeSlimsteMens extends Gameshow {
	constructor() {
		super();

		this.websocket.on('points_awarded', (pointsAwarded) => { 
			this.pointsAwarded(pointsAwarded); });
		this.websocket.on('clock_start', () => { 
			this.clockStarted(); });
		this.websocket.on('clock_stop', () => { 
			this.clockStopped(); });
		this.websocket.on('video', (filename) => { 
			AuxiliaryMedia.playVideo(filename); });

		this._currentSubroundText = null;

		this.scoreDomBuilt = false;

		this.scores = new Scores();

		this.latestState = null;
	}

	renderState(state) {
		// First state render
		if (this.latestState == null) {
			this.latestState = state;

			// We need to make a timer so we can cancel it, basically
			this.setupTimer();

			// Timer could have started before we loaded the page!
			if (state.timer_running) {
				this.timer.start();
			}
		}

		// Detect game start
		if (!this.latestState.running && state.running && !host) {
			Bumper.playBumper("De Slimste Mens Ter Wereld", true);
			Sound.playSound("intro");
		}

		// Detect game win
		if (this.latestState.running && !state.running && !host) {
			Sound.playSound("finale");
		}

		// Detect round change
		if ((this.latestState.current_round_text != state.current_round_text) && !host) {
			Bumper.playBumper(state.current_round_text);
			Sound.playSound("bumper");
		}

		// If the clock has been stopped server side (this is possible when all answers were found),
		// we need to stop our local clock
		if (!state.timer_running && this.timer.running) {
			this.clockStopped();
		}

		// Save the latest state
		this.latestState = state;

		// Pass to super method
		super.renderState(state);

		// Debug
		document.getElementById("currentround").innerHTML = state.current_round_text;

		// Hide all rounds...
		let roundContainers = document.getElementsByClassName("round");
		let currentRound = state.current_round_text;
		// Only render the game if it is running
		Array.from(roundContainers).forEach(roundContainer => roundContainer.classList.remove("current"));
		if (!state.running) {
			currentRound = "start";
		}

		// ..then only show the current one
		// or render game start if host
		document.getElementById(`round_${currentRound}`).classList.add("current");

		document.body.classList.remove("unadvanced");
		// Add a specific class if to_advance is not null
		if (state.to_advance != null) {
			document.body.classList.add("unadvanced");
		}

		document.body.classList.remove("clocktogglevisible");
		// Add a specific class if clock toggle is visible
		if (state.clock_visible) {
			document.body.classList.add("clocktogglevisible");
		}

		// Round-specific rendering
		switch (state.current_round_text) {
			case "3-6-9":
				ThreeSixNine.renderState(state);
				break;
			case "Open deur":
				OpenDeur.renderState(state);
				Answers.renderAnswers(state);
				break;
			case "Puzzel":
				Puzzel.renderState(state);
				Answers.renderAnswers(state);
				break;
			case "Galerij":
				Galerij.renderState(state);
				Answers.renderAnswers(state);
				break;
			case "Collectief geheugen":
				CollectiefGeheugen.renderState(state);
				Answers.renderAnswers(state);
				break;
			case "Finale":
				Finale.renderState(state);
				Answers.renderAnswers(state);
				break;
		}

		// Render scores
		// The second argument will block score updating if the timer is running
		this.scores.renderState(state, !this.timer.running);

		// Toggle the clock button UI
		// "Start klok" and "Stop klok"
		this.setClockUI(state.timer_running);

		// Render auxiliary media (if necessary)
		AuxiliaryMedia.renderState(state);

		// Host/client-specific rendering
		if (host)
		{
			this.renderStateHost(state);
		}
		else
		{
			this.renderStateGame(state);
		}
	}

	renderStateHost(state) {

	}

	renderStateGame(state) {

	}

	/* Communication */
	correct(answerValue = null)
	{
		this.websocket.emit("answer_correct", answerValue);
	}

	pass()
	{
		this.websocket.emit("answer_pass");
	}

	openDeurChoose(questioneerIndex) {
		this.websocket.emit("open_deur_choose", questioneerIndex);
	}

	pointsAwarded(pointsAwarded) {
		if (this.latestState.current_round_text != "Finale" && pointsAwarded != null) {
			this.timer.currentPoints += pointsAwarded;
			this.timer.tick(false);
		}

		if (!host && pointsAwarded != null) {
			Sound.playSound("correct");
		}
	}

	setupTimer() {
		this.timer = new Timer(this.scores,
							   this.latestState.active_player_index,
							   this.latestState.active_player.points);
	}

	clockStart() {
		this.websocket.emit("clock_start");
	}

	clockStarted() {
		this.setupTimer();
		this.timer.start();
	}

	clockStop() {
		this.websocket.emit("clock_stop");
	}

	clockStopped() {
		this.timer.stop();
	}

	clockToggle() {
		this.websocket.emit("clock_toggle");
	}

	setClockUI(timer_running) {
		document.getElementById("button_clock_toggle").innerHTML = 
			timer_running ? "Stop klok" : "Start klok";
	}

	releaseAdvance() {
		this.websocket.emit("release_advance");
	}
}

dsmtw = new DeSlimsteMens();