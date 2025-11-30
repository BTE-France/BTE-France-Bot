import copy
import json
import os
import re

import interactions
import pandas as pd
from deepdiff import DeepDiff

import variables
from utils import create_embed, create_error_embed, create_info_embed, get_env

ICONS_DICT = {
    "orange": "Orange (projet débuté)",
    "yellow": "Jaune (projet avancé)",
    "green": "Vert (projet terminé)",
    "blue": "Bleu (commune terminée)",
}
QUALITY_DICT = {"orange": 0, "yellow": 1, "green": 2, "blue": 3}
DEFAULT_JSON_DICT = {"label": "Marqueurs", "toggleable": True, "default-hidden": False, "sorting": 0}
MIN_DISTANCE = 50
PROPORTIONALITY = 25
MINIMUM_ZOOM_FILTER = 2500
MAXIMUM_ZOOM_FILTER = 1000000
MAXIMUM_NEIGHBORS = 3
JUMP = 20
BLUEMAP_MODAL = interactions.Modal(
    interactions.ShortText(label="ID", custom_id="id", placeholder="Doit être unique, et respecter le patterne [a-z-]+"),
    interactions.ShortText(label="Nom", custom_id="label", placeholder="Nom, peut contenir n'importe quel caractère"),
    interactions.ShortText(label="Coordonnées", custom_id="coords", placeholder="Coordonnées sous format x,y,z"),
    interactions.LabelComponent(
        label="Icône",
        component=interactions.StringSelectMenu(
            *[interactions.StringSelectOption(label=value, value=key) for key, value in ICONS_DICT.items()],
            custom_id="icon",
        ),
    ),
    title="Création d'un marqueur Bluemap",
)


