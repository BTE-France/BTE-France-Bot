import discord
import variables
from discord.ext import commands

rules_message_FR = {
    "Toute forme de racisme, de sexisme, d'homophobie et d'autres formes de préjugés est interdite.": "Comprend les canaux vocaux, les canaux textuels, les DMs sans exceptions.",
    "Envoyer toute pièce jointe (vidéo/image/lien) contenant du contenu érotique/sexuel ou gore est interdit": "Du NSFW mineur dans un texte, vocal, emoji ou réaction est également interdit, mais pris plus à la légère.",
    "Il est interdit de parler de politique et d'autres sujets lourds sur tout les canaux": "Il s'agit d'un serveur dédié à Build The Earth, et nous ne permettons pas de discuter de sujets lourds ou diviseurs.",
    "Tout les aspects des CGU de Discord doivent être respectés (y compris, mais sans s'y limiter, la condition d'âge de 13 ans)": "Les blagues sur la rupture des CGU seront traitées comme des faits. Lisez ici: https://discord.com/terms.",
    "Vous n'êtes pas autorisé à jouer sur un compte piraté/crack (un compte Minecraft illégitime)": "Ceci n'inclut pas les launchers tels que MultiMC ou Badlion car vous avez besoin d'un compte Minecraft légitime pour les utiliser.",
    "Les comportements criminels (menaces de mort, chantage, etc...) ne sont pas autorisés.": "Si le contexte sert à réfuter le comportement criminel, il sera répondu par un avertissement pour plus de discrétion.",
    "Il est interdit de perturber ou de bait le chat.": "Cela inclut le spam textuel, le copier-coller de murs de texte et le spoil bait pour faire croire aux autres à un mot interdit. Il faut également éviter le ping excessif et inutile, la surutilisation de majuscules et le formatage du texte.",
    "Il est interdit d'avoir un nom d'utilisateur, une photo de profil, un statut ou une activité de jeu qui enfreint nos règles.": "Cela inclut également l'usurpation de l'identité de membres du Staff (avoir une photo ou un nom d'utilisateur identique).",
    "La publicité non sollicitée (par voix, texte ou DM) est interdite": " ⁣⁣",
    "Il est interdit d'accuser quelqu'un d'enfreindre les règles dans les chats publics": "De telles situations sont considérées comme diffamatoires. Si vous avez des preuves, contactez un membre du Staff en privé à ce sujet et nous traiterons la situation en conséquence",
    "Le comportement toxique général n'est autorisé dans aucun canal.": "Cela inclut, mais n'est pas limité à, du earrape, des bruits et des cris forts/désagréables dans les chats vocaus ou fichiers postés, la diffusion de calomnies/mensonges, et un langage grossier, insultant ou désobligeant envers les utilisateurs ou Staff.",
    "L'utilisation de canaux qui s'écartent de leur but n'est pas autorisée.": "Veuillez lire la description du canal avant de chatter afin d'éviter toute sanction.",
    "Eviter toute punition est fortement interdit.": " ⁣⁣",
    "Il est interdit d'exploiter une faille des règles.": "Le bon sens général s'applique à toutes les règles et doit être signalé immédiatement",
}
rules_message_EN = {
    "All forms of racism, sexism, homophobia, and other forms of prejudice are prohibited.": "Includes voice, Text channels, DMs with no exceptions.",
    "Sending any attachment (video/image/link) that contains erotic/sexual content or gore is forbidden.": "Suggestive/Minor NSFW in text, voice, emojis and reactions is also not allowed, but is taken more lightly.",
    "Talk of politics and other heavy topics is prohibited in all channels.": "This is a server dedicated to the Build The Earth project alone, and we do not allow heavy or dividing topics to be discussed.",
    "All aspects of Discord TOS must be followed (including but not limited to the age requirement of 13).": "Jokes about breaking TOS will be treated as facts. Read up here: https://discord.com/terms.",
    "You are not allowed to play on a cracked account (an illegitimate Minecraft account).": "This does not include launchers like MultiMc or Badlion as you require a legitimate Minecraft account to use them.",
    "Criminal behaviour (death threats, blackmailing, etc...) is not allowed.": "If the context is shown to disprove actual criminal behaviour, it will be met by a warning for further discretion.",
    "Disrupting and baiting the chat is not allowed.": "This includes text spam, copy-pasted text walls and spoiler baiting to make others believe its a banned word. Excessive unnecessary pings, overuse of caps/text formatting.",
    "Having a username/profile picture/status/Game Activity that contains any violation of our rules is prohibited.": "This also includes impersonation of Staff members (Having an identical profile picture and username/nickname).",
    "Unsolicited advertising (through voice, text channels, or DMs) is prohibited.": " ⁣⁣",
    "Accusing someone for breaking rules in public chats is prohibited.": "Instances of such are considered defamatory. If you have any proof, contact a Staff member privately about it and we will handle the situation accordingly.",
    "General toxic behaviour is not allowed in any channels.": "This includes, but is not limited to, earrape, loud/annoying noises and screams in voice chats and posted audio/video files, spreading slander/lies, and rude, insulting or derogatory language towards users/staff.",
    "Usage of channels that deviate from their purpose is not allowed.": "Please read the channel description before chatting to avoid punishment by Staff.",
    "Evading any punishment is heavily forbidden.": " ⁣⁣",
    "Exploiting rule loopholes is also not allowed.": "General common sense applies to all rules, and must be reported immediately.",
}
emotes = [
    "globe_with_meridians",
    "underage",
    "bank",
    "hammer",
    "desktop",
    "punch",
    "abcd",
    "bust_in_silhouette",
    "telephone",
    "speaking_head",
    "face_with_symbols_over_mouth",
    "speech_balloon",
    "notebook",
    "infinity",
]


