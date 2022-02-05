from utils.embed import create_embed, create_info_embed
from variables import server, comment_rejoindre_channel
import interactions


class RandomCommands(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="clear", description="Clear x last messages", scope=server, options=[
        interactions.Option(type=interactions.OptionType.INTEGER, name="number", description="Number of messages to clear")
    ])
    async def clear(self, ctx: interactions.CommandContext, number: int = 1):
        channel: interactions.Channel = await ctx.get_channel()
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"You have purged the last {number} messages!"
        ), ephemeral=True)

    @interactions.extension_command(name="map", description="BTE map link", scope=server)
    async def map(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Map du Projet BTE",
            description="https://buildtheearth.net/map",
            color=0x00FF00
        ))

    @interactions.extension_command(name="bedrock", description="Bedrock tutorial", scope=server)
    async def bedrock(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Comment rejoindre BTE quand on joue sur Bedrock?",
            description="https://docs.google.com/document/d/12QG9d_O2ZX-OH9CdC44urpfWCnSmSon4nhsSXyuuGsM/edit?usp=drivesdk",
            color=0x0800FF
        ))

    @interactions.extension_command(name="lire", description="Read the rules", scope=server)
    async def lire(self, ctx: interactions.CommandContext):
        channel = interactions.Channel(**await self.client._http.get_channel(comment_rejoindre_channel))
        await ctx.send(embeds=create_info_embed(
            f"As-tu bien lu le salon {channel.mention}?"
        ))

    @interactions.extension_command(name="ip", description="IPs list", scope=server)
    async def ip(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="IPs de BTE: France",
            description=":arrow_right: Version Java: `buildtheearth.net`, puis `/bt FR` quand vous êtes dans le lobby\n:arrow_right: Version Bedrock: `bedrock.buildtheearth.net`, port `19132`.",
            color=0x0800FF
        ))

    @interactions.extension_listener()
    async def on_guild_ban_add(self, guild_ban: interactions.GuildBan):
        logs_channel = 347310057853026305
        channel = interactions.Channel(**await self.client._http.get_channel(logs_channel), _client=self.client._http)
        for ban in await self.client._http.get_guild_bans(guild_ban.guild_id):
            banned_user: interactions.User = interactions.User(**ban["user"])
            if int(banned_user.id) == int(guild_ban.user.id) and not banned_user.bot:
                await channel.send(f"**{banned_user.username}#{banned_user.discriminator} banned for the following reason:**\n{ban['reason']}")
                return


def setup(client: interactions.Client):
    RandomCommands(client)
