# GBox Design

### <u>Usage</u>

<strong>GBox</strong> is a JukeBox application where users can contribute songs (or videos) to a joint queue. To add songs to the queue, users will simply submit a <strong>URL</strong> to a <strong>YouTube</strong> video. <strong>GBox</strong> will take the URL and using the <strong>YouTube IFrame API</strong>, will add it to the IFrame Queue and play them one after the other. 

### <u>Users</u>

There are three different Types of Users

**Player** 
- Initial User type
- There can only be one Player, this is the Interface that holds the ```<iframe>``` that is playing the videos that are added to the queue. 

**Admin** 
- Special user type
- Can <strong>Add</strong> songs to the queue
- Has special privlages, that allow them to <b>Pause/Play</b>, <b>Skip</b>, or <b>Edit</b> the queue.

| Pause/Play | Skip | Edit |
| :-- | :-- | :-- |
| Pause or Play the song currently in the ```<iframe>``` | Skip to the next song in the queue | Remove or change order of songs in the queue 

**User**
- Default user type
- Only has the ability to <strong>Add</strong> songs to queue

