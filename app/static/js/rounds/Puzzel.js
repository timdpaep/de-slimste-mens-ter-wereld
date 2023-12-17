class Puzzel {
	static renderState(state) {
		let puzzle = document.getElementById("round_Puzzel_puzzle");
		if (state.turn_history.length == 1 && !state.timer_running && !host) {
			puzzle.style.visibility = "hidden";
		} else {
			puzzle.style.visibility = "visible";
		}

		// Puzzle matrix
		let answerColours = [ "teal", "yellow", "green" ];

		for (let i = 0; i < state.current_question.keywords.length; i++) {
			let keyword = state.current_question.keywords[i];
			let answerIndex = state.current_question.answer_indices[i];

			let keywordElement = document.getElementById(`round_Puzzel_puzzle_keyword_${i}`);
			keywordElement.innerHTML = keyword;
			keywordElement.className = "";

			if (state.answers_found.includes(answerIndex) || state.to_advance || host) {
				keywordElement.classList.add(answerColours[answerIndex]);
			}
		}

		for (let i = 0; i < state.current_question.answers.length; i++) {
			let answerTextElement = document.getElementById(`round_Puzzel_answer_${i}`);
			answerTextElement.classList.remove(answerColours[i]);
			if (state.answers_found.includes(i) || state.to_advance || host) {
				answerTextElement.classList.add(answerColours[i]);
			}
		}
	}
}