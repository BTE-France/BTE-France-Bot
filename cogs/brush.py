from utils.embed import create_error_embed, create_embed
from imgur_python import Imgur
from variables import server
from PIL import Image
import interactions
import random
import os


class Brush(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client
        self.imgur_client = Imgur({
            "client_id": os.environ["IMGUR_ID"],
            "client_secret": os.environ["IMGUR_SECRET"],
            "access_token": os.environ["IMGUR_TOKEN"]
        })

    @interactions.extension_command(name="brush", description="Brush command, replicating the one from WorldEdit", scope=server, options=[
        interactions.Option(type=interactions.OptionType.STRING, name="pattern", description="WorldEdit pattern", required=True),
        interactions.Option(type=interactions.OptionType.INTEGER, name="size", description="Size of the brush", required=False, min_value=20, max_value=100),
    ])
    async def brush(self, ctx: interactions.CommandContext, pattern: str, size: int = 20):
        await ctx.defer()

        pattern_split = pattern.split(",")
        weights, materials = [], []
        forget_weights = False
        for pat in pattern_split:
            result = pat.split("%")
            if len(result) == 2:
                materials.append(result[1])
                try:
                    weights.append(int(result[0]))
                except ValueError:  # Weight is not a number
                    await ctx.send(embeds=create_error_embed(f"Wrong weight detected: {result[0]}"))
                    return
            elif len(result) == 1:  # No weight set, cancelling weights for all blocks
                forget_weights = True
                materials.append(result[0])
            else:
                await ctx.send(embeds=create_error_embed("Wrong syntax in materials!"))
                return
        weights = None if forget_weights else weights
        weighted_list = random.choices(
            population=materials, weights=weights, k=size ** 2
        )

        final_image = Image.new("RGB", (size * 16, size * 16), (250, 250, 250))
        not_found = []
        for y in range(size):
            for x in range(size):
                block_raw = weighted_list[y * size + x]
                block = self.get_emoji(block_raw)
                if block is None:
                    final_image.paste(
                        Image.open("blocks/question.png"), (x * 16, y * 16)
                    )
                    if block_raw not in not_found:
                        not_found.append(block_raw)
                else:
                    final_image.paste(
                        Image.open(f"blocks/{block}.png"), (x * 16, y * 16)
                    )

        # Upload image to imgur.com
        name = "BTEFranceBrush.png"
        album_id = "R22ds3m"
        final_image.save(name)
        response = self.imgur_client.image_upload(name, name, "", album=album_id)
        os.remove(name)

        await ctx.send(embeds=create_embed(
            title=f"Pattern: {pattern}",
            description=f":question: `Unrecognized IDs: {', '.join(sorted(not_found))} ` :question:" if not_found else "",
            image=response["response"]["data"]["link"]
        ))

    def get_emoji(self, block_raw):
        for block_id, block_aliases in blocks.items():
            if block_id == block_raw or block_raw in block_aliases:
                return block_id
        return None


def setup(client: interactions.Client):
    Brush(client)


blocks = {
    "beacon": ["138"],
    "bedrock": ["7"],
    "bone_block": ["216"],
    "bookshelf": ["47"],
    "brick": ["45"],
    "cactus": ["81"],
    "cake": ["92"],
    "chain_command_block": ["211"],
    "chorus_flower": ["200"],
    "clay": ["82"],
    "coal_block": ["173"],
    "coal_ore": ["16"],
    "coarse_dirt": ["3:1"],
    "cobblestone": ["4"],
    "cobblestone_mossy": ["48"],
    "command_block": ["137"],
    "comparator_off": ["149"],
    "comparator_on": ["150"],
    "concrete_black": ["251:15"],
    "concrete_blue": ["251:11"],
    "concrete_brown": ["251:12"],
    "concrete_cyan": ["251:9"],
    "concrete_gray": ["251:7"],
    "concrete_green": ["251:13"],
    "concrete_light_blue": ["251:3"],
    "concrete_lime": ["251:5"],
    "concrete_magenta": ["251:2"],
    "concrete_orange": ["251:1"],
    "concrete_pink": ["251:6"],
    "concrete_powder_black": ["252:15"],
    "concrete_powder_blue": ["252:11"],
    "concrete_powder_brown": ["252:12"],
    "concrete_powder_cyan": ["252:9"],
    "concrete_powder_gray": ["252:7"],
    "concrete_powder_green": ["252:13"],
    "concrete_powder_light_blue": ["252:3"],
    "concrete_powder_lime": ["252:5"],
    "concrete_powder_magenta": ["252:2"],
    "concrete_powder_orange": ["252:1"],
    "concrete_powder_pink": ["252:6"],
    "concrete_powder_purple": ["252:10"],
    "concrete_powder_red": ["252:14"],
    "concrete_powder_silver": ["252:8"],
    "concrete_powder_white": ["252"],
    "concrete_powder_yellow": ["252:4"],
    "concrete_purple": ["251:10"],
    "concrete_red": ["251:14"],
    "concrete_silver": ["251:8"],
    "concrete_white": ["251"],
    "concrete_yellow": ["251:4"],
    "crafting_table_top": ["58", "crafting_table"],
    "daylight_detector_inverted_top": ["178", "daylight_detector_inverted"],
    "daylight_detector_top": ["151", "daylight_detector"],
    "diamond_block": ["57"],
    "diamond_ore": ["56"],
    "dirt": ["3"],
    "dirt_podzol_top": ["3:2", "podzol"],
    "dispenser_front": ["23", "dispenser"],
    "dropper_front": ["158", "dropper"],
    "emerald_block": ["133"],
    "emerald_ore": ["129"],
    "enchanting_table_top": ["116", "enchanting_table"],
    "end_bricks": ["206"],
    "end_stone": ["121"],
    "endframe_top": ["120", "end_portal_frame"],
    "farmland_dry": ["60"],
    "farmland_wet": ["60:1"],
    "furnace_front_off": ["61", "furnace"],
    "glass": ["20"],
    "glass_black": ["95:15", "160:15"],
    "glass_blue": ["95:11", "160:11"],
    "glass_brown": ["95:12", "160:12"],
    "glass_cyan": ["95:9", "160:9"],
    "glass_gray": ["95:7", "160:7"],
    "glass_green": ["95:13", "160:13"],
    "glass_light_blue": ["95:3", "160:3"],
    "glass_lime": ["95:5", "160:5"],
    "glass_magenta": ["95:2", "160:2"],
    "glass_orange": ["95:1", "160:1"],
    "glass_pink": ["95:6", "160:6"],
    "glass_purple": ["95:10", "160:10"],
    "glass_red": ["95:14", "160:14"],
    "glass_silver": ["95:8", "160:8"],
    "glass_white": ["95", "160"],
    "glass_yellow": ["95:4", "160:4"],
    "glazed_terracotta_black": ["250"],
    "glazed_terracotta_blue": ["246"],
    "glazed_terracotta_brown": ["247"],
    "glazed_terracotta_cyan": ["244"],
    "glazed_terracotta_gray": ["242"],
    "glazed_terracotta_green": ["248"],
    "glazed_terracotta_light_blue": ["238"],
    "glazed_terracotta_lime": ["240"],
    "glazed_terracotta_magenta": ["237"],
    "glazed_terracotta_orange": ["236"],
    "glazed_terracotta_pink": ["241"],
    "glazed_terracotta_purple": ["245"],
    "glazed_terracotta_red": ["249"],
    "glazed_terracotta_silver": ["243"],
    "glazed_terracotta_white": ["235"],
    "glazed_terracotta_yellow": ["239"],
    "glowstone": ["89"],
    "gold_block": ["41"],
    "gold_ore": ["14"],
    "grass": ["2"],
    "grass_path_top": ["208", "grass_path"],
    "gravel": ["13"],
    "hardened_clay": ["172"],
    "hardened_clay_stained_black": [
        "159:15",
        "black_hardened_clay",
        "hardened_clay_black",
    ],
    "hardened_clay_stained_blue": [
        "159:11",
        "blue_hardened_clay",
        "hardened_clay_blue",
    ],
    "hardened_clay_stained_brown": [
        "159:12",
        "brown_hardened_clay",
        "hardened_clay_brown",
    ],
    "hardened_clay_stained_cyan": ["159:9", "cyan_hardened_clay", "hardened_clay_cyan"],
    "hardened_clay_stained_gray": ["159:7", "gray_hardened_clay", "hardened_clay_gray"],
    "hardened_clay_stained_green": [
        "159:13",
        "green_hardened_clay",
        "hardened_clay_green",
    ],
    "hardened_clay_stained_light_blue": [
        "159:3",
        "light_blue_hardened_clay",
        "hardened_clay_light_blue",
    ],
    "hardened_clay_stained_lime": ["159:5", "lime_hardened_clay", "hardened_clay_lime"],
    "hardened_clay_stained_magenta": [
        "159:2",
        "magenta_hardened_clay",
        "hardened_clay_magenta",
    ],
    "hardened_clay_stained_orange": [
        "159:1",
        "orange_hardened_clay",
        "hardened_clay_orange",
    ],
    "hardened_clay_stained_pink": ["159:6", "pink_hardened_clay", "hardened_clay_pink"],
    "hardened_clay_stained_purple": [
        "159:10",
        "purple_hardened_clay",
        "hardened_clay_purple",
    ],
    "hardened_clay_stained_red": ["159:14", "red_hardened_clay", "hardened_clay_red"],
    "hardened_clay_stained_silver": [
        "159:8",
        "silver_hardened_clay",
        "hardened_clay_silver",
    ],
    "hardened_clay_stained_white": [
        "159",
        "white_hardened_clay",
        "hardened_clay_white",
    ],
    "hardened_clay_stained_yellow": [
        "159:4",
        "yellow_hardened_clay",
        "hardened_clay_yellow",
    ],
    "hay_block_top": ["170", "hay_block", "170:12"],
    "ice": ["79"],
    "ice_packed": ["174", "packed_ice"],
    "iron_bars": ["101"],
    "iron_block": ["42"],
    "iron_ore": ["15"],
    "iron_trapdoor": ["167"],
    "jukebox_side": ["84"],
    "ladder": ["65"],
    "lapis_block": ["22"],
    "lapis_ore": ["21"],
    "lava_still": ["10", "11", "lava"],
    "leaves_acacia": ["161"],
    "leaves_big_oak": ["161:1"],
    "leaves_birch": ["18:2"],
    "leaves_jungle": ["18:3"],
    "leaves_oak": ["18"],
    "leaves_spruce": ["18:1"],
    "log_acacia": ["162", "162:12"],
    "log_big_oak": ["162:1", "162:13"],
    "log_birch": ["17:2", "17:14"],
    "log_jungle": ["17:3", "17:15"],
    "log_oak": ["17", "17:12"],
    "log_spruce": ["17:1", "17:13"],
    "magma": ["213"],
    "melon_side": ["103", "melon", "melon_block"],
    "mob_spawner": ["52"],
    "mushroom_block_inside": ["100:0"],
    "mushroom_block_skin_brown": ["99"],
    "mushroom_block_skin_red": ["100"],
    "mushroom_block_skin_stem": ["100:15", "100:10"],
    "mycelium_top": ["110", "mycelium"],
    "nether_brick": ["112"],
    "nether_wart_block": ["214"],
    "netherrack": ["87"],
    "noteblock": ["25"],
    "observer_front": ["218", "observer"],
    "obsidian": ["49"],
    "piston_top_normal": ["33", "34", "piston", "33:7"],
    "piston_top_sticky": ["29", "sticky_piston", "29:7"],
    "planks_acacia": ["5:4"],
    "planks_big_oak": ["5:5"],
    "planks_birch": ["5:2"],
    "planks_jungle": ["5:3"],
    "planks_oak": ["5"],
    "planks_spruce": ["5:1"],
    "prismarine_bricks": ["168:1"],
    "prismarine_dark": ["168:2"],
    "prismarine_rough": ["168", "prismarine"],
    "pumpkin_face": ["86", "pumpkin", "86:4"],
    "purpur_block": ["201"],
    "purpur_pillar": ["202"],
    "quartz_block_top": ["155", "quartz_block"],
    "quartz_block_chiseled": ["155:1"],
    "quartz_block_lines": ["155:2"],
    "quartz_ore": ["153"],
    "red_nether_brick": ["215"],
    "red_sand": ["12:1"],
    "red_sandstone_top": ["179", "red_sandstone"],
    "red_sandstone_carved": ["179:1"],
    "red_sandstone_smooth": ["179:2", "181:12"],
    "redstone_block": ["152"],
    "redstone_lamp_off": ["123"],
    "redstone_lamp_on": ["124"],
    "redstone_ore": ["73"],
    "repeater_off": ["93", "unpowered_repeater"],
    "repeater_on": ["94", "powered_repeater"],
    "repeating_command_block": ["210"],
    "sand": ["12"],
    "sandstone_top": ["24"],
    "sandstone_carved": ["24:1"],
    "sandstone_smooth": ["24:2", "43:9"],
    "sea_lantern": ["169"],
    "shulker_top_black": ["234", "black_shulker_box"],
    "shulker_top_blue": ["230", "blue_shulker_box"],
    "shulker_top_brown": ["231", "brown_shulker_box"],
    "shulker_top_cyan": ["228", "cyan_shulker_box"],
    "shulker_top_gray": ["226", "gray_shulker_box"],
    "shulker_top_green": ["232", "green_shulker_box"],
    "shulker_top_light_blue": ["222", "light_blue_shulker_box"],
    "shulker_top_lime": ["224", "lime_shulker_box"],
    "shulker_top_magenta": ["221", "magenta_shulker_box"],
    "shulker_top_orange": ["220", "orange_shulker_box"],
    "shulker_top_pink": ["225", "pink_shulker_box"],
    "shulker_top_purple": ["229", "purple_shulker_box"],
    "shulker_top_red": ["233", "red_shulker_box"],
    "shulker_top_silver": ["227", "silver_shulker_box"],
    "shulker_top_white": ["219", "white_shulker_box"],
    "shulker_top_yellow": ["223", "yellow_shulker_box"],
    "slime": ["165"],
    "snow": ["78"],
    "soul_sand": ["88"],
    "sponge": ["19"],
    "sponge_wet": ["19:1"],
    "stone": ["1"],
    "stone_andesite": ["1:5"],
    "stone_andesite_smooth": ["1:6"],
    "stone_diorite": ["1:3"],
    "stone_diorite_smooth": ["1:4"],
    "stone_granite": ["1:1"],
    "stone_granite_smooth": ["1:2"],
    "stone_slab_top": ["43", "44", "43:8", "stone_slab"],
    "stonebrick": ["98", "97:2"],
    "stonebrick_carved": ["98:3", "97:5"],
    "stonebrick_cracked": ["98:2", "97:4"],
    "stonebrick_mossy": ["98:1", "97:3"],
    "tnt_side": ["46", "tnt"],
    "trapdoor": ["96"],
    "water": ["8", "9"],
    "web": ["30", "cobweb"],
    "wool_colored_black": ["35:15"],
    "wool_colored_blue": ["35:11"],
    "wool_colored_brown": ["35:12"],
    "wool_colored_cyan": ["35:9"],
    "wool_colored_gray": ["35:7"],
    "wool_colored_green": ["35:13"],
    "wool_colored_light_blue": ["35:3"],
    "wool_colored_lime": ["35:5"],
    "wool_colored_magenta": ["35:2"],
    "wool_colored_orange": ["35:1"],
    "wool_colored_pink": ["35:6"],
    "wool_colored_purple": ["35:10"],
    "wool_colored_red": ["35:14"],
    "wool_colored_silver": ["35:8"],
    "wool_colored_white": ["35"],
    "wool_colored_yellow": ["35:4"],
}
