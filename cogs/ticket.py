import asyncio
import re
from datetime import timedelta

import interactions

import variables
from utils import (
    create_embed,
    create_error_embed,
    create_info_embed,
    escape_minecraft_username_markdown,
    log,
)

TICKET_BUILDER_PATTERN = re.compile(r"ticket_builder_(fr|en)")
TICKET_BUILDER_FR_TEXT = """# <a:btefrance:844495279977791498> Comment devenir Builder?

Après avoir publié votre progression dans <#700757392157048892>, vous pouvez demander le grade Builder.
<:dot:1121528899621376131> Cliquez sur le bouton `Faire sa demande Builder` ci-dessous. Un fil sera ouvert pour discuter de vos constructions.
<:dot:1121528899621376131> Dans ce fil, veuillez envoyer:
- Des photos de vos ___***deux***___ bâtiments __Minecraft__
- Des photos ___***StreetView***___ de vos deux bâtiments de candidature, avec le même point de vue qu'en jeu
- L'adresse **exacte** (ou monument) de vos bâtiments.

> *A noter : deux bâtiments minimum sont requis*
> *Les bâtiments pris en photo doivent être les vôtres*

## Si votre candidature est rejetée, vous pouvez la réitérer quand vous le souhaitez."""
TICKET_BUILDER_EN_TEXT = """# <a:btefrance:844495279977791498> How to become a Builder?

After publishing your progress in <#700757392157048892>, you can apply for the Builder rank.
<:dot:1121528899621376131> Click on the `Apply for Builder rank` below. A thread will be opened to discuss your builds.
<:dot:1121528899621376131> In this thread, please send:
- Photos of your ___***two***___ __Minecraft__ buildings.
- ___***StreetView***___ photos of your two application buildings, with the same viewpoint as in-game
- The **exact** address (or monument) of your buildings.

> *Note: a minimum of two buildings is required.*
> *The buildings photographed must be your own*.

## If your application is rejected, you can submit it again at any time."""
BUILDER_BUTTON_PATTERN = re.compile(r"builder_(validate|deny)_([0-9]+)")
BUILDER_THREAD_FR_TEXT = """### Envoyer ici :
* Une photo de vos deux bâtiments Minecraft
* Une photo StreetView de vos deux bâtiments de candidature, de préférence le même point de vue qu'en jeu
* L'adresse exacte (ou monument) de vos bâtiments."""
BUILDER_THREAD_EN_TEXT = """### Send here:
* A photo of your two Minecraft buildings
* A StreetView photo of your two buildings, preferably from the same viewpoint as in-game.
* The exact address (or monument) of your buildings."""
DEBUTANT_BUTTON_PATTERN = re.compile(r"debutant_validate_([0-9]+)")
TICKET_DEBUTANT_PATTERN = re.compile(r"ticket_debutant_(fr|en)")
TICKET_DEBUTANT_FR_TEXT = """#  <:btefr:1111011027300139078> ・Devenir débutant

Commencez à construire sur le serveur en demandant votre grade débutant.

> __Ce grade vous offre 2 possibilités :__
> _ _
> -  Commencer où vous voulez sur un terrain vierge (hors Paris)
> _ _
> - Commencer en zone débutante si vous ne savez pas où construire : `/zones`

> __Pour cela, cliquez sur le bouton ci-dessous et indiquez dans la demande :__
> - Votre pseudo Minecraft
> - L'endroit **exact** où vous voulez construire (On conseille de commencer par des habitations simples)

## Vous serez ping lorsqu'un staff sera connecté sur le serveur pour qu'il puisse vous mettre le grade.

### Pour construire à Paris, vous devrez faire vos preuves dans une zone débutant à Paris avant de choisir votre endroit."""
TICKET_DEBUTANT_EN_TEXT = """# <:btefr:1111011027300139078> ・Become a beginner

Start building on the server by requesting your beginner rank.

> __This grade offers you 2 possibilities:__
> _ _
> - Start wherever you want on virgin territory (outside Paris)
> _ _
> - Start in beginner zone if you don't know where to build: `/zones`

> __To do this, click on the button below and indicate in the request:__
> - Your Minecraft nickname
> - The **exact** place where you want to build (We recommend starting with simple homes)

## You will be pinged when a staff is connected to the server so that they can give you the rank.

### To build in Paris, you will need to prove yourself in a beginner area in Paris before choosing your location."""


