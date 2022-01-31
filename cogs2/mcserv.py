from mcstatus import MinecraftServer
from utils.embed import create_embed
from variables import server
import interactions
import socket


# List of servers to get the status from.
servers = [
    {
        "ip": "btefr.thesmyler.fr:7000",
        "desc": "Serveur Moddé 1.12 - IP: buildtheearth.net, /bt FR",
    }
]


class MCServ(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="mc", description="Statut du serveur Minecraft", scope=server)
    async def mc(self, ctx: interactions.CommandContext):
        fields = []
        for server_dict in servers:

            try:
                status = MinecraftServer.lookup(server_dict["ip"]).status()

            except (ConnectionRefusedError, socket.timeout):
                embed_value = ":x: Serveur hors ligne!"
                embed_value += "\n\n_ _" if server_dict == servers[0] else ""
                fields.append(interactions.EmbedField(name=server_dict["desc"], value=embed_value, inline=False))

            else:
                online_players = status.players.online
                sample = sorted([p.name for p in status.players.sample]) if status.players.sample is not None else []

                sample_title = "Joueurs Connectés" if online_players != 1 else "Joueur Connecté"

                sample_txt = ""
                if online_players != 0:
                    diff = online_players - len(sample)
                    if diff > 0:
                        sample_txt = ", ".join(sample) + f" et {diff} autre"
                        sample_txt += "." if diff == 1 else "s."
                    elif online_players == 1:
                        sample_txt = sample[0]
                    else:
                        sample_txt = ", ".join(sample[:-1]) + " et " + sample[-1]
                sample_txt = sample_txt.replace("_", r"\_").replace("*", r"\*")  # Escape markdown symbols that could be present in players' names

                embed_value = f":white_check_mark: Serveur en ligne!\n\n**{online_players} {sample_title}**\n" + sample_txt
                fields.append(interactions.EmbedField(name=server_dict["desc"], value=embed_value, inline=False))

        await ctx.send(embeds=create_embed(
            title="**Statut du serveur Minecraft BTE France**",
            description="_ _\n",
            fields=fields
        ))


def setup(client: interactions.Client):
    MCServ(client)
