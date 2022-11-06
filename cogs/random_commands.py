from utils.embed import create_embed, create_info_embed
from variables import server, comment_rejoindre_channel, logs_channel
import interactions
import string


class RandomCommands(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_listener()
    async def on_start(self):
        self.guild: interactions.Guild = await interactions.get(self.client, interactions.Guild, object_id=server)
        self.logs_channel = await interactions.get(self.client, interactions.Channel, object_id=logs_channel)

    @interactions.extension_command(name="clear", description="Supprimer les x derniers messages", default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    @interactions.option("Nombre de messages à supprimer")
    async def clear(self, ctx: interactions.CommandContext, number: int = 1):
        channel = await ctx.get_channel()
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"Tu as supprimé les {number} dernier(s) message(s)!"
        ), ephemeral=True)

    @interactions.extension_message_command(name="Supprimer messages après", default_member_permissions=interactions.Permissions.MANAGE_MESSAGES)
    async def clear_after(self, ctx: interactions.CommandContext):
        channel = await ctx.get_channel()
        messages = await self.client._http.get_channel_messages(channel_id=int(ctx.channel_id), limit=100, after=int(ctx.target.id))
        number = len(messages) + 1
        await channel.purge(amount=number)
        await ctx.send(embeds=create_info_embed(
            f"Tu as supprimé les {number} dernier(s) message(s)!"
        ), ephemeral=True)

    @interactions.extension_command(name="map", description="Lien Maps BTE")
    async def map(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Maps de BTE",
            description="[**Map internationale**](https://buildtheearth.net/map)\n\n[**Map française**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)",
            color=0x00FF00
        ))

    @interactions.extension_command(name="lire", description="Lis les règles")
    async def lire(self, ctx: interactions.CommandContext):
        channel = await interactions.get(self.client, interactions.Channel, object_id=comment_rejoindre_channel)
        await ctx.send(embeds=create_info_embed(
            f"As-tu bien lu le salon {channel.mention}?"
        ))

    @interactions.extension_listener()
    async def on_guild_ban_add(self, _):
        audit_logs = await self.guild.get_latest_audit_log_action(interactions.AuditLogEvents.MEMBER_BAN_ADD)
        audit_log_entry = audit_logs.audit_log_entries[0]
        mod_user = interactions.search_iterable(audit_logs.users, lambda user: int(user.id) == int(audit_log_entry.user_id))[0]

        if not mod_user.bot:
            banned_user = interactions.search_iterable(audit_logs.users, lambda user: int(user.id) == int(audit_log_entry.target_id))[0]
            await self.logs_channel.send(embeds=create_info_embed(
                f"**{banned_user.username}#{banned_user.discriminator} a été banni par {mod_user.mention} pour la raison suivante:**\n{audit_log_entry.reason}"
            ))

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
