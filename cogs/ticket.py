import re
from dataclasses import dataclass
from typing import Coroutine

import interactions

import variables
from utils import (
    BROADCAST_PROMOTE_MESSAGE,
    RANK_DICT,
    create_embed,
    create_error_embed,
    create_info_embed,
    escape_minecraft_username_markdown,
    log,
    lp_add_node_to_user,
    lp_get_user,
    lp_lookup_user,
    lp_promote_user,
    lp_search_nodes,
    minecraft_username_to_uuid,
)

TICKET_CREATION_MSG = """# 📨  Tickets

> Ici vous pouvez créer une demande privée, entre le staff et vous.

### Pour cela, cliquez sur le bouton `Créer un ticket`, vous avez trois choix :

## <:upvote:748611592517583021>  Promotion
> Crée un ticket candidature pour le grade honorifique situé au-dessus de votre grade actuel (ex.: vous êtes Contremaître, vous postulez pour Architecte). **Disponible à partir de Builder.**

## <:axiom:1437503730378342400>  Axiom
> Pour demander la permission Axiom, **disponible à partir de Builder.**

## ❓  Autre
> Crée un ticket privé pour toute demande particulière, partenariat, concernant une sanction, ou tout autre sujet dont vous souhaitez ne pas en parler en salons publics."""


@dataclass
class Ticket:
    name: str
    emoji: str
    func_create_ticket: Coroutine


BUILDER_BUTTON_PATTERN = re.compile(r"builder_(validate|deny)_([0-9]+)")
AXIOM_BUTTON_PATTERN = re.compile(r"axiom_(validate|deny)_([0-9]+)")
CLOSE_TICKET_BUTTON = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Clore le ticket",
    emoji="✅",
    custom_id="ticket_close",
)


