const socket = io("http://127.0.0.1:5000");

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
    url = input.value;
    console.log(url);
    if (validateYouTubeUrl(url)) {
        socket.emit("client_message", {
            url: input.value,
        });
        input.value = "";
    } else {
        input.value = ""; // Clears the field
        message.innerText = "Please enter a valid name."; // Tells user what's wrong
        message.style.color = "red";
    }
}

function addMessage(message) {
    const li = document.createElement("li");
    li.textContent = message;
    document.getElementById("messages").appendChild(li);
}

function validateYouTubeUrl(url) {
    if (url) {
        var regExp =
            /^(?:https?:\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
        return url.match(regExp) ? true : false;
    }

    return false;
}
