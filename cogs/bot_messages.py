import interactions
import validators

from utils import create_error_embed, create_info_embed, log

ZERO_WIDTH_SPACE_CHARACTER = "​"
RULES_FR_TEXTS = [
    """## 📚 • Règlement Général
> <:dot:1121528899621376131> Le respect du règlement est obligatoire pour accéder au serveur.
> <:dot:1121528899621376131> Les [**CGU Discord**](<https://discord.com/terms>) ainsi que le [**règlement de BuildTheEarth.net**](<https://discord.com/channels/690908396404080650/713963824687874048>) s’appliquent intégralement ; l’âge minimum requis par Discord en France est de 15 ans.
> <:dot:1121528899621376131> Le staff se réserve le droit de sanctionner tout comportement nuisible, même non explicitement mentionné dans le règlement.
> <:dot:1121528899621376131> L’exploitation de failles, permissions ou sanctions est interdite.
> <:dot:1121528899621376131> Toute infraction entraînera une sanction adaptée à sa gravité.
> <:dot:1121528899621376131> Les contestations de sanctions se font uniquement via ticket, message privé ou mail.
## 💬 • Communication & Contenu
> <:dot:1121528899621376131> Les contenus suivants sont strictement interdits :
> 	<:dot_vide:1130257115278213250> Racisme, sexisme, homophobie et discriminations
> 	<:dot_vide:1130257115278213250> Contenus sexuels, érotiques, gores ou choquants
> 	<:dot_vide:1130257115278213250> Comportements toxiques, offensants, provocateurs ou criminels
> <:dot:1121528899621376131> Les sujets politiques, religieux ou sensibles sont à éviter.
> <:dot:1121528899621376131> Les pseudos, skins, bios, photos de profil, statuts, activités et tags doivent respecter le règlement.
> <:dot:1121528899621376131> Le spam, flood, spoil, abus de ping, markdown ou ASCII art sont interdits.
> <:dot:1121528899621376131> Les salons doivent rester lisibles et utilisés pour leur usage prévu.
> <:dot:1121528899621376131> Toute publicité non sollicitée est interdite.
> <:dot:1121528899621376131> Ne partagez jamais d’informations privées ou de fichiers malveillants.
** **""",
    """## <a:bloc:847141863654686741> • Règles Minecraft
__***Construction***__
> <:dot:1121528899621376131> Seule la version Java officielle de Minecraft est autorisée.
> <:dot:1121528899621376131> La construction de bâtiments en dehors du territoire de BTE France (France métropolitaine, Outre-Mer et Monaco) est interdite.
> <:dot:1121528899621376131> Les constructions sans lien avec le projet doivent rester temporaires ; les structures d’aide à la construction sont autorisées.
> <:dot:1121528899621376131> Toute construction faisant référence à un contenu interdit sera supprimée.
__***Zones & Projets Sensibles***__
> <:dot:1121528899621376131> Les secteurs complexes suivants nécessitent un niveau adapté et/ou une autorisation préalable :
> 	<:dot_vide:1130257115278213250> 🗼 Paris : obligation de suivre le guide pour [**#Construire à Paris**](<https://discord.com/channels/694003889506091100/1130172157868118198>).
> 	<:dot_vide:1130257115278213250> 🇲🇨 Monaco : contacter un staff dans le salon [**#paca-monaco**](https://discord.com/channels/694003889506091100/694029532507668541).
> 	<:dot_vide:1130257115278213250> 🏛 Monuments historiques et structures complexes : consultation obligatoire du [**#Responsable de Région**](<https://discord.com/channels/694003889506091100/1329131948874006677>) avant de débuter, à partir de <@&694176169465086003>""",
    """__***Technique & Stabilité***__
> <:dot:1121528899621376131> Générer des chunks uniquement pour explorer la carte est interdit ; utilisez les /warps pour vos déplacements longue distance.
> <:dot:1121528899621376131> Modifier une construction existante nécessite l’accord du créateur ou du staff après 7 jours sans réponse.
> <:dot:1121528899621376131> Le grief, l’exploitation de bugs, les crashs volontaires, les machines à lag et le spam d’entités/objets sont interdits.
> <:dot:1121528899621376131> En construction, les [**Entités**](<https://minecraft.wiki/w/Entity>) sont interdites, sauf les Armor Stands à utiliser avec parcimonie ; les shulkers sont également à éviter.
> <:dot:1121528899621376131> Limitez l’usage de FAWE et Axiom à des sélections raisonnables liées à votre zone de build.
> <:dot:1121528899621376131> Le [**#Modpack BTE France**](<https://discord.com/channels/694003889506091100/1477270197411774618>) est recommandé ; les texture packs sont déconseillés.
** **""",
    """## <:evaluateur:1361394843129090128> • Contributions & droits d'utilisation

> <:dot:1121528899621376131> Il est interdit de récupérer, copier, reproduire, extraire ou redistribuer une construction dont vous n’êtes pas l’auteur sans autorisation, mais les [**#Schematics**](<https://discord.com/channels/694003889506091100/1170473400871964783>) de vos propres constructions peuvent être récupérés en ouvrant un [**#ticket**](<https://discord.com/channels/694003889506091100/1112828812976214026>).
> <:dot:1121528899621376131> La restitution de schematics peut être accordée ou refusée à la discrétion du staff.
> <:dot:1121528899621376131> Le serveur est fourni « en l’état ». BTE France ne saurait être tenu responsable des pertes de données, interruptions de service, sanctions appliquées conformément au règlement ou dommages indirects liés à son utilisation.
> <:dot:1121528899621376131> Les utilisateurs garantissent disposer des droits et autorisations nécessaires sur toute construction importée et en assument l’entière responsabilité.
> <:dot:1121528899621376131> En important ou en réalisant une construction sur le serveur, l’utilisateur accorde à BTE France une licence gratuite, non exclusive, irrévocable et permanente permettant de conserver, reproduire, modifier, adapter, diffuser et exploiter cette contribution dans le cadre du projet.
> <:dot:1121528899621376131> Ces droits subsistent après le départ, l’inactivité ou le bannissement du contributeur.
> <:dot:1121528899621376131> Toute utilisation d’une contribution dans le cadre du financement du fonctionnement ou du développement du projet nécessite l’accord préalable de son auteur.
** **""",
    """🔺 *Le règlement peut être modifié à tout moment et sans préavis, toute utilisation du serveur implique l’acceptation de sa version la plus récente. Vous serez notifiés de chaque modification du règlement.*""",
]
RULES_EN_TEXTS = [
    """## 📚 • General Rules
> <:dot:1121528899621376131> Compliance with these rules is mandatory to access the server.
> <:dot:1121528899621376131> The [**Discord Terms of Service**](<https://discord.com/terms>) and the [**BuildTheEarth.net rules**](<https://discord.com/channels/690908396404080650/713963824687874048>) apply in full; the minimum age required by Discord in France is 15.
> <:dot:1121528899621376131> Staff reserve the right to penalize any disruptive behavior, even if not explicitly mentioned in the rules.
> <:dot:1121528899621376131> Exploiting loopholes, permissions, or restrictions is prohibited.
> <:dot:1121528899621376131> Any violation will result in a punishment proportionate to its severity.
> <:dot:1121528899621376131> Appeals of penalties may only be made via ticket, private message, or email.
## 💬 • Communication & Content
> <:dot:1121528899621376131> The following content is strictly prohibited:
>	<:dot_vide:1130257115278213250> Racism, sexism, homophobia, and discrimination
>	<:dot_vide:1130257115278213250> Sexual, erotic, gory, or shocking content
>	<:dot_vide:1130257115278213250> Toxic, offensive, provocative, or criminal behavior
> <:dot:1121528899621376131> Political, religious, or sensitive topics should be avoided.
> <:dot:1121528899621376131> Usernames, skins, bios, profile pictures, statuses, activities, and tags must comply with the rules.
> <:dot:1121528899621376131> Spam, flooding, spoilers, excessive pinging, and the use of Markdown or ASCII art are prohibited.
> <:dot:1121528899621376131> Channels must remain readable and used for their intended purpose.
> <:dot:1121528899621376131> Any unsolicited advertising is prohibited.
> <:dot:1121528899621376131> Never share private information or malicious files.
** **""",
    """## <a:bloc:847141863654686741> • Minecraft Rules
__***Construction***__
> <:dot:1121528899621376131> Only the official Java version of Minecraft is allowed.
> <:dot:1121528899621376131> Building structures outside the territory of BTE France (mainland France, overseas territories, and Monaco) is prohibited.
> <:dot:1121528899621376131> Structures unrelated to the project must remain temporary; structures that aid in construction are permitted.
> <:dot:1121528899621376131> Any structure referencing prohibited content will be removed.
__***Sensitive Areas & Projects***__
> <:dot:1121528899621376131> The following complex areas require an appropriate level and/or prior authorization:
>     <:dot_vide:1130257115278213250> 🗼 **Paris:** you must follow the guide for [**#Building in Paris**](<https://discord.com/channels/694003889506091100/1163819748920926258>).
>     <:dot_vide:1130257115278213250> 🇲🇨 **Monaco:** contact a staff member in the [**#paca-monaco**](https://discord.com/channels/694003889506091100/694029532507668541) channel.
>     <:dot_vide:1130257115278213250> 🏛 **Historic monuments and complex structures:** you must consult the [**#Region Manager**](<https://discord.com/channels/694003889506091100/1460994559571132496>) before starting, available from <@&694176169465086003> rank""",
    """__***Technique & Stability***__
> <:dot:1121528899621376131> Generating chunks solely for the purpose of exploring the map is prohibited; use /warps for long-distance travel.
> <:dot:1121528899621376131> Modifying an existing structure requires the creator’s consent or staff approval after 7 days without a response.
> <:dot:1121528899621376131> Griefing, exploiting bugs, intentional crashes, lag machines, and entity/item spam are prohibited.
> <:dot:1121528899621376131> For construction, [**Entities**](<https://minecraft.wiki/w/Entity>) are prohibited, except for Armor Stands, which should be used sparingly; Shulkers should also be avoided.
> <:dot:1121528899621376131> Limit the usage of FAWE and Axiom to reasonable selections related to your build area.
> <:dot:1121528899621376131> The [**#BTE France modpack**](<https://discord.com/channels/694003889506091100/1477352238530822247>) is recommended; texture packs are strongly discouraged.
** **""",
    """## <:evaluateur:1361394843129090128> • Contributions & Usage Rights

> <:dot:1121528899621376131> You may not retrieve, copy, reproduce, extract, or redistribute a design that you did not create without permission, but the [**#Schematics**](<https://discord.com/channels/694003889506091100/1170473400871964783>) for your own builds can be retrieved by opening a [**# ticket**](<https://discord.com/channels/694003889506091100/1112828812976214026>).
> <:dot:1121528899621376131> The staff may grant or deny requests to retrieve schematics at their discretion.
> <:dot:1121528899621376131> The server is provided “as is.” BTE France shall not be held liable for any data loss, service interruptions, penalties imposed in accordance with the rules, or indirect damages related to its use.
> <:dot:1121528899621376131> Users warrant that they possess the necessary rights and permissions for any imported construction and assume full responsibility for it.
> <:dot:1121528899621376131> By importing or creating a structure on the server, the user grants BTE France a free, non-exclusive, irrevocable, and perpetual license to store, reproduce, modify, adapt, distribute, and use this contribution within the scope of the project.
> <:dot:1121528899621376131> These rights remain in effect after the contributor leaves, becomes inactive, or is banned.
> <:dot:1121528899621376131> Any use of a contributed work for the purpose of funding the operation or development of the project requires the prior consent of its author.
** **""",
    """🔺 *The rules may be modified at any time without notice; any use of the server implies acceptance of the most recent version. You will be notified of any changes to the rules.*""",
]


