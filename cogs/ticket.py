import asyncio
import re

import interactions

import variables
from utils import create_embed, create_error_embed, create_info_embed, log

BUILDER_BUTTON_PATTERN = re.compile(r"builder_(validate|deny)_([0-9]+)")
BUILDER_TEXT = """# <a:btefrance:844495279977791498> Comment devenir Builder?

Une fois que vous êtes satisfaits de vos constructions et que vous pensez pouvoir demander à devenir un Builder, suivez ces étapes:
- Cliquez sur le bouton `Faire sa demande Builder` ci-dessous. Cela vous créera un fil de discussion où des membres du Staff pourront vous donner leurs ressentis sur vos constructions.
- Dans ce fil, veuillez envoyer:
 - Une photo de vos ___***deux***___ bâtiments __Minecraft__
 - Une photo ___***StreetView***___ de vos deux bâtiments de candidature, prenez de préférence le même point de vue qu'en jeu
 - L'adresse **exacte** (ou monument) de vos bâtiments.

> *A noter : au minimum deux bâtiments sont requis, sans quoi la candidature est rejetée*
> *Les bâtiments pris en photo doivent être les vôtres (cas des zones débutants si vous construisez dedans)*

## Les demandes seront traitées le plus rapidement possible, une fois la candidature validée et le grade donné, celle-ci sera supprimée du salon"""
BUILDER_THREAD_TEXT = """### Envoyer ici :
* Une photo de vos deux bâtiments Minecraft
* Une photo StreetView de vos deux bâtiments de candidature, de préférence le même point de vue qu'en jeu
* L'adresse exacte (ou monument) de vos bâtiments."""
DEBUTANT_BUTTON_PATTERN = re.compile(r"debutant_validate_([0-9]+)")
DEBUTANT_TEXT = """#  <:btefr:1111011027300139078> ・Devenir débutant

Commencez à construire sur le serveur en demandant votre grade débutant.

> Ce grade vous offre 2 possibilités :
> _ _
> - Commencer où vous voulez sur un terrain vierge (hors Paris)
> _ _
> - Commencer en zone débutante si vous ne savez pas où construire : `/zones`

> Pour cela, cliquez sur le bouton ci-dessous et indiquez dans la demande :
> - Votre pseudo Minecraft
> - L'endroit exact où vous voulez construire (On conseille de commencer par des habitations simples)

Vous serez ping lorsqu'un staff sera connecté sur le serveur pour qu'il puisse vous mettre le grade.

Pour construire à Paris, vous devrez faire vos preuves dans une zone débutant à Paris avant de choisir votre endroit."""
DEBUTANT_MODAL = interactions.Modal(
    interactions.ShortText(
        label="Pseudo Minecraft",
        custom_id="pseudo",
    ),
    interactions.ShortText(
        label="Lieu souhaité de construction",
        custom_id="lieu",
        placeholder="Ex: Paris 6ème, Lyon, Marseille...",
    ),
    title="Demande Débutant",
    custom_id="debutant_modal",
)


