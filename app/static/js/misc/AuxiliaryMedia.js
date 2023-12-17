class AuxiliaryMedia {
	static renderState(state) {
		let container = document.getElementById("container_auxiliaryMedia");
		container.classList.add("d-none");

		if (state.current_question == null) {
			return;
		}

		if (!("image" in state.current_question) && !("video" in state.current_question)) {
			return;
		}

		if (state.current_question.image != null | state.current_question.video != null) {
			if ([ "Galerij" ].includes(state.current_round_text) && state.turn_history.length == 1 && !state.timer_running && !host) {
				return;
			}

			container.classList.remove("d-none");
		}

		let auxiliaryMediaElement = document.getElementById("auxiliaryMedia");
		if (state.current_question.image != null) {
			auxiliaryMediaElement.src = 
				`/resources/${state.current_question.image}`;
		} else {
			auxiliaryMediaElement.src = "";
		}
	}

	static playVideo(filename) {
		if (host) {
			return;
		}

		let auxiliaryMediaElementVideo = document.getElementById("auxiliaryMedia_video");
		auxiliaryMediaElementVideo.classList.remove("d-none");
		auxiliaryMediaElementVideo.src = `resources/${filename}`;
		auxiliaryMediaElementVideo.play();

		auxiliaryMediaElementVideo.onended = () => { auxiliaryMediaElementVideo.classList.add("d-none"); };
	}
}