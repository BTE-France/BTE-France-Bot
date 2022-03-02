import interactions
import variables


def create_embed(title: str = None, description: str = None, fields: list[interactions.EmbedField] = [], color: int = 0x0000FF, footer_text: str = None, footer_image: str = None, include_thumbnail: bool = True, image: str = None, video: str = None) -> interactions.Embed:
    footer = interactions.EmbedFooter(text=footer_text, icon_url=footer_image if footer_image else variables.bte_france_icon) if footer_text else None
    return interactions.Embed(
        title=title,
        description=description,
        color=color,
        footer=footer,
        thumbnail=interactions.EmbedImageStruct(url=variables.bte_france_icon)._json if include_thumbnail else None,
        image=interactions.EmbedImageStruct(url=image)._json if image else None,
        video=interactions.EmbedImageStruct(url=video)._json if video else None,
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
