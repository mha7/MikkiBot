import discord
import secrets
from discord.ext import commands
import music
import random

bot = commands.Bot(command_prefix="~")
bot.add_cog(music.Music(bot))


@bot.event
async def on_ready():
    print('===================')
    print('Logged in as: ')
    print(bot.user.name)
    print(bot.user.id)
    print('===================')


@bot.command(aliases=['fite'])
async def fiteme():
    """
    This command returns a fight me emoji
    :return: string -- (ง •̀_•́)ง
    """
    return await bot.say("(ง •̀_•́)ง")

async def robert():
    """
    This command return a random quote of robert
    :return: string
    """
    pass

@bot.command(pass_context=True, aliases=['letmedie', 'pullit', 'pulltheplug'])
async def pull_the_plug(ctx):
    channel = ctx.message.channel
    return await bot.send_file(channel, 'images/pulltheplug.jpg')

@bot.command(pass_context=True, aliases=['imagetest'])
async def image_test(ctx):
    channel = ctx.message.channel
    return await bot.send_file(channel, 'http://i.imgur.com/62Mgzr0.gif')

@bot.command(pass_context=True, aliases=['smugface', 'smugfaces'])
async def smug_face(ctx):
    """
    This command returns a random smug face
    :param ctx: Context of the one who used the command
    :return: a random smug face image
    """
    channel = ctx.message.channel
    f = 'images/smug/' + secrets.SMUG_LIST[random.randrange(0, secrets.SMUG_LIST_SIZE)]
    print(f)
    return await bot.send_file(channel, f)

@bot.command(pass_context=True, aliases=['saythis'])
async def say(ctx, *args):
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
    await bot.send_message(ctx.message.channel, str, tts=True )
    return await bot.purge_from(ctx.message.channel, limit=2)

@bot.command(pass_context=True, aliases=['deletemessage', 'delete'])
async def purge(ctx, m):
    if m is None:
        p_limit = 100
    else:
        try:
            p_limit = int(m)
        except Exception:
            return await bot.say('Please put in a number')

    return await bot.purge_from(ctx.message, limit=p_limit)

bot.run(secrets.CLIENT_TOKEN)