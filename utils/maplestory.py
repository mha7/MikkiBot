import re
import bs4
import json
import discord
import urllib.request
from discord.ext import commands
from collections import OrderedDict
from utils.embed_builder import EmbedBuilder


class Maplestory:
    # ========================================= INITIALIZATION =========================================
    def __init__(self, bot):
        self.bot = bot

    # ============================================ COMMANDS ============================================

    @commands.command(pass_context=True, no_pm=True, aliases=['msearch', 'ms'])
    async def maple_search(self, ctx, *, player_name: str = ''):
        if not player_name:
            await self.bot.say('Please input a name')
            return

        info = self._search_player(player_name)
        if not player_name: # No player found
            await self.bot.say('Unable to find the player: ' + player_name)
        else:
            em = EmbedBuilder.build(info)
            await self.bot.send_message(ctx.message.channel, embed=em)

    # ======================================== COMMAND HANDLERS ========================================

    def _search_player(self, player_name):
        info = {}
        url = "http://maplestory.nexon.net/rankings/overall-ranking/legendary?" \
              "pageIndex=1&character_name="+player_name+"&search=true#ranking"

        source = urllib.request.urlopen(url).read()

        soup = bs4.BeautifulSoup(source, 'html.parser')

        info = dict()
        for tr in soup.find_all('tr'):

            if player_name in tr.text.lower():
                td = tr.find_all('td')

                ranking = str(td[0].string).strip()               # Ranking
                thumbnail = td[1].find('img')['src']              # Avatar Image
                ign = td[2].string                                # IGN
                server = td[3].find('a')['title']                 # Server
                job = td[4].find('img')['title']                  # Job / Class

                level = re.findall(r"[\w']+", (str(td[5].text)))  # Level - Exp - Move
                level_string = level[0] + '(' + level[1] + ')'

                # Setting up general info
                info['title'] = 'Maplestory Character Search'
                info['url'] = url
                info['description'] = ign
                info['thumbnail'] = thumbnail

                # Setting up additional field

                extra = OrderedDict(
                    [
                        ('Server', {'value': server,
                                    'inline': True}),
                        ('Rank', {'value': ranking,
                                  'inline': True}),
                        ('Job', {'value': job,
                                 'inline': True}),
                        ('Level', {'value': level_string,
                                   'inline': True})

                    ]
                )

                info['extra'] = extra

                break

        return info
