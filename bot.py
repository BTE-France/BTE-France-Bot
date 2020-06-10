import os
import discord
from discord.ext import commands
from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready!')

client.run(os.environ['DISCORD_TOKEN'])
