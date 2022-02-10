import discord
import variables
from discord.ext import commands


class RandomCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.thumbnail_url = variables.bte_france_icon

    @commands.command(brief="Donne la latence du bot")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency*1000)}ms")

    @commands.command(aliases=["purge"], brief="Supprime les x derniers messages")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True, manage_channels=True))
    async def clear(self, ctx, number=1):
        try:
            await ctx.channel.purge(limit=number + 1)
        except AttributeError:  # Purging a DM/Group channel
            pass

    @commands.command(brief="Lien des maps BTE")
    async def map(self, ctx):
        embed = discord.Embed(
            title="Maps de BTE",
            colour=discord.Colour(0x00FF00),
            description="[**Map internationale**](https://buildtheearth.net/map)\n\n[**Map française**](https://www.google.com/maps/d/edit?mid=17R3mouwkPRlzvkT4NKH1idmB9M9xTCcv&usp=sharing)",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien YouTube", aliases=["ytb", "yt"])
    async def youtube(self, ctx):
        embed = discord.Embed(
            title="YouTube de BTE: France",
            colour=discord.Colour(0xFF0000),
            description="https://www.youtube.com/c/BTEFrance",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien Twitter", aliases=["twi", "tw"])
    async def twitter(self, ctx):
        embed = discord.Embed(
            title="Twitter de BTE: France",
            colour=discord.Colour(0x0000FF),
            description="https://twitter.com/BTE_France",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien Instagram", aliases=["insta"])
    async def instagram(self, ctx):
        embed = discord.Embed(
            title="Instagram de BTE: France",
            colour=discord.Colour(0xFFFF00),
            description="https://www.instagram.com/bte_france/",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien Facebook", aliases=["fb"])
    async def facebook(self, ctx):
        embed = discord.Embed(
            title="Facebook de BTE: France",
            colour=discord.Colour(0x0800FF),
            description="https://www.facebook.com/Build-The-Earth-France-113380800556340",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien Reddit")
    async def reddit(self, ctx):
        embed = discord.Embed(
            title="Reddit de BTE: France",
            colour=discord.Colour(0x0800FF),
            description="https://www.reddit.com/user/BTE_France/",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien PlanetMinecraft", aliases=["pm"])
    async def planetminecraft(self, ctx):
        embed = discord.Embed(
            title="PlanetMinecraft de BTE: France",
            colour=discord.Colour(0x0800FF),
            description="https://www.planetminecraft.com/member/bte-france",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Lien TikTok", aliases=["tk"])
    async def tiktok(self, ctx):
        embed = discord.Embed(
            title="TikTok de BTE: France",
            colour=discord.Colour(0x0800FF),
            description="https://www.tiktok.com/@btefrance",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Tutoriel Bedrock")
    async def bedrock(self, ctx):
        embed = discord.Embed(
            title="Comment rejoindre BTE quand on joue sur Bedrock?",
            colour=discord.Colour(0x0800FF),
            description="https://docs.google.com/document/d/12QG9d_O2ZX-OH9CdC44urpfWCnSmSon4nhsSXyuuGsM/edit?usp=drivesdk",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Read the rules")
    async def lire(self, ctx):
        embed = discord.Embed(
            description=f"As-tu bien lu le salon {self.client.get_channel(variables.comment_rejoindre_channel).mention}?",
            colour=discord.Colour(0xFF0000),
        )
        await ctx.send(embed=embed)

    @commands.command(brief="Liste IPs")
    async def ip(self, ctx):
        embed = discord.Embed(
            title="IPs de BTE: France",
            colour=discord.Colour(0x0800FF),
            description=":arrow_right: Version Java: `buildtheearth.net`, puis `/bt FR` quand vous êtes dans le lobby\n:arrow_right: Version Bedrock: `bedrock.buildtheearth.net`, port `19132`.",
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Ban Image")
    async def ban(self, ctx):
        await ctx.send("https://i.imgur.com/RGfJXmZ.png")

    @commands.command(brief="Read the Rules Image", aliases=["regles"])
    async def lis(self, ctx):
        await ctx.send("https://i.imgur.com/AP0CD1J.png")

    @commands.command(brief="Stonks GIF")
    async def stonks(self, ctx):
        await ctx.send("https://media2.giphy.com/media/YnkMcHgNIMW4Yfmjxr/giphy.gif")

    @commands.command(brief="Triforce image")
    async def triforce(self, ctx):
        await ctx.send("https://i.imgur.com/DNxRVsV.png")

    @commands.command(brief="Sel image")
    async def sel(self, ctx):
        await ctx.send("https://i.imgur.com/8RoWypa.png")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        for log in logs:
            if log.target == member and not log.user.bot:
                await self.client.get_channel(variables.logs_channel).send(f'**{log.user} banned {log.target} for the reason:**\n{log.reason}')


def setup(client):
    client.add_cog(RandomCommands(client))
