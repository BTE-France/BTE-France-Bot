import json
import os
import random
import re
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import interactions

import variables
from utils.embed import create_embed


@dataclass
class Warp:
    name: str
    warp: str
    description: str
    image: str


WARP_PATTERN = re.compile(
    r"^.* ([\w*]+) issued server command: /([\w-]+) ([\w:'-]+).*$"
)
LUCKPERMS_PATTERN = re.compile(
    r"^.* ([\w*]+) issued server command: /lp user ([\w*]+) ([\w]+) rank.*$"
)
RANK_DICT = {
    "default": "Visiteur",
    "debutant": "Débutant",
    "builders": "Builder",
    "contremaitre": "Contremaître",
    "architecte": "Architecte",
    "ingenieur": "Ingénieur",
    "aide_archive": "Aide Archiviste",
    "archiviste": "Archiviste",
    "helper": "Helper",
    "dev": "Développeur",
    "admin": "Staff",
    "owner": "Fondateur",
}
EDIT_BUTTON = interactions.Button(
    label="Editer",
    custom_id="warp_edit",
    emoji="⚙️",
    style=interactions.ButtonStyle.SUCCESS,
)
EDIT_MODAL = interactions.Modal(
    interactions.InputText(
        style=interactions.TextStyles.SHORT,
        label="Informations complémentaires",
        custom_id="information",
        required=False,
    ),
    title="Edition du Warp",
    custom_id="warp_modal",
)
WARPS = [
    Warp(
        "La Défense",
        "defense_esplanade",
        "Quartier d'affaires de Paris connu pour ses nombreux gratte-ciels.\nBusiness district of Paris known for its numerous skyscrapers.",
        "https://imgur.com/ZOTj9dn.png",
    ),
    Warp(
        "Arc de Triomphe",
        "paris:etoile",
        "Arc au coeur de Paris, situé sur l'avenue des Champs-Elysées.\nArc at the heart of Paris, situated on the Avenue des Champs-Elysées.",
        "https://imgur.com/OBemDc5.png",
    ),
    Warp(
        "Ile de la Cité",
        "Ile_de_la_Cite",
        "Le berceau de la ville de Paris, construit par la team ETB.\nThe cradle of Paris, built by the ETB team.",
        "https://imgur.com/FcLGAae.png",
    ),
    Warp(
        "Nantes",
        "Nantes:cathedrale",
        "Cité des Ducs de Bretagne, non loin de l'océan Atlantique.\nCity of Dukes of Brittany, not far from the Atlantic ocean.",
        "https://imgur.com/WM4frCq.png",
    ),
    Warp(
        "Turenne",
        "turenne",
        "Village en Corrèze, réalisé en 48h en tant qu'évènement communautaire.\n Village in Corrèze, realized in 48h as a community event.",
        "https://imgur.com/j5qThvh.png",
    ),
    Warp(
        "Le Puy-Notre-Dame",
        "lepuynotredame",
        "Petite commune dans le Maine-et-Loire.\nSmall town in the Maine-et-Loire.",
        "https://imgur.com/VFyfKzR.png",
    ),
    Warp(
        "Le Mont-Saint-Michel",
        "mont-saint-michel",
        "Îlot roché situé en Normandie, une des icones de la France.\nTidal island located in Normandy, one of the icons of France.",
        "https://imgur.com/M9nsIbr.png",
    ),
    Warp(
        "Turckheim",
        "Turckheim",
        "Petite commune en Alsace avec notamment beaucoup de maisons à colombages.\nSmall town in Alsace with many half-timbered houses.",
        "https://imgur.com/qsjFdo6.png",
    ),
    Warp(
        "Monaco",
        "monaco",
        "Principauté située sur la côte méditéranéenne, construite par la team Build It 1:1.\nPrincipality located on the Mediterranean coast, built by the Build It 1:1 team.",
        "https://imgur.com/gA9DGCf.png",
    ),
    Warp(
        "Viaduc de Millau",
        "viaduc_de_millau",
        "Le viaduc avec les pylônes les plus hauts du monde (343m).\nThe viaduct with the highest pylons in the world (343m).",
        "https://imgur.com/P7ex8lG.png",
    ),
]


def remove_codeblock_markdown(string: str) -> str:
    return string.replace("```diff", "").replace("```", "").strip()


