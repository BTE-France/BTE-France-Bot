import discord
from discord.ext import commands


class Node:
    def __init__(self, question, emoji):
        self.question = question
        self.emoji = emoji
        self.children = []

    def add_children(self, *children):
        for child in children:
            self.children.append(child)

    def get_node(self, question):
        l = self.create_list()
        for node in l:
            if node.question == question:
                return node
        raise Exception("There is no node with this question in this tree!")

    def create_list(self, l=[]):
        l.append(self)
        for child in self.children:
            child.create_list(l)
        return l

    def print_tree(self):
        print(self.question)
        for child in self.children:
            child.print_tree()


root = Node(':one: Comment rejoindre le serveur MC?\n:two: Comment devenir builder officiel?', None)
second = Node('Il faut déjà être builder officiel!', '1\N{COMBINING ENCLOSING KEYCAP}')
third = Node("Il faut constuire 2 bâtiments en solo.", '2\N{COMBINING ENCLOSING KEYCAP}')
root.add_children(second, third)


class HelpBuilding(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def add_emojis(self, message, node):
        for child in node.children:
            try:
                await message.add_reaction(child.emoji)
            except discord.errors.HTTPException:
                print(f"Emoji {child.emoji} not found!")

    @commands.command(brief='Help with building in private messages')
    async def build(self, ctx):
        message = await ctx.author.send(embed=discord.Embed(type='rich', description=root.question))
        await self.add_emojis(message, root)

    @commands.command(brief='Find the name of an emoji')
    async def emojiname(self, ctx, emoji):
        await ctx.author.send(emoji.encode('ascii', 'namereplace'))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.type == discord.ChannelType.private and not user.bot:
            try:
                node = root.get_node(reaction.message.embeds[0].description)
            except Exception:
                return
            for child in node.children:
                if child.emoji == reaction.emoji:
                    message = await reaction.message.channel.send(embed=discord.Embed(type='rich', description=child.question))
                    await self.add_emojis(message, child)
                    break


def setup(client):
    client.add_cog(HelpBuilding(client))
