import asyncio
from datetime import timedelta

import interactions

import variables
from utils import create_embed, create_info_embed

NEW_WORD_MODAL = interactions.Modal(
    interactions.ParagraphText(
        label="Texte",
        custom_id="text",
    ),
    title="Word",
    custom_id="new_word_modal",
)
WORD_MODAL = interactions.Modal(
    interactions.ParagraphText(
        label="Texte",
        custom_id="text",
    ),
    title="Word",
    custom_id="word_modal",
)
EDIT_WORD_BUTTON = interactions.Button(
    label="Editer",
    custom_id="word_edit",
    emoji="⚙️",
    style=interactions.ButtonStyle.SUCCESS,
)


class RandomCommands(interactions.Extension):
    @interactions.slash_command(name="ping")
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
        min_value=1,
        max_value=100,
    )
    async def clear(self, ctx: interactions.SlashContext, number: int = 1):
        "Supprimer les x derniers messages"
        n = await ctx.channel.purge(deletion_limit=number)
        await ctx.send(
            embeds=create_info_embed(f"Tu as supprimé les {n} dernier(s) message(s)!"),
            ephemeral=True,
        )

    @interactions.message_context_menu(name="Supprimer messages après")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def clear_after(self, ctx: interactions.ContextMenuContext):
        messages = await ctx.channel.history(limit=99, after=ctx.target_id).flatten()
        number = len(messages) + 1
        n = await ctx.channel.purge(deletion_limit=number)
        await ctx.send(
            embeds=create_info_embed(f"Tu as supprimé les {n} dernier(s) message(s)!"),
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
                f"As-tu bien lu le salon <#{variables.Channels.DEBUTEZ_ICI}>?"
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
    async def on_guild_ban_add(self, event: interactions.events.BanCreate):
        await asyncio.sleep(3)  # Leave some time for the audit log to be updated
        audit_logs = await event.guild.fetch_audit_log(
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
            await event.guild.get_channel(variables.Channels.LOGS).send(
                embeds=create_info_embed(
                    f"**{banned_user.tag} a été banni par {mod_user.mention} pour la raison suivante:**\n{audit_log_entry.reason}"
                )
            )

    @interactions.message_context_menu(name="Copier message")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def copy(self, ctx: interactions.ContextMenuContext):
        await ctx.send(f"```{ctx.target.content}```", ephemeral=True)

    @interactions.slash_command(name="pingn")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def pingn(self, ctx: interactions.SlashContext):
        """Ping tous les nouveaux"""
        now = interactions.Timestamp.utcnow()
        newbies = []
        for member in ctx.guild.members:
            if now - member.joined_at < timedelta(days=1):
                newbies.append(member)
        if not newbies:
            return await ctx.send(
                embed=create_info_embed("Aucun nouveau membre trouvé!"),
                ephemeral=True,
            )

        send_button = interactions.Button(
            style=interactions.ButtonStyle.GRAY,
            custom_id="newbies_ping",
            label="Ping tous les nouveaux",
        )
        user_ids_string = " ".join([member.mention for member in newbies])
        await ctx.send(f"`{user_ids_string}`", components=send_button, ephemeral=True)

        try:
            await self.bot.wait_for_component(components=send_button, timeout=30)
            await ctx.channel.send(
                f"{user_ids_string} **Bienvenue sur le serveur BTE France!** Pour visiter ou construire, n'hésitez pas à lire <#{variables.Channels.DEBUTEZ_ICI}>!"
            )
        except asyncio.TimeoutError:
            pass
        # Small hack to delete the ephemeral /pingn message
        await self.bot.http.delete_interaction_message(self.bot.app.id, ctx.token)
