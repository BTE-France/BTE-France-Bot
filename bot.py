import discord
from discord.ext import commands

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready!')

client.run('NzIwMzgzMDk5Njg2NjE3MTE4.XuFLWg.la17vTnNnpYndTCban1bgxwWwRE')
