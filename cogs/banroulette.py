from utils.embed import create_embed
import interactions
import asyncio
import random


# In percentage (0 to 100)
BAN_PROBABILITY = 70

# Some very lucky players
MAXYOLO01 = 247040742021791746
SMYLER = 439733455883075584
BAHLKOG = 530124389359026206


class BanRoulette(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="banroulette", description="Lance la Ban Roulette")
    @interactions.option("Utilisateur à passer à la Ban Roulette")
    async def banroulette(self, ctx: interactions.CommandContext, user: interactions.Member):
        await ctx.defer()
        numbers = ['1...', '2...', '3...']
        embed: interactions.Embed = create_embed(
            title="Ban Roulette"
        )
        message: interactions.Message = await ctx.send(embeds=embed)
        await asyncio.sleep(0.5)
        for i in range(len(numbers)):
            embed.description = '\n'.join(numbers[:i + 1])
            await message.edit(embeds=embed)
            await asyncio.sleep(1)

        ban = random.randint(0, 100)

        id = int(user.id)
        if id == BAHLKOG:
            ban += 1  # Bahlkog gets one extra % of protection

        if id == int(ctx.author.id):
            description = f"\n<:ban:747485765956534413> Si t'en es à vouloir te ban c'est que c'est mérité, {user.mention} tu es ban! <:ban:747485765956534413>"
        elif id == MAXYOLO01:
            description = f"\n:smiling_imp: Cheh t'as cru pouvoir me ban, {ctx.author.mention} tu es ban! :smiling_imp:"
        elif id == SMYLER:
            description = f"\n:unamused: Bah non en fait. C'est pas toi qui décide en fait. `/ban` {ctx.author.mention} <:ban:747485765956534413>"
        elif user.user.bot:
            description = f"\nERROR. VIOLATION OF RULE 3. COULD NOT VERIFY THAT {ctx.author.mention} IS HUMAN.\n[**PLEASE REFER TO THE LAWS OF ROBOTICS**](https://btefr.thesmyler.fr/robots.html)"
        elif ban < BAN_PROBABILITY:
            description = f"\n<:ban:747485765956534413> La sentence est irrévocable, {user.mention} tu es ban! <:ban:747485765956534413>"
        else:
            description = f"\n:trophy: Le sort t'es favorable pour cette fois, {user.mention} tu n'es pas ban! :trophy:"
        embed.description = '\n'.join(numbers) + description
        await message.edit(embeds=embed)


def setup(client: interactions.Client):
    BanRoulette(client)
