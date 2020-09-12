# 4chan-to-youtube

Scrapes a specified 4chan catalogue for trigger words in thread snippets. Then scrapes those threads for youtube videos and adds them to a playlist.
Should create a new playlist with the same name everytime 5000 videos have been reached but I haven't gotten that far yet.


You need to get a credentials file from the [google api credentials page](https://console.developers.google.com/apis/credentials). Create project, add credentials etc.
First time you start it you have to auth a specific google user with your credentials. That user should have a youtube channel.
