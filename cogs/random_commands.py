import asyncio
from utils.embed import create_embed, create_info_embed
from variables import server, comment_rejoindre_channel, logs_channel
import interactions


class RandomCommands(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="clear", description="Clear x last messages", scope=server, default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    @interactions.option("Number of messages to clear")
    async def clear(self, ctx: interactions.CommandContext, number: int = 1):
        channel = await ctx.get_channel()
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"You have purged the last {number} messages!"
        ), ephemeral=True)

    @interactions.extension_message_command(name="Clear all messages after", scope=server, default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    async def clear_after(self, ctx: interactions.CommandContext):
        channel = await ctx.get_channel()
        messages = await self.client._http.get_channel_messages(channel_id=int(ctx.channel_id), limit=100, after=int(ctx.target.id))
        number = len(messages) + 1
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"You have purged the last {number} messages!"
        ), ephemeral=True)

    @interactions.extension_command(name="map", description="BTE map link", scope=server)
    async def map(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Maps de BTE",
            description="[**Map internationale**](https://buildtheearth.net/map)\n\n[**Map française**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)",
            color=0x00FF00
        ))

    @interactions.extension_command(name="lire", description="Read the rules", scope=server)
    async def lire(self, ctx: interactions.CommandContext):
        channel = await interactions.get(self.client, interactions.Channel, object_id=comment_rejoindre_channel)
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
        await asyncio.sleep(3)  # Leave some time for the audit log to be updated
        audit_log = await self.client._http.get_guild_auditlog(server, action_type=22, limit=5)
        for entry in audit_log["audit_log_entries"]:
            if int(entry["target_id"]) == int(guild_ban.user.id):
                mod_user: interactions.User = await interactions.get(self.client, interactions.User, object_id=entry["user_id"])
                if not mod_user.bot:
                    channel = await interactions.get(self.client, interactions.Channel, object_id=logs_channel)
                    await channel.send(f"**{guild_ban.user.username}#{guild_ban.user.discriminator} was banned by {mod_user.username}#{mod_user.discriminator} for the following reason:**\n{entry['reason']}")
                return


def setup(client: interactions.Client):
    RandomCommands(client)
