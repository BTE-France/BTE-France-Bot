import random
from dataclasses import dataclass

import interactions

from utils import create_embed


@dataclass
class Warp:
    name: str
    warp: str
    description: str
    image: str


WARPS = [
    Warp(
        "La Défense",
        "defense_esplanade",
        "Quartier d'affaires de Paris connu pour ses nombreux gratte-ciels.\nBusiness district of Paris known for its numerous skyscrapers.",
        "https://imgur.com/ZOTj9dn.png",
    ),
    Warp(
        "Arc de Triomphe",
        "paris:etoile",
        "Arc au coeur de Paris, situé sur l'avenue des Champs-Elysées.\nArc at the heart of Paris, situated on the Avenue des Champs-Elysées.",
        "https://imgur.com/OBemDc5.png",
    ),
    Warp(
        "Ile de la Cité",
        "Ile_de_la_Cite",
        "Le berceau de la ville de Paris, construit par la team ETB.\nThe cradle of Paris, built by the ETB team.",
        "https://imgur.com/FcLGAae.png",
    ),
    Warp(
        "Nantes",
        "Nantes:cathedrale",
        "Cité des Ducs de Bretagne, non loin de l'océan Atlantique.\nCity of Dukes of Brittany, not far from the Atlantic ocean.",
        "https://imgur.com/WM4frCq.png",
    ),
    Warp(
        "Turenne",
        "turenne",
        "Village en Corrèze, réalisé en 48h en tant qu'évènement communautaire.\n Village in Corrèze, realized in 48h as a community event.",
        "https://imgur.com/j5qThvh.png",
    ),
    Warp(
        "Le Puy-Notre-Dame",
        "lepuynotredame",
        "Petite commune dans le Maine-et-Loire.\nSmall town in the Maine-et-Loire.",
        "https://imgur.com/VFyfKzR.png",
    ),
    Warp(
        "Le Mont-Saint-Michel",
        "mont-saint-michel",
        "Îlot roché situé en Normandie, une des icones de la France.\nTidal island located in Normandy, one of the icons of France.",
        "https://imgur.com/M9nsIbr.png",
    ),
    Warp(
        "Turckheim",
        "Turckheim",
        "Petite commune en Alsace avec notamment beaucoup de maisons à colombages.\nSmall town in Alsace with many half-timbered houses.",
        "https://imgur.com/qsjFdo6.png",
    ),
    Warp(
        "Monaco",
        "monaco",
        "Principauté située sur la côte méditéranéenne, construite par la team Build It 1:1.\nPrincipality located on the Mediterranean coast, built by the Build It 1:1 team.",
        "https://imgur.com/gA9DGCf.png",
    ),
    Warp(
        "Viaduc de Millau",
        "viaduc_de_millau",
        "Le viaduc avec les pylônes les plus hauts du monde (343m).\nThe viaduct with the highest pylons in the world (343m).",
        "https://imgur.com/P7ex8lG.png",
    ),
]


class Warps(interactions.Extension):
    @interactions.slash_command(name="warps")
    async def warps(self, ctx: interactions.SlashContext):
        "Liste des meilleurs Warps BTE France"
        # Randomize warps and chunk in 10 warps (max embeds per message is 10)
        random.shuffle(WARPS)
        chunked_warps_list = [WARPS[i : i + 10] for i in range(0, len(WARPS), 10)]  # noqa

        # Create all embeds
        chunked_embeds = []
        for warp_list in chunked_warps_list:
            embed_list = [
                create_embed(
                    title=warp.name,
                    color=0xFFFFFF,
                    fields=[(f"/warp {warp.warp}", warp.description, False)],
                    image=warp.image,
                )
                for warp in warp_list
            ]
            chunked_embeds.append(embed_list)

        for i, embed_list in enumerate(chunked_embeds):
            await ctx.author.send(
                ":flag_fr: **Liste des meilleurs warps sur le serveur BTE France** :flag_fr:" if i == 0 else "",
                embeds=embed_list,
            )
        await ctx.send("Regarde tes MPs! :mailbox:")
