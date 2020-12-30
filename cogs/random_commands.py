import discord
from discord.ext import commands


class RandomCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.thumbnail_url = "https://cdn.discordapp.com/icons/694003889506091100/a_c40ba19cfcfbb9db5f5060e85f6539cf.png?size=128"
        self.map_embed = discord.Embed(
            title="Map du Projet BTE",
            colour=discord.Colour(0x00FF00),
            description="https://buildtheearth.net/map"
        )
        self.youtube_embed = discord.Embed(
            title="YouTube de BTE: France",
            colour=discord.Colour(0xFF0000),
            description="https://www.youtube.com/c/BTEFrance"
        )
        self.twitter_embed = discord.Embed(
            title="Twitter de BTE: France",
            colour=discord.Colour(0x0000FF),
            description="https://twitter.com/BuildFr"
        )
        self.instagram_embed = discord.Embed(
            title="Instagram de BTE: France",
            colour=discord.Colour(0xFFFF00),
            description="https://www.instagram.com/bte_france/"
        )
        self.facebook_embed = discord.Embed(
            title="Facebook de BTE: France",
            colour=discord.Colour(0x0800FF),
            description="https://www.facebook.com/Build-The-Earth-France-113380800556340"
        )
        self.map_embed.set_thumbnail(url=self.thumbnail_url)
        self.youtube_embed.set_thumbnail(url=self.thumbnail_url)
        self.twitter_embed.set_thumbnail(url=self.thumbnail_url)
        self.instagram_embed.set_thumbnail(url=self.thumbnail_url)
        self.facebook_embed.set_thumbnail(url=self.thumbnail_url)

    @commands.command(brief='Donne la latence du bot')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency*1000)}ms')

    @commands.command(aliases=['purge'], brief='Supprime les x derniers messages')
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True, manage_channels=True))
    async def clear(self, ctx, number=1):
        await ctx.channel.purge(limit=number + 1)

    @commands.command(brief='Lien de la Map BTE')
    async def map(self, ctx):
        await ctx.send(embed=self.map_embed)

    @commands.command(brief='Lien YouTube', aliases=['ytb', 'yt'])
    async def youtube(self, ctx):
        await ctx.send(embed=self.youtube_embed)

    @commands.command(brief='Lien Twitter', aliases=['twi', 'tw'])
    async def twitter(self, ctx):
        await ctx.send(embed=self.twitter_embed)

    @commands.command(brief='Lien Instagram', aliases=['insta'])
    async def instagram(self, ctx):
        await ctx.send(embed=self.instagram_embed)

    @commands.command(brief='Lien Facebook', aliases=['fb'])
    async def facebook(self, ctx):
        await ctx.send(embed=self.facebook_embed)


def setup(client):
    client.add_cog(RandomCommands(client))
