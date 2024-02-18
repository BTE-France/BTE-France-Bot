import json
import os
import re

import aiohttp
import interactions

import variables
from utils import (
    create_embed,
    escape_minecraft_username_markdown,
    format_byte_size,
    log,
)

WARP_PATTERN = re.compile(r"^.* ([\w*]+) issued server command: /([\w-]+) ([\w:'-]+).*$")
LUCKPERMS_PATTERN = re.compile(r"^.* ([\w*]+) issued server command: /lp user ([\w*]+) ([\w]+) rank.*$")
SCHEMATIC_PATTERN = re.compile(r"^.* ([\w*]+) saved /home/container/plugins/FastAsyncWorldEdit/schematics/([\w-]+\.schem)$")
RANK_DICT = {
    "default": "Visiteur",
    "debutant": "Débutant",
    "builder": "Builder",
    "contremaitre": "Contremaître",
    "architecte": "Architecte",
    "ingenieur": "Ingénieur",
    "archiviste": "Archiviste",
    "helper": "Helper",
    "dev": "Développeur",
    "admin": "Admin",
}
EDIT_WARP_BUTTON = interactions.Button(
    label="Editer",
    custom_id="warp_edit",
    emoji="⚙️",
    style=interactions.ButtonStyle.SUCCESS,
)
EDIT_WARP_MODAL = interactions.Modal(
    interactions.InputText(
        style=interactions.TextStyles.SHORT,
        label="Informations complémentaires",
        custom_id="information",
        required=False,
    ),
    title="Edition du Warp",
    custom_id="warp_modal",
)
EDIT_PERMS_BUTTON = interactions.Button(
    label="Editer",
    custom_id="perms_edit",
    emoji="⚙️",
    style=interactions.ButtonStyle.SUCCESS,
)
EDIT_PERMS_MODAL = interactions.Modal(
    interactions.InputText(
        style=interactions.TextStyles.SHORT,
        label="Informations complémentaires",
        custom_id="information",
        required=False,
    ),
    title="Edition du Warp",
    custom_id="perms_modal",
)


def remove_codeblock_markdown(string: str) -> str:
    return string.replace("```diff", "").replace("```", "").strip()


