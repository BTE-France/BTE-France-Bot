import asyncio
import json
import os
import re

import interactions
from aiosseclient import Event, aiosseclient

import variables
from utils import (
    RANK_DICT,
    create_embed,
    escape_minecraft_username_markdown,
    format_byte_size,
    get_env,
    log,
    lp_get_user,
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
        self.schematics_folder = get_env("SCHEMATICS_FOLDER")
        await self.luckperms_sse_handler()

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

        if hasattr(self, "schematics_folder") and (match := SCHEMATIC_PATTERN.search(message)):
            await schematics_regex(match)

    async def luckperms_sse_handler(self):
        while True:
            async for event in aiosseclient(
                "https://luckperms.btefrance.fr/event/log-broadcast", headers={"Authorization": f"Bearer {get_env('LUCKPERMS_REST_AUTH_KEY')}"}
            ):
                await self.parse_event(event)
            log("Connection to LuckPerms SSE API lost, retring in 60 seconds...")
            await asyncio.sleep(60)

    async def parse_event(self, event: Event):
        # Events whose source is directly the REST API will NOT appear here, only external events appear (Console or Minecraft)
        if event.event != "message":
            return
        data = json.loads(event.data)
        desc = data.get("entry").get("description")
        if desc not in ("promote rank", "demote rank"):
            return
        source = data.get("entry").get("source").get("name")
        target = data.get("entry").get("target").get("name")
        user = await lp_get_user(data.get("entry").get("target").get("uniqueId"))
        rank = RANK_DICT.get(user.get("metadata").get("primaryGroup"))

        title = (
            f"{escape_minecraft_username_markdown(target)} promu au rang de {rank}."
            if desc == "promote rank"
            else f"{escape_minecraft_username_markdown(target)} rétrogradé au rang de {rank}."
        )
        embed = create_embed(
            title=title,
            footer_text=source,
            color=0x00FF00 if desc == "promote rank" else 0xFF0000,
        )
        await self.ranking_channel.send(embeds=embed, components=EDIT_PERMS_BUTTON)
        log(f"{'Promoted' if desc == 'promote rank' else 'Demoted'} {target} to {rank}")

    @interactions.component_callback(EDIT_PERMS_BUTTON.custom_id)
    async def on_perms_edit_button(self, ctx: interactions.ComponentContext):
        modal = EDIT_PERMS_MODAL
        desc = ctx.message.embeds[0].description.replace("Information: ", "") if ctx.message.embeds[0].description else ""
        modal.components[0].value = desc
        await ctx.send_modal(modal)

    @interactions.modal_callback(EDIT_PERMS_MODAL.custom_id)
    async def on_perms_modal_answer(self, ctx: interactions.ModalContext, information: str):
        embed: interactions.Embed = ctx.message.embeds[0]
        embed.description = f"Information: {information}" if information else ""
        await ctx.message.edit(embeds=embed, components=ctx.message.components)
        await ctx.send(
            f"Information ajoutée: `{information}`" if information else "Information supprimée.",
            ephemeral=True,
        )
