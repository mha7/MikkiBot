from configs import configs


class VoiceEntry:

    # General object that holds youtube video information
    def __init__(self, message, state, ytv):
        self.requester = message.author
        self.channel = message.channel
        self.state = state
        self.ytv = ytv  # YoutubeVideo object
        self.player = None
        self.error_played = ''

    async def create_player(self):
        try:
            before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            # print(self.ytv.url)
            player = await self.state.voice.create_ytdl_player(self.ytv.url,
                                                               ytdl_options=configs.YOUTUBE_DL_CONFIGS,
                                                               after=self.state.toggle_next,
                                                               before_options=before_args)

            player.volume = configs.MUSIC_VOLUME_DEFAULT
            self.player = player

        except Exception as e:
            fmt = 'Unable to play this video due to the following error: ```py\n{}: {}\n```'
            self.error_played = fmt.format(type(e).__name__, e)

    def __str__(self):
        fmt = '**{0.title}** added by **{1.display_name}** `[{0.duration}]`'

        return fmt.format(self.ytv, self.requester)
