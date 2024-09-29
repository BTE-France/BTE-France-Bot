import json
import os
import socket

import interactions
from mcstatus import JavaServer

from utils import (
    RANK_DICT,
    RANK_EMOTE_DICT,
    create_embed,
    escape_minecraft_username_markdown,
    log,
)

SERVER_IP = "btefrance.fr:7011"
SERVER_DESC = "Serveur Java 1.20.1 - IP: btefrance.fr"


class MCServ(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        self.user_role_dict = {}
        if users_json_file := os.getenv("LUCKPERMS_USERS_JSON_FILE"):
            self.users_json_file = users_json_file
            await self.update_user_role_dict()
            self.update_user_role_dict.start()
        else:
            log("No LUCKPERMS_USERS_JSON_FILE variable found!")

    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    def update_user_role_dict(self):
        """Find staff players that have helper or above role using the LuckPerms file"""
        self.user_role_dict = {}
        with open(self.users_json_file, "r") as file:
            users = json.load(file)
            for user_dict in users.values():
                name = user_dict["name"]
                for group in user_dict["parents"]:
                    if (role := group.get("group")) in list(RANK_DICT.keys()):  # exclude regional groups
                        self.user_role_dict[name.lower()] = role
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
            users_per_role_dict = {}
            for player in query.players.names:
                player_role = self.user_role_dict.get(player.lower(), "default")
                if player_role not in users_per_role_dict:
                    users_per_role_dict[player_role] = [escape_minecraft_username_markdown(player)]
                else:
                    users_per_role_dict[player_role].append(escape_minecraft_username_markdown(player))
            users_per_role_dict = {
                key: users_per_role_dict[key] for key in list(RANK_DICT.keys()) if key in users_per_role_dict
            }  # order dict per role (Admin first, Visiteur last)

            len_players = 0
            for user_list in users_per_role_dict.values():
                user_list.sort(key=str.lower)
                len_players += len(user_list)
            title = f"{len_players} {'Joueurs Connectés' if len_players != 1 else 'Joueur Connecté'}"

            txt_per_role = []
            for role, users in users_per_role_dict.items():
                txt = f"{RANK_EMOTE_DICT.get(role)} {RANK_DICT.get(role)}{'s' if len(users) > 1 else ''}: {', '.join(users)}"
                if role in ("admin", "dev", "helper"):
                    txt = f"**{txt}**"
                txt_per_role.append(txt)
            txt = "\n".join(txt_per_role)
            embed_value = f":white_check_mark: Serveur en ligne!\n\n**{title}**\n" + txt

        embed.add_field(name=SERVER_DESC, value=embed_value, inline=False)
        await ctx.send(embeds=embed)
