import os

import aiohttp
import interactions

import variables
from utils import log


class BuilderSync(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        if not (api_key := os.getenv("BTE_API_KEY")):
            log("No BTE_API_KEY variable found!")
            return
        self.headers = {
            "Host": "buildtheearth.net",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        self.guild = await self.bot.fetch_guild(variables.SERVER)
        await self.guild.gateway_chunk()  # Fetch all members of the server
        self.get_builders.start()

    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    async def get_builders(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://buildtheearth.net/api/v1/members", headers=self.headers
                ) as response:
                    json_response = await response.json()
        except Exception as e:
            log(f"Error while accessing BTE API:\n {e}")
            return

        for user in json_response["members"]:
            member = self.guild.get_member(user["discordId"])

            if not member:  # Member is not anymore in the guild
                continue

            if not member.has_role(variables.Roles.BUILDER):
                await member.add_role(
                    role=variables.Roles.BUILDER,
                    reason="Automatically added as a Builder!",
                )
                await member.remove_roles(
                    [variables.Roles.DEBUTANT, variables.Roles.VISITEUR]
                )
                log(f"Added {member.user.tag} as a Builder!")
