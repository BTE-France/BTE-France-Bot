import asyncio

import interactions

import variables
from utils.embed import create_embed, create_info_embed


class RandomCommands(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.guild = await self.bot.fetch_guild(variables.SERVER)
        self.logs_channel = await self.bot.fetch_channel(variables.Channels.LOGS)

    @interactions.slash_command(name="ping", scopes=[])
    async def ping(self, ctx: interactions.SlashContext):
        "Ping"
        await ctx.send(
            embeds=create_info_embed(f"Pong! {int(self.bot.latency)}ms."),
            ephemeral=True,
        )

    @interactions.slash_command(name="clear")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    @interactions.slash_option(
        name="number",
        description="Nombre de messages à supprimer",
        opt_type=interactions.OptionType.INTEGER,
    )
    async def clear(self, ctx: interactions.SlashContext, number: int = 1):
        "Supprimer les x derniers messages"
        await ctx.channel.purge(deletion_limit=number)
        await ctx.send(
            embeds=create_info_embed(
                f"Tu as supprimé les {number} dernier(s) message(s)!"
            ),
            ephemeral=True,
        )

    @interactions.context_menu(
        name="Supprimer messages après", context_type=interactions.CommandType.MESSAGE
    )
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def clear_after(self, ctx: interactions.ContextMenuContext):
        messages = await ctx.channel.history(limit=100, after=ctx.target_id).flatten()
        number = len(messages) + 1
        await ctx.channel.purge(deletion_limit=number)
        await ctx.send(
            embeds=create_info_embed(
                f"Tu as supprimé les {number} dernier(s) message(s)!"
            ),
            ephemeral=True,
        )

    @interactions.slash_command(name="map")
    async def map(self, ctx: interactions.SlashContext):
        "Lien Maps BTE"
        await ctx.send(
            embeds=create_embed(
                title="Maps de BTE",
                description="""[**Carte Dynmap**](https://map.btefrance.fr/)
            _Carte qui permet de voir les constructions les plus notables du serveur, avec une vue satellite._

            [**Carte des projets**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)
            _Carte de progression qui permet de recenser toutes les constructions sur le serveur._""",
                color=0x00FF00,
                include_thumbnail=True,
            )
        )

    @interactions.slash_command(name="lire")
    async def lire(self, ctx: interactions.SlashContext):
        "Lis les règles"
        await ctx.send(
            embeds=create_info_embed(
                f"As-tu bien lu le salon <#{variables.Channels.COMMENT_REJOINDRE}>?"
            )
        )

    @interactions.slash_command(name="builder")
    async def builder(self, ctx: interactions.SlashContext):
        "Instructions pour devenir Builder"
        await ctx.send(
            embeds=create_info_embed(
                "Tu veux savoir comment devenir builder officiel? [**C'est par ici!**](https://docs.google.com/document/d/1DHMOEcmepY_jGlS_-tvCvpJmSbaoHmofnamTJleQYik/edit?usp=sharing)"
            )
        )

    @interactions.listen(interactions.events.BanCreate)
    async def on_guild_ban_add(self, _):
        await asyncio.sleep(3)  # Leave some time for the audit log to be updated
        audit_logs = await self.guild.fetch_audit_log(
            action_type=interactions.AuditLogEventType.MEMBER_BAN_ADD, limit=1
        )
        audit_log_entry = audit_logs.entries[0]
        mod_user = next(
            (user for user in audit_logs.users if user.id == audit_log_entry.user_id),
            None,
        )

        if not mod_user.bot:
            banned_user = next(
                (
                    user
                    for user in audit_logs.users
                    if user.id == audit_log_entry.target_id
                ),
                None,
            )
            await self.logs_channel.send(
                embeds=create_info_embed(
                    f"**{banned_user.username}#{banned_user.discriminator} a été banni par {mod_user.mention} pour la raison suivante:**\n{audit_log_entry.reason}"
                )
            )
