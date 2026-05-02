const socket = io("http://127.0.0.1:5000");

const youtubeRegex = `^(?:https?:)?(?:\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|live\/|shorts\/|watch\?.+&v=))([\w-]{11})(?:\S+)?$`;

socket.on("connect", () => {
	addMessage("Connected to server");
});

socket.on("server_message", (data) => {
	addMessage(data.message);
});

socket.on("backend_update", (data) => {
	document.getElementById("counter").textContent = data.count;
	addMessage(data.message);
});

function sendMessage() {
	const input = document.getElementById("messageInput");

	socket.emit("client_message", {
		message: input.value
	});

	input.value = "";
}

function addMessage(message) {
	const li = document.createElement("li");
	li.textContent = message;
	document.getElementById("messages").appendChild(li);
}
