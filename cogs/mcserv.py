import discord
import socket
import variables
from discord.ext import commands
from mcstatus import MinecraftServer


class MCServ(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.servers = [
            {
                "ip": "btefr.thesmyler.fr:7000",
                "desc": "Serveur Moddé 1.12 - IP: buildtheearth.net, /bt FR",
            },
        ]
        self.mc_embed = discord.Embed(
            title="**Statut des serveurs Minecraft BTE - France**", description="_ _\n"
        )
        self.mc_embed.set_thumbnail(url=variables.bte_france_icon)

    @commands.command(
        brief="Statut du serveur Minecraft", aliases=["mcserv", "mcstatus", "status"]
    )
    async def mc(self, ctx):
        self.mc_embed.clear_fields()
        for server in self.servers:
            try:
                status = MinecraftServer.lookup(server["ip"]).status()
            except (ConnectionRefusedError, socket.timeout):
                embed_value = ":x: Serveur hors ligne!"
                embed_value += "\n\n_ _" if server == self.servers[0] else ""
                self.mc_embed.add_field(
                    name=server["desc"], value=embed_value, inline=False
                )
            else:
                online_players = status.players.online
                sample = (
                    sorted([p.name for p in status.players.sample])
                    if status.players.sample is not None
                    else []
                )
                sample_title = (
                    "Joueurs Connectés" if online_players != 1 else "Joueur Connecté"
                )
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
                embed_value = (
                    f":white_check_mark: Serveur en ligne!\n\n**{online_players} {sample_title}**\n"
                    + discord.utils.escape_markdown(sample_txt)
                )
                # embed_value += '\n\n_ _' if server == self.servers[0] else ''
                self.mc_embed.add_field(
                    name=server["desc"], value=embed_value, inline=False
                )
        await ctx.send(embed=self.mc_embed)


def setup(client):
    client.add_cog(MCServ(client))