class Ticket(interactions.Extension):
    @interactions.slash_command("ticket")
    @interactions.slash_default_member_permission(
        interactions.Permissions.ADMINISTRATOR
    )
    async def ticket(self, ctx: interactions.SlashContext):
        ...

    @ticket.subcommand("builder")
    async def ticket_builder(self, ctx: interactions.SlashContext):
        """Créer le système de ticket pour devenir builder"""
        await ctx.send("Ticket Builder créé", ephemeral=True)
        await ctx.channel.send(
            BUILDER_TEXT,
            components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Faire sa demande Builder",
                emoji="⛏",
                custom_id="ticket_builder",
            ),
        )

    @interactions.component_callback("ticket_builder")
    async def on_ticket_creation(self, ctx: interactions.ComponentContext):
        if variables.Roles.BUILDER in ctx.author.roles:
            return await ctx.send(
                embed=create_error_embed(
                    "Tu ne peux pas créer de demande car tu es déjà Builder!"
                ),
                ephemeral=True,
            )

        # Check if user has already created a thread
        thread_name = ctx.author.tag
        threads = (await ctx.channel.fetch_active_threads()).threads
        thread_names = [thread.name for thread in threads]
        if thread_name in thread_names:
            return await ctx.send(
                embed=create_error_embed(
                    f"Tu as déjà créé une demande Builder! ({threads[thread_names.index(thread_name)].mention})"
                ),
                ephemeral=True,
            )

        thread = await ctx.channel.create_private_thread(name=thread_name)
        await ctx.send(
            embed=create_info_embed(f"Demande créée ({thread.mention})"), ephemeral=True
        )
        first_message = await thread.send(
            f"## Demande de Builder de {ctx.author.mention}\n{BUILDER_THREAD_TEXT}",
            components=[
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
            ],
        )
        await first_message.pin()

        # Add author & all staff MC
        await thread.add_member(ctx.author)
        msg = await thread.send(f"<@&{variables.Roles.STAFF_MINECRAFT}>", silent=True)
        await msg.delete()

    @interactions.component_callback(BUILDER_BUTTON_PATTERN)
    async def on_ticket_button(self, ctx: interactions.ComponentContext):
        if not ctx.author.has_permission(interactions.Permissions.MANAGE_MESSAGES):
            return await ctx.send(
                embed=create_error_embed(
                    "Tu n'as pas les permissions nécessaires pour valider ou refuser une demande!"
                ),
                ephemeral=True,
            )
        if not (match := BUILDER_BUTTON_PATTERN.search(ctx.custom_id)):
            return
        action, author_id = match.group(1, 2)
        author = await ctx.guild.fetch_member(author_id)

        if action == "validate":
            await ctx.send(
                embed=create_embed(
                    description=f"✅ **Demande acceptée par {ctx.author.mention}**",
                    color=0x00FF00,
                )
            )
            await author.remove_roles(
                [variables.Roles.VISITEUR, variables.Roles.DEBUTANT]
            )
            await author.add_role(variables.Roles.BUILDER)
            await ctx.guild.get_channel(variables.Channels.FRENCH_CHAT).send(
                f"**<:gg:776560537777602630> Félicitations à {author.mention} qui est devenu Builder!**"
            )
            log(f"{ctx.author.tag} validated {author.tag} builder request.")
        elif action == "deny":
            await ctx.send(
                embed=create_embed(
                    description=f"❌ **Demande refusée par {ctx.author.mention}**",
                    color=0xFF0000,
                )
            )
            log(f"{ctx.author.tag} denied {author.tag} builder request.")
        await ctx.channel.archive(locked=True)

    @ticket.subcommand("débutant")
    async def ticket_debutant(self, ctx: interactions.SlashContext):
        """Créer le système de ticket pour devenir débutant"""
        await ctx.send("Ticket Débutant créé", ephemeral=True)
        await ctx.channel.send(
            DEBUTANT_TEXT,
            components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Faire sa demande Débutant",
                emoji="⛏",
                custom_id="ticket_debutant",
            ),
        )

    @interactions.component_callback("ticket_debutant")
    async def on_debutant_button(self, ctx: interactions.ComponentContext):
        if not ctx.author.has_role(variables.Roles.VISITEUR):
            return await ctx.send(
                embed=create_error_embed(
                    "Seuls les visiteurs peuvent faire une demande Débutant!"
                ),
                ephemeral=True,
            )

        if str(ctx.author.id) in await self.get_all_debutant_user_ids(ctx.channel):
            return await ctx.send(
                embed=create_error_embed("Tu as déjà créé une demande Débutant!"),
                ephemeral=True,
            )

        await ctx.send_modal(DEBUTANT_MODAL)
        modal_ctx = await self.bot.wait_for_modal(DEBUTANT_MODAL)
        pseudo = modal_ctx.responses["pseudo"]
        lieu = modal_ctx.responses["lieu"]

        await modal_ctx.send(
            embed=create_info_embed("Demande Débutant créée!"), ephemeral=True
        )
        await ctx.channel.send(
            embed=create_embed(
                description=f"## **Demande de Débutant de {ctx.author.mention}**",
                fields=[
                    ("Pseudo Minecraft", pseudo, False),
                    ("Lieu souhaité de construction", lieu, False),
                ],
                color=0x0000FF,
                footer_image=ctx.author.display_avatar.url,
                footer_text=ctx.author.tag,
            ),
            components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Valider la demande",
                emoji="✅",
                custom_id=f"debutant_validate_{ctx.author.id}",
            ),
        )

    @interactions.component_callback(DEBUTANT_BUTTON_PATTERN)
    async def on_debutant_validate(self, ctx: interactions.ComponentContext):
        if not ctx.author.has_permission(interactions.Permissions.MANAGE_MESSAGES):
            return await ctx.send(
                embed=create_error_embed(
                    "Tu n'as pas les permissions nécessaires pour passer quelqu'un débutant!"
                ),
                ephemeral=True,
            )
        if not (match := DEBUTANT_BUTTON_PATTERN.search(ctx.custom_id)):
            return
        author_id = match.group(1)
        author = await ctx.guild.fetch_member(author_id)

        await ctx.send(
            embed=create_info_embed(f"{author.mention} passé Débutant!"), ephemeral=True
        )
        await author.remove_role(variables.Roles.VISITEUR)
        await author.add_role(variables.Roles.DEBUTANT)
        embed = ctx.message.embeds[0]
        pseudo, lieu = embed.fields[0].value, embed.fields[1].value
        await author.edit_nickname(f"{pseudo} [{lieu}]")
        await ctx.message.delete()
        log(f"{ctx.author.tag} validated {author.tag} débutant request.")

    @interactions.slash_command(name="pingd")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def pingd(self, ctx: interactions.SlashContext):
        """Ping toutes les personnes ayant fait une demande débutant"""
        if not ctx.channel == variables.Channels.DEBUTANT:
            return await ctx.send(
                embed=create_error_embed(
                    f"La commande ne peut être utilisée que dans <#{variables.Channels.DEBUTANT}>!"
                ),
                ephemeral=True,
            )

        user_ids = await self.get_all_debutant_user_ids(ctx.channel)
        if not user_ids:
            return await ctx.send(
                embed=create_info_embed("Aucune demande débutant trouvée!"),
                ephemeral=True,
            )

        send_button = interactions.Button(
            style=interactions.ButtonStyle.GRAY,
            custom_id="debutant_ping",
            label="Ping toutes les demandes de débutant",
        )
        user_ids_string = " ".join([f"<@{id}>" for id in user_ids])
        await ctx.send(f"`{user_ids_string}`", components=send_button, ephemeral=True)

        try:
            await self.bot.wait_for_component(components=send_button, timeout=30)
            await ctx.channel.send(
                user_ids_string
                + " **Un membre du staff est connecté sur le serveur pour vous passer débutant!**"
            )
        except asyncio.TimeoutError:
            pass
        # Small hack to delete the ephemeral /pingd message
        await self.bot.http.delete_interaction_message(self.bot.app.id, ctx.token)

    async def get_all_debutant_user_ids(self, channel: interactions.GuildText):
        custom_ids: list[str] = []
        messages = await channel.fetch_messages(limit=100)
        for message in messages:
            if message.components:
                for actionrow in message.components:
                    for component in actionrow.components:
                        custom_ids.append(component.custom_id)

        user_ids: list[str] = []
        for custom_id in custom_ids:
            if match := DEBUTANT_BUTTON_PATTERN.search(custom_id):
                user_ids.append(match.group(1))
        return user_ids
