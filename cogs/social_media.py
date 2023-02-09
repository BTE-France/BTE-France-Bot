from dataclasses import dataclass

import interactions

from utils.embed import create_embed


@dataclass
class Social:
    id: str
    name: str
    link: str


SOCIALS = [
    Social("youtube", "YouTube", "https://www.youtube.com/c/BTEFrance"),
    Social("twitter", "Twitter", "https://twitter.com/BTE_France"),
    Social("instagram", "Instagram", "https://www.instagram.com/bte_france"),
    Social("facebook", "Facebook", "https://www.facebook.com/Build-The-Earth-France-113380800556340"),
    Social("reddit", "Reddit", "https://www.reddit.com/user/BTE_France"),
    Social("planet-minecraft", "PlanetMinecraft", "https://www.planetminecraft.com/member/bte-france"),
    Social("tiktok", "Tiktok", "https://www.tiktok.com/@btefrance")
]


class SocialMedia(interactions.Extension):
    @interactions.slash_command(name="social")
    @interactions.slash_option("media", "Nom du réseau", choices=[
        interactions.SlashCommandChoice(name=social.id, value=social.id) for social in SOCIALS
    ], opt_type=interactions.OptionType.STRING, required=True)
    async def social(self, ctx: interactions.SlashContext, media: str):
        "Liens réseaux sociaux"
        for social in SOCIALS:
            if social.id == media:
                await ctx.send(embeds=create_embed(
                    title=f"{social.name} de BTE: France",
                    description=social.link,
                    include_thumbnail=True
                ))
                return
