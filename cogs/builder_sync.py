import requests
import discord
from bs4 import BeautifulSoup
from discord.ext import commands, tasks


class Builder_Sync(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.main_url = "https://buildtheearth.net/buildteams/74/members"
        self.main_page = requests.get(self.main_url)
        self.main_soup = BeautifulSoup(self.main_page.content, 'html.parser')
        self.sync.start()

    @tasks.loop(minutes=1.0)
    async def sync(self):
        await self.client.wait_until_ready()
        l = [a.text for a in self.main_soup.find_all('a', href=True) if 'page' in a['href']]
        num = int(max(l)) if l else 1
        users = []
        to_exclude = ['Builder', 'Reviewer', 'Co-leader', 'Leader']
        for i in range(1, num + 1):
            page = requests.get(f"{self.main_url}?page={i}")
            soup = BeautifulSoup(page.content, 'html.parser')
            users += [a.text for a in soup.find_all('td', text=True) if a.text not in to_exclude]
        guild = self.client.get_guild(694003889506091100)
        notBuilderRole = discord.utils.get(guild.roles, id=694176792675614800)
        builderRole = discord.utils.get(guild.roles, id=694176169465086003)
        for user in users:
            member = guild.get_member_named(user)
            if member is not None and notBuilderRole in member.roles:
                await member.add_roles(builderRole)
                await member.remove_roles(notBuilderRole)
                print(f'Added {user} as a Builder!')


def setup(client):
    client.add_cog(Builder_Sync(client))
