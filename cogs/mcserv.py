import os
import discord
from discord.ext import commands
from mcstatus import MinecraftServer


class MCServ(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.server = MinecraftServer.lookup(os.environ["MCSERV_IP"])
        self.thumbnail_url = "https://cdn.discordapp.com/icons/694003889506091100/a_c40ba19cfcfbb9db5f5060e85f6539cf.png?size=128"
        self.offline_embed = discord.Embed(
            title="Status du serveur Minecraft BTE - France",
            colour=discord.Colour(0xFF0000),
            description=":x: Serveur hors ligne!"
        )
        self.offline_embed.set_thumbnail(url=self.thumbnail_url)
        self.online_embed = discord.Embed(
            title="Statut du serveur Minecraft BTE - France",
            colour=discord.Colour(0x00FF00),
            description=":white_check_mark: Serveur en ligne!"
        )
        self.online_embed.set_thumbnail(url=self.thumbnail_url)

    @commands.command(brief='Statut du serveur Minecraft', aliases=['mcserv', 'mcstatus', 'status'])
    async def mc(self, ctx):
        try:
            status = self.server.status()
        except ConnectionRefusedError:
            await ctx.send(embed=self.offline_embed)
        else:
            self.online_embed.clear_fields()
            online = status.players.online
            self.online_embed.add_field(
                name="En ligne:",
                value=f"{online}/{status.players.max}",
                inline=False
            )
            if status.players.sample is not None:
                sample = sorted([p.name for p in status.players.sample])
            else:
                sample = []
            if online != 0:
                diff = online - len(sample)
                sample_title = "Joueurs: "
                if diff > 0:
                    sample_txt = ", ".join(sample) + f" et {diff} autre"
                    sample_txt += "." if diff == 1 else "s."
                elif online == 1:
                    sample_title = "Joueur: "
                    sample_txt = sample[0]
                else:
                    sample_txt = ", ".join(sample[:-1]) + " et " + sample[-1]
                self.online_embed.add_field(
                    name=sample_title,
                    value=discord.utils.escape_markdown(sample_txt),
                    inline=False
                )
            await ctx.send(embed=self.online_embed)


def setup(client):
    client.add_cog(MCServ(client))
