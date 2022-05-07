from utils.embed import create_embed
from variables import server
import interactions


class SocialMedia(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="youtube", description="Youtube link", scope=server)
    async def youtube(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="YouTube de BTE: France",
            description="https://www.youtube.com/c/BTEFrance",
            color=0xFF0000
        ))

    @interactions.extension_command(name="twitter", description="Twitter link", scope=server)
    async def twitter(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Twitter de BTE: France",
            description="https://twitter.com/BTE_France",
            color=0x0000FF
        ))

    @interactions.extension_command(name="instagram", description="Instagram link", scope=server)
    async def instagram(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Instagram de BTE: France",
            description="https://www.instagram.com/bte_france/",
            color=0xFFFF00
        ))

    @interactions.extension_command(name="facebook", description="Facebook link", scope=server)
    async def facebook(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Facebook de BTE: France",
            description="https://www.facebook.com/Build-The-Earth-France-113380800556340",
            color=0x0800FF
        ))

    @interactions.extension_command(name="reddit", description="Reddit link", scope=server)
    async def reddit(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Reddit de BTE: France",
            description="https://www.reddit.com/user/BTE_France/",
            color=0x0800FF
        ))

    @interactions.extension_command(name="planet-minecraft", description="PlanetMinecraft link", scope=server)
    async def planet_minecraft(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="PlanetMinecraft de BTE: France",
            description="https://www.planetminecraft.com/member/bte-france",
            color=0x0800FF
        ))

    @interactions.extension_command(name="tiktok", description="Tiktok link", scope=server)
    async def tiktok(self, ctx: interactions.CommandContext):
        await ctx.send(embeds=create_embed(
            title="Tiktok de BTE: France",
            description="https://www.tiktok.com/@btefrance",
            color=0x0000FF
        ))


def setup(client: interactions.Client):
    SocialMedia(client)
