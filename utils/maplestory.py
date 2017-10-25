import re
import bs4
import json
import discord
import requests
import urllib.request
from discord.ext import commands
from collections import OrderedDict
from utils.embed_builder import EmbedBuilder


class Maplestory:
    # ========================================= INITIALIZATION =========================================
    def __init__(self, bot):
        self.bot = bot
        self.explorer = ['beginner', 'warrior', 'magician', 'bowman', 'thief', 'pirate']
        self.cygnus = ['noblesse', 'dawn warrior', 'blaze wizard', 'wind archer', 'night walker', 'thunder breaker']
        self.resistance = ['citizen', 'demon slayer', 'battle mage', 'wild hunter', 'mechanic']
        self.sengoku = ['hayato', 'kanna']

    # ============================================ COMMANDS ============================================

    @commands.command(pass_context=True, no_pm=True, aliases=['msearch', 'ms'])
    async def maple_search(self, ctx, *, player_name: str = ''):
        if not player_name:
            await self.bot.say('Please input a name')
            return

        info = self._search_player(player_name)
        if not info: # No player found
            info['title'] = 'No player found!'

        em = EmbedBuilder.build(info)
        await self.bot.send_message(ctx.message.channel, embed=em)

    # ======================================== COMMAND HANDLERS ========================================

    def _search_player(self, player_name):
        info = {}
        url = "http://maplestory.nexon.net/rankings/overall-ranking/legendary?" \
              "pageIndex=1&character_name="+player_name+"&search=true#ranking"

        source = requests.get(url)

        soup = bs4.BeautifulSoup(source.text, 'html.parser')

        info = dict()
        extra = None

        ign = None
        ranking = None
        thumbnail = None
        server = None
        job = None

        found = False

        for tr in soup.find_all('tr'):
            if player_name.lower() in tr.text.lower():
                td = tr.find_all('td')

                ranking = str(td[0].string).strip()               # Ranking
                thumbnail = td[1].find('img')['src']              # Avatar Image
                ign = td[2].string                                # IGN
                server = td[3].find('a')['title']                 # Server
                job = td[4].find('img')['title']                  # Job / Class

                level = re.findall(r"[\w']+", (str(td[5].text)))  # Level - Exp - Move
                level_string = level[0] + '(' + level[1] + ')'

                # Setting up general info
                info['thumbnail'] = thumbnail

                # Setting up additional field

                extra = \
                    [
                        ('Name', {'value': ign,
                                  'inline': True}),

                        ('Job', {'value': job,
                                 'inline': True}),
                        ('Level', {'value': level_string,
                                   'inline': True}),

                        ('World', {'value': server,
                                   'inline': True}),

                        ('Overall Rank', {'value': ranking,
                                          'inline': True}),

                    ]
                found = True
                break

        if found:  # Character on ranking

            # Find World Ranking
            url = "http://maplestory.nexon.net/rankings/world-ranking/"+server+"?" \
                        "pageIndex=1&character_name="+player_name+"&search=true#ranking"

            source = requests.get(url)

            soup = bs4.BeautifulSoup(source.text, 'html.parser')

            for tr in soup.find_all('tr'):
                if player_name.lower() in tr.text.lower():
                    td = tr.find_all('td')
                    extra.append(
                        ('World Rank', {'value': str(td[0].string).strip(),
                         'inline': True})
                    )
                    break

            # Find Job Ranking

            classification = None
            job_filtered = job.strip().replace(' ', '-')

            if job in self.explorer:
                classification = 'explorer'
            elif job in self.cygnus:
                classification = 'cygnus-knights'
            elif job in self.resistance:
                classification = 'resistance'
            elif job in self.sengoku:
                classification = 'sengoku'
            else:
                classification = job_filtered

            url = "http://maplestory.nexon.net/rankings/job-ranking/"+classification+"/"+job_filtered+"?" \
                  "pageIndex=1&character_name="+player_name+"&search=true#ranking"

            source = requests.get(url)

            soup = bs4.BeautifulSoup(source.text, 'html.parser')

            for tr in soup.find_all('tr'):
                if player_name.lower() in tr.text.lower():
                    td = tr.find_all('td')
                    extra.append(
                        ('Job Rank', {'value': str(td[0].string).strip(),
                                      'inline': True})
                    )
                    break

            # Find Legion Ranking

            url = "http://maplestory.nexon.net/rankings/legion/"+server+"?pageIndex=1&character_name="+player_name+"&" \
                                                                        "search=true#ranking"

            source = requests.get(url)

            soup = bs4.BeautifulSoup(source.text, 'html.parser')

            for tr in soup.find_all('tr'):
                if player_name.lower() in tr.text.lower():
                    td = tr.find_all('td')
                    rank_value = None
                    try:
                        l_rank = td[0].find('img')['src']
                        rank_value = l_rank[-5]
                    except Exception:
                        pass
                        rank_value = str(td[0].string).strip()

                    extra.append(
                        ('Legion Rank', {'value': rank_value,
                         'inline': True})
                    )
                    break
                else:
                    extra.append(
                        ('Legion Rank', {'value': 'N/A',
                         'inline': True})
                    )

            info['extra'] = OrderedDict(extra)

        return info
