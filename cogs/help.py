from utils.embed import create_embed
from variables import server
import interactions


class Help(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="help", description="Montre toutes les commandes du bot", scope=server)
    async def help(self, ctx: interactions.CommandContext):
        commands: list[interactions.ApplicationCommand] = [
            interactions.ApplicationCommand(**command) for command in await self.client._http.get_application_commands(application_id=self.client.me.id, guild_id=server)
        ]

        embed = create_embed(
            title="Help!",
            color=0xFF0000,
            footer_text="Contacte @mAxYoLo01#4491 si tu trouves des bugs / suggestions!"
        )
        for command in commands:
            embed.add_field(name=f"/{command.name}", value=command.description)

        await ctx.author.send(embeds=embed)
        await ctx.send("Regarde tes MPs! :mailbox:")


def setup(client: interactions.Client):
    Help(client)
