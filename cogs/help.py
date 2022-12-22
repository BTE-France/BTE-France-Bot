import interactions

from utils.embed import create_embed


class Help(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="help", description="Montre toutes les commandes du bot")
    async def help(self, ctx: interactions.CommandContext):
        embed = create_embed(
            title="Help!",
            color=0xFF0000,
            footer_text="Contacte @mAxYoLo01#4491 si tu trouves des bugs / suggestions!"
        )
        for command in self.client._commands:
            if command.type == interactions.ApplicationCommandType.CHAT_INPUT:
                embed.add_field(name=f"/{command.name}", value=command.description)

        await ctx.author.send(embeds=embed)
        await ctx.send("Regarde tes MPs! :mailbox:")


def setup(client: interactions.Client):
    Help(client)