class Rules(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rules_embed_FR = discord.Embed(
            title=":flag_fr: **Règles** :flag_fr:", colour=discord.Colour(0xFF0000)
        )
        for i, (key, value) in enumerate(rules_message_FR.items()):
            self.rules_embed_FR.add_field(
                name=f":{emotes[i]}: {i+1}. {key}", value=value, inline=False
            )
        self.rules_embed_FR.set_thumbnail(url=variables.bte_france_icon)
        self.rules_embed_EN = discord.Embed(
            title=":flag_us: **Rules** :flag_us:", colour=discord.Colour(0xFF0000)
        )
        for i, (key, value) in enumerate(rules_message_EN.items()):
            self.rules_embed_EN.add_field(
                name=f":{emotes[i]}: {i+1}. {key}", value=value, inline=False
            )
        self.rules_embed_EN.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(brief="Mettre à jour les règles du serveur")
    @commands.check_any(
        commands.is_owner(), commands.has_permissions(administrator=True)
    )
    async def rules(self, ctx):
        await self.client.get_channel(variables.rules_channel).send(
            embed=self.rules_embed_FR
        )
        await self.client.get_channel(variables.rules_channel).send(
            embed=self.rules_embed_EN
        )

    @commands.command(brief="Mettre à jour les IPs du serveur")
    @commands.check_any(
        commands.is_owner(), commands.has_permissions(administrator=True)
    )
    async def ip_embed(self, ctx):
        embed = discord.Embed(title="**Comment rejoindre le serveur BTE France**", color=16098851)
        embed.add_field(name="__IPs JAVA__", value="(Version PC)", inline=False)
        embed.add_field(name="<:mc:695357986427895869>", value="Principale : ```buildtheearth.net``` __Puis faites une fois en jeu :__```/bt FR```", inline=True)
        embed.add_field(name="<:mc:695357986427895869>", value="Alternative :```bte.thesmyler.fr```", inline=True)
        embed.add_field(name="__IP BEDROCK__", value="(Windows 10, consoles...)", inline=False)
        embed.add_field(name="<:mc:695357986427895869>", value="```bedrock.buildtheearth.net```Port:```19132```", inline=True)
        embed.set_thumbnail(url=variables.bte_france_icon)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Rules(client))
