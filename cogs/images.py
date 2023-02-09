import interactions


class Images(interactions.Extension):
    @interactions.slash_command(name="ban")
    async def ban(self, ctx: interactions.SlashContext):
        "Image Ban"
        await ctx.send("https://i.imgur.com/RGfJXmZ.png")

    @interactions.slash_command(name="regles")
    async def regles(self, ctx: interactions.SlashContext):
        "Images Lis les règles"
        await ctx.send("https://i.imgur.com/AP0CD1J.png")

    @interactions.slash_command(name="stonks")
    async def stonks(self, ctx: interactions.SlashContext):
        "GIF Stonks"
        await ctx.send("https://media2.giphy.com/media/YnkMcHgNIMW4Yfmjxr/giphy.gif")

    @interactions.slash_command(name="triforce")
    async def triforce(self, ctx: interactions.SlashContext):
        "Image Triforce"
        await ctx.send("https://i.imgur.com/DNxRVsV.png")

    @interactions.slash_command(name="sel")
    async def sel(self, ctx: interactions.SlashContext):
        "Image Sel"
        await ctx.send("https://i.imgur.com/8RoWypa.png")
