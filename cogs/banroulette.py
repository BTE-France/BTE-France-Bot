from discord.ext import commands
import variables
import discord
import asyncio
import random

# In percentage (0 to 100)
BAN_PROBABILITY = 70


class BanRoulette(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.invalid_embed = discord.Embed(
            title="Ban Roulette",
            description="Invalid member!\n**Correct syntax: .banroulette <mentioned_user>**",
            colour=discord.Colour(0xFF0000)
        )
        self.invalid_embed.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(brief="Ban Roulette")
    async def banroulette(self, ctx, member: discord.User = None):
        if not member:
            await ctx.send(embed=self.invalid_embed)
            return

        numbers = ['1...', '2...', '3...']
        embed = discord.Embed(title="Ban Roulette", colour=discord.Colour(0x0000FF))
        embed.set_thumbnail(url=variables.bte_france_icon)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        for i in range(len(numbers)):
            embed.description = '\n'.join(numbers[:i + 1])
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        ban = random.randint(0, 100)
        if member.id == 247040742021791746:
            embed.description += f"\n:smiling_imp: Cheh t'as cru pouvoir me ban, {ctx.author.mention} tu es ban! :smiling_imp:"
        elif member.id == 439733455883075584:
            embed.description += f"\n:unamused: Bah non en fait. C'est pas toi qui décide en fait. `/ban` {ctx.author.mention} <:ban:747485765956534413>"
        elif ban < BAN_PROBABILITY:
            embed.description += f"\n<:ban:747485765956534413> La sentence est irrévocable, {member.mention} tu es ban! <:ban:747485765956534413>"
        else:
            embed.description += f"\n:trophy: Le sort t'es favorable pour cette fois, {member.mention} tu n'es pas ban! :trophy:"
        await message.edit(embed=embed)

    @banroulette.error
    async def brush_handler(self, ctx, error):
        if isinstance(error, commands.errors.UserNotFound):
            await ctx.send(embed=self.invalid_embed)
            return


def setup(client):
    client.add_cog(BanRoulette(client))
