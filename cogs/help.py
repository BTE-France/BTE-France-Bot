import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief='Menu avec toutes les commandes disponibles!', aliases=['h'])
    async def help(self, ctx):
        if ctx.channel.type != discord.ChannelType.private:
            await ctx.send(f"{ctx.author.mention}, regarde tes MPs! :mailbox:")
        embed = discord.Embed(title='Help!', colour=discord.Colour(0xFF0000))
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/694003889506091100/a_c40ba19cfcfbb9db5f5060e85f6539cf.png?size=128")
        embed.set_footer(text='Contacte @mAxYoLo01#4491 si tu trouves des bugs / suggestions!', icon_url='https://cdn.discordapp.com/icons/694003889506091100/a_c40ba19cfcfbb9db5f5060e85f6539cf.png?size=128')
        for cog in [self.client.get_cog(cogs) for cogs in self.client.cogs]:
            for command in cog.get_commands():
                if command.checks:
                    for check in command.checks:
                        try:
                            await check(ctx)
                            name = ' / '.join([self.client.command_prefix + command.name] + [self.client.command_prefix + alias for alias in command.aliases])
                            embed.add_field(name=name, value=command.brief, inline=False)
                        except commands.errors.CheckAnyFailure:
                            pass
                else:
                    name = ' / '.join([self.client.command_prefix + command.name] + [self.client.command_prefix + alias for alias in command.aliases])
                    embed.add_field(name=name, value=command.brief, inline=False)
        await ctx.author.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
