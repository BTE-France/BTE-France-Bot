import interactions

import variables
from utils import create_error_embed, create_info_embed, log


class Guides(interactions.Extension):
    @interactions.slash_command("guide")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def guide(self, ctx: interactions.SlashContext):
        ...

    @guide.subcommand("create_guide")
    async def create_guide(self, ctx: interactions.SlashContext):
        """Créer un nouveau guide"""
        modal = interactions.Modal(
            interactions.ShortText(
                label="Titre du guide", custom_id="title", required=True, max_length=45
            ),
            interactions.ParagraphText(label="Texte", custom_id="text", required=True),
            title="Créer un nouveau guide",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        title, text = modal_ctx.responses["title"], modal_ctx.responses["text"]
        guide_forum = ctx.guild.get_channel(variables.Channels.GUIDE)
        post = await guide_forum.create_post(title, text)
        await modal_ctx.send(
            embed=create_info_embed(f"Le guide {post.mention} a été créé!"),
            ephemeral=True,
        )
        log(f"New guide called {title} created by {ctx.author.tag}.")

    @guide.subcommand("create_message")
    async def create_message(self, ctx: interactions.SlashContext):
        """Créer un nouveau message dans ce guide"""
        if ctx.channel.parent_id != variables.Channels.GUIDE:
            return await ctx.send(
                embed=create_error_embed(
                    f"Un message peut être créé seulement dans un guide de <#{variables.Channels.GUIDE}>!"
                ),
                ephemeral=True,
            )

        modal = interactions.Modal(
            interactions.ParagraphText(label="Texte", custom_id="text", required=True),
            title="Créer un nouveau message dans ce guide",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = modal_ctx.responses["text"]
        await ctx.channel.send(text)
        msg = await modal_ctx.send(
            embed=create_info_embed("Le nouveau message a été créé!"),
            ephemeral=True,
        )
        log(f"New message ({msg.jump_url}) added to a guide by {ctx.author.tag}.")

    @interactions.message_context_menu("Editer guide")
    @interactions.slash_default_member_permission(
        interactions.Permissions.MANAGE_MESSAGES
    )
    async def edit_guide(self, ctx: interactions.ContextMenuContext):
        if ctx.channel.parent_id != variables.Channels.GUIDE:
            return await ctx.send(
                embed=create_error_embed(
                    f"Seul un message du bot dans un guide de <#{variables.Channels.GUIDE}> peut être édité!"
                ),
                ephemeral=True,
            )

        modal = interactions.Modal(
            interactions.ParagraphText(
                label="Texte",
                custom_id="text",
                value=ctx.target.content,
                required=True,
            ),
            title=f"Editer le guide {ctx.channel.name}",
        )
        await ctx.send_modal(modal)
        modal_ctx = await self.bot.wait_for_modal(modal)
        text = modal_ctx.responses["text"]
        await ctx.target.edit(content=text)
        await modal_ctx.send(
            embed=create_info_embed("Le guide a été édité!"),
            ephemeral=True,
        )
        log(f"Guide at {ctx.target.jump_url} edited by {ctx.author.tag}.")
