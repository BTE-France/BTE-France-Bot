from utils.embed import create_embed
from variables import server
import interactions


class RandomCommands(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="clear", description="Clear x last messages", scope=server, options=[
        interactions.Option(type=interactions.OptionType.INTEGER, name="number", description="Number of messages to clear")
    ])
    async def clear(self, ctx: interactions.CommandContext, number: int = 1):
        channel = interactions.Channel(**await self.client._http.get_channel(int(ctx.channel_id)))
        await channel.purge(amount=number + 1)

    @interactions.extension_command(name="map", description="BTE map link", scope=server)
    async def map(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Map du Projet BTE",
            description="https://buildtheearth.net/map",
            color=0x00FF00
        ))


def setup(client: interactions.Client):
    RandomCommands(client)
