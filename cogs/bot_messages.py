import interactions

from utils import create_error_embed, create_info_embed, log


class BotMessages(interactions.Extension):
    @interactions.slash_command("bot")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def _bot(self, ctx: interactions.SlashContext):
        ...

    @_bot.subcommand("create_message")
    async def create_message(self, ctx: interactions.SlashContext):
        """Envoyer un message via le bot"""
        modal = interactions.Modal(
            interactions.ParagraphText(label="Texte", custom_id="text", required=True),
            title="Créer un nouveau message via le bot",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = convert_to_correct_text(modal_ctx.responses["text"])
        msg = await modal_ctx.channel.send(text)
        await modal_ctx.send(
            embed=create_info_embed(f"Message créé: {msg.jump_url}"), ephemeral=True
        )
        log(f"New message ({msg.jump_url}) was created by {ctx.author.tag}.")

    @_bot.subcommand("create_forum_post")
    @interactions.slash_option(
        name="forum",
        description="Forum où sera créé le post",
        opt_type=interactions.OptionType.CHANNEL,
        required=True,
        channel_types=[interactions.ChannelType.GUILD_FORUM],
    )
    async def create_forum_post(
        self, ctx: interactions.SlashContext, forum: interactions.GuildForum
    ):
        """Créer un nouveau post dans un forum"""
        modal = interactions.Modal(
            interactions.ShortText(
                label="Titre du post", custom_id="title", required=True, max_length=100
            ),
            interactions.ParagraphText(label="Texte", custom_id="text", required=True),
            title="Créer un nouveau post dans le forum",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        title, text = (
            modal_ctx.responses["title"],
            convert_to_correct_text(modal_ctx.responses["text"]),
        )
        post = await forum.create_post(title, text)
        await modal_ctx.send(
            embed=create_info_embed(f"Post créé: {post.mention}"), ephemeral=True
        )
        log(f"New forum post ({post.mention}) was created by {ctx.author.tag}.")

    @interactions.message_context_menu("Editer message")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def edit_message(self, ctx: interactions.ContextMenuContext):
        message: interactions.Message = ctx.target
        if message.author != self.bot.user:
            return await ctx.send(
                embed=create_error_embed("Seul un message du bot peut être édité!"),
                ephemeral=True,
            )
        if not message.content.endswith("** **"):
            return await ctx.send(
                embed=create_error_embed("Ce message du bot ne peut pas être édité!"),
                ephemeral=True,
            )

        modal = interactions.Modal(
            interactions.ParagraphText(
                label="Texte",
                custom_id="text",
                value=message.content.removesuffix("** **"),
                required=True,
            ),
            title="Editer le message",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = convert_to_correct_text(modal_ctx.responses["text"])
        await message.edit(content=text)
        await modal_ctx.send(
            embed=create_info_embed(f"Message édité: {message.jump_url}"),
            ephemeral=True,
        )
        log(f"Message ({message.jump_url}) was edited by {ctx.author.tag}.")


def convert_to_correct_text(input: str) -> str:
    text = input
    # If the text ends with a correct bold/italic markdown (* or **), an extra space must be added
    if text.endswith("*"):
        text += " "
    text += "** **"
    return text
