const socket = io();

const page = document.body;
const username = page.dataset.username;
const songForm = document.getElementById("song-form");
const urlInput = document.getElementById("youtube-url");
const formMessage = document.getElementById("form-message");
const connectionStatus = document.getElementById("connection-status");
const queueContainer = document.getElementById("queue");
const queueEmpty = document.getElementById("queue-empty");

socket.on("connect", () => {
    connectionStatus.textContent = "Connected";
});

socket.on("disconnect", () => {
    connectionStatus.textContent = "Disconnected. Reconnecting…";
});

socket.on("connect_error", () => {
    connectionStatus.textContent = "Unable to connect. Retrying…";
});

socket.on("queue_update", (queueState) => {
    updateQueue(queueState);
});

songForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const url = urlInput.value.trim();
    if (!isYouTubeUrl(url)) {
        formMessage.textContent = "Enter a valid YouTube URL.";
        urlInput.focus();
        return;
    }

    if (!socket.connected) {
        formMessage.textContent =
            "The server is disconnected. Try again shortly.";
        return;
    }

    formMessage.textContent = "Downloading song…";
    socket.emit("submit_song", { url, username }, (response) => {
        if (response?.ok) {
            urlInput.value = "";
            formMessage.textContent = "Song added to the queue.";
            return;
        }

        formMessage.textContent =
            response?.error || "Unable to add that song. Please try again.";
    });
});

function updateQueue(queueState) {
    queueContainer.replaceChildren();

    if (!Array.isArray(queueState)) {
        queueEmpty.textContent = "The queue is unavailable.";
        queueEmpty.hidden = false;
        return;
    }

    if (queueState.length === 0) {
        queueEmpty.textContent = "The queue is empty.";
        queueEmpty.hidden = false;
        return;
    }

    queueEmpty.hidden = true;
    const entries = document.createDocumentFragment();

    queueState.forEach((song, index) => {
        const entry = document.createElement("div");
        const title = document.createElement("span");
        const submitter = document.createElement("span");

        title.textContent = `${index + 1}. ${song?.title || "Untitled video"}`;
        submitter.textContent = ` — submitted by ${song?.user || "Unknown user"}`;

        entry.append(title, submitter);
        entries.appendChild(entry);
    });

    queueContainer.appendChild(entries);
}

function isYouTubeUrl(value) {
    let url;
    try {
        url = new URL(value);
    } catch {
        return false;
    }

    if (url.protocol !== "http:" && url.protocol !== "https:") {
        return false;
    }

    const hostname = url.hostname.toLowerCase().replace(/^www\./, "");
    const isVideoId = (candidate) =>
        /^[A-Za-z0-9_-]{11}$/.test(candidate || "");

    if (hostname === "youtu.be") {
        return isVideoId(url.pathname.split("/").filter(Boolean)[0]);
    }

    const youtubeHosts = new Set([
        "youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtube-nocookie.com",
    ]);
    if (!youtubeHosts.has(hostname)) {
        return false;
    }

    if (url.pathname === "/watch") {
        return isVideoId(url.searchParams.get("v"));
    }

    const [kind, videoId] = url.pathname.split("/").filter(Boolean);
    return (
        ["embed", "live", "shorts", "v"].includes(kind) && isVideoId(videoId)
    );
}
