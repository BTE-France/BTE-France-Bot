import interactions
import validators

from utils import create_error_embed, create_info_embed, log

ZERO_WIDTH_SPACE_CHARACTER = "​"
RULES_FR_TEXT = """> <:dot:1113767008752914492> Pas de racisme, sexisme, homophobie ou d'autres formes de préjugés.
> <:dot:1113767008752914492> Aucun contenu érotique/sexuel/gore.
> <:dot:1113767008752914492> Pas de politique ou sujets lourds.
> <:dot:1113767008752914492> Respect des [CGU Discord](https://discord.com/terms).
> <:dot:1113767008752914492> Respect des [règles en jeu](https://discord.com/channels/694003889506091100/1130179699570643005).
> <:dot:1113767008752914492> **__Pas de Minecraft cracké !__** Uniquement le launcher officiel est autorisé.
> <:dot:1113767008752914492> Pas de comportements toxiques et criminels.
> <:dot:1113767008752914492> Pas de perturbation du chat (spam, ASCII, flood, spoil, pings et markdown intensifs...)
> <:dot:1113767008752914492> Les noms d'utilisateur, photos de profil, statuts et activités doivent respecter les règles.
> <:dot:1113767008752914492> Pas de publicité non sollicitée.
> <:dot:1113767008752914492> Pas d'accusation publique d'enfreinte des règles. Allez voir un staff en privé.
> <:dot:1113767008752914492> L'utilisation de canaux qui s'écartent de leur but n'est pas autorisée.
> <:dot:1113767008752914492> Les sanctions ne doivent pas être contournées. Il est interdit d'exploiter les failles des règles."""
RULES_EN_TEXT = """> <:dot:1113767008752914492> No racism, sexism, homophobia or other forms of prejudice.
> <:dot:1113767008752914492> No erotic/sexual/gore content.
> <:dot:1113767008752914492> No politics or heavy topics.
> <:dot:1113767008752914492> Respect of [Discord's TOS](https://discord.com/terms).
> <:dot:1113767008752914492> Respect of [ingame rules](https://discord.com/channels/694003889506091100/1163807707174817872).
> <:dot:1113767008752914492> **__No cracked Minecraft!__** Only the official launcher is allowed.
> <:dot:1113767008752914492> No toxic or criminal behavior.
> <:dot:1113767008752914492> No chat disturbances (spam, ASCII, flood, spoil, intensive pings and markdown...).
> <:dot:1113767008752914492> Usernames, profile photos, statuses and activities must comply with the rules.
> <:dot:1113767008752914492> No unsolicited advertising.
> <:dot:1113767008752914492> No public accusations of rule-breaking. Go see a staff member in private.
> <:dot:1113767008752914492> The use of channels that deviate from their intended purpose is not permitted.
> <:dot:1113767008752914492> Sanctions must not be circumvented. Exploiting loopholes in the rules is forbidden."""


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
    async def send_predefined_message(self, ctx: interactions.SlashContext, message: str):
        """Envoyer un message préécrit"""
        if message == "rules":
            msg = await ctx.channel.send("https://media.discordapp.net/attachments/1113857454015533117/1113904168604803173/regle2.png")
            await ctx.channel.send(RULES_FR_TEXT)
            await ctx.channel.send(
                components=interactions.Button(
                    style=interactions.ButtonStyle.GRAY,
                    label="English Translation",
                    emoji="🇬🇧",
                    custom_id="rules_translation",
                ),
            )
            await ctx.send(embed=create_info_embed(f"Message envoyé: {msg.jump_url}"), ephemeral=True)

    @interactions.component_callback("rules_translation")
    async def on_rules_translation_button(self, ctx: interactions.ComponentContext):
        file = interactions.File("resources/rules_icon.png")
        await ctx.send(
            RULES_EN_TEXT,
            file=file,
            ephemeral=True,
        )