class BotMessages(interactions.Extension):
    @interactions.slash_command("bot")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def _bot(self, ctx: interactions.SlashContext): ...

    @_bot.subcommand("create_message")
    async def create_message(self, ctx: interactions.SlashContext):
        """Envoyer un message via le bot"""
        modal = interactions.Modal(
            interactions.ParagraphText(
                label="Texte (max 2000 caractères)",
                custom_id="text",
                max_length=2000,
                required=True,
            ),
            title="Créer un nouveau message via le bot",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = modal_ctx.responses["text"]
        if not validators.url(text):  # Text is not a valid image URL
            text += ZERO_WIDTH_SPACE_CHARACTER
        msg = await modal_ctx.channel.send(text, allowed_mentions=interactions.AllowedMentions())
        await modal_ctx.send(embed=create_info_embed(f"Message créé: {msg.jump_url}"), ephemeral=True)
        log(f"New message ({msg.jump_url}) was created by {ctx.author.tag}.")

    @_bot.subcommand("create_forum_post")
    @interactions.slash_option(
        name="forum",
        description="Forum où sera créé le post",
        opt_type=interactions.OptionType.CHANNEL,
        required=True,
        channel_types=[interactions.ChannelType.GUILD_FORUM],
    )
    async def create_forum_post(self, ctx: interactions.SlashContext, forum: interactions.GuildForum):
        """Créer un nouveau post dans un forum"""
        modal = interactions.Modal(
            interactions.ShortText(label="Titre du post", custom_id="title", required=True, max_length=100),
            interactions.ParagraphText(
                label="Texte (max 2000 caractères)",
                custom_id="text",
                max_length=2000,
                required=True,
            ),
            title="Créer un nouveau post dans le forum",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        title, text = (
            modal_ctx.responses["title"],
            modal_ctx.responses["text"],
        )
        if not validators.url(text):  # Text is not a valid image URL
            text += ZERO_WIDTH_SPACE_CHARACTER
        post = await forum.create_post(title, text, allowed_mentions=interactions.AllowedMentions())
        await modal_ctx.send(embed=create_info_embed(f"Post créé: {post.mention}"), ephemeral=True)
        log(f"New forum post ({post.mention}) was created by {ctx.author.tag}.")

    @interactions.message_context_menu("Editer message")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def edit_message(self, ctx: interactions.ContextMenuContext):
        message: interactions.Message = ctx.target
        if message.author != self.bot.user:
            return await ctx.send(
                embed=create_error_embed("Seul un message du bot peut être édité!"),
                ephemeral=True,
            )
        if (not message.content.endswith(ZERO_WIDTH_SPACE_CHARACTER)) and (not validators.url(message.content)):
            return await ctx.send(
                embed=create_error_embed("Ce message du bot ne peut pas être édité!"),
                ephemeral=True,
            )

        modal = interactions.Modal(
            interactions.ParagraphText(
                label="Texte (max 2000 caractères)",
                custom_id="text",
                value=message.content.removesuffix(ZERO_WIDTH_SPACE_CHARACTER),
                max_length=2000,
                required=True,
            ),
            title="Editer le message",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = modal_ctx.responses["text"]
        if not validators.url(text):  # Text is not a valid image URL
            text += ZERO_WIDTH_SPACE_CHARACTER
        await message.edit(content=text, allowed_mentions=interactions.AllowedMentions())
        await modal_ctx.send(
            embed=create_info_embed(f"Message édité: {message.jump_url}"),
            ephemeral=True,
        )
        log(f"Message ({message.jump_url}) was edited by {ctx.author.tag}.")

    @_bot.subcommand("send_predefined_message")
    @interactions.slash_option(
        name="message",
        description="Nom du message",
        opt_type=interactions.OptionType.STRING,
        required=True,
        choices=[interactions.SlashCommandChoice("Règles/Rules", "rules")],
    )
    @interactions.auto_defer(ephemeral=True, time_until_defer=1.5)
    async def send_predefined_message(self, ctx: interactions.SlashContext, message: str):
        """Envoyer un message préécrit"""
        if message == "rules":
            msg = await ctx.channel.send(file=interactions.File("resources/rules_icon_fr.png"))
            for fr_msg in RULES_FR_TEXTS:
                await ctx.channel.send(fr_msg, allowed_mentions=interactions.AllowedMentions())

            msg = await ctx.channel.send("## 🇬🇧  English translation below")
            thread = await msg.create_thread("Rules")
            msg = await thread.send(file=interactions.File("resources/rules_icon_en.png"))
            for en_msg in RULES_EN_TEXTS:
                await thread.send(en_msg, allowed_mentions=interactions.AllowedMentions())

            await ctx.send(embed=create_info_embed(f"Message envoyé: {msg.jump_url}"), ephemeral=True)
