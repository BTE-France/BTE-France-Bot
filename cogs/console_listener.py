import json
import os
import re

import aiohttp
import interactions

import variables
from utils import (
    RANK_DICT,
    create_embed,
    escape_minecraft_username_markdown,
    format_byte_size,
    get_env,
    log,
    minecraft_username_to_uuid,
)

LUCKPERMS_PATTERN = re.compile(r"^.* ([\w*]+) issued server command: /lp user ([\w*]+) ([\w]+) rank.*$")
SCHEMATIC_PATTERN = re.compile(r"^.* ([\w*]+) saved /home/container/plugins/FastAsyncWorldEdit/schematics/([\w-]+\.schem)$")
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
        self.ranking_channel = await self.bot.fetch_channel(variables.Channels.RANKING)
        self.schem_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        self.users_json_file = get_env("LUCKPERMS_USERS_JSON_FILE")
        self.schematics_folder = get_env("SCHEMATICS_FOLDER")

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

        if hasattr(self, "users_json_file") and (match := LUCKPERMS_PATTERN.search(message)):
            await luckperms_regex(match)

        if hasattr(self, "schematics_folder") and (match := SCHEMATIC_PATTERN.search(message)):
            await schematics_regex(match)

    async def get_new_rank(self, player: str):
        uuid = await minecraft_username_to_uuid(player)
        with open(self.users_json_file, "r") as file:
            users = json.load(file)
            # Get the new rank
            for rank in [child["group"] for child in users[uuid]["parents"]]:
                if rank := RANK_DICT.get(rank):
                    return rank

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
