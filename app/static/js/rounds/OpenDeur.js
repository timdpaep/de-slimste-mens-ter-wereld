class OpenDeur {
	static renderState(state) {
		let questioneersElement = document.getElementById("round_Open deur_questioneers");
		questioneersElement.classList.remove("d-none");
		let answersElement = document.getElementById("round_Open deur_answers");
		answersElement.classList.remove("d-none");

		// No answer time, so show questioneers
		if (!state.answer_time) {
			answersElement.classList.add("d-none");

			questioneersElement.innerHTML = "";
	
			for (let i = 0; i < state.no_players; i++) {
				let column = document.createElement("div");
				column.className = "col";
	
				let image = document.createElement("img");
				image.className = "questioneer";
				image.src = `resources/${state.available_questions[i].image}`;
	
				if (state.question_history.includes(i)) {
					image.classList.add("chosen");
				} else {
					column.onclick = () => {
						dsmtw.openDeurChoose(i);
					};
				}
	
				column.appendChild(image);
				questioneersElement.appendChild(column);
			}
		}
		// Answer time, so show answers
		else {
			questioneersElement.classList.add("d-none");

			if (host) {
				document.getElementById("round_Open deur_question").innerHTML = 
					state.current_question.question;
			}
		}
	}
}