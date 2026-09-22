import json
import os
from pathlib import Path

import interactions
import watchdog.events
import yaml
from hachiko.hachiko import AIOEventHandler, AIOWatchdog

import variables
from utils import EventQueue, get_env, log

DEFAULT_JSON_DICT = {"label": "Régions WorldGuard", "toggleable": True, "default-hidden": True, "sorting": 10}


class WorldguardFolderHandler(AIOEventHandler):
    def __init__(self, ext, worldguard_folder):
        super().__init__()
        self.ext: interactions.Extension = ext
        self.worldguard_folder: str = worldguard_folder
        self.worldguard_output_json_file = get_env("WORLDGUARD_OUTPUT_JSON_FILE")

        self.event_queue = EventQueue(self.process_event)

    async def on_moved(self, event: watchdog.events.FileMovedEvent):
        # why do we not listen to FileCreated or FileModified events on Linux?
        # because in Linux, there is a temporary .yml.tmp that is created BEFORE the final .yml file:
        # FileCreated .tmp > FileOpened .tmp > FileModified .tmp > FileClosed .tmp > FileMoved .tmp to .yml
        # therefore we only listen to the final FileMovedEvent
        if os.name != "nt":  # Linux
            self.event_queue.queue(event, event.dest_path)

    async def on_created(self, event: watchdog.events.FileCreatedEvent):
        if os.name == "nt":  # Windows
            self.event_queue.queue(event, event.src_path)

    async def on_modified(self, event: watchdog.events.FileModifiedEvent):
        if os.name == "nt":  # Windows
            self.event_queue.queue(event, event.src_path)

    async def process_event(self, event: watchdog.events.FileSystemEvent, filename: str):
        await self._on_modify(event, filename)

    async def _on_modify(self, event: watchdog.events.FileSystemEvent, filename: str):
        if event.is_directory or Path(filename).name != "regions.yml":
            return  # we only care of changes in regions.yml

        with open(filename, "r") as f:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)

        # generate Bluemap shape markers
        markers = self.generate_markers(yaml_data["regions"])
        new_json_dict = {**DEFAULT_JSON_DICT, "markers": markers}

        # save new Bluemap config and reload
        with open(self.worldguard_output_json_file, "r") as file:
            old_json_dict = json.load(file)
            if old_json_dict == new_json_dict:
                return  # do not save the Bluemap markers & reload if there hasn't been a significant change

        with open(self.worldguard_output_json_file, "w") as file:
            json.dump(new_json_dict, file, indent=2)
        console_channel = await self.ext.bot.fetch_channel(variables.Channels.CONSOLE)
        await console_channel.send("bluemap reload light")

    def generate_markers(self, regions: dict):
        markers = {}
        for region_id, region in regions.items():
            if region_id == "__global__":
                continue  # skip global region
            marker = {}
            marker["label"] = region_id
            marker["detail"] = region_id
            marker["type"] = "extrude"
            marker["line-width"] = 5
            marker["line-color"] = {"r": 255, "g": 0, "b": 0, "a": 1.0}
            marker["fill-color"] = {"r": 200, "g": 0, "b": 0, "a": 0.3}
            match type := region["type"]:
                case "cuboid":
                    min = region["min"]
                    max = region["max"]
                    marker["shape-min-y"] = min["y"]
                    marker["shape-max-y"] = max["y"]
                    marker["shape"] = [
                        {"x": min["x"], "z": min["z"]},
                        {"x": max["x"], "z": min["z"]},
                        {"x": max["x"], "z": max["z"]},
                        {"x": min["x"], "z": max["z"]},
                    ]
                case "poly2d":
                    marker["shape-min-y"] = region["min-y"]
                    marker["shape-max-y"] = region["max-y"]
                    marker["shape"] = region["points"]
                case _:
                    log(f"WorldGuard type {type} not supported!")
                    continue
            x_list = [shape["x"] for shape in marker["shape"]]
            z_list = [shape["z"] for shape in marker["shape"]]
            pos_x = sum(x_list) / len(x_list)
            pos_z = sum(z_list) / len(z_list)
            marker["position"] = {"x": pos_x, "y": marker["shape-max-y"], "z": pos_z}
            markers[region_id] = marker
        return markers


class WatchdogWorldguard(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.worldguard_folder = get_env("WORLDGUARD_FOLDER")
        self.watchdog = AIOWatchdog(self.worldguard_folder, event_handler=WorldguardFolderHandler(self, self.worldguard_folder))
        self.watchdog.start()

    @interactions.listen(interactions.events.Disconnect)
    async def on_disconnect(self):
        self.watchdog.stop()
