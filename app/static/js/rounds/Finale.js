class Finale {
	static renderState(state) {
		document.getElementById("round_Finale_question").innerHTML = state.current_question.question;
	}
}