import os
from datetime import datetime

import aiohttp
import interactions
from interactions.ext.tasks import IntervalTrigger, create_task

import variables


class BuilderSync(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.guild_member_IDs, self.builder_IDs = set(), set()

    @interactions.extension_listener()
    async def on_start(self):
        try:
            api_key = os.environ["BTE_API_KEY"]
        except KeyError:
            print("BTE API key not found, cannot synchronize builders!")
            return
        self.headers = {
            "Host": "buildtheearth.net",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        self.guild = await interactions.get(self.client, interactions.Guild, object_id=variables.SERVER)
        guild_members = await self.guild.get_all_members()
        for member in guild_members:
            self.guild_member_IDs.add(int(member.id))
            if variables.Roles.BUILDER in member.roles:
                self.builder_IDs.add(int(member.id))

        self.get_builders.start(self)
        print("Synchronizing guild members finished!")

    @create_task(IntervalTrigger(60))
    async def get_builders(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://buildtheearth.net/api/v1/members", headers=self.headers) as response:
                    json_response = await response.json()
        except Exception as e:
            print("Error while accessing BTE API:\n ", e)
            return

        for user in json_response["members"]:
            if int(user["discordId"]) in self.builder_IDs:
                continue

            if int(user["discordId"]) in self.guild_member_IDs:
                member = await self.guild.get_member(int(user["discordId"]))
                await self.add_builder_role(member)

    @interactions.extension_listener()
    async def on_guild_member_add(self, member: interactions.GuildMember):
        if int(member.guild_id) != variables.SERVER:
            return
        self.guild_member_IDs.add(int(member.id))

    @interactions.extension_listener()
    async def on_guild_member_remove(self, member: interactions.GuildMember):
        if not member:
            return
        try:
            self.guild_member_IDs.remove(int(member.id))
        except KeyError:  # Member was not registered in cache
            pass

    @interactions.extension_listener()
    async def on_raw_guild_member_update(self, member: interactions.GuildMember):
        if int(member.guild_id) != variables.SERVER:
            return

        if variables.Roles.BUILDER in member.roles:
            self.builder_IDs.add(int(member.id))
        else:
            try:
                self.builder_IDs.remove(int(member.id))
            except KeyError:  # Member was not registered in cache
                pass

    async def add_builder_role(self, member: interactions.GuildMember):
        self.builder_IDs.add(int(member.id))
        await member.add_role(role=variables.Roles.BUILDER, guild_id=variables.SERVER, reason="Automatically added as a Builder!")
        await member.remove_role(role=variables.Roles.BUILDER_NON_CONFIRME, guild_id=variables.SERVER)
        date = datetime.now().strftime("%d/%m - %H:%M")
        print(f"[{date}] Added {member.user.username}#{member.user.discriminator} as a Builder!")


def setup(client: interactions.Client):
    BuilderSync(client)
