import json
import requests
from configs import configs


class Twitch:
    def __init__(self):

        self.client_id = 'nna8pzo47eafrt7bj1ttxhduy0xr8h'
        self.client_secret = 'xa94el3onn6jsr8onfmkh65brl0iko'

        # self.client_id = configs.TWITCH_CLIENT_ID
        # self.client_secret = configs.TWITCH_CLIENT_SECRET

    def get_channel_info(self, name):
        url = "https://api.twitch.tv/kraken/channels/" + name + "?client_id=" + self.client_id
        details = json.loads(requests.get(url).text)

        return details

twitch = Twitch()
print(twitch.get_channel_info('riotgames'))