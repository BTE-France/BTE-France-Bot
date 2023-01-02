import aiohttp
import interactions

import variables
from utils.embed import create_embed, create_error_embed, create_info_embed

# Webhooks are formatted as a list of dictionaries, with each dictionary representing one message to be sent.
WEBHOOKS = {
    "Règles du serveur": [{"embeds": create_embed(
            title="🇫🇷 **Règles** 🇫🇷",
            color=0xFF0000,
            fields=[
                ("🌐 Toute forme de racisme, de sexisme, d'homophobie et d'autres formes de préjugés est interdite.", "Comprend les canaux vocaux, les canaux textuels, les DMs sans exceptions.", False),
                ("🔞 Envoyer toute pièce jointe (vidéo/image/lien) contenant du contenu érotique/sexuel ou gore est interdit", "Du NSFW mineur dans un texte, vocal, emoji ou réaction est également interdit, mais pris plus à la légère.", False),
                ("🏦 Il est interdit de parler de politique et d'autres sujets lourds sur tout les canaux", "Il s'agit d'un serveur dédié à Build The Earth, et nous ne permettons pas de discuter de sujets lourds ou diviseurs.", False),
                ("🔨 Tout les aspects des CGU de Discord doivent être respectés (y compris, mais sans s'y limiter, la condition d'âge de 13 ans)", "Les blagues sur la rupture des CGU seront traitées comme des faits. Lisez ici: https://discord.com/terms.", False),
                ("🖥️ Vous n'êtes pas autorisé à jouer sur un compte piraté/crack (un compte Minecraft illégitime)", "Ceci n'inclut pas les launchers tels que MultiMC ou Badlion car vous avez besoin d'un compte Minecraft légitime pour les utiliser.", False),
                ("👊 Les comportements criminels (menaces de mort, chantage, etc...) ne sont pas autorisés.", "Si le contexte sert à réfuter le comportement criminel, il sera répondu par un avertissement pour plus de discrétion.", False),
                ("🔡 Il est interdit de perturber ou de bait le chat.", "Cela inclut le spam textuel, le copier-coller de murs de texte et le spoil bait pour faire croire aux autres à un mot interdit. Il faut également éviter le ping excessif et inutile, la surutilisation de majuscules et le formatage du texte.", False),
                ("👤 Il est interdit d'avoir un nom d'utilisateur, une photo de profil, un statut ou une activité de jeu qui enfreint nos règles.", "Cela inclut également l'usurpation de l'identité de membres du Staff (avoir une photo ou un nom d'utilisateur identique).", False),
                ("☎️ La publicité non sollicitée (par voix, texte ou DM) est interdite", " ⁣⁣", False),
                ("🗣️ Il est interdit d'accuser quelqu'un d'enfreindre les règles dans les chats publics", "De telles situations sont considérées comme diffamatoires. Si vous avez des preuves, contactez un membre du Staff en privé à ce sujet et nous traiterons la situation en conséquence", False),
                ("🤬 Le comportement toxique général n'est autorisé dans aucun canal.", "Cela inclut, mais n'est pas limité à, du earrape, des bruits et des cris forts/désagréables dans les chats vocaus ou fichiers postés, la diffusion de calomnies/mensonges, et un langage grossier, insultant ou désobligeant envers les utilisateurs ou Staff.", False),
                ("💬 L'utilisation de canaux qui s'écartent de leur but n'est pas autorisée.", "Veuillez lire la description du canal avant de chatter afin d'éviter toute sanction.", False),
                ("📓 Eviter toute punition est fortement interdit.", " ⁣⁣", False),
                ("♾️ Il est interdit d'exploiter une faille des règles.", "Le bon sens général s'applique à toutes les règles et doit être signalé immédiatement", False)
            ]
        )}, {"embeds": create_embed(
            title="🇬🇧 **Rules** 🇬🇧",
            color=0xFF0000,
            fields=[
                ("🌐 All forms of racism, sexism, homophobia, and other forms of prejudice are prohibited.", "Includes voice, Text channels, DMs with no exceptions.", False),
                ("🔞 Sending any attachment (video/image/link) that contains erotic/sexual content or gore is forbidden.", "Suggestive/Minor NSFW in text, voice, emojis and reactions is also not allowed, but is taken more lightly.", False),
                ("🏦 Talk of politics and other heavy topics is prohibited in all channels.", "This is a server dedicated to the Build The Earth project alone, and we do not allow heavy or dividing topics to be discussed.", False),
                ("🔨 All aspects of Discord TOS must be followed (including but not limited to the age requirement of 13).", "Jokes about breaking TOS will be treated as facts. Read up here: https://discord.com/terms.", False),
                ("🖥️ You are not allowed to play on a cracked account (an illegitimate Minecraft account).", "This does not include launchers like MultiMc or Badlion as you require a legitimate Minecraft account to use them.", False),
                ("👊 Criminal behaviour (death threats, blackmailing, etc...) is not allowed.", "If the context is shown to disprove actual criminal behaviour, it will be met by a warning for further discretion.", False),
                ("🔡 Disrupting and baiting the chat is not allowed.", "This includes text spam, copy-pasted text walls and spoiler baiting to make others believe its a banned word. Excessive unnecessary pings, overuse of caps/text formatting.", False),
                ("👤 Having a username/profile picture/status/Game Activity that contains any violation of our rules is prohibited.", "This also includes impersonation of Staff members (Having an identical profile picture and username/nickname).", False),
                ("☎️ Unsolicited advertising (through voice, text channels, or DMs) is prohibited.", " ⁣⁣", False),
                ("🗣️ Accusing someone for breaking rules in public chats is prohibited.", "Instances of such are considered defamatory. If you have any proof, contact a Staff member privately about it and we will handle the situation accordingly.", False),
                ("🤬 General toxic behaviour is not allowed in any channels.", "This includes, but is not limited to, earrape, loud/annoying noises and screams in voice chats and posted audio/video files, spreading slander/lies, and rude, insulting or derogatory language towards users/staff.", False),
                ("💬 Usage of channels that deviate from their purpose is not allowed.", "Please read the channel description before chatting to avoid punishment by Staff.", False),
                ("📓 Evading any punishment is heavily forbidden.", " ⁣⁣", False),
                ("♾️ Exploiting rule loopholes is also not allowed.", "General common sense applies to all rules, and must be reported immediately.", False)
            ]
        )}],
    "Accueil": [
        {"embeds": [
            create_embed(
                title="🇫🇷 Bienvenue sur le serveur Discord BTE France 🇫🇷",
                description=f"""Le projet est simple, construire la planète Terre à l'échelle 1:1 sur Minecraft.
                Le serveur est dédié à la construction de la France métropolitaine et de ses DOM-TOM.

                Si vous souhaitez rejoindre le serveur en tant que builder ou bien pour visiter, toutes les étapes sont dans <#{variables.Channels.COMMENT_REJOINDRE}>"""
            ), create_embed(
                title="🇬🇧 Welcome to the BTE France Discord server 🇬🇧",
                description=f"""The project is simple, build the planet Earth at a 1:1 scale on Minecraft.
                The server is dedicated to the construction of metropolitan France and its overseas departments and territories.

                If you want to join our server as a builder or just to visit, you must follow the steps in <#{variables.Channels.HOW_TO_JOIN}>."""
            )
        ]},
        {
            "content": "_ _\n_ _\n_ _",
            "embeds": create_embed(
                title="⬇️ Choisis ta langue / Choose your language ⬇️",
                description="""⚠️ **Vous devez choisir votre langage pour avoir accès à l'entièreté du serveur!**

                ⚠️ **You must choose your language to get access to the entirety of the server!**""",
            ), "components": [
                interactions.Button(custom_id="verify_french", style=interactions.ButtonStyle.PRIMARY, label="Français", emoji=interactions.Emoji(name="🇫🇷")),
                interactions.Button(custom_id="verify_english", style=interactions.ButtonStyle.PRIMARY, label="English", emoji=interactions.Emoji(name="🇬🇧"))
            ]
        }
    ],
    "IP": [
        {
            "embeds": [create_embed(
                title="🇫🇷 **IP BTE France** 🇫🇷",
                fields=[
                    ("Version Java", f"_Il vous faudra télécharger le modpack BTE pour accéder au serveur. Les liens d'installation sont dans <#{variables.Channels.COMMENT_REJOINDRE}>._\n**IP: btefrance.fr**", False),
                    ("Version Bedrock", "_Il est actuellement impossible d'accéder au serveur via une version Bedrock du jeu (mobile, W10, console, ...)_", False)
                ]
            ), create_embed(
                title="🇬🇧 **BTE France IP** 🇬🇧",
                fields=[
                    ("Java Version", f"_You will need to download the BTE modpack to access the server. The installation links can be found in <#{variables.Channels.HOW_TO_JOIN}>._\n**IP: btefrance.fr**", False),
                    ("Bedrock Version", "_It is currently impossible to access the server using a Bedrock version of the game (mobile, W10, console, ...)_", False)
                ]
            )]
        }
    ],
    "Comment rejoindre?": [
        {"embeds": [
            create_embed(
                title="🏦 Comment rejoindre le projet? 🏦",
                description="""➡️ Il faut que vous ayez lancé au moins une fois la version 1.12.2 de Minecraft.

                ➡️ Puis, il vous faudra télécharger le modpack avec les liens ci-dessous:
                - [Windows](https://s3.buildtheearth.net/public/installer/latest/BTEInstaller-windows.zip)
                - [Linux](https://s3.buildtheearth.net/public/installer/latest/BTEInstaller-linux.AppImage)
                - [MacOS](https://s3.buildtheearth.net/public/installer/latest/BTEInstaller-mac.dmg)
                - [Universal](https://s3.buildtheearth.net/public/installer/latest/BTEInstaller-universal.jar)

                Tout est automatique, dézippez le fichier, ouvrez-le et cliquez sur **Install**, vous trouverez dans votre launcher Minecraft un nouveau profil BTE **(⚠️ fermez votre Launcher pendant l'installation)**""",
            ),
            create_embed(
                title="⚙️ Quelle est l'IP? ⚙️",
                description=f"➡️ Vous trouverez l'IP dans <#{variables.Channels.IP}> une fois avoir certifié la lecture des salons.",
            ),
            create_embed(
                title="⛏️ Comment fonctionne le serveur? ⛏️",
                description="""➡️ Accessible à la visite.
                ➡️ Pour commencer à construire, demandez le grade `Débutant` **sur le serveur Minecraft à un membre du staff.**
                ➡️ Pour devenir builder officiel (pas obligatoire), suivez [**ce document**](https://docs.google.com/document/d/1DHMOEcmepY_jGlS_-tvCvpJmSbaoHmofnamTJleQYik/edit?usp=sharing)"""
            ),
            create_embed(
                title="👍 Comment bien débuter? 👍",
                description="""➡️ Avoir le modpack (le lien juste au dessus)
                ➡️ Se repérer grâce à Terramap, touche M du clavier en jeu
                ➡️ Avoir Google Earth Pro afin de pouvoir mesurer les bâtiments en 3D
                ➡️ Visiter le serveur pour voir comment chaque builder a construit son bâtiment. (`/visite` ou `/warps` sur le serveur)""",
            ),
            create_embed(
                title="📍 Comment se téléporter? 📍",
                description="""➡️ `/tpll [coordonnées]` (réservé aux builders)
                ➡️ `/visite` pour nos plus belles constructions
                ➡️ `/warps` pour tout voir
                Utiliser `/tpll` ⤵️""",
                image="https://s10.gifyu.com/images/TPLL_Help.gif"
            ),
            create_embed(
                title="‼️ Il est impératif de lire ce salon avant de poser une question, merci ‼️",
                description=f"Pour accéder à l'entièreté du Discord, n'oubliez pas de sélectionner votre langue dans <#{variables.Channels.ACCUEIL}>.",
                color=0xFF0000
            )
        ]}
    ]
}


