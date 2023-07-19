import socket

import interactions
from mcstatus import JavaServer

from utils import create_embed

STAFF_USERNAMES = [
    "lennah_",
    "*maxdrey49",
    "bahlkog",
    "l0pal",
    "luckylukass",
    "madin0",
    "maxyolo01",
    "serenityjane",
    "weelly_",
    "eklo",
    "egan83",
    "babyoda_",
    "maxdrey",
    "smyler_",
    "thesmyler",
    "__elfi__",
    "litverkzad",
    "repsic",
    "zxsp3ctrom",
    "tytarex",
    "lclc",
    "azguendare",
    "dstarmc",
]
SERVER_IP = "btefr.thesmyler.fr:7011"
SERVER_DESC = "Serveur Java 1.20.1 - IP: btefrance.fr"


def escape_markdown(string: str) -> str:
    return string.replace("_", r"\_").replace(
        "*", r"\*"
    )  # Escape markdown symbols that could be present in players' names


class MCServ(interactions.Extension):
    @interactions.slash_command(name="mc")
    async def mc(self, ctx: interactions.SlashContext):
        "Statut du serveur Minecraft"
        await ctx.defer()

        embed = create_embed(
            title="**Statut du serveur Minecraft BTE France**",
            description="_ _\n",
            include_thumbnail=True,
        )

        try:
            query = await (await JavaServer.async_lookup(SERVER_IP)).async_query()

        except (ConnectionRefusedError, socket.timeout):
            embed_value = ":x: Serveur hors ligne!"

        else:
            staff, players = [], []
            for player in query.players.names:
                if player.lower() in STAFF_USERNAMES:
                    staff.append(f"**{escape_markdown(player)}**")
                else:
                    players.append(escape_markdown(player))

            staff.sort(key=str.lower)
            players.sort(key=str.lower)

            len_players = len(staff) + len(players)
            title = f"{len_players} {'Joueurs Connectés' if len_players != 1 else 'Joueur Connecté'}"

            txt = ", ".join(staff + players)
            embed_value = f":white_check_mark: Serveur en ligne!\n\n**{title}**\n" + txt

        embed.add_field(name=SERVER_DESC, value=embed_value, inline=False)
        await ctx.send(embeds=embed)
