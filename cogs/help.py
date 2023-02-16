import interactions

from utils.embed import create_embed


class Help(interactions.Extension):
    @interactions.slash_command(name="help")
    async def help(self, ctx: interactions.SlashContext):
        "Montre toutes les commandes du bot"
        embed = create_embed(
            title="Help!",
            color=0xFF0000,
            footer_text="Contacte @mAxYoLo01#4491 si tu trouves des bugs / suggestions!",
            include_thumbnail=True,
        )

        for command in self.bot.application_commands:
            if type(command) is interactions.SlashCommand:
                embed.add_field(name=f"/{command.name}", value=command.description)

        await ctx.author.send(embeds=embed)
        await ctx.send("Regarde tes MPs! :mailbox:")
