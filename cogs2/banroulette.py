from utils.embed import create_embed
from variables import server
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

    @interactions.extension_command(name="banroulette", description="Ban Roulette", scope=server, options=[
        interactions.Option(type=interactions.OptionType.USER, name="user", description="User to summon ban roulette upon", required=True)
    ])
    async def banroulette(self, ctx: interactions.CommandContext, user: str):
        user: interactions.User = interactions.User(**await self.client._http.get_user(int(user)))

        numbers = ['1...', '2...', '3...']
        embed: interactions.Embed = create_embed(
            title="Ban Roulette"
        )
        message: interactions.Message = await ctx.send(embeds=embed)
        await asyncio.sleep(1)
        for i in range(len(numbers)):
            embed: interactions.Embed = create_embed(
                title="Ban Roulette",
                description='\n'.join(numbers[:i + 1])
            )
            await message.edit(embeds=embed)
            await asyncio.sleep(1)

        ban = random.randint(0, 100)

        if int(user.id) == BAHLKOG:
            ban += 1  # Bahlkog gets one extra % of protection

        if int(user.id) == ctx.author.id:
            description = f"\n<:ban:747485765956534413> Si t'en es à vouloir te ban c'est que c'est mérité, {user.mention} tu es ban! <:ban:747485765956534413>"
        elif int(user.id) == MAXYOLO01:
            description = f"\n:smiling_imp: Cheh t'as cru pouvoir me ban, {ctx.author.mention} tu es ban! :smiling_imp:"
        elif int(user.id) == SMYLER:
            description = f"\n:unamused: Bah non en fait. C'est pas toi qui décide en fait. `/ban` {ctx.author.mention} <:ban:747485765956534413>"
        elif user.bot:
            description = f"\nERROR. VIOLATION OF RULE 3. COULD NOT VERIFY THAT {ctx.author.mention} IS HUMAN.\nPLEASE REFER TO THE LAWS OF ROBOTICS: https://btefr.thesmyler.fr/robots.html"
        elif ban < BAN_PROBABILITY:
            description = f"\n<:ban:747485765956534413> La sentence est irrévocable, {user.mention} tu es ban! <:ban:747485765956534413>"
        else:
            description = f"\n:trophy: Le sort t'es favorable pour cette fois, {user.mention} tu n'es pas ban! :trophy:"
        embed: interactions.Embed = create_embed(
            title="Ban Roulette",
            description='\n'.join(numbers) + description
        )
        await message.edit(embeds=embed)


def setup(client: interactions.Client):
    BanRoulette(client)