class TicketExtension(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.TICKETS = {
            "promotion": Ticket(name="Promotion", emoji="<:upvote:748611592517583021>", func_create_ticket=self.promotion_ticket_creation),
            "axiom": Ticket(name="Demande Axiom", emoji="<:axiom:1437503730378342400>", func_create_ticket=self.axiom_ticket_creation),
            "other": Ticket(name="Autre", emoji="❓", func_create_ticket=self.general_ticket_creation),
        }
        self.TICKET_CREATION_MODAL = interactions.Modal(
            interactions.LabelComponent(
                label="Type",
                component=interactions.StringSelectMenu(
                    *[interactions.StringSelectOption(label=ticket.name, value=id, emoji=ticket.emoji) for id, ticket in self.TICKETS.items()],
                    custom_id="type",
                ),
            ),
            title="Créer un ticket",
            custom_id="create_ticket",
        )

    @interactions.slash_command("ticket")
    @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def ticket_command(self, ctx: interactions.SlashContext):
        """Setup le système de ticket"""
        await ctx.send("Ticket Builder créé", ephemeral=True)
        await ctx.channel.send(
            TICKET_CREATION_MSG,
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Créer un ticket",
                    emoji="🗒️",
                    custom_id="ticket_create_button",
                ),
            ],
        )

    @interactions.component_callback("ticket_create_button")
    async def on_ticket_button_click(self, ctx: interactions.ComponentContext):
        await ctx.send_modal(self.TICKET_CREATION_MODAL)

    @interactions.modal_callback("create_ticket")
    async def on_ticket_creation(self, ctx: interactions.ModalContext):
        type = ctx.responses.get("type")[0]
        ticket = self.TICKETS.get(type)

        await ctx.defer(ephemeral=True)
        await ticket.func_create_ticket(ctx)

    async def general_ticket_creation(self, ctx: interactions.ModalContext):
        thread = await ctx.channel.create_private_thread(
            name=f"[Ticket] {ctx.author.tag}", invitable=False, auto_archive_duration=interactions.AutoArchiveDuration.ONE_WEEK
        )
        await ctx.send(embed=create_info_embed(f"Ticket créé: {thread.mention}"), ephemeral=True)

        first_message = await thread.send(
            f"## Ticket créé par {ctx.author.mention}\n*Une fois que le ticket est répondu, merci de clore le ticket avec le bouton ci-dessous.*",
            components=[CLOSE_TICKET_BUTTON],
        )
        await first_message.pin()

        # Add author and staff
        await thread.add_member(ctx.author)
        msg = await thread.send(f"<@&{variables.Roles.ADMIN}> <@&{variables.Roles.MODERATOR}> <@&{variables.Roles.SUPPORT}>", silent=True)
        await msg.delete()

    @interactions.component_callback("ticket_close")
    async def general_ticket_close_button(self, ctx: interactions.ComponentContext):
        await ctx.send(embed=create_info_embed(f"Ticket clos par {ctx.author.mention}"))
        await ctx.channel.archive(locked=True)

    async def promotion_ticket_creation(self, ctx: interactions.ModalContext):
        if variables.Roles.INGENIEUR in ctx.author.roles:
            return await ctx.send(
                embed=create_error_embed(
                    "Tu ne peux pas créer de demande de promotion car tu as déjà atteint le rang maximal! <:gg:776560537777602630>"
                ),
                ephemeral=True,
            )
        elif variables.Roles.ARCHITECTE in ctx.author.roles:
            role = ctx.guild.get_role(variables.Roles.INGENIEUR)
        elif variables.Roles.CONTREMAITRE in ctx.author.roles:
            role = ctx.guild.get_role(variables.Roles.ARCHITECTE)
        elif variables.Roles.BUILDER in ctx.author.roles:
            role = ctx.guild.get_role(variables.Roles.CONTREMAITRE)
        elif variables.Roles.DEBUTANT in ctx.author.roles:
            role = ctx.guild.get_role(variables.Roles.BUILDER)
        else:
            return await ctx.send(
                embed=create_error_embed(
                    f"Tu ne peux pas créer de demande de promotion car tu n'es pas encore Débutant!\nPour devenir Débutant, fais ta demande dans <#{variables.Channels.DEBUTANT}>."
                ),
                ephemeral=True,
            )

        # Check if user has already created a thread
        thread_name = f"[Demande {role.name}] {ctx.author.tag}"
        threads = (await ctx.channel.fetch_active_threads()).threads
        thread_names = [thread.name for thread in threads]
        if thread_name in thread_names:
            return await ctx.send(
                embed=create_error_embed(f"Tu as déjà créé une demande de {role.name}! ({threads[thread_names.index(thread_name)].mention})"),
                ephemeral=True,
            )

        thread = await ctx.channel.create_private_thread(
            name=thread_name, invitable=False, auto_archive_duration=interactions.AutoArchiveDuration.ONE_WEEK
        )
        await ctx.send(embed=create_info_embed(f"Demande créée: {thread.mention}"), ephemeral=True)
        first_message = await thread.send(
            f"## Demande de {role.name} de {ctx.author.mention}\n*Personnaliser texte ici en fonction du rôle*",
            components=(
                [
                    interactions.Button(
                        style=interactions.ButtonStyle.SUCCESS,
                        label="Valider la demande",
                        emoji="✅",
                        custom_id=f"builder_validate_{ctx.author.id}",
                    ),
                    interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        label="Refuser la demande",
                        emoji="❌",
                        custom_id=f"builder_deny_{ctx.author.id}",
                    ),
                ]
                if role == ctx.guild.get_role(variables.Roles.BUILDER)  # promotions above buider are monthly, so manual
                else [CLOSE_TICKET_BUTTON]
            ),
        )
        await first_message.pin()

        # Add author & Evaluators
        await thread.add_member(ctx.author)
        msg = await thread.send(f"<@&{variables.Roles.EVALUATEUR}>", silent=True)
        await msg.delete()

    @interactions.component_callback(BUILDER_BUTTON_PATTERN)
    async def builder_ticket_button(self, ctx: interactions.ComponentContext):
        if interactions.Permissions.MANAGE_MESSAGES not in ctx.channel.permissions_for(ctx.author):
            return await ctx.send(
                embed=create_error_embed("Tu n'as pas les permissions nécessaires pour valider ou refuser une demande!"),
                ephemeral=True,
            )
        if not (match := BUILDER_BUTTON_PATTERN.search(ctx.custom_id)):
            return
        action, author_id = match.group(1, 2)
        await ctx.defer(ephemeral=True)

        author = await ctx.guild.fetch_member(author_id)
        username = "?"

        if action == "validate":
            await ctx.channel.send(
                embed=create_embed(
                    description=f"✅ **Demande acceptée par {ctx.author.mention}**",
                    color=0x00FF00,
                )
            )
            await author.remove_roles([variables.Roles.VISITEUR, variables.Roles.DEBUTANT])
            await author.add_role(variables.Roles.BUILDER)
            await ctx.guild.get_channel(variables.Channels.FRENCH_CHAT).send(
                f"**<:gg:776560537777602630> Félicitations à {author.mention} qui est devenu Builder!**"
            )
            nodes: list = await lp_search_nodes(f"discord_id_{author_id}")
            if len(nodes) == 0:  # Discord <-> MC relation not found, therefore cannot pass Builder on the server
                await ctx.send(
                    embed=create_info_embed(f"Demande validée mais sans passer l'utilisateur Builder sur le serveur Minecraft automatiquement!")
                )
            else:
                uuid = nodes[0].get("uniqueId")
                user = await lp_get_user(uuid)
                username = user.get("username")
                if (rank := user.get("metadata", {}).get("primaryGroup")) != "debutant":  # user is NOT a debutant
                    return await ctx.send(embed=create_error_embed(f"[ERREUR] `{username}` est déjà {RANK_DICT.get(rank)}!"))
                promote = await lp_promote_user(uuid)
                if promote is None or not promote.get("success"):
                    await ctx.send(
                        embed=create_error_embed(
                            f"[ERREUR] `{username}` n'a pas pu être passé Builder sur Minecraft?\nRésultat opération:`{promote}`"
                        )
                    )
                else:
                    await ctx.send(
                        embed=create_info_embed(f"Demande validée et `{username}` passé Builder sur le serveur Minecraft automatiquement!")
                    )
                    await ctx.guild.get_channel(variables.Channels.CONSOLE).send(BROADCAST_PROMOTE_MESSAGE.format(username, RANK_DICT.get("builder")))
            log(f"{ctx.author.tag} validated {author.tag} builder request.")
            await ctx.bot.get_channel(variables.Channels.RANKING).send(
                embed=create_embed(
                    description=f"## <:builder:1289872528734687256> **Demande de Builder de {author.mention} validée**",
                    color=0x00FF00,
                    fields=[
                        ("Minecraft", escape_minecraft_username_markdown(username), False),
                    ],
                    footer_text=f"Validée par {ctx.author.tag}",
                )
            )
        elif action == "deny":
            await ctx.channel.send(
                embed=create_embed(
                    description=f"❌ **Demande refusée par {ctx.author.mention}**",
                    color=0xFF0000,
                )
            )
            await ctx.send(embed=create_info_embed(f"Demande refusée."))
            log(f"{ctx.author.tag} denied {author.tag} builder request.")
        await ctx.channel.archive(locked=True)

    async def axiom_ticket_creation(self, ctx: interactions.ModalContext):
        if variables.Roles.AXIOM in ctx.author.roles:
            return await ctx.send(embed=create_error_embed("Tu as déjà le rôle Axiom!"), ephemeral=True)

        thread = await ctx.channel.create_private_thread(
            name=f"[Axiom] {ctx.author.tag}", invitable=False, auto_archive_duration=interactions.AutoArchiveDuration.ONE_WEEK
        )
        await ctx.send(embed=create_info_embed(f"Ticket créé: {thread.mention}"), ephemeral=True)

        first_message = await thread.send(
            f"## Ticket créé par {ctx.author.mention}\n*Rajouter blablabla*",
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Valider la demande",
                    emoji="✅",
                    custom_id=f"axiom_validate_{ctx.author.id}",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.DANGER,
                    label="Refuser la demande",
                    emoji="❌",
                    custom_id=f"axiom_deny_{ctx.author.id}",
                ),
            ],
        )
        await first_message.pin()

        # Add author & Evaluators
        await thread.add_member(ctx.author)
        msg = await thread.send(f"<@&{variables.Roles.EVALUATEUR}>", silent=True)
        await msg.delete()

    @interactions.component_callback(AXIOM_BUTTON_PATTERN)
    async def axiom_ticket_button(self, ctx: interactions.ComponentContext):
        if interactions.Permissions.MANAGE_MESSAGES not in ctx.channel.permissions_for(ctx.author):
            return await ctx.send(
                embed=create_error_embed("Tu n'as pas les permissions nécessaires pour valider ou refuser une demande!"),
                ephemeral=True,
            )
        if not (match := AXIOM_BUTTON_PATTERN.search(ctx.custom_id)):
            return
        action, author_id = match.group(1, 2)
        await ctx.defer(ephemeral=True)

        author = await ctx.guild.fetch_member(author_id)
        username = "?"

        if action == "validate":
            await ctx.channel.send(
                embed=create_embed(
                    description=f"✅ **Demande acceptée par {ctx.author.mention}**",
                    color=0x00FF00,
                )
            )
            await author.add_role(variables.Roles.AXIOM)
            nodes: list = await lp_search_nodes(f"discord_id_{author_id}")
            if len(nodes) == 0:  # Discord <-> MC relation not found, therefore cannot pass Axiom on the server
                await ctx.send(
                    embed=create_info_embed(f"Demande validée mais sans donner la permission Axiom sur le serveur Minecraft automatiquement!")
                )
            else:
                uuid = nodes[0].get("uniqueId")
                user = await lp_get_user(uuid)
                username = user.get("username")
                await lp_add_node_to_user(uuid, {"key": "group.axiom", "value": True})
                await ctx.send(embed=create_info_embed(f"Demande validée et Axiom ajouté à `{username}` sur le serveur Minecraft automatiquement!"))
            log(f"{ctx.author.tag} validated {author.tag} axiom request.")
            await ctx.bot.get_channel(variables.Channels.RANKING).send(
                embed=create_embed(
                    description=f"## <:axiom:1437503730378342400> **Demande d'Axiom de {author.mention} validée**",
                    color=0x00FF00,
                    fields=[
                        ("Minecraft", escape_minecraft_username_markdown(username), False),
                    ],
                    footer_text=f"Validée par {ctx.author.tag}",
                )
            )
        elif action == "deny":
            await ctx.channel.send(
                embed=create_embed(
                    description=f"❌ **Demande refusée par {ctx.author.mention}**",
                    color=0xFF0000,
                )
            )
            await ctx.send(embed=create_info_embed(f"Demande refusée."))
            log(f"{ctx.author.tag} denied {author.tag} axiom request.")
        await ctx.channel.archive(locked=True)
