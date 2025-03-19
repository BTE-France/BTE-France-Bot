import os
from pathlib import Path

import interactions
import watchdog.events
import watchdog.observers
import yaml
from hachiko.hachiko import AIOEventHandler, AIOWatchdog

import variables
from utils import create_embed, get_env, log, minecraft_uuid_to_username

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


class WarpsFolderHandler(AIOEventHandler):
    def __init__(self, ext, warps_folder):
        super().__init__()
        self.ext: interactions.Extension = ext
        self.warps_folder: str = warps_folder

        # initialize a list that contains all warp files as dict
        self.warps_dict = {}
        for file in os.listdir(self.warps_folder):
            self.warps_dict[file] = self.get_warp_file_dict(os.path.join(self.warps_folder, file))

    def get_warp_file_dict(self, filename) -> dict:
        if not os.path.exists(filename):
            log(f"[ERROR] {filename} does not exist!")
            return
        with open(filename, "r") as f:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
            return yaml_data

    async def send_embed(self, warp_dict: dict, _type: str, color: int):
        title = f"Warp {_type}: {warp_dict.get('name')}"
        embed = create_embed(
            title=title,
            fields=[("X", int(warp_dict.get("x")), True), ("Y", int(warp_dict.get("y")), True), ("Z", int(warp_dict.get("z")), True)],
            footer_text=await minecraft_uuid_to_username(warp_dict.get("lastowner")),
            color=color,
        )
        await self.ext.warps_channel.send(embeds=embed, components=EDIT_WARP_BUTTON)

    async def on_moved(self, event: watchdog.events.FileMovedEvent):
        # why do we not listen to FileCreated or FileModified events?
        # because in Linux, there is a temporary .yml.tmp that is created BEFORE the final .yml file:
        # FileCreated .tmp > FileOpened .tmp > FileModified .tmp > FileClosed .tmp > FileMoved .tmp to .yml
        # therefore we only listen to the final FileMovedEvent
        if event.is_directory:
            return
        warp_dict = self.get_warp_file_dict(event.dest_path)
        self.warps_dict[Path(event.dest_path).name] = warp_dict
        await self.send_embed(warp_dict, "créé", 0x00FF00)
        log(f"Added warp {warp_dict.get('name')}")

    async def on_deleted(self, event: watchdog.events.FileDeletedEvent):
        if event.is_directory:
            return
        warp_dict = self.warps_dict.get(Path(event.src_path).name)
        if warp_dict is not None:
            del self.warps_dict[Path(event.src_path).name]
            await self.send_embed(warp_dict, "supprimé", 0xFF0000)
            log(f"Deleted warp {warp_dict.get('name')}")


class Watchdog(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.warps_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        self.warps_folder = get_env("WARPS_FOLDER")
        self.watchdog = AIOWatchdog(self.warps_folder, event_handler=WarpsFolderHandler(self, self.warps_folder))
        self.watchdog.start()

    @interactions.listen(interactions.events.Disconnect)
    async def on_disconnect(self):
        self.watchdog.stop()

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
