import variables
import json
import googletrans
import discord
from discord.ext import commands


class Translator(commands.Cog):
    """Thanks to @Benjy#1026 for the idea and the help!"""

    def __init__(self, client):
        self.client = client
        self.translator = googletrans.Translator()

    def get_language(self, flag):
        with open("languages.json", "r") as datafile:
            jsondata = json.loads(datafile.read())
            return jsondata.get(flag)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        language = self.get_language(reaction.emoji)
        if language:
            text = str(reaction.message.content)
            if (
                language not in googletrans.LANGUAGES
                and language not in googletrans.LANGCODES
            ):
                await reaction.message.channel.send(
                    embed=discord.Embed(title="Translation failed!", colour=0xFF0000)
                )
            else:
                translated_text = self.translator.translate(text, dest=language).text
                embed = discord.Embed(
                    title=f"Translation to {language}  {reaction.emoji}",
                    description=translated_text,
                    colour=discord.Colour(0xA6A67A),
                )
                embed.set_thumbnail(url=variables.bte_france_icon)
                embed.set_footer(
                    text=f"Requested by @{user.name}#{user.discriminator}",
                    icon_url=user.avatar_url,
                )
                await reaction.message.channel.send(embed=embed)


def setup(client):
    client.add_cog(Translator(client))