class Webhooks(interactions.Extension):
    @interactions.extension_listener()
    async def on_start(self):
        self.guild: interactions.Guild = await interactions.get(self.client, interactions.Guild, object_id=variables.SERVER)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.guild.icon_url) as response:
                self.icon_image = interactions.Image("BTEFrance.gif", fp=await response.read())

    @interactions.extension_command(name="webhooks", description="Envoyer un webhook", default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    @interactions.option("Webhook à envoyer", choices=[
        interactions.Choice(name=webhook, value=webhook)
        for webhook in list(WEBHOOKS.keys())
    ])
    async def webhooks(self, ctx: interactions.CommandContext, title: str):
        webhook_list = WEBHOOKS.get(title)
        if not webhook_list:
            return await ctx.send(embeds=create_error_embed(f"Le Webhook appelé {title} n'existe pas!"), ephemeral=True)

        channel = await ctx.get_channel()
        if channel.thread_metadata:
            channel_id = int(channel.parent_id)
            thread_id = int(ctx.channel_id)
        else:
            channel_id = int(ctx.channel_id)
            thread_id = None

        webhook = await interactions.Webhook.create(self.client._http, channel_id, ctx.guild.name, self.icon_image)
        for webhook_dict in webhook_list:
            await webhook.execute(**webhook_dict, thread_id=thread_id)
        await webhook.delete()

        await ctx.send(embeds=create_info_embed(f"Le Webhook appelé {title} a bien été envoyé"), ephemeral=True)

    @interactions.extension_component("verify_french")
    async def on_verify_french(self, ctx: interactions.ComponentContext):
        if variables.Roles.FRANCAIS in ctx.author.roles:
            await self.guild.remove_member_role(variables.Roles.FRANCAIS, ctx.author)
            await ctx.send("Vous n'avez plus le rôle Français.", ephemeral=True)
        else:
            await self.guild.add_member_role(variables.Roles.FRANCAIS, ctx.author)
            await ctx.send("Vous avez reçu le rôle Français. Bienvenue sur le serveur!", ephemeral=True)

    @interactions.extension_component("verify_english")
    async def on_verify_english(self, ctx: interactions.ComponentContext):
        if variables.Roles.ENGLISH in ctx.author.roles:
            await self.guild.remove_member_role(variables.Roles.ENGLISH, ctx.author)
            await ctx.send("You lost the English role.", ephemeral=True)
        else:
            await self.guild.add_member_role(variables.Roles.ENGLISH, ctx.author)
            await ctx.send("You received the English role. Welcome on the server!", ephemeral=True)


def setup(client: interactions.Client):
    Webhooks(client)
