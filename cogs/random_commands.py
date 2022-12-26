import asyncio

import interactions

import variables
from utils.embed import create_embed, create_info_embed


class RandomCommands(interactions.Extension):
    @interactions.extension_listener()
    async def on_start(self):
        self.guild: interactions.Guild = await interactions.get(self.client, interactions.Guild, object_id=variables.SERVER)
        self.logs_channel = await interactions.get(self.client, interactions.Channel, object_id=variables.Channels.LOGS)

    @interactions.extension_command(name="ping", description="Ping", default_scope=False)
    async def ping(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_info_embed(f"Pong! {int(self.client.latency)}ms."), ephemeral=True)

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
            description="""[**Carte Dynmap**](https://map.btefrance.fr/)
            _Carte qui permet de voir les constructions les plus notables du serveur, avec une vue satellite._

            [**Carte des projets**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)
            _Carte de progression qui permet de recenser toutes les constructions sur le serveur._""",
            color=0x00FF00,
            include_thumbnail=True
        ))

    @interactions.extension_command(name="lire", description="Lis les règles")
    async def lire(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_info_embed(
            f"As-tu bien lu le salon <#{variables.Channels.COMMENT_REJOINDRE}>?"
        ))

    @interactions.extension_listener()
    async def on_guild_ban_add(self, _):
        await asyncio.sleep(3)  # Leave some time for the audit log to be updated
        audit_logs = await self.guild.get_latest_audit_log_action(interactions.AuditLogEvents.MEMBER_BAN_ADD)
        audit_log_entry = audit_logs.audit_log_entries[0]
        mod_user = interactions.search_iterable(audit_logs.users, lambda user: int(user.id) == int(audit_log_entry.user_id))[0]

        if not mod_user.bot:
            banned_user = interactions.search_iterable(audit_logs.users, lambda user: int(user.id) == int(audit_log_entry.target_id))[0]
            await self.logs_channel.send(embeds=create_info_embed(
                f"**{banned_user.username}#{banned_user.discriminator} a été banni par {mod_user.mention} pour la raison suivante:**\n{audit_log_entry.reason}"
            ))


def setup(client: interactions.Client):
    RandomCommands(client)
