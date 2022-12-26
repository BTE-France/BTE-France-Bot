import interactions

import variables


def create_embed(
    title: str = "",
    description: str = "",
    fields: list[tuple[str, str, bool]] = [],
    color: int = 0x0000FF,
    footer_text: str = None,
    footer_image: str = None,
    include_thumbnail: bool = False,
    image: str = None,
    video: str = None
) -> interactions.Embed:
    embed = interactions.Embed(
        title=title,
        description=description,
        color=color
    )
    if image:
        embed.set_image(url=image)
    if video:
        embed.set_video(url=video)
    if include_thumbnail:
        embed.set_thumbnail(url=variables.BTE_FRANCE_ICON)
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_image if footer_image else variables.BTE_FRANCE_ICON)
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])
    return embed


def create_error_embed(text: str) -> interactions.Embed:
    return create_embed(
        description=text,
        color=0xFF0000
    )


def create_info_embed(text: str) -> interactions.Embed:
    return create_embed(
        description=text,
        color=0x787774
    )
