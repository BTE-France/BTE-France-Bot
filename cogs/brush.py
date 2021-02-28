import variables
import discord
import random
from discord.ext import commands

# emoji_servers = {serverID: blockIdUpperBound, ...}
emoji_servers = {815307423979667487: 33, 815309118348853289: 89, 815310995958005762: 154,
                 815314056193376306: 213, 815314860560220190: 250, 815317197366493184: 255}


class Brush(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.syntax_embed = discord.Embed(
            title="Wrong syntax! Write .br <material> [size=8]", colour=discord.Colour(0xFF0000))
        self.syntax_embed.add_field(
            name="Maximum size: 8", value='_ _', inline=False)
        self.syntax_embed.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(aliases=['br'], brief='Brush command to replicate the WorldEdit brush')
    async def brush(self, ctx, material=None, size=8):
        if material is None or size > 8:
            await ctx.send(embed=self.syntax_embed)
            return
        material_split = material.split(',')
        weights, materials = [], []
        forget_weights = False
        for mat in material_split:
            result = mat.split('%')
            if len(result) == 2:
                materials.append(result[1])
                try:
                    weights.append(int(result[0]))
                except ValueError:  # Weight is not a number
                    await ctx.send("Wrong weight detected: " + result[0])
                    return
            elif len(result) == 1:  # No weight set, cancelling weights for all blocks
                forget_weights = True
                materials.append(result[0])
            else:
                await ctx.send("Wrong syntax in materials!")
                return
        weights = None if forget_weights else weights
        weighted_list = random.choices(
            population=materials, weights=weights, k=size**2)
        # print('\n'.join(weighted_list))
        columns, not_found = ["" for _ in range(size)], []
        for j in range(size):
            for i in range(size):
                emoji_raw = weighted_list[j * size + i]
                emoji = self.get_emoji(emoji_raw)
                if emoji is None:
                    columns[j] += ":question:"
                    if emoji_raw not in not_found:
                        not_found.append(emoji_raw)
                else:
                    columns[j] += str(emoji)
        await ctx.send('\n'.join(columns))
        if not_found:
            await ctx.send(':question: `Unrecognized IDs: ' + ', '.join(sorted(not_found)) + '` :question:')

    @brush.error
    async def brush_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(embed=self.syntax_embed)
            return

    def get_emoji(self, emoji_raw):
        try:
            emoji_id = int(emoji_raw.split(':')[0])
        except ValueError:  # Emoji is not a number
            return None
        if emoji_id < 0 or emoji_id > 255:
            return None
        for serverID, upperBound in emoji_servers.items():
            if emoji_id <= upperBound:
                server = serverID
                break
        if server is None:
            return None
        for emoji in self.client.get_guild(server).emojis:
            if emoji.name == '_' + emoji_raw.replace(':', '_'):
                return emoji
        return None


def setup(client):
    client.add_cog(Brush(client))
