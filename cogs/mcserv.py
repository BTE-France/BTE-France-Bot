import socket

import interactions
from mcstatus import JavaServer

from utils.embed import create_embed

STAFF_USERNAMES = [
    "lennah_",
    "*maxdrey49",
    "bahlkog",
    "l0pal",
    "luckylukass",
    "madin0",
    "maxyolo01",
    "raphinoj",
    "sandpaper_dreams",
    "serenityjane",
    "weelly_",
    "eklo",
    "egan83",
    "goul20",
    "babyoda_",
    "maxdrey",
    "smyler_",
    "thesmyler",
    "__elfi__",
    "litverkzad",
    "picopioche",
    "repsic",
    "zxsp3ctrom",
    "tytarex",
    "lclc",
    "azguendare",
]

# List of servers to get the status from.
SERVERS = [
    ("btefr.thesmyler.fr:7000", "Serveur Moddé 1.12 - IP: bte.thesmyler.fr")
]


def escape_markdown(string: str) -> str:
    return string.replace("_", r"\_").replace("*", r"\*")  # Escape markdown symbols that could be present in players' names


class MCServ(interactions.Extension):
    @interactions.extension_command(name="mc", description="Statut du serveur Minecraft")
    async def mc(self, ctx: interactions.CommandContext):
        await ctx.defer()

        embed = create_embed(
            title="**Statut du serveur Minecraft BTE France**",
            description="_ _\n",
        )

        for _server in SERVERS:
            ip, desc = _server
            try:
                query = await (await JavaServer.async_lookup(ip)).async_query()

            except (ConnectionRefusedError, socket.timeout):
                embed_value = ":x: Serveur hors ligne!"
                embed_value += "\n\n_ _" if _server == SERVERS[0] else ""
                embed.add_field(name=desc, value=embed_value, inline=False)

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
                value = f":white_check_mark: Serveur en ligne!\n\n**{title}**\n" + txt
                embed.add_field(name=desc, value=value, inline=False)

        await ctx.send(embeds=embed)


def setup(client: interactions.Client):
    MCServ(client)
