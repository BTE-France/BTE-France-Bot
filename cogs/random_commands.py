from discord.ext import commands


class RandomCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief='Check the latency between the bot and the user')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency*1000)}ms')

    @commands.command(aliases=['purge'], brief='Clear the last x messages sent in the channel')
    async def clear(self, ctx, number=5):
        await ctx.channel.purge(limit=number + 1)


def setup(client):
    client.add_cog(RandomCommands(client))
