import json
import os
import socket

import interactions
from mcstatus import JavaServer

from utils import create_embed, escape_minecraft_username_markdown, log

SERVER_IP = "btefr.thesmyler.fr:7011"
SERVER_DESC = "Serveur Java 1.20.1 - IP: btefrance.fr"


class MCServ(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.staff_players = []
        if users_json_file := os.getenv("LUCKPERMS_USERS_JSON_FILE"):
            self.users_json_file = users_json_file
            self.staff_players = []
            await self.update_staff_players()
            self.update_staff_players.start()
        else:
            log("No LUCKPERMS_USERS_JSON_FILE variable found!")

    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    def update_staff_players(self):
        """Find staff players that have helper or above role using the LuckPerms file"""
        self.staff_players = []
        with open(self.users_json_file, "r") as file:
            users = json.load(file)
            for user_dict in users.values():
                name = user_dict["name"]
                for group in user_dict["parents"]:
                    if group["group"] in ("admin", "dev", "helper"):
                        self.staff_players.append(name.lower())
                        break

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
                if player.lower() in self.staff_players:
                    staff.append(f"**{escape_minecraft_username_markdown(player)}**")
                else:
                    players.append(escape_minecraft_username_markdown(player))

            staff.sort(key=str.lower)
            players.sort(key=str.lower)

            len_players = len(staff) + len(players)
            title = f"{len_players} {'Joueurs Connectés' if len_players != 1 else 'Joueur Connecté'}"

            txt = ", ".join(staff + players)
            embed_value = f":white_check_mark: Serveur en ligne!\n\n**{title}**\n" + txt

        embed.add_field(name=SERVER_DESC, value=embed_value, inline=False)
        await ctx.send(embeds=embed)
