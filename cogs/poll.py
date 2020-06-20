import discord
from discord.ext import commands

emoji_list = [
    ['1\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':one:'],
    ['2\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':two:'],
    ['3\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':three:'],
    ['4\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':four:'],
    ['5\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':five:'],
    ['6\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':six:'],
    ['7\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':seven:'],
    ['8\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':eight:'],
    ['9\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}', ':nine:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER A}', ':regional_indicator_a:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER B}', ':regional_indicator_b:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER C}', ':regional_indicator_c:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER D}', ':regional_indicator_d:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER E}', ':regional_indicator_e:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER F}', ':regional_indicator_f:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER G}', ':regional_indicator_g:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER H}', ':regional_indicator_h:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER I}', ':regional_indicator_i:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER J}', ':regional_indicator_j:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER K}', ':regional_indicator_k:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER L}', ':regional_indicator_l:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER M}', ':regional_indicator_m:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER N}', ':regional_indicator_n:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER O}', ':regional_indicator_o:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER P}', ':regional_indicator_p:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER Q}', ':regional_indicator_q:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER R}', ':regional_indicator_r:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER S}', ':regional_indicator_s:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER T}', ':regional_indicator_t:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER U}', ':regional_indicator_u:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER V}', ':regional_indicator_v:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER W}', ':regional_indicator_w:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER X}', ':regional_indicator_x:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER Y}', ':regional_indicator_y:'],
    ['\N{REGIONAL INDICATOR SYMBOL LETTER Z}', ':regional_indicator_z:'],
]


class Poll(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.title = None
        self.choices = []

    @commands.command(brief='Create a poll')
    async def poll(self, ctx, action, *args):
        if action == 'create':
            title = ''
            for i in range(len(args)):
                title += args[i] + ' '
            self.title = title

        elif action == 'reset':
            self.title = None
            self.choices = []

        elif action == 'add':
            choice = ''
            for i in range(len(args)):
                choice += args[i] + ' '
            self.choices.append(choice)

        elif action == 'show':
            if self.title is not None:
                if len(self.choices) <= len(emoji_list):
                    if len(self.choices) != 0:
                        embed = discord.Embed(title=self.title, type='rich')
                        emojis = []
                        for i in range(len(self.choices)):
                            emojis.append(emoji_list[i])
                        desc = ''
                        for i in range(len(self.choices)):
                            desc += f'{emojis[i][1]} {self.choices[i]}\n'
                        embed.description = desc
                        message = await ctx.channel.send(embed=embed)
                        for emoji in emojis:
                            await message.add_reaction(emoji[0])
                    else:
                        await ctx.channel.send("No choices exist!")
                else:
                    await ctx.channel.send("Too many choices! (max: 35)")
            else:
                await ctx.channel.send("No poll exists!")


def setup(client):
    client.add_cog(Poll(client))
