- [x] Python WebAPP
- [x] SQLite Database

Application Behavior:

- there should be a text box that will be the main UI.
- The user will send a YouTube URL. The URL will be validated with a regex before being sent to backend
- backend will receive it and try to download the URL. If that fails then it will send back a message
- once the video has been downloaded and added to the queue the backend will emit a socket message
  to every connection updating the queue.

You should watch this video to figure out how we can work with sockets: https://www.youtube.com/watch?v=o5vDco6OVTs

- [x] Test it with multiple browsers
- [ ] fix the GBoxQueue so that it has a place for the currently playing song
- [ ] update the json message to hold the currently playing song
- [ ] Update the frontend to have the currently playing song in its own special box
- [ ] When the player completes a song it should send an update to the frontend
- [ ] Disable the button and clear the submit field before sending the url to the backend
- [ ] Make a script that will automatically try and update yt-dlp when you run the app
- [ ] Make pages for the admin password and the admin index
