import os
import requests
import discord
import variables
from discord.ext import commands, tasks


class Builder_Sync(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sync.start()

    @tasks.loop(minutes=1.0)
    async def sync(self):
        await self.client.wait_until_ready()
        try:
            api_key = os.environ['API_KEY']
        except KeyError:
            return
        headers = {"Host": "buildtheearth.net", "Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        response = requests.get("https://buildtheearth.net/api/v1/members", headers=headers).json()
        guild = self.client.get_guild(variables.server)
        builderNonConfirmeRole = discord.utils.get(guild.roles, id=variables.builder_non_confirme)
        builderRole = discord.utils.get(guild.roles, id=variables.builder)
        for user in response['members']:
            try:
                member = await guild.fetch_member(user['discordId'])
                if builderNonConfirmeRole in member.roles:
                    await member.add_roles(builderRole)
                    await member.remove_roles(builderNonConfirmeRole)
                    print('Added ' + user['discordTag'] + ' as a Builder!')
            except discord.errors.NotFound:  # Member not in the server
                continue


def setup(client):
    client.add_cog(Builder_Sync(client))
