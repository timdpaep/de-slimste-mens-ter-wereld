class Timer {
	constructor(scores, activePlayerIndex, startingPoints) {
		//this.startTime = this.getEpoch();

		this.scores = scores;
		this.activePlayerIndex = activePlayerIndex;
		this.currentPoints = startingPoints;

		// Parent can check whether the timer isr unning
		this.running = false;

		this.interval = null;
	}

	start() {
		this.interval = setInterval(() => { this.tick(); }, 1000);
		this.running = true;
		Sound.playSound("clock");
	}

	stop() {
		if (this.interval != null) {
			clearInterval(this.interval);
		}
		this.running = false;
		Sound.stopSound("clock");
		Sound.playSound("clock_end");
	}

	tick(deductPoints=true) {
		if (deductPoints) {
			this.currentPoints -= 1;
		}
		this.scores.adjustPlayerPoints(this.activePlayerIndex, this.currentPoints);
	}

	getEpoch() {
		return new Date().getTime() / 1000;
	}
}