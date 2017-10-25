import math
import asyncio
import datetime
from music.audio_object.audio_state import AudioState


class VoiceState:
    # Object that holds information about the voice channel, audio player, and manages audio player tasks
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.play_radio_station = asyncio.Event()
        # self.songs = [asyncio.Queue(), asyncio.Queue()]
        self.songs = asyncio.Queue()
        self.list = []  # side list for easier access to songs
        self.radio_entry = None
        # self.current_queue = 0
        self.skip_votes = set()  # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())  # For youtube videos
        self.radio_player = self.bot.loop.create_task(self.radio_player_task())  # For radios
        self.audio_state = AudioState.NONE  # State of audio playing [ 0 - None, 1 - Youtube, 2 - Radio ]

        self.video_start = None  # To track the progress of the playing video
        # It's ugly but I can't track the stream of FFMPEG

        self.video_pauses = []  # Tracks the pauses

        self.youtube_paused = False

    def get_duration(self):
        """This function calculate and returns the progress of the current playing video."""
        if self.video_start is None:  # Didn't start
            return 0, 0, 0
        elif not self.video_pauses:  # No pauses
            now = datetime.datetime.now()

            return math.trunc((now - self.video_start).total_seconds())

        else:  # pauses exists
            elapsed = (self.video_pauses[0] - self.video_start).total_seconds()
            if len(self.video_pauses) % 2 == 0:  # Even len, which mean the video is playing
                idx = 1
                while idx <= len(self.video_pauses) - 1:
                    if idx == len(self.video_pauses) - 1:
                        elapsed += (datetime.datetime.now() - self.video_pauses[idx]).total_seconds()
                    else:
                        elapsed += (self.video_pauses[idx+1] - self.video_pauses[idx]).total_seconds()

                    idx += 2

            else:  # Odd len, which mean the video is paused
                idx = 2
                while idx <= len(self.video_pauses) - 1:
                    elapsed += (self.video_pauses[idx] - self.video_pauses[idx-1]).total_seconds()
                    idx += 2

            return math.trunc(elapsed)

    def switch_audio_context(self, ctx):
        if not (self.audio_state == ctx):
            self.audio_state = ctx

    def is_youtube_paused(self):
        return self.youtube_paused

    def is_playing(self):
        if self.voice is None:
            return False

        is_playing = self.youtube_playing() or self.radio_playing()
        return is_playing

    def youtube_playing(self):
        if self.current is None:
            return False

        player = self.current.player
        return player.is_playing()

    def youtube_done(self):
        if self.current is None:
            return True

        player = self.current.player
        return player.is_done()

    def radio_playing(self):
        if self.radio_entry is None or self.radio_entry.player is None:
            return False
        player = self.radio_entry.player
        return player.is_playing()

    def radio_done(self):
        if self.radio_entry is None or self.radio_entry.player is None:
            return False
        player = self.radio_entry.player
        return player.is_done()

    def current_state(self):
        if self.voice is None or self.current is None:
            return False
        return type(self.audio_state)

    def get_song_list(self):
        return self.list

    @property
    def player(self):
        return self.current.player

    def radio_entry(self):
        return self.radio_entry

    async def switch_station(self, radio_station, radio_station_title):
        self.radio_entry.set_title(radio_station_title)
        self.radio_entry.set_station(radio_station)
        if '.m3u8' in radio_station:
            await self.radio_entry.create_player()
        else:
            await self.radio_entry.create_player()

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_radio(self):
        self.bot.loop.call_soon_threadsafe(self.play_radio_station.set)

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def radio_player_task(self):
        while True:
            self.play_radio_station.clear()
            if self.audio_state == AudioState.RADIO:  # Radio player
                if self.radio_entry is not None:
                    self.radio_entry.player.start()
            await self.play_radio_station.wait()

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            try:
                self.current = await self.songs.get()
                self.list = self.list[1:]  # remove first object
                await self.bot.send_message(self.current.channel, 'Now playing: \n' + str(self.current))

                await self.current.create_player()
                if self.current.player is not None:
                    self.video_start = datetime.datetime.now()
                    self.video_pauses = []  # reinstantiate pause array for new video
                    self.youtube_paused = False  # video starts playing, pause is now false
                    self.current.player.start()  # starts music
                else:
                    await self.bot.send_message(self.current.channel, self.current.error_played)

            except Exception as e:
                pass

                fmt = 'Unable to play video due to the following error:\n```\n{0}```\nSkipping to next video...'
                error_message = fmt.format(e)
                print(type(e).__name__, '\n', e)
                await self.bot.say(error_message)

            await self.play_next_song.wait()
