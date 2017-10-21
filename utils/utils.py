import bs4
import urllib
import asyncio
import discord
from discord.ext import commands
class Utils:
    """ Miscellaneous utility command options"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def stock(self, ctx, *, name: str):
        """Return requested stock price"""
        if not name:
            await self.bot.say('Please enter a name for the stock.')
        try:
            url = "https://www.google.com/finance"
            req = urllib.request.Request(url)
            url_full = url + "?" + urllib.parse.urlencode({"q": name})
            req = urllib.request.Request(url_full)
            resp = urllib.request.urlopen(req)
            data = resp.read()

            bs = bs4.BeautifulSoup(data, "html.parser")
            div_price = bs.find(attrs={"id": "price-panel"})
            span_price = div_price.find(attrs={"class": "pr"})
            up = div_price.find(attrs={"class": "ch bld"})

        except Exception as e:
            print(type(e).__name__, '\n', str(e))
            await self.bot.say('Unable to find company stock, please be more specific (i.e. NASDAQ -> NASDAQ Composite')
        pass