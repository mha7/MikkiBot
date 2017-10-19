# MikkiBot
A discord bot made for my servers
# Requirements:
* Python 3.4+
* discord.py[voice] version
* asyncio
* ffmpeg 
* google-api-python-client 
* youtube-dl
* pm2 (if you want to run on your cloud server)
# Configurations
To setup the bot, you will need to create and provide your own credentials in config/credentials.ini for the following: 
* Discord ID ( Your real ID, not something like John#1234 )
```
OWNER_ID = YOUR_ID_HERE
```
* [Youtube API Credentials](https://developers.google.com/youtube/registering_an_application)
# How to use
After adding the credentials and edit other options to your preference, you can start the bot by running bot_main.py.
If you're going to run the bot on your cloud server, install pm2 and start it as a fork.
```
pm2 start ./PATH_TO_FILE/bot_main.py --interpreter=python3
```