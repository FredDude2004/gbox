- [ ] Python WebAPP
- [ ] SQLite Database

Application Behavior:

- there should be a text box that will be the main UI.
- The user will send a YouTube URL. The URL will be validated with a regex before being sent to backend
- backend will receive it and try to download the URL. If that fails then it will send back a message
- once the video has been downloaded and added to the queue the backend will emit a socket message
  to every connection updating the queue.

You should watch this video to figure out how we can work with sockets: https://www.youtube.com/watch?v=o5vDco6OVTs
