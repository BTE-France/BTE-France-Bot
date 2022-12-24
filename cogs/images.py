import interactions


class Images(interactions.Extension):
    @interactions.extension_command(name="ban", description="Image Ban")
    async def ban(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/RGfJXmZ.png")

    @interactions.extension_command(name="regles", description="Images Lis les règles")
    async def regles(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/AP0CD1J.png")

    @interactions.extension_command(name="stonks", description="GIF Stonks")
    async def stonks(self, ctx: interactions.CommandContext):
        await ctx.send("https://media2.giphy.com/media/YnkMcHgNIMW4Yfmjxr/giphy.gif")

    @interactions.extension_command(name="triforce", description="Image Triforce")
    async def triforce(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/DNxRVsV.png")

    @interactions.extension_command(name="sel", description="Image Sel")
    async def sel(self, ctx: interactions.CommandContext):
        await ctx.send("https://i.imgur.com/8RoWypa.png")


def setup(client: interactions.Client):
    Images(client)
