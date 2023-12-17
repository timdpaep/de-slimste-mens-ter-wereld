class Bumper {
	static playBumper(text, intro=false) {
		let bumperContainer = document.getElementById("bumper");
		let bumperText = document.getElementById("bumper_text");

		bumperContainer.className = "";

		bumperText.className = "animate__animated animate__fadeInLeft"
		bumperText.innerHTML = text;

		if (intro) {
			bumperContainer.className = "small";
		}

		let bumperTime = 4000;
		if (intro) {
			bumperTime = 17000;
		}

		setTimeout(() => {
			bumperText.className = "animate__animated animate__fadeOutRight"

		 }, bumperTime);
	
		setTimeout(() => {
			bumperContainer.className = "d-none";
		}, bumperTime + 1000);
	}
}