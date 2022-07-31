from utils.embed import create_embed, create_error_embed, create_info_embed
from variables import server, rules_channel, ip_channel, comment_rejoindre_channel, verify_channel
import interactions


class Embeds(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="embeds", description="Update the server's embeds", scope=server, default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    @interactions.option("Channel to update", channel_types=[interactions.ChannelType.GUILD_TEXT])
    async def embeds(self, ctx: interactions.CommandContext, channel: interactions.Channel):
        channel_id = int(channel.id)

        if channel_id == rules_channel:
            embeds = self.rules_embed()
        elif channel_id == ip_channel:
            embeds = self.ip_embed()
        elif channel_id == comment_rejoindre_channel:
            embeds = self.comment_rejoindre_embed()
        else:
            await ctx.send(embeds=create_error_embed(f"{channel.mention} does not have a corresponding embed!"), ephemeral=True)
            return

        await channel.send(embeds=embeds)
        await ctx.send(embeds=create_info_embed(f"The embed has successfully been updated in {channel.mention}"), ephemeral=True)

    def rules_embed(self) -> list[interactions.Embed]:
        RULES_FR = {
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
        RULES_EN = {
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
        RULES_EMOTES = [
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
        RULES = [
            create_embed(
                title=":flag_fr: **Règles** :flag_fr:",
                color=0xFF0000,
                fields=[
                    (f":{RULES_EMOTES[i]}: {i+1}. {key}", value, False) for i, (key, value) in enumerate(RULES_FR.items())
                ]
            ),
            create_embed(
                title=":flag_us: **Rules** :flag_us:",
                color=0xFF0000,
                fields=[
                    (f":{RULES_EMOTES[i]}: {i+1}. {key}", value, False) for i, (key, value) in enumerate(RULES_EN.items())
                ]
            )
        ]
        return RULES

    def ip_embed(self) -> list[interactions.Embed]:
        IP = [
            create_embed(
                title="**Comment rejoindre le serveur BTE France ?**",
                color=0x0000FF,
                fields=[
                    ("__IPs JAVA__", "(Version PC)", False),
                    ("<:minecraft_heart:922583879469117491>", "BTE Hub : ```buildtheearth.net``` __Puis faites une fois en jeu :__```/bt FR```", True),
                    ("<:minecraft_heart:922583879469117491>", "BTE France :```bte.thesmyler.fr```", True),
                    ("__IP BEDROCK__", "(Windows 10, mobile, consoles)", False),
                    ("<:bedrock:922583660761333850>", "```bedrock.buildtheearth.net, port: 19132```", True)
                ]
            )
        ]
        return IP

    def comment_rejoindre_embed(self) -> list[interactions.Embed]:
        ip = interactions.Channel(id=ip_channel, type=0).mention
        verify = interactions.Channel(id=verify_channel, type=0).mention
        COMMENT_REJOINDRE = [
            create_embed(
                title=":bank: Comment rejoindre le projet? :bank:",
                description=":arrow_right: Il vous faut premièrement le modpack, à télécharger ci-dessous **(INUTILE POUR BEDROCK)**\nTout est automatique, dézippez le fichier, ouvrez-le et cliquez sur **Install**, vous le retrouverez dans votre launcher Minecraft **(:warning: fermez votre launcher pendant l'installation)**",
                fields=[
                    ("Liens d'installation:", "[Windows](https://s3.buildtheearth.net/public/installer/v1.20/BTEInstaller-1.20.0-windows.zip)\n[Linux](https://s3.buildtheearth.net/public/installer/v1.20/BTEInstaller-1.20.0-linux.AppImage)\n[Mac](https://s3.buildtheearth.net/public/installer/v1.20/BTEInstaller-1.20.0-mac.dmg)\n[Universal](https://s3.buildtheearth.net/public/installer/v1.20/BTEInstaller-1.20.0-universal.jar)", False)
                ]
            ),
            create_embed(
                title=":gear: Quelle est l'IP? :gear:",
                description=f":arrow_right: Vous trouverez l'IP dans {ip} une fois avoir certifié la lecture des salons dans {verify}.",
            ),
            create_embed(
                title=":pick: Comment fonctionne le serveur? :pick:",
                description=":arrow_right: Accessible à la visite.\n:arrow_right: Pour construire, demandez le grade __Débutant__ **SUR le serveur Minecraft à un membre du staff.**",
                fields=[
                    ("Devenir builder officiel (pas obligatoire) :arrow_heading_down:", "[**Document**](https://docs.google.com/document/d/1DHMOEcmepY_jGlS_-tvCvpJmSbaoHmofnamTJleQYik/edit?usp=sharing)", False)
                ]
            ),
            create_embed(
                title=":thumbsup: Comment bien débuter? :thumbsup:",
                description=":arrow_right: Avoir le modpack (le lien juste au dessus)\n:arrow_right: Se repérer grâce à Terramap, touche M du clavier en jeu\n:arrow_right: Avoir Google Earth Pro afin de pouvoir mesurer les bâtiments en 3D\n:arrow_right: Visiter le serveur pour voir comment chaque builder a construit son bâtiment. (`/visite` ou `/warps` sur le serveur)",
            ),
            create_embed(
                title=":round_pushpin: Comment se téléporter? :round_pushpin:",
                description=":arrow_right: `/tpll [coordonnées]` (réservé aux builders)\n:arrow_right: `/visite` pour nos plus belles constructions\n:arrow_right: `/warps` pour tout voir\n\nUtiliser `/tpll` :arrow_heading_down:",
                image="https://s10.gifyu.com/images/TPLL_Help.gif"
            ),
            create_embed(
                title=":bangbang: Il est impératif de lire ce salon avant de poser une question, merci :bangbang:",
                description=f"Pour accéder à l'entièreté du Discord, n'oubliez pas de cliquez sur le :white_check_mark: dans {verify}.\n\n:red_square: **VERSIONS JAVA ET BEDROCK OFFICIELLES SEULEMENT** :red_square:",
            )
        ]
        return COMMENT_REJOINDRE


def setup(client: interactions.Client):
    Embeds(client)
