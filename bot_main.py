import os
import random
import asyncio
import discord
import traceback
from music import music
from configs import configs
from utils import maplestory
from discord.ext import commands
from utils.embed_builder import EmbedBuilder

# Instantiate MongoDB database

# Bot Commands

class MikkiBot:
    """ This class manages regular commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['myid'])
    async def get_my_id(self, ctx):
        """ Return full user id of the requester"""
        req_id = ctx.message.author.id
        await self.bot.say(req_id)

    @commands.command(aliases=['fite'])
    async def fiteme(self):
        """
        This command returns a fight me emoji
        :return: string -- (ง •̀_•́)ง
        """
        await self.bot.say("(ง •̀_•́)ง")

    @commands.command(pass_context=True)
    async def change_status(self, ctx, *, game):
        if ctx.message.author.id == configs.OWNER_ID:
            new_game = discord.Game(name=game)
            print(game)
            print(type(self.bot))
            await self.bot.change_status(game=new_game)
        else:
            await self.bot.say('Available for admins only.')

    @commands.command(pass_context=True, aliases=['letmedie', 'pullit', 'pulltheplug'])
    async def pull_the_plug(self, ctx):
        channel = ctx.message.channel
        member = "@" + str(ctx.message.author)
        #em = discord.Embed(title="", description="", color=0xef1b1)
        #em.set_author(name=member)

       # em.set_image(url='https://cdn.discordapp.com/attachments/228002157482213376/281540296292958209/pulltheplug.jpg')

        path = os.path.abspath('images/pulltheplug.jpg')
        await self.bot.send_file(channel, path)

    @commands.command(pass_context=True, aliases=['please'])
    async def pls(self, ctx):
        channel = ctx.message.channel
        path = os.path.abspath('images/pls.png')
        await self.bot.send_file(channel, path)

    @commands.command(pass_context=True, aliases=['ded'])
    async def rip(self, ctx):
        channel = ctx.message.channel
        try:
            path = os.path.abspath('images/rip/' + configs.RIP_LIST[random.randrange(0, configs.RIP_LIST_SIZE)])
            print(path)
            await self.bot.send_file(channel, path)
        except Exception:
            await self.bot.say(traceback.print_exc())

    @commands.command(pass_context=True, aliases=['cs_irl', 'csproblems', 'CSProblems'])
    async def cs_problems(self, ctx):
        channel = ctx.message.channel

        info = dict()
        info['title'] = 'CS Problems'
        info['image'] = 'https://media.giphy.com/media/l3V0el2rHaKdAReyk/giphy.gif'

        em = EmbedBuilder.build(info)
        await self.bot.send_message(channel, embed=em)

    @commands.command(pass_context=True, aliases=['imagetest'])
    async def image_test(self, ctx):
        channel = ctx.message.channel
        await self.bot.send_message(channel, 'http://i.imgur.com/62Mgzr0.gif')

    @commands.command(pass_context=True, aliases=['smugface', 'smugfaces'])
    async def smug_face(self, ctx):
        """
        This command returns a random smug face
        :param ctx: Context of the one who used the command
        :return: a random smug face image
        """
        channel = ctx.message.channel
        try:
            f = os.path.abspath( 'images/smug/' + configs.SMUG_LIST[random.randrange(0, configs.SMUG_LIST_SIZE)])
            print(f)
            await self.bot.send_file(channel, f)
        except Exception:
            await self.bot.say(traceback.print_exc())

    @commands.command(pass_context=True, aliases=['unimpressed', 'link'])
    async def link_face(self, ctx):
        channel = ctx.message.channel
        try:
            f = os.path.abspath('images/link/' + configs.LINK_LIST[random.randrange(0, configs.LINK_LIST_SIZE)])
            print(f)
            await self.bot.send_file(channel, f)
        except Exception:
            await self.bot.say(traceback.print_exc())


    @commands.command(pass_context=True, aliases=['saythis'])
    async def say(self, ctx, *args):
        """
            This command makes the bot say whatever after the command in the channel
        :param ctx: Context of the message
        :param args: String of what is after the command
        :return: Text-To-Speech of the string
        """
        str = ''
        for words in args:
            str = str + ' ' + words
        print(str)
        await self.bot.send_message(ctx.message.channel, str, tts=True )
        await self.bot.purge_from(ctx.message.channel, limit=2)


    @commands.command(pass_context=True, aliases=['deletemessage', 'delete'])
    async def purge(self, ctx, m):
        if m is None:
            p_limit = 100
        else:
            try:
                p_limit = int(m)
                await self.bot.purge_from(ctx.message.channel, limit=p_limit)

            except Exception:
                await self.bot.say('Please input a number.')
                return

    @commands.command()
    async def path_test(self):
        await self.bot.say(os.path.abspath('images/pulltheplug.jpg'))


if __name__ == '__main__':

    description = 'Mikki\'s personal bot at your service.'

    mikkibot = commands.Bot(command_prefix=configs.CLIENT_PREFIX, description=description)

    mikkibot.add_cog(MikkiBot(mikkibot))
    mikkibot.add_cog(music.Music(mikkibot))
    mikkibot.add_cog(maplestory.Maplestory(mikkibot))

    @mikkibot.event
    async def on_ready():
        print('===================')
        print('Logged in as: ')
        print(mikkibot.user.name)
        print(mikkibot.user.id)
        print('===================')

    mikkibot.run(configs.CLIENT_TOKEN)