class Bluemap(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.bluemap_markers_json_file = get_env("BLUEMAP_MARKERS_JSON_FILE")
        self.bluemap_output_json_file = get_env("BLUEMAP_OUTPUT_JSON_FILE")
        self.schem_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        self.console_channel = await self.bot.fetch_channel(variables.Channels.CONSOLE)
        with open(self.bluemap_markers_json_file, "r", encoding="utf8") as markers_file:
            self.markers: dict = json.load(markers_file)

    @interactions.slash_command("bluemap")
    @interactions.slash_default_member_permission(interactions.Permissions.MANAGE_MESSAGES)
    async def bluemap(self, ctx: interactions.SlashContext): ...

    @bluemap.subcommand("add", sub_cmd_description="Créer un nouveau marqueur Bluemap")
    async def bluemap_add(self, ctx: interactions.SlashContext):
        await ctx.send_modal(BLUEMAP_MODAL)
        modal_ctx = await self.bot.wait_for_modal(BLUEMAP_MODAL)

        answer, responses = self.sanitize_bluemap_modal(modal_ctx.responses)
        if answer:  # incorrect values
            return await modal_ctx.send(embed=create_error_embed(answer), ephemeral=True)

        if (id := responses["id"]) in self.markers:
            return await modal_ctx.send(embed=create_error_embed(f"Le marqueur `{id}` existe déjà!"), ephemeral=True)

        self.markers[id] = {"label": responses["label"], "x": responses["x"], "y": responses["y"], "z": responses["z"], "icon": responses["icon"][0]}
        await modal_ctx.defer(ephemeral=True)
        await self.update_markers()
        await modal_ctx.send(embed=create_info_embed(f"Le marqueur `{id}` a bien été créé."), ephemeral=True)
        await self.schem_channel.send(
            embed=create_embed(
                title="BlueMap: Marqueur créé",
                fields=[
                    ("ID", id, False),
                    ("Nom", responses["label"], False),
                    ("X", responses["x"], True),
                    ("Y", responses["y"], True),
                    ("Z", responses["z"], True),
                    ("Icône", ICONS_DICT.get(responses["icon"][0]), False),
                ],
                footer_text=ctx.author.tag,
                color=0x00FF00,
            )
        )

    @bluemap.subcommand("modify", sub_cmd_description="Modifier un marqueur Bluemap")
    @interactions.slash_option(name="id", description="ID du marqueur", opt_type=interactions.OptionType.STRING, required=True, autocomplete=True)
    async def bluemap_modify(self, ctx: interactions.SlashContext, id: str):
        if id not in self.markers:
            return await ctx.send(embed=create_error_embed(f"Le marqueur `{id}` n'existe pas!"), ephemeral=True)
        old_marker = self.markers[id]

        # autocomplete modal
        modal_modify = copy.deepcopy(BLUEMAP_MODAL)
        modal_modify.title = f"Modification du marqueur Bluemap {id}"[:45]
        modal_modify.components.pop(0)  # delete ID field (since shouldn't be modified!)
        modal_modify.components[0].value = old_marker["label"]
        modal_modify.components[1].value = f"{old_marker['x']},{old_marker['y']},{old_marker['z']}"
        for i, option in enumerate(modal_modify.components[2].component.options):
            if option.value == old_marker["icon"]:
                modal_modify.components[2].component.options[i].default = True
                break

        await ctx.send_modal(modal_modify)
        modal_ctx = await self.bot.wait_for_modal(modal_modify)

        answer, responses = self.sanitize_bluemap_modal(modal_ctx.responses)
        if answer:  # incorrect values
            return await modal_ctx.send(embed=create_error_embed(answer), ephemeral=True)

        new_marker = {"label": responses["label"], "x": responses["x"], "y": responses["y"], "z": responses["z"], "icon": responses["icon"][0]}
        if old_marker == new_marker:
            return await modal_ctx.send(embed=create_error_embed(f"Aucun attribut du marqueur `{id}` n'a été modifié!"), ephemeral=True)

        self.markers[id] = new_marker
        await modal_ctx.defer(ephemeral=True)
        await self.update_markers()
        await modal_ctx.send(embed=create_info_embed(f"Le marqueur `{id}` a bien été modifié."), ephemeral=True)
        await self.schem_channel.send(
            embed=create_embed(
                title="BlueMap: Marqueur modifié",
                fields=[
                    ("ID", id, False),
                    ("Nom", responses["label"], False),
                    ("X", responses["x"], True),
                    ("Y", responses["y"], True),
                    ("Z", responses["z"], True),
                    ("Icône", ICONS_DICT.get(responses["icon"][0]), False),
                ],
                footer_text=ctx.author.tag,
                color=0x0000FF,
            )
        )

    @bluemap_modify.autocomplete("id")
    async def on_bluemap_modify_autocomplete(self, ctx: interactions.AutocompleteContext):
        await ctx.send(self.get_autocomplete_marker_ids(ctx))

    @bluemap.subcommand("delete", sub_cmd_description="Supprimer un marqueur Bluemap")
    @interactions.slash_option(name="id", description="ID du marqueur", opt_type=interactions.OptionType.STRING, required=True, autocomplete=True)
    async def bluemap_delete(self, ctx: interactions.SlashContext, id: str):
        if id not in self.markers:
            return await ctx.send(embed=create_error_embed(f"Le marqueur `{id}` n'existe pas!"), ephemeral=True)

        del self.markers[id]
        await ctx.defer(ephemeral=True)
        await self.update_markers()
        await ctx.send(embed=create_info_embed(f"Le marqueur `{id}` a bien été supprimé."), ephemeral=True)
        await self.schem_channel.send(
            embed=create_embed(
                title="BlueMap: Marqueur supprimé",
                fields=[("ID", id, False)],
                footer_text=ctx.author.tag,
                color=0xFF0000,
            )
        )

    @bluemap_delete.autocomplete("id")
    async def on_bluemap_delete_autocomplete(self, ctx: interactions.AutocompleteContext):
        await ctx.send(self.get_autocomplete_marker_ids(ctx))

    def sanitize_bluemap_modal(self, responses: dict):
        answer = None
        responses_sanitized = responses.copy()
        for custom_id, response in responses.items():
            match custom_id:
                case "id":
                    if not re.match(re.compile(r"^[a-z-]+$"), response):
                        answer = f"L'ID `{response}` ne respecte pas le bon format `[a-z-]+`"
                        break
                case "coords":
                    if not re.match(re.compile(r"^-?\d+,-?\d+,-?\d+$"), response):
                        answer = f"Les coordonnées `{response}` ne respectent pas le bon format `x,y,z`"
                        break
                    else:
                        x, y, z = response.split(",")
                        responses_sanitized["x"] = int(x)
                        responses_sanitized["y"] = int(y)
                        responses_sanitized["z"] = int(z)
        return answer, responses_sanitized

    async def update_markers(self):
        # update markers json file
        with open(self.bluemap_markers_json_file, "w", encoding="utf8") as markers_file:
            json.dump(self.markers, markers_file, indent=2)

        # generate actual Bluemap markers dict
        output_markers = self.generate_markers_dict()
        for marker in output_markers.values():
            marker["max-distance"] = self.calculate_max_distance(marker, output_markers)

        # save new Bluemap config and reload
        new_json_dict = {**DEFAULT_JSON_DICT, "markers": output_markers}
        with open(self.bluemap_output_json_file, "w") as file:
            json.dump(new_json_dict, file, indent=2)
        await self.console_channel.send("bluemap reload light")

    def get_autocomplete_marker_ids(self, ctx: interactions.AutocompleteContext):
        choices = []
        for id in self.markers.keys():
            if ctx.input_text in id:
                choices.append(id)
        return choices[:25]

    def generate_markers_dict(self) -> dict:
        markers = {}
        for id, input_marker in self.markers.items():
            marker = {}
            marker["label"] = input_marker["label"]
            marker["position"] = {"x": input_marker["x"], "y": input_marker["y"], "z": input_marker["z"]}
            marker["icon"] = f"assets/icons/{input_marker['icon']}.png"
            marker["quality"] = QUALITY_DICT.get(input_marker["icon"])  # used later for calculating max distance
            marker["type"] = "poi"
            marker["anchor"] = {"x": 20, "y": 40}
            marker["min-distance"] = MIN_DISTANCE
            markers[id] = marker
        return markers

    def calculate_max_distance(self, input_marker: dict, markers: dict[str, dict]):
        """Implemented by Elfi"""
        # Cette variable représente l'intervalle sur le périmètre entre chaque vérification
        jump = JUMP
        # Cette variable est le périmètre minimale de vérification, elle est calculé grâce au niveau de zoom minimale et le coefficiant de proportionalité décrit dans le fichier config
        perimeter = MINIMUM_ZOOM_FILTER / PROPORTIONALITY
        # Boucle de 100 pour éviter de faire une boucle infini, elle s'arrête systématiquement après un nombre qui dépend des paramètres de base. avec des paramètres résonable elle n'est pas supposée dépasser 90 itérations
        for _ in range(100):
            distance_counter = 0
            upper_poi = False
            for marker in markers.values():
                distance_squared = ((marker["position"]["x"] - input_marker["position"]["x"]) ** 2) + (
                    (marker["position"]["y"] - input_marker["position"]["y"]) ** 2
                )
                if distance_squared < perimeter**2 and input_marker["quality"] <= marker["quality"]:
                    # Compteur des POI d'avancement égale ou supérieur dans le périmètre
                    distance_counter += 1
                if distance_squared < perimeter**2 and input_marker["quality"] < marker["quality"]:
                    # Témoin de la présence d'un POI d'un avancement supérieur dans le périmètre
                    upper_poi = True

            # Si le nombre detecté de POI excède le nombre renseigné dans le fichier config (+1 car le POI étudié se détecte aussi lui même) et qu'un POI plus avancé est présent dans la zone, alors le POI est masqué
            if (MAXIMUM_NEIGHBORS + 1) < distance_counter and upper_poi or MAXIMUM_ZOOM_FILTER < perimeter * PROPORTIONALITY:
                # Juste après la fin de la boucle, la fonction return est utilisé
                break
            perimeter += jump
            # Le zoom de la bluemap évolue de façon expodentielle et est bien plus lent près du sol. Puisque de moins en moins de précision est demandé à mesure que l'on s'éloigne du sol, la variable jump est augmenté de 110% à chaque itération afin d'avoir un niveau de précision et un temps de calcul correcte
            jump = jump * 1.1
        # max-distance est calculé grâce au coefficiant de proportionalité et du périmètre sur lequel la boucle s'est brisé
        return round(perimeter * PROPORTIONALITY)