class Ticket(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.old_messages: list[interactions.Message] = []
        self.delete_old_debutant_tickets.start()

    @interactions.slash_command("ticket")
    @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def ticket(self, ctx: interactions.SlashContext): ...

    @ticket.subcommand("builder")
    async def ticket_builder(self, ctx: interactions.SlashContext):
        """Créer le système de ticket pour devenir builder"""
        await ctx.send("Ticket Builder créé", ephemeral=True)
        await ctx.channel.send(
            TICKET_BUILDER_FR_TEXT,
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Faire sa demande Builder",
                    emoji="⛏",
                    custom_id="ticket_builder_fr",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.GRAY,
                    label="English Translation",
                    emoji="🇬🇧",
                    custom_id="ticket_builder_translation",
                ),
            ],
        )

    @interactions.component_callback("ticket_builder_translation")
    async def on_builder_translation_button(self, ctx: interactions.ComponentContext):
        await ctx.send(
            TICKET_BUILDER_EN_TEXT,
            components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Apply for Builder rank",
                emoji="⛏",
                custom_id="ticket_builder_en",
            ),
            ephemeral=True,
        )

    @interactions.component_callback(TICKET_BUILDER_PATTERN)
    @interactions.auto_defer(ephemeral=True, time_until_defer=1.5)
    async def on_ticket_creation(self, ctx: interactions.ComponentContext):
        if not (match := TICKET_BUILDER_PATTERN.search(ctx.custom_id)):
            return
        fr = match.group(1) == "fr"

        if variables.Roles.BUILDER in ctx.author.roles:
            return await ctx.send(
                embed=create_error_embed(
                    "Tu ne peux pas créer de demande car tu es déjà Builder!" if fr else "You cannot apply since you already are Builder!"
                ),
                ephemeral=True,
            )

        if variables.Roles.DEBUTANT not in ctx.author.roles:
            return await ctx.send(
                embed=create_error_embed(
                    f"Tu ne peux pas créer de demande car tu n'es pas encore Débutant!\nPour devenir Débutant, fais ta demande dans <#{variables.Channels.DEBUTANT}>."
                    if fr
                    else f"You cannot apply since you are not yet a Beginner!\nTo become a Beginner, apply in <#{variables.Channels.DEBUTANT}>."
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
                    if fr
                    else f"You already applied for Builder! ({threads[thread_names.index(thread_name)].mention})"
                ),
                ephemeral=True,
            )

        thread = await ctx.channel.create_private_thread(name=thread_name)
        await ctx.send(
            embed=create_info_embed(f"Demande créée ({thread.mention})" if fr else f"Application created ({thread.mention})"),
            ephemeral=True,
        )
        first_message = await thread.send(
            (
                f"## Demande de Builder de {ctx.author.mention}\n{BUILDER_THREAD_FR_TEXT}"
                if fr
                else f"## Builder application from {ctx.author.mention}\n{BUILDER_THREAD_EN_TEXT}"
            ),
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
        msg = await thread.send(f"<@&{variables.Roles.EVALUATEUR}>", silent=True)
        await msg.delete()

    @interactions.component_callback(BUILDER_BUTTON_PATTERN)
    async def on_ticket_button(self, ctx: interactions.ComponentContext):
        if interactions.Permissions.MANAGE_MESSAGES not in ctx.channel.permissions_for(ctx.author):
            return await ctx.send(
                embed=create_error_embed("Tu n'as pas les permissions nécessaires pour valider ou refuser une demande!"),
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
            await author.remove_roles([variables.Roles.VISITEUR, variables.Roles.DEBUTANT])
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
            TICKET_DEBUTANT_FR_TEXT,
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Faire sa demande Débutant",
                    emoji="⛏",
                    custom_id="ticket_debutant_fr",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.GRAY,
                    label="English Translation",
                    emoji="🇬🇧",
                    custom_id="ticket_debutant_translation",
                ),
            ],
        )

    @interactions.component_callback("ticket_debutant_translation")
    async def on_debutant_translation_button(self, ctx: interactions.ComponentContext):
        await ctx.send(
            TICKET_DEBUTANT_EN_TEXT,
            components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Apply to get beginner rank",
                emoji="⛏",
                custom_id="ticket_debutant_en",
            ),
            ephemeral=True,
        )

    @interactions.component_callback(TICKET_DEBUTANT_PATTERN)
    @interactions.auto_defer(ephemeral=True, time_until_defer=1.5)
    async def on_debutant_button(self, ctx: interactions.ComponentContext):
        if not (match := TICKET_DEBUTANT_PATTERN.search(ctx.custom_id)):
            return
        fr = match.group(1) == "fr"

        if ctx.author.has_role(variables.Roles.BUILDER) or ctx.author.has_role(variables.Roles.DEBUTANT):
            return await ctx.send(
                embed=create_error_embed(
                    "Seuls les visiteurs peuvent faire une demande Débutant!" if fr else "Only visitors can apply for the beginner rank!"
                ),
                ephemeral=True,
            )

        if str(ctx.author.id) in await self.get_all_debutant_user_ids(ctx.guild):
            return await ctx.send(
                embed=create_error_embed("Tu as déjà créé une demande Débutant!" if fr else "You already applied for the beginner rank!"),
                ephemeral=True,
            )

        DEBUTANT_MODAL = interactions.Modal(
            interactions.ShortText(
                label="Pseudo Minecraft" if fr else "Minecraft Username",
                custom_id="pseudo",
                max_length=20,
            ),
            interactions.ShortText(
                label="Ville" if fr else "City",
                custom_id="ville",
                placeholder="Ex: Paris, Lyon, Montcuq...",
                max_length=50,
            ),
            interactions.ShortText(
                label="Plus de détails" if fr else "Additional details",
                custom_id="lieu",
                placeholder="Ex: 6ème arrondissement, mairie, nom de la rue..." if fr else "Ex: townhall, name of the street...",
                required=False,
            ),
            title="Demande Débutant" if fr else "Beginner application",
        )
        await ctx.send_modal(DEBUTANT_MODAL)
        modal_ctx: interactions.ModalContext = await self.bot.wait_for_modal(DEBUTANT_MODAL)
        pseudo = escape_minecraft_username_markdown(modal_ctx.responses["pseudo"])
        ville = modal_ctx.responses["ville"]
        lieu = modal_ctx.responses["lieu"]

        await modal_ctx.defer(ephemeral=True)
        thread = await ctx.guild.fetch_thread(variables.Channels.DEBUTANT_THREAD)
        msg = await thread.send(
            embed=create_embed(
                description=f"## **Demande de Débutant de {ctx.author.mention}**",
                fields=[
                    ("Pseudo Minecraft", pseudo, False),
                    ("Ville", ville, False),
                    ("Plus de détails", lieu or "/", False),
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
        await modal_ctx.send(
            embed=create_info_embed(f"Demande Débutant créée: {msg.jump_url}" if fr else f"Beginner application created: {msg.jump_url}"),
            ephemeral=True,
        )

        # Silently add user to the thread
        msg = await thread.send(ctx.author.mention, silent=True)
        await msg.delete()

    @interactions.component_callback(DEBUTANT_BUTTON_PATTERN)
    async def on_debutant_validate(self, ctx: interactions.ComponentContext):
        if interactions.Permissions.MANAGE_MESSAGES not in ctx.channel.permissions_for(ctx.author):
            return await ctx.send(
                embed=create_error_embed("Tu n'as pas les permissions nécessaires pour passer quelqu'un débutant!"),
                ephemeral=True,
            )
        if not (match := DEBUTANT_BUTTON_PATTERN.search(ctx.custom_id)):
            return
        author_id = match.group(1)
        author = await ctx.guild.fetch_member(author_id)

        await ctx.send(embed=create_info_embed(f"{author.mention} passé Débutant!"), ephemeral=True)
        await author.remove_role(variables.Roles.VISITEUR)
        await author.add_role(variables.Roles.DEBUTANT)
        embed = ctx.message.embeds[0]
        await ctx.message.delete()
        log(f"{ctx.author.tag} validated {author.tag} débutant request.")

        # Rename user, can throw error if the user has admin perms
        pseudo, ville = embed.fields[0].value.replace("\\", ""), embed.fields[1].value
        nickname = f"{pseudo} ["
        num_characters_available = 31 - len(nickname)
        if len(ville) > num_characters_available:
            nickname += ville[: num_characters_available - 3] + "..."
        else:
            nickname += ville
        nickname += "]"
        await author.edit_nickname(nickname)

    @interactions.slash_command(name="pingd")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def pingd(self, ctx: interactions.SlashContext):
        """Ping toutes les personnes ayant fait une demande débutant"""
        if not ctx.channel == variables.Channels.DEBUTANT_THREAD:
            return await ctx.send(
                embed=create_error_embed(f"La commande ne peut être utilisée que dans <#{variables.Channels.DEBUTANT_THREAD}>!"),
                ephemeral=True,
            )

        user_ids = await self.get_all_debutant_user_ids(ctx.guild)
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
                user_ids_string + " **Un staff est connecté pour vous donner le rôle, connectez-vous EN JEU pour obtenir le grade Débutant!**"
            )
        except asyncio.TimeoutError:
            pass
        # Small hack to delete the ephemeral /pingd message
        await self.bot.http.delete_interaction_message(self.bot.app.id, ctx.token)

    async def get_all_debutant_user_ids(self, guild: interactions.Guild):
        thread = await guild.fetch_thread(variables.Channels.DEBUTANT_THREAD)
        messages = await thread.fetch_messages(limit=100)
        user_ids: list[str] = []
        now = interactions.Timestamp.utcnow()
        for message in messages:
            if message.components:
                for actionrow in message.components:
                    for component in actionrow.components:
                        if match := DEBUTANT_BUTTON_PATTERN.search(component.custom_id):
                            if now - message.timestamp > timedelta(days=30):
                                self.old_messages.append(message)
                            else:
                                user_ids.append(match.group(1))
                            break

        return user_ids

    @interactions.Task.create(interactions.IntervalTrigger(seconds=10))
    async def delete_old_debutant_tickets(self):
        for message in self.old_messages:
            log(f"Automatically deleted débutant ticket with ID: {int(message.id)}")
            self.old_messages.remove(message)
            await message.delete()
