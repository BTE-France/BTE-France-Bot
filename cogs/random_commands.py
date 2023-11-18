import asyncio
from datetime import timedelta

import interactions

import variables
from utils import create_embed, create_error_embed, create_info_embed

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
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    @interactions.slash_option(
        name="number",
        description="Nombre de messages à supprimer",
        opt_type=interactions.OptionType.INTEGER,
        min_value=1,
        max_value=100,
    )
    async def clear(self, ctx: interactions.SlashContext, number: int = 1):
        "Supprimer les x derniers messages"
        messages = await ctx.channel.history(limit=number).flatten()
        after = messages[-1].id
        number = len(messages)
        await self._clear(ctx, number, after)

    @interactions.message_context_menu(name="Supprimer messages après")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def clear_after(self, ctx: interactions.ContextMenuContext):
        after = ctx.target_id
        messages = await ctx.channel.history(limit=99, after=after).flatten()
        number = len(messages) + 1
        await self._clear(ctx, number, after)

    async def _clear(
        self,
        ctx: interactions.SlashContext | interactions.ContextMenuContext,
        number: int,
        after: interactions.Snowflake,
    ):
        n = await ctx.channel.purge(deletion_limit=number)  # n = actual number of messages deleted
        if n == number:
            return await ctx.send(
                embeds=create_info_embed(f"✅ Tu as supprimé les {n} dernier(s) message(s)!"),
                ephemeral=True,
            )

        confirm_button = interactions.Button(
            style=interactions.ButtonStyle.GREEN,
            emoji="✅",
            label="Oui",
        )
        await ctx.send(
            embeds=create_info_embed(
                f"Message(s) supprimé(s): {n}\n{number - n} message(s) n'ont pas été supprimés car ils datent d'il y a plus de 14 jours.\nVeux-tu quand même les supprimer? **⚠️ Peut durer longtemps ⚠️**"
            ),
            components=confirm_button,
            ephemeral=True,
        )

        delete_messages = False
        try:
            component = await self.bot.wait_for_component(components=confirm_button, timeout=30)
            delete_messages = True
        except asyncio.TimeoutError:
            pass

        # Small hack to delete the ephemeral clear confirm message
        await self.bot.http.delete_interaction_message(self.bot.app.id, ctx.token)

        if delete_messages:
            if not component.ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
                return await component.ctx.send(
                    embeds=create_error_embed(
                        f"❌ Seuls les administrateurs peuvent supprimer les messages qui datent d'il y a plus de 14 jours!"
                    ),
                    ephemeral=True,
                )

            await component.ctx.defer(ephemeral=True)
            await self.bot.http.delete_message(ctx.channel_id, after)
            async for message in ctx.channel.history(after=after):
                await self.bot.http.delete_message(ctx.channel_id, message.id)
            return await component.ctx.send(
                embeds=create_info_embed(f"✅ Tu as supprimé les {number} dernier(s) message(s)!"),
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

    @interactions.slash_command(name="bte")
    async def bte(self, ctx: interactions.SlashContext):
        "Lien Discord BTE"
        await ctx.send("https://discord.gg/GTQf7BqX2e")

    @interactions.slash_command(name="lire")
    async def lire(self, ctx: interactions.SlashContext):
        "Lis les règles"
        await ctx.send(embeds=create_info_embed(f"As-tu bien lu le salon <#{variables.Channels.DEBUTEZ_ICI}>?"))

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
                (user for user in audit_logs.users if user.id == audit_log_entry.target_id),
                None,
            )
            await event.guild.get_channel(variables.Channels.LOGS).send(
                embeds=create_info_embed(
                    f"**{banned_user.tag} a été banni par {mod_user.mention} pour la raison suivante:**\n{audit_log_entry.reason}"
                )
            )

    @interactions.message_context_menu(name="Copier message")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def copy(self, ctx: interactions.ContextMenuContext):
        await ctx.send(f"```{ctx.target.content}```", ephemeral=True)

    @interactions.slash_command(name="role")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def role(self, ctx: interactions.SlashContext):
        ...

    @role.subcommand("social")
    async def role_social(self, ctx: interactions.SlashContext):
        msg = await ctx.channel.send(
            f"Si tu souhaites recevoir le rôle <@&{variables.Roles.SOCIAL}>, clique dessous!",
            components=interactions.Button(
                style=interactions.ButtonStyle.GREEN,
                label="Recevoir rôle Social",
                custom_id="role_social",
            ),
            allowed_mentions=interactions.AllowedMentions(),
        )
        await ctx.send(embed=create_info_embed(f"Message envoyé: {msg.jump_url}"), ephemeral=True)

    @interactions.component_callback("role_social")
    async def on_role_social_button(self, ctx: interactions.ComponentContext):
        if variables.Roles.SOCIAL in ctx.author.roles:
            await ctx.author.remove_role(variables.Roles.SOCIAL)
            await ctx.send(
                embeds=create_info_embed("Tu n'as plus le rôle Social."),
                ephemeral=True,
            )
        else:
            await ctx.author.add_role(variables.Roles.SOCIAL)
            await ctx.send(
                embeds=create_info_embed("Tu as reçu le rôle Social!"),
                ephemeral=True,
            )

    @role.subcommand("event")
    async def role_event(self, ctx: interactions.SlashContext):
        msg = await ctx.channel.send(
            f"Si tu souhaites recevoir le rôle <@&{variables.Roles.EVENT}>, clique dessous!",
            components=interactions.Button(
                style=interactions.ButtonStyle.GREEN,
                label="Recevoir rôle Event",
                custom_id="role_event",
            ),
            allowed_mentions=interactions.AllowedMentions(),
        )
        await ctx.send(embed=create_info_embed(f"Message envoyé: {msg.jump_url}"), ephemeral=True)

    @interactions.component_callback("role_event")
    async def on_role_event_button(self, ctx: interactions.ComponentContext):
        if variables.Roles.EVENT in ctx.author.roles:
            await ctx.author.remove_role(variables.Roles.EVENT)
            await ctx.send(
                embeds=create_info_embed("Tu n'as plus le rôle Event."),
                ephemeral=True,
            )
        else:
            await ctx.author.add_role(variables.Roles.EVENT)
            await ctx.send(
                embeds=create_info_embed("Tu as reçu le rôle Event!"),
                ephemeral=True,
            )

    @interactions.slash_command(name="pingn")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
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
