const socket = io("https://link/to/thing");

// TODO: Make events

socket.on("queue_update", (data) => {
    // call event handler
    updateQueue(data.queue_state);
});

// TODO: Make event handlers

// TODO: this function will get the state of the queue as json
//       and it will render it on the screen in real time
//       there are a few different ways that the queue
//       can be updated
//        - user adds a song
//        - admin skips a song
//        - admin bumps a song up
//        - admin bumps a song down
function updateQueue(queueState) {
    console.log(queueState);
    return null;
}

// TODO: add funcitons for document

// TODO: add a function to validate a url with regex

// TODO: figure out a way to send the url along with the user data

// TODO: add a function to send the url to the backend
