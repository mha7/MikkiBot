import datetime
import math
import re
from urllib.parse import urlparse, parse_qs

import discord
import requests
from discord.ext import commands

import configs.radio_defaults as defaults
from music.audio_object.audio_state import AudioState
from music.audio_object.radio_object import RadioEntry
from music.audio_object.voice_object import VoiceEntry
from music.audio_object.voice_state import VoiceState
from utils.youtube_search import YouTubeSearch


class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        # Assign bot to music init
        self.bot = bot

        # Create list of voice states for different servers
        self.voice_states = {}  # this is a dict of all voice states ( for music queueing purposes )

        # Creates a dict that contains server as key and another dict as value. The dict
        # value contains user id as key and the value is an array of songs they searched
        # before. This is to implement the "play n" command.
        self.song_search = {}

        # Create YoutubeSearch Object to search for videos
        self.youtube_search = YouTubeSearch()

        self.radio_defaults = defaults.RADIO_DEFAULT

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                state.radio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except Exception:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel: discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def joinme(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
            await self.bot.say('Ready to play audio in ' + summoned_channel.name)

        return True

    def _search_song(self, song):
        """ Testing search function """
        songs = self.youtube_search.search_youtube(song)

        return songs

    @staticmethod
    def _check_int(option):
        try:
            int(option)
            return True
        except ValueError:
            return False

    @staticmethod
    def _check_url(url):
        """" Checks if the input url is valid """
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme)

    async def manage_station(self, state, ctx, url, title):
        """ This function is for starting / switching radio stations"""
        try:
            if state.radio_entry is None:  # No RadioEntry object has been created, usually when the bot starts
                state.radio_entry = RadioEntry(ctx.message, state, radio_stream=url, title=title)
                await state.radio_entry.create_player()
                state.toggle_radio()
                await self.bot.say('Now starting radio player...')
                return
            elif state.radio_entry.url() == url:  # Current URL stream in object is the same as new
                await self.bot.say('Already on this radio station.')
            else:
                if state.radio_playing() or not state.radio_done():  #
                    player = state.radio_entry.player
                    player.stop()
                await state.switch_station(url, title)
                state.toggle_radio()
                await self.bot.say('Switching to new station...')
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            error = fmt.format(type(e).__name__, e)
            print(type(e).__name__, '\n', e)
            await self.bot.send_message(ctx.message.channel, error)

    @staticmethod
    async def _get_radio_stream_from_url(url):
        """ This function downloads the file from the url and find the stream URL from the file.
            Returns two field: title and stream. Title is probably only from pls files if it is included. If title is
            not included in the file, then the inputted url will be the title."""
        if '.pls' in url:
            try:
                file_text = requests.get(url).text
                pls_stream = re.search(r"File1=(.*)\n", file_text).group(1)
                stream_title = url
                if 'Title' in file_text:
                    stream_title = re.search(r"Title\w+=(.*)\n", file_text).group(1)

                return stream_title, pls_stream
            except Exception as e:
                print(type(e).__name__, '\n', e)
                return '', ''
        elif '.m3u8' in url:
            return url, url
        elif '.m3u' in url:
            try:
                file = requests.get(url)
                file_text = file.text
                text_lines = file_text.split('\n')
                m3u_stream = -1
                for idx, line in enumerate(text_lines):
                    if not line.startswith('#') and not line == '\n':
                        m3u_stream = idx
                        break
                if m3u_stream == -1:
                    return '', ''
                else:
                    return url, text_lines[m3u_stream].strip()
            except Exception as e:
                print(type(e).__name__, '\n', e)
                return '', ''
        else:
            return '', ''

    @commands.command(pass_context=True, no_pm=True, aliases=['play_radio', 'pr', 'playradio'])
    async def radio(self, ctx, *, station: str = ''):
        """ Plays a radio station from given URL. The URL must contain extension of .pls or .m3u."""
        state = self.get_voice_state(ctx.message.server)
        summoned_channel = ctx.message.author.voice_channel

        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return

        if state.voice is None:  # not in a voice channel
            success = await ctx.invoke(self.joinme)
            if not success:
                await self.bot.say('The bot is not in a voice channel.')
                return

        if state.audio_state == AudioState.YOUTUBE and state.youtube_playing():
            await self.bot.say('The bot is currently playing youtube videos, please pause it before'
                               'switching to the radio.')
            return

        state.switch_audio_context(AudioState.RADIO)
        message = 'Please input a valid radio stream URL with `.pls` or `.m3u` extension.\nYou' \
                  ' can also select from the following default stations using the command ' \
                  '`~radio n`.```'
        for idx, r_defaults in enumerate(self.radio_defaults):
            message = message + '\n' + str(idx+1) + '. ' + r_defaults[0]

        message = message + '```'

        if self._check_url(station):  # valid url
            if '.pls' not in station and '.m3u' not in station:
                await self.bot.say(message)
            # elif '.m3u8' in station:
            #     await self.bot.say('.m3u8 links are currently being work on, please enter `.pls` or `.m3u` links'
            #                        ' instead.')
            else:
                title, stream = await self._get_radio_stream_from_url(station)
                if not title and not stream:  # Both string are empty so that mean an exception occured
                    await self.bot.say('Something went wrong, please try again later.')
                else:
                    await self.manage_station(state, ctx, stream, title)
        else:
            if not station or not self._check_int(station):  # Command with no input string
                await self.bot.say(message)
                return
            else:
                idx = int(station)
                await self.manage_station(state, ctx, self.radio_defaults[idx-1][1], self.radio_defaults[idx-1][0])

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str = ''):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        """

        state = self.get_voice_state(ctx.message.server)
        summoned_channel = ctx.message.author.voice_channel

        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return

        if state.audio_state == AudioState.RADIO and state.radio_playing():
            await self.bot.say('The radio is currently playing, please pause it first...')
            return

        if state.voice is None:  # not in a voice channel
            success = await ctx.invoke(self.joinme)
            if not success:
                await self.bot.say('The bot is not in a voice channel.')
                return

        state.switch_audio_context(AudioState.YOUTUBE)

        if self._check_url(song):
            # Valid url

            if 'youtube' in song.lower() or 'youtu.be' in song.lower():  # check if youtube link
                if 'list=' in song:  # playlist
                    try:
                        playlist_videos = self.youtube_search.get_playlist_videos(song)

                        if not playlist_videos:  # returned list is empty
                            await self.bot.say('No working video found in the playlist.')
                            return

                        for vid in playlist_videos:
                            entry = VoiceEntry(ctx.message, state, vid)
                            await state.songs.put(entry)
                            state.list.append(entry)

                        await self.bot.say('Enqueued ' + str(len(playlist_videos)) +
                                           ' new songs from playlist.')

                    except Exception as e:
                        fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                        error = fmt.format(type(e).__name__, e)
                        print(type(e).__name__, '\n', e)
                        await self.bot.send_message(ctx.message.channel, error)

                else:  # regular link
                    try:
                        video = self.youtube_search.get_metadata(song)
                        if video is None:
                            await self.bot.say('Could not find the video, please try a different URL.')
                            return

                        entry = VoiceEntry(ctx.message, state, video)

                        await state.songs.put(entry)
                        state.list.append(entry)

                        await self.bot.say('Enqueued ' + str(entry))

                    except Exception as e:
                        fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                        error = fmt.format(type(e).__name__, e)
                        print(type(e).__name__, '\n', e)
                        await self.bot.send_message(ctx.message.channel, error)
            else:
                await self.bot.say('This bot currently only accepting Youtube links, sorry!')
        elif not song:  # string is empty
            await self.bot.say('Please input search terms or valid URL.')

        elif self._check_int(song) and ctx.message.author.id in self.song_search[ctx.message.server]:
            # if the tern is a number and the user has previously search a song

            idx = int(song)
            if 5 < idx or idx < 0:
                await self.bot.say("Invalid song index.")
                return
            else:

                try:
                    ytv = self.song_search[ctx.message.server][ctx.message.author.id][idx-1]

                    entry = VoiceEntry(ctx.message, state, ytv)
                    await state.songs.put(entry)
                    state.list.append(entry)

                    await self.bot.say('Enqueued ' + str(entry))

                except Exception as e:
                    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                    error = fmt.format(type(e).__name__, e)
                    print(error)
                    await self.bot.send_message(ctx.message.channel, error)

        else:  # search the song terms
            s_list = tuple(self._search_song(song))
            if not s_list:  # song search returns empty list
                await self.bot.say("**No matches with the query:** " + song)
            else:
                self.song_search[ctx.message.server] = {ctx.message.author.id: s_list}

                song_str = "**Select an option using `~play n` command:**"
                idx = 1
                for song in s_list:
                    song_str += "\n`[" + str(idx) + "]` " + str(song)
                    idx += 1
                await self.bot.say(song_str)
            return

    @commands.command(pass_context=True, no_pm=True,  aliases=['nowplaying', 'currently_playing',
                                                               'song', 'playing'])
    async def now_playing(self, ctx):
        """Get current playing song,"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():

            if state.radio_playing():
                # TODO: Add Gensokyo current music scraping
                # if 'Gensokyo' in state.radio_entry.title:
                #     ...
                # else:

                message = '**Currently playing station:**\n```' + state.radio_entry.title + '```'
                await self.bot.say(message)
                return
            else:
                player = state.player

                # getting the video id
                video_id_parse = urlparse(player.url)
                video_id = ''

                parse = parse_qs(video_id_parse.query).get('v')
                if parse:
                    video_id = parse[0]

                # Embed message title with url link and color bar
                em = discord.Embed(title=player.title, url=player.url, color=0xde50d0)

                # Author / Uploader
                em.set_author(name=player.uploader)

                # Duration field
                elapsed = state.get_duration()  # current playing progress duration

                # total duration
                t_m, t_s = divmod(player.duration, 60)
                t_h, t_m = divmod(t_m, 60)

                t_duration = ''
                if t_h == 0:
                    playing = "[{0[0]}m {0[1]}s /".format(divmod(elapsed, 60))
                    duration = " {0[0]}m {0[1]}s]".format(divmod(player.duration, 60))
                    t_duration = playing + duration
                else:
                    m, s = divmod(elapsed, 60)
                    h, m = divmod(m, 60)
                    t_duration = "[" + str(h) + "h " + str(m) + "m " + str(s) + "s / " + \
                                 " " + str(t_h) + "h " + str(t_m) + "m " + str(t_s) + "s ]"

                em.add_field(name="Duration", value=t_duration, inline=True)

                # Thumbnail image
                img_url = 'https://img.youtube.com/vi/' + video_id + '/hqdefault.jpg'
                em.set_thumbnail(url=img_url)

                # Likes
                likes_dislikes = str(player.likes) + ":thumbsup: / " + str(player.dislikes) + ":thumbsdown:"
                em.add_field(name="Likes / Dislikes", value=likes_dislikes, inline=True)

                # Description field
                description = player.description
                if description:
                    description = (description[:500] + '...') if len(description) > 500 else description
                else:
                    description = "[No description available]"
                em.add_field(name="Description", value=description, inline=False)

                await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.say('No song currently playing.')

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('No audio is playing...')
        elif state.youtube_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))
        else:
            player = state.radio_entry.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.youtube_playing():
            player = state.player
            player.pause()
            state.video_pauses.append(datetime.datetime.now())
            state.youtube_paused = True
        else:
            self.bot.say('The bot is not playing any youtube videos...')

    @commands.command(pass_context=True, no_pm=True)
    async def radio_pause(self, ctx):
        """Pauses the currently playing radio station."""
        state = self.get_voice_state(ctx.message.server)
        if state.radio_playing():
            await self.bot.say('Pausing radio player...')
            player = state.radio_entry.player
            player.pause()
        elif state.youtube_playing():
            self.bot.say('Please pause the youtube music player to resume radio...')
        else:
            self.bot.say('The bot is not playing any radio station...')

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.radio_playing():
            await self.bot.say('Please pause the radio first...')
        elif state.current.player.is_playing():
            await self.bot.say('Music player is already playing...')
        else:
            await self.bot.say('Resuming music player...')
            player = state.player
            player.resume()
            state.video_pauses.append(datetime.datetime.now())
            state.youtube_paused = False

    @commands.command(pass_context=True, no_pm=True)
    async def radio_resume(self, ctx):
        """ Resumes the current radio station."""
        state = self.get_voice_state(ctx.message.server)
        if state.youtube_playing():
            await self.bot.say('Please pause the music player first...')
        elif state.radio_playing():
            await self.bot.say('Radio player is already playing...')
        else:
            await self.bot.say('Resuming radio station player...')

            player = state.radio_entry.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        """Leave channel
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.youtube_playing():
            player = state.player
            player.stop()

        if state.radio_playing():
            player = state.radio_entry.player
            player.stop()

        try:
            state.audio_player.cancel()
            state.radio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except Exception:
            pass

    @commands.command(pass_context=True, no_pm=True, aliases=['skipnow'])
    async def skip(self, ctx):
        """Skip the song without voting
        """
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return
        elif state.radio_playing():
            await self.bot.say('Cannot skip when playing the radio...')
        else:
            await self.bot.say('Skipping song...')
            state.skip()

    @commands.command(pass_context=True, no_pm=True)
    async def playlist(self, ctx, *, page=1):
        """Show all the songs in the queue"""
        state = self.get_voice_state(ctx.message.server)
        if len(state.list) == 0 and state.current is None:
            await self.bot.say('**No song in queue or playing.**')
        elif len(state.list) == 0 and state.current is not None:
            await self.bot.say('Now playing {}. \n\n**No other song in queue.**'.format(state.current))
        else:
            if not self._check_int(page):
                await self.bot.say('**Invalid page value.**')
            else:
                page_number = int(page)
                queue = state.get_song_list()
                max_page = math.ceil(len(queue) / 10)
                if page_number < 0 or max_page < page:
                    message = '**Invalid page number. Please select from page 1 to '+str(max_page)+'.**'
                    await self.bot.say(message)
                else:
                    page_list = [queue[x:x+10] for x in range(0, len(queue), 10)]
                    playlist = "Page: **" + str(page_number) + "** of **" + str(max_page) + "**.\n"

                    for ytv, back_idx in zip(page_list[page_number-1], range(10)):
                        if back_idx == 9:
                            playlist = playlist + '\n `[' + str(page_number) + '0]` ' + str(ytv)
                        else:
                            playlist = playlist + '\n `[' + str(page_number-1) + str(back_idx+1)+']` ' + str(ytv)

                    playlist = playlist + '\n\nThere are **' + str(len(queue)) + '** videos in the queue.'
                    await self.bot.say(playlist)
