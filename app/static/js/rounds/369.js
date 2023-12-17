class ThreeSixNine {
	static renderState(state) {
		// Get all question circles
		let circles = Array.from(document.querySelectorAll(".ThreeSixNine.circle"));

		// Highlight the current turn
		circles.forEach(circle => {
			circle.classList.remove("turn");

			if (state.current_subround + 1 == circle.getAttribute("dsmtw-question-number")) {
				circle.classList.add("turn");
			}
		});

		if (host) {
			document.getElementById("round_3-6-9_question").innerHTML = state.current_question.question;
			document.getElementById("round_3-6-9_answer").innerHTML = state.current_question.answer;
		}
	}
}