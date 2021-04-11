import discord
import variables
from discord.ext import commands

nums = [
    ":one:",
    ":two:",
    ":three:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
]
emoji_list = [
    [f"{i+1}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}", nums[i]]
    for i in range(len(nums))
]
emoji_list += [
    ["\N{REGIONAL INDICATOR SYMBOL LETTER A}", ":regional_indicator_a:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER B}", ":regional_indicator_b:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER C}", ":regional_indicator_c:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER D}", ":regional_indicator_d:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER E}", ":regional_indicator_e:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER F}", ":regional_indicator_f:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER G}", ":regional_indicator_g:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER H}", ":regional_indicator_h:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER I}", ":regional_indicator_i:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER J}", ":regional_indicator_j:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER K}", ":regional_indicator_k:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER L}", ":regional_indicator_l:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER M}", ":regional_indicator_m:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER N}", ":regional_indicator_n:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER O}", ":regional_indicator_o:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER P}", ":regional_indicator_p:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER Q}", ":regional_indicator_q:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER R}", ":regional_indicator_r:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER T}", ":regional_indicator_t:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER V}", ":regional_indicator_v:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER W}", ":regional_indicator_w:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER X}", ":regional_indicator_x:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER Y}", ":regional_indicator_y:"],
    ["\N{REGIONAL INDICATOR SYMBOL LETTER Z}", ":regional_indicator_z:"],
]


class Poll(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.title = None
        self.choices = []
        prefix = self.client.command_prefix
        self.poll_embed = discord.Embed(
            title="Poll Help", colour=discord.Colour(0x0000FF)
        )
        self.poll_embed.add_field(
            name=":one: Create a poll",
            value=f"{prefix}poll create <title>",
            inline=False,
        )
        self.poll_embed.add_field(
            name=":two: Add choices", value=f"{prefix}poll add <choice>", inline=False
        )
        self.poll_embed.add_field(
            name=":three: Show the poll", value=f"{prefix}poll show", inline=False
        )
        self.poll_embed.add_field(
            name=":four: Reset the poll", value=f"{prefix}poll reset", inline=False
        )
        self.poll_embed.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(brief="Création d'un sondage. .poll help pour plus d'infos")
    @commands.check_any(
        commands.is_owner(),
        commands.has_permissions(manage_roles=True, manage_channels=True),
    )
    async def poll(self, ctx, *args):
        try:
            action = args[0]
            args = args[1:]
            if action == "create":
                title = ""
                for i in range(len(args)):
                    title += args[i] + " "
                self.title = title
                return

            elif action == "reset":
                self.title = None
                self.choices = []
                return

            elif action == "add":
                choice = ""
                for i in range(len(args)):
                    choice += args[i] + " "
                self.choices.append(choice)
                return

            elif action == "show":
                if self.title is not None:
                    if len(self.choices) <= len(emoji_list):
                        if len(self.choices) != 0:
                            embed = discord.Embed(title=self.title, type="rich")
                            emojis = [emoji_list[i] for i in range(len(self.choices))]
                            embed.description = "\n".join(
                                [
                                    f"{emojis[i][1]} {self.choices[i]}"
                                    for i in range(len(self.choices))
                                ]
                            )
                            message = await ctx.channel.send(embed=embed)
                            for emoji in emojis:
                                await message.add_reaction(emoji[0])
                        else:
                            await ctx.channel.send("No choices exist!")
                    else:
                        await ctx.channel.send("Too many choices! (max: 35)")
                else:
                    await ctx.channel.send("No poll exists!")
                return
        except IndexError:
            pass
        await ctx.send(embed=self.poll_embed)


def setup(client):
    client.add_cog(Poll(client))
