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
            description="https://www.youtube.com/channel/UCZwaYbXg_umFjI0knBV5PhA"
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
        self.warps_embed = discord.Embed(
            title="Warps de BTE: France",
            colour=discord.Colour(0xFFFFFF),
            description="https://cutt.ly/warps"
        )
        self.map_embed.set_thumbnail(url=self.thumbnail_url)
        self.youtube_embed.set_thumbnail(url=self.thumbnail_url)
        self.twitter_embed.set_thumbnail(url=self.thumbnail_url)
        self.instagram_embed.set_thumbnail(url=self.thumbnail_url)
        self.warps_embed.set_thumbnail(url=self.thumbnail_url)

    @commands.command(brief='Check the latency between the bot and the user')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency*1000)}ms')

    @commands.command(aliases=['purge'], brief='Clear the last x messages sent in the channel')
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True, manage_channels=True))
    async def clear(self, ctx, number=1):
        await ctx.channel.purge(limit=number + 1)

    @commands.command(brief='Map Link')
    async def map(self, ctx):
        await ctx.send(embed=self.map_embed)

    @commands.command(brief='YouTube Link', aliases=['ytb', 'yt'])
    async def youtube(self, ctx):
        await ctx.send(embed=self.youtube_embed)

    @commands.command(brief='Twitter Link', aliases=['twi'])
    async def twitter(self, ctx):
        await ctx.send(embed=self.twitter_embed)

    @commands.command(brief='Instagram Link', aliases=['insta'])
    async def instagram(self, ctx):
        await ctx.send(embed=self.instagram_embed)

    @commands.command(brief='Warps Link', aliases=['warp'])
    async def warps(self, ctx):
        await ctx.send(embed=self.warps_embed)


def setup(client):
    client.add_cog(RandomCommands(client))
