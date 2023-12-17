class Galerij {
	static renderState(state) {
		let slideshowControl = document.getElementById("round_Galerij_slideshow_controls");
		slideshowControl.classList.remove("d-none");
		let answersElement = document.getElementById("round_Galerij_answers");
		answersElement.classList.remove("d-none");

		// Hide the slideshow if we're in the complementing phase
		if (state.turn_history.length > 1) {
			slideshowControl.classList.add("d-none");
		} else {
			answersElement.classList.add("d-none");
		}

		if (host) {
			document.getElementById("round_Galerij_answer").innerHTML = 
				state.current_question.answers[state.galerij_index];

			let correctButton = document.getElementById("round_Galerij_correct_button");

			correctButton.onclick = () => {
				dsmtw.correct(state.galerij_index);
			};

			// Hide the "correct" button in the overview stage
			if (state.overview) {
				correctButton.classList.add("d-none");
			} else {
				correctButton.classList.remove("d-none");
			}
		}

	}
}