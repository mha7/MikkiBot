from configs import configs


class RadioEntry:

    # Radio object that contains radio information
    def __init__(self, message, state, radio_stream, title=''):
        self.title = title
        self.requester = message.author
        self.channel = message.channel
        self.state = state
        self.radio_stream = radio_stream
        self.player = None
        self.error_played = ''

    async def create_player(self):
        try:
            # Using FFMPEG native downloader
            # beforeArgs = "-re"
            # options = "-b:a 900k -maxrate 750k -bufsize 3000k"
            # player = self.state.voice.create_ffmpeg_player(self.radio_stream,
            #                                                options=options,
            #                                                before_options=beforeArgs)

            # Using Youtube-DL
            before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            player = await self.state.voice.create_ytdl_player(self.radio_stream,
                                                               ytdl_options=configs.YOUTUBE_DL_CONFIGS,
                                                               before_options=before_args)

            self.player = player
            self.player.volume = configs.MUSIC_VOLUME_DEFAULT

        except Exception as e:
            fmt = 'Unable to play this video due to the following error: ```py\n{}: {}\n```'
            error = fmt.format(type(e).__name__, e)
            self.error_played = error
            print(type(e).__name__, '\n', e)

    def create_player_for_m3u8(self):  # WORKING IN PROGRESS
        # Man, fuck m3u8....
        # Youtube-dl and ffmpeg doesn't support em well enough for live streaming
        try:
            youtube_dl_config_for_radio = {
                'no-check-certificate': 'True',
                'default_search': 'auto',
                # 'quiet': True,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'hls-prefer-native': True,
                'external-downloader-args': 'avconv',
                'no-resize-buffer': True,
                'fragment-retries': '30',
                'abort-on-unavailable-fragment': True,
                'w': True
            }

            beforeArgs = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 --verbose" \
                         "--hls-prefer-native"
            player = self.state.voice.create_ytdl_player(self.radio_stream,
                                                         ytdl_options=youtube_dl_config_for_radio,
                                                         before_options=beforeArgs)

            self.player = player
            self.player.volume = configs.MUSIC_VOLUME_DEFAULT

        except Exception as e:
            fmt = 'Unable to play this video due to the following error: ```py\n{}: {}\n```'
            error = fmt.format(type(e).__name__, e)
            self.error_played = error
            print(error)

    def set_title(self, title):
        self.title = title

    def set_station(self, radio_stream):
        self.radio_stream = radio_stream

    def url(self):
        return self.radio_stream
