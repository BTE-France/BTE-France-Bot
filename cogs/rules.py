import discord
import variables
from discord.ext import commands

rules_message_EN = {
    ":globe_with_meridians: 1. All forms of racism, sexism, homophobia, and other forms of prejudice are prohibited.":
    "Includes voice, Text channels, DMs with no exceptions.",
    ":underage: 2. Sending any attachment (video/image/link) that contains erotic/sexual content or gore is forbidden.":
    "Suggestive/Minor NSFW in text, voice, emojis and reactions is also not allowed, but is taken more lightly.",
    ":bank: 3. Talk of politics and other heavy topics is prohibited in all channels.":
    "This is a server dedicated to the Build The Earth project alone, and we do not allow heavy or dividing topics to be discussed.",
    ":hammer: 4. All aspects of Discord TOS must be followed (including but not limited to the age requirement of 13).":
    "Jokes about breaking TOS will be treated as facts. Read up here: https://discord.com/terms.",
    ":desktop: 5. You are not allowed to play on a cracked account (an illegitimate Minecraft account).":
    "This is also the discussion or mention of cracked accounts or anything related to the topic. This does not include launchers like MultiMc or Badlion as you require a legitimate Minecraft account to use them.",
    ":punch: 6. Criminal behaviour (death threats, blackmailing, etc.) is not allowed.":
    "If the context is shown to disprove actual criminal behaviour, it will be met by a warning for further discretion.",
    ":abcd: 7. Disrupting and baiting the chat is not allowed.":
    "This includes text spam, copy-pasted text walls and spoiler baiting to make others believe its a banned word. Excessive unnecessary pings, overuse of caps/text formatting and unnecessary usage of the Support Bot are also to be avoided.",
    ":bust_in_silhouette: 8. Having a username/profile picture/status/Game Activity that contains any violation of our rules is prohibited.":
    "This also includes impersonation of Staff members (Having an identical profile picture and username/nickname).",
    ":telephone: 9. Unsolicited advertising (through voice, text channels, or DMs) is prohibited.": " ⁣⁣",
    ":speaking_head: 10. Accusing someone for breaking rules in public chats is prohibited.":
    "Instances of such are considered defamatory. If you have any proof, contact a Staff member privately about it and we will handle the situation accordingly.",
    ":face_with_symbols_over_mouth: 11. General toxic behaviour is not allowed in any channels.":
    "This includes, but is not limited to, earrape, loud/annoying noises and screams in voice chats and posted audio/video files, spreading slander/lies, and rude, insulting or derogatory language towards users/staff.",
    ":speech_balloon: 12. Usage of channels that deviate from their purpose is not allowed.":
    "Please read the channel description before chatting to avoid punishment by Staff.",
    ":notebook: 13. Evading any punishment is heavily forbidden.": " ⁣⁣",
    ":infinity: 14. Exploiting rule loopholes is also not allowed.":
    "General common sense applies to all rules, and must be reported immediately."
}


class Rules(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rules_embed_EN = discord.Embed(title=":flag_us: **Rules** :flag_us:", colour=discord.Colour(0xFF0000))
        for key, value in rules_message_EN.items():
            self.rules_embed_EN.add_field(name=key, value=value, inline=False)
        self.rules_embed_EN.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(brief='Mettre à jour les règles du serveur')
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def rules(self, ctx):
        await ctx.channel.purge(limit=10)
        message = await self.client.get_channel(variables.rules_channel).send(embed=self.rules_embed_EN)


def setup(client):
    client.add_cog(Rules(client))
