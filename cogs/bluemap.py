import json
import os

import interactions
import pandas as pd
from deepdiff import DeepDiff

import variables
from utils import log

ICONS_DICT = {
    "Orange (projet débuté)": "orange",
    "Jaune (projet avancé)": "yellow",
    "Vert (projet terminé)": "green",
    "Bleu (commune terminée)": "blue",
}
QUALITY_DICT = {
    "Orange (projet débuté)": 0,
    "Jaune (projet avancé)": 1,
    "Vert (projet terminé)": 2,
    "Bleu (commune terminée)": 3,
}
DEFAULT_JSON_DICT = {
    "label": "Marqueurs",
    "toggleable": True,
    "default-hidden": False,
    "sorting": 0,
}
MIN_DISTANCE = 50
PROPORTIONALITY = 25
MINIMUM_ZOOM_FILTER = 2500
MAXIMUM_ZOOM_FILTER = 1000000
MAXIMUM_NEIGHBORS = 3
JUMP = 20


class Bluemap(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        if (bluemap_gsheet_id := os.getenv("BLUEMAP_GSHEET_ID")) and (bluemap_json_file := os.getenv("BLUEMAP_JSON_FILE")):
            self.bluemap_gsheet_id = bluemap_gsheet_id
            self.bluemap_json_file = bluemap_json_file
        else:
            log("Bluemap variable(s) missing!")
            return

        self.schem_channel = await self.bot.fetch_channel(variables.Channels.SCHEMATIC_WARPS)
        self.console_channel = await self.bot.fetch_channel(variables.Channels.CONSOLE)
        self.update_bluemap.start()

    @interactions.Task.create(interactions.IntervalTrigger(hours=1))
    async def update_bluemap(self):
        sheetUrl = f"https://docs.google.com/spreadsheets/export?id={self.bluemap_gsheet_id}&format=xlsx"
        table = pd.read_excel(sheetUrl, sheet_name="Database", header=1, usecols="B:G").dropna(axis=0)
        new_markers = dict(sorted(self.generate_markers_dict(table).items()))
        with open(self.bluemap_json_file, "r") as file:
            old_markers = dict(sorted(json.load(file)["markers"].items()))
            for marker in old_markers.values():
                if marker.get("max-distance"):
                    del marker["max-distance"]

        if old_markers == new_markers:
            return  # Database hasn't changed, no need to continue

        # Send diff in channel
        embed = interactions.Embed("Update BlueMap", timestamp=interactions.Timestamp.now())
        diff = DeepDiff(old_markers, new_markers)
        if items_added := diff.get("dictionary_item_added"):
            fields = []
            for item in items_added:
                id = item.removeprefix("root['").removesuffix("']")
                fields.append(new_markers[id]["label"])
            embed.add_field("✅ Ajouté", "\n".join(fields), inline=True)
        if items_changed := diff.get("values_changed"):
            fields = []
            for item in items_changed.keys():
                id = item.removeprefix("root['").split("'")[0]
                fields.append(new_markers[id]["label"])
            embed.add_field(":arrows_counterclockwise: Modifié", "\n".join(fields), inline=True)
        if items_removed := diff.get("dictionary_item_removed"):
            fields = []
            for item in items_removed:
                id = item.removeprefix("root['").removesuffix("']")
                fields.append(old_markers[id]["label"])
            embed.add_field("❌ Supprimé", "\n".join(fields), inline=True)
        await self.schem_channel.send(embed=embed)

        # add max distance for each marker (takes time so done only when an update is needed)
        for marker in new_markers.values():
            marker["max-distance"] = self.calculate_max_distance(marker, new_markers)

        # save new Bluemap config and reload
        new_json_dict = {**DEFAULT_JSON_DICT, "markers": new_markers}
        with open(self.bluemap_json_file, "w") as file:
            json.dump(new_json_dict, file, indent=2)
        await self.console_channel.send("bluemap reload light")

    def generate_markers_dict(self, table: pd.DataFrame) -> dict:
        markers = {}
        for _, row in table.iterrows():
            marker = {}
            marker["label"] = row["Label"]
            marker["position"] = {"x": int(row["X"]), "y": int(row["Y"]), "z": int(row["Z"])}
            marker["icon"] = f"assets/icons/{ICONS_DICT.get(row['Icône'])}.png"
            marker["quality"] = QUALITY_DICT.get(row["Icône"])  # used later for calculating max distance
            marker["type"] = "poi"
            marker["anchor"] = {"x": 20, "y": 40}
            marker["min-distance"] = MIN_DISTANCE
            markers[row["ID"]] = marker
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
