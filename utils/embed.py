import interactions
import variables


def create_embed(title: str = None, description: str = None, fields: list[interactions.EmbedField] = [], color: int = 0x0000FF, footer: str = None, include_thumbnail: bool = True) -> interactions.Embed:
    return interactions.Embed(
        title=title,
        description=description,
        color=color,
        footer=interactions.EmbedFooter(text=footer, icon_url=variables.bte_france_icon),
        thumbnail=interactions.EmbedImageStruct(url=variables.bte_france_icon)._json if include_thumbnail else None,
        fields=fields
    )


def create_error_embed(text: str) -> interactions.Embed:
    return create_embed(
        description=text,
        color=0xFF0000,
        include_thumbnail=False
    )


def create_info_embed(text: str) -> interactions.Embed:
    return create_embed(
        description=text,
        color=0x787774,
        include_thumbnail=False
    )
