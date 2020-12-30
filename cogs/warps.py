import discord
import variables
from discord.ext import commands

warps = {
    "La Défense": ["defense_esplanade", "Quartier d'affaires de Paris connu pour ses nombreux gratte-ciels.\nBusiness district of Paris known for its numerous skyscrapers.", "https://media.discordapp.net/attachments/694325296106569748/719921092814438460/2020-06-09_10.27.30.png?width=1194&height=671"],
    "Arc de Triomphe": ["arc_de_triomphe", "Arc au coeur de Paris, situé sur l'avenue des Champs-Elysées.\nArc at the heart of Paris, situated on the Avenue des Champs-Elysées.", "https://images-ext-1.discordapp.net/external/zzWs72V7Gglq3vHYKV9r33NAhYssRQ9WhDFeL0XMqZM/https/i.imgur.com/ey0Dewp.png?width=641&height=672"],
    "Île Saint-Louis": ["saint-louis", "Île en plein milieu de Paris et bordée par la Seine.\nIsland in the middle of Paris and bordered by the Seine.", "https://media.discordapp.net/attachments/694325296106569748/719704689318559795/2020-06-09_02.00.20.png?width=1268&height=671"],
    "Nantes": ["nantes", "Cité des Ducs de Bretagne, non loin de l'océan Atlantique.\nCity of Dukes of Brittany, not far from the Atlantic ocean.", "https://i.imgur.com/DW9k26J.png"],
    "Turenne": ["turenne", "Village en Corrèze, réalisé en 48h en tant qu'évènement communautaire.\n Village in Corrèze, realized in 48h as a community event.", "https://images-ext-1.discordapp.net/external/pbkeBOTWQVA-IUa8blek5pNI-sUZhNIPu_Yw-WgLM-U/https/i.imgur.com/hvd2klJ.jpg?width=1194&height=671"],
    "Belle-Île-en-Mer": ["belle_ile", "Île dans l'océan Atlantique ayant été une forteresse auparavant.\nIsland in the Atlantic ocean having been previously a fortress.", "https://media.discordapp.net/attachments/694325296106569748/708468079658795018/2020-05-09_01.34.14.png?width=1268&height=671"],
    "Quimper": ["quimper", "Chef-lieu du Finistère, le centre ayant été construit en 96h en tant qu'évènement communautaire.\nCapital of Finistère, the center having been built in 48h as a community event.", "https://media.discordapp.net/attachments/692259936012468235/714577660742729738/Image_04_000.png?width=1194&height=671"],
    "Bordeaux": ["bordeaux", "Cinquième ville de France, connue mondialement pour son vin.\nFifth city of France, known worldwide for its wine.", "https://media.discordapp.net/attachments/694325296106569748/710989490688360469/Image_01_005.png?width=1443&height=641"],
    "Le Puy-Notre-Dame": ["lepuynotredame", "Petite commune dans le Maine-et-Loire.\nSmall town in the Maine-et-Loire.", "https://images-ext-1.discordapp.net/external/VcCWLicW7-sua-rBPR9cwcy4D2GYGAAW1tSWxOf1-B8/https/i.imgur.com/aG42ecr.png?width=1283&height=671"],
    "Pointe Saint-Mathieu": ["pointe_saint-mathieu", "Pointe du Finistère, au bord des falaises.\nHeadland of Finistère, flanked by cliffs.", "https://media.discordapp.net/attachments/694325296106569748/733279570395922462/2020-07-16_13.08.23.png?width=1268&height=671"],
}


class Warps(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.thumbnail_url = variables.bte_france_icon

    @commands.command(brief='Liste des meilleurs Warps', aliases=['warp'])
    async def warps(self, ctx):
        if ctx.channel.type != discord.ChannelType.private:
            await ctx.send(f"{ctx.author.mention}, regarde tes MPs! :mailbox:")
        await ctx.author.send(":flag_fr: **Liste des meilleurs warps sur le serveur BTE France** :flag_fr:")
        for name, desc in warps.items():
            embed = discord.Embed(
                title=name,
                colour=discord.Colour(0xFFFFFF)
            )
            embed.add_field(name=f'/warp {desc[0]}', value=desc[1], inline=False)
            embed.set_image(url=desc[2])
            embed.set_thumbnail(url=self.thumbnail_url)
            await ctx.author.send(embed=embed)


def setup(client):
    client.add_cog(Warps(client))
