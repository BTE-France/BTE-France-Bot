import discord
import variables
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")

    @commands.command(
        brief="Menu avec toutes les commandes disponibles!", aliases=["h"]
    )
    async def help(self, ctx):
        if ctx.channel.type != discord.ChannelType.private:
            await ctx.send(f"{ctx.author.mention}, regarde tes MPs! :mailbox:")
        embed = discord.Embed(title="Help!", colour=discord.Colour(0xFF0000))
        embed.set_thumbnail(url=variables.bte_france_icon)
        embed.set_footer(
            text="Contacte @mAxYoLo01#4491 si tu trouves des bugs / suggestions!",
            icon_url=variables.bte_france_icon,
        )
        for cog in [self.client.get_cog(cogs) for cogs in self.client.cogs]:
            for command in cog.get_commands():
                # Add the command to the help list only if all checks are passed (i.e. user has access to this command)
                if command.checks:
                    try:
                        all([await check(ctx) for check in command.checks])
                    except commands.errors.CheckAnyFailure:
                        continue
                name = " / ".join(
                    [self.client.command_prefix + command.name] + [
                        self.client.command_prefix + alias
                        for alias in command.aliases
                    ]
                )
                embed.add_field(name=name, value=command.brief, inline=False)
        await ctx.author.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