class ConsoleListener(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.warps_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        self.ranking_channel = await self.bot.fetch_channel(variables.Channels.RANKING)
        self.schem_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        if users_json_file := os.getenv("LUCKPERMS_USERS_JSON_FILE"):
            self.users_json_file = users_json_file
        else:
            log("No LUCKPERMS_USERS_JSON_FILE variable found!")
        if schematics_folder := os.getenv("SCHEMATICS_FOLDER"):
            self.schematics_folder = schematics_folder
        else:
            log("No SCHEMATICS_FOLDER variable found!")

    @interactions.listen(interactions.events.MessageCreate)
    async def on_console_message_create(self, message_create: interactions.events.MessageCreate):
        if message_create.message._channel_id != variables.Channels.CONSOLE:
            return

        for msg in remove_codeblock_markdown(message_create.message.content).splitlines():
            msg = msg.strip()
            if not msg:
                continue

            await self.test_for_regex(msg)

    @interactions.listen(interactions.events.MessageUpdate)
    async def on_console_message_update(self, message_update: interactions.events.MessageUpdate):
        if message_update.after._channel_id != variables.Channels.CONSOLE:
            return

        if not message_update.before:
            return

        # Get difference between before & after messages
        before_msg, after_msg = remove_codeblock_markdown(message_update.before.content), remove_codeblock_markdown(message_update.after.content)

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
        async def warp_regex(match: re.Match):
            player, command, warp = match.group(1, 2, 3)
            if command not in ("setwarp", "delwarp"):
                return
            title = f"Warp créé: {warp}" if command == "setwarp" else f"Warp supprimé: {warp}"
            embed = create_embed(
                title=title,
                footer_text=player,
                color=0x00FF00 if command == "setwarp" else 0xFF0000,
            )
            await self.warps_channel.send(embeds=embed, components=EDIT_WARP_BUTTON)
            log(f"{'Added' if command == 'setwarp' else 'Removed'} warp {warp}")

        async def luckperms_regex(match: re.Match):
            moderator, player, action = match.group(1, 2, 3)
            if action not in ("promote", "demote"):
                return
            if not (rank := await self.get_new_rank(player)):
                return
            title = (
                f"{escape_minecraft_username_markdown(player)} promu au rang de {rank}."
                if action == "promote"
                else f"{escape_minecraft_username_markdown(player)} rétrogradé au rang de {rank}."
            )
            embed = create_embed(
                title=title,
                footer_text=moderator,
                color=0x00FF00 if action == "promote" else 0xFF0000,
            )
            await self.ranking_channel.send(embeds=embed, components=EDIT_PERMS_BUTTON)
            log(f"{'Promoted' if action == 'promote' else 'Demoted'} {player} to {rank}")

        async def schematics_regex(match: re.Match):
            player, schem_name = match.group(1, 2)
            schem_file = os.path.join(self.schematics_folder, schem_name)
            embed = create_embed(
                title="Nouvelle schematic!",
                color=0x00FF00,
                fields=[
                    ("Nom", escape_minecraft_username_markdown(schem_name), False),
                    ("Auteur", escape_minecraft_username_markdown(player), False),
                    (
                        "Taille du fichier",
                        format_byte_size(os.stat(schem_file).st_size),
                        False,
                    ),
                ],
                include_thumbnail=True,
            )
            await self.schem_channel.send(embed=embed, file=interactions.File(schem_file))

        if match := WARP_PATTERN.search(message):
            await warp_regex(match)

        if hasattr(self, "users_json_file") and (match := LUCKPERMS_PATTERN.search(message)):
            await luckperms_regex(match)

        if hasattr(self, "schematics_folder") and (match := SCHEMATIC_PATTERN.search(message)):
            await schematics_regex(match)

    async def get_new_rank(self, player: str):
        async with aiohttp.ClientSession() as session:
            # Convert player name to its proper UUID equivalent
            async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{player}") as response:
                id: str = (await response.json())["id"]
                id = f"{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}"
        with open(self.users_json_file, "r") as file:
            users = json.load(file)
            # Get the new rank
            for rank in [child["group"] for child in users[id]["parents"]]:
                if rank := RANK_DICT.get(rank):
                    return rank

    @interactions.component_callback("warp_edit")
    async def on_warp_edit_button(self, ctx: interactions.ComponentContext):
        modal = EDIT_WARP_MODAL
        desc = ctx.message.embeds[0].description.replace("Information: ", "") if ctx.message.embeds[0].description else ""
        modal.components[0].value = desc
        await ctx.send_modal(modal)

    @interactions.modal_callback("warp_modal")
    async def on_warp_modal_answer(self, ctx: interactions.ModalContext, information: str):
        embed: interactions.Embed = ctx.message.embeds[0]
        embed.description = f"Information: {information}" if information else ""
        await ctx.message.edit(embeds=embed, components=ctx.message.components)
        await ctx.send(
            f"Information ajoutée: `{information}`" if information else "Information supprimée.",
            ephemeral=True,
        )

    @interactions.component_callback("perms_edit")
    async def on_perms_edit_button(self, ctx: interactions.ComponentContext):
        modal = EDIT_PERMS_MODAL
        desc = ctx.message.embeds[0].description.replace("Information: ", "") if ctx.message.embeds[0].description else ""
        modal.components[0].value = desc
        await ctx.send_modal(modal)

    @interactions.modal_callback("perms_modal")
    async def on_perms_modal_answer(self, ctx: interactions.ModalContext, information: str):
        embed: interactions.Embed = ctx.message.embeds[0]
        embed.description = f"Information: {information}" if information else ""
        await ctx.message.edit(embeds=embed, components=ctx.message.components)
        await ctx.send(
            f"Information ajoutée: `{information}`" if information else "Information supprimée.",
            ephemeral=True,
        )
