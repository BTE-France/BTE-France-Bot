from variables import server
import interactions


class Images(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="ban", description="Image Ban", scope=server)
    async def ban(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/RGfJXmZ.png")

    @interactions.extension_command(name="regles", description="Images Lis les règles", scope=server)
    async def regles(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/AP0CD1J.png")

    @interactions.extension_command(name="stonks", description="GIF Stonks", scope=server)
    async def stonks(self, ctx: interactions.CommandContext):
        await ctx.send("https://media2.giphy.com/media/YnkMcHgNIMW4Yfmjxr/giphy.gif")

    @interactions.extension_command(name="triforce", description="Image Triforce", scope=server)
    async def triforce(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/DNxRVsV.png")

    @interactions.extension_command(name="sel", description="Image Sel", scope=server)
    async def sel(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/8RoWypa.png")


def setup(client: interactions.Client):
    Images(client)