class Warps(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.warps_channel = await self.bot.fetch_channel(
            variables.Channels.SCHEMATIC_WARPS
        )
        self.debutant_channel = await self.bot.fetch_channel(
            variables.Channels.DEBUTANT
        )
        try:
            self.users_json_file = os.environ["LUCKPERMS_USERS_JSON_FILE"]
        except KeyError:
            print(
                "LuckPerms users.json file not found, cannot synchronize rank promotions!"
            )

    @interactions.slash_command(name="warps")
    async def warps(self, ctx: interactions.SlashContext):
        "Liste des meilleurs Warps BTE France"
        # Randomize warps and chunk in 10 warps (max embeds per message is 10)
        random.shuffle(WARPS)
        chunked_warps_list = [
            WARPS[i : i + 10] for i in range(0, len(WARPS), 10)
        ]  # noqa

        # Create all embeds
        chunked_embeds = []
        for warp_list in chunked_warps_list:
            embed_list = [
                create_embed(
                    title=warp.name,
                    color=0xFFFFFF,
                    fields=[(f"/warp {warp.warp}", warp.description, False)],
                    image=warp.image,
                )
                for warp in warp_list
            ]
            chunked_embeds.append(embed_list)

        for i, embed_list in enumerate(chunked_embeds):
            await ctx.author.send(
                ":flag_fr: **Liste des meilleurs warps sur le serveur BTE France** :flag_fr:"
                if i == 0
                else "",
                embeds=embed_list,
            )
        await ctx.send("Regarde tes MPs! :mailbox:")

    @interactions.listen(interactions.events.MessageCreate)
    async def on_console_message_create(
        self, message_create: interactions.events.MessageCreate
    ):
        if message_create.message._channel_id != variables.Channels.CONSOLE:
            return

        for msg in remove_codeblock_markdown(
            message_create.message.content
        ).splitlines():
            msg = msg.strip()
            if not msg:
                continue

            await self.test_for_regex(msg)

    @interactions.listen(interactions.events.MessageUpdate)
    async def on_console_message_update(
        self, message_update: interactions.events.MessageUpdate
    ):
        if message_update.after._channel_id != variables.Channels.CONSOLE:
            return

        if not message_update.before:
            return

        # Get difference between before & after messages
        before_msg, after_msg = remove_codeblock_markdown(
            message_update.before.content
        ), remove_codeblock_markdown(message_update.after.content)

        if len(before_msg) > len(after_msg):
            diff = before_msg.replace(after_msg, "")
        else:
            diff = after_msg.replace(before_msg, "")

        for msg in diff.splitlines():
            msg = msg.strip()
            if not msg:
                continue

            await self.test_for_regex(msg)

    async def test_for_regex(self, message: str):
        if match := WARP_PATTERN.search(message):
            player, command, warp = match.group(1, 2, 3)
            if command not in ("setwarp", "delwarp"):
                return
            title = (
                f"Warp créé: {warp}"
                if command == "setwarp"
                else f"Warp supprimé: {warp}"
            )
            embed = create_embed(
                title=title,
                footer_text=player,
                color=0x00FF00 if command == "setwarp" else 0xFF0000,
            )
            await self.warps_channel.send(embeds=embed, components=EDIT_BUTTON)
            date = datetime.now().strftime("%d/%m - %H:%M")
            print(
                f"[{date}] {'Added' if command == 'setwarp' else 'Removed'} warp {warp}"
            )

        elif hasattr(self, "users_json_file") and (
            match := LUCKPERMS_PATTERN.search(message)
        ):
            moderator, player, action = match.group(1, 2, 3)
            if action not in ("promote", "demote"):
                return
            if not (rank := await self.get_new_rank(player)):
                return
            title = (
                f"{player} promu au rang de {rank}."
                if action == "promote"
                else f"{player} rétrogradé au rang de {rank}."
            )
            embed = create_embed(
                title=title,
                footer_text=moderator,
                color=0x00FF00 if action == "promote" else 0xFF0000,
            )
            await self.debutant_channel.send(embeds=embed)
            date = datetime.now().strftime("%d/%m - %H:%M")
            print(
                f"[{date}] {'Promoted' if action == 'promote' else 'Demoted'} {player} to {rank}"
            )

    async def get_new_rank(self, player: str):
        async with aiohttp.ClientSession() as session:
            # Convert player name to its proper UUID equivalent
            async with session.get(
                f"https://api.mojang.com/users/profiles/minecraft/{player}"
            ) as response:
                id: str = (await response.json())["id"]
                id = f"{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}"
        with open(self.users_json_file, "r") as file:
            users = json.load(file)
            # Get the new rank
            for rank in [child["group"] for child in users[id]["parents"]]:
                if rank := RANK_DICT.get(rank):
                    return rank

    @interactions.component_callback("warp_edit")
    async def on_edit_button(self, ctx: interactions.ComponentContext):
        modal = EDIT_MODAL
        modal.components[0].value = ctx.message.embeds[0].description.replace(
            "Information: ", ""
        )
        await ctx.send_modal(modal)

    @interactions.modal_callback("warp_modal")
    async def on_modal_answer(self, ctx: interactions.ModalContext, information: str):
        embed: interactions.Embed = ctx.message.embeds[0]
        embed.description = f"Information: {information}" if information else ""
        await ctx.message.edit(embeds=embed, components=ctx.message.components)
        await ctx.send(
            f"Information ajoutée: `{information}`"
            if information
            else "Information supprimée.",
            ephemeral=True,
        )
