import os

import deepl
import interactions

from utils.embed import create_embed, create_error_embed

# List of messages (to avoid same message been translated multiple times)
MESSAGES = {deepl.Language.FRENCH: [], deepl.Language.ENGLISH_BRITISH: []}
TEXT = {
    deepl.Language.FRENCH: [
        "🇫🇷 Traduction en français 🇫🇷",
        "Demandée par",
        "Le message a déjà été traduit!",
        "Le message n'a pas pu être traduit!",
        "Message original"
    ], deepl.Language.ENGLISH_BRITISH: [
        "🇬🇧 Translation to english 🇬🇧",
        "Requested by",
        "The message has already been translated!",
        "The message could not be translated!",
        "Original message"
    ]
}


class Translator(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client
        try:
            self.translator = deepl.Translator(os.environ["DEEPL_TOKEN"])
        except KeyError:
            print("Deepl API key has not been found!")

    @interactions.extension_message_command(name="Traduire en français")
    async def translate_french(self, ctx: interactions.CommandContext):
        await self.translate(ctx, deepl.Language.FRENCH)

    @interactions.extension_message_command(name="Translate to english")
    async def translate_english(self, ctx: interactions.CommandContext):
        await self.translate(ctx, deepl.Language.ENGLISH_BRITISH)

    async def translate(self, ctx: interactions.CommandContext, language: str):
        message: interactions.Message = ctx.target
        user: interactions.User = ctx.member.user

        if int(message.id) in MESSAGES[language]:
            return await ctx.send(embeds=create_error_embed(TEXT[language][2]), ephemeral=True)
        if not message.content:
            return await ctx.send(embeds=create_error_embed(TEXT[language][3]), ephemeral=True)

        MESSAGES[language].append(int(message.id))
        translated_text = self.translator.translate_text(message.content, target_lang=language).text

        embed = create_embed(
            title=TEXT[language][0],
            description=translated_text,
            color=0xA6A67A,
            footer_text=f"{TEXT[language][1]} @{user.username}#{user.discriminator}",
            footer_image=user.avatar_url
        )
        button = interactions.Button(style=interactions.ButtonStyle.LINK, label=TEXT[language][4], url=message.url)
        await ctx.send(embeds=embed, components=button)


def setup(client: interactions.Client):
    Translator(client)
