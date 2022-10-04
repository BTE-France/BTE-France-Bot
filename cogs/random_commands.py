import asyncio
from utils.embed import create_embed, create_info_embed
from variables import server, comment_rejoindre_channel, logs_channel
import interactions
import string


class RandomCommands(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="clear", description="Supprimer les x derniers messages", scope=server, default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    @interactions.option("Nombre de messages à supprimer")
    async def clear(self, ctx: interactions.CommandContext, number: int = 1):
        channel = await ctx.get_channel()
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"You have purged the last {number} messages!"
        ), ephemeral=True)

    @interactions.extension_message_command(name="Supprimer messages après", scope=server, default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    async def clear_after(self, ctx: interactions.CommandContext):
        channel = await ctx.get_channel()
        messages = await self.client._http.get_channel_messages(channel_id=int(ctx.channel_id), limit=100, after=int(ctx.target.id))
        number = len(messages) + 1
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"You have purged the last {number} messages!"
        ), ephemeral=True)

    @interactions.extension_command(name="map", description="Lien Maps BTE", scope=server)
    async def map(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Maps de BTE",
            description="[**Map internationale**](https://buildtheearth.net/map)\n\n[**Map française**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)",
            color=0x00FF00
        ))

    @interactions.extension_command(name="lire", description="Lis les règles", scope=server)
    async def lire(self, ctx: interactions.CommandContext):
        channel = await interactions.get(self.client, interactions.Channel, object_id=comment_rejoindre_channel)
        await ctx.send(embeds=create_info_embed(
            f"As-tu bien lu le salon {channel.mention}?"
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
                    await channel.send(f"**{guild_ban.user.username}#{guild_ban.user.discriminator} a été banni par {mod_user.username}#{mod_user.discriminator} pour la raison suivante:**\n{entry['reason']}")
                return

    @interactions.extension_listener()
    async def on_message_create(self, message: interactions.Message):
        if not message.content or message.author.bot:
            return

        words = ("quoi", "koi")
        text = message.content.lower()

        if not any([word in text for word in words]):
            return
        text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
        last_word = text.split()[-1]

        if last_word in words:
            await message.reply(stickers=[interactions.Sticker(id=1026620857767956551)])


def setup(client: interactions.Client):
    RandomCommands(client)
