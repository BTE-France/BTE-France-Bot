import os

import deepl
import interactions

from utils import create_embed, create_error_embed, log

# List of messages (to avoid same message been translated multiple times)
MESSAGES = {deepl.Language.FRENCH: [], deepl.Language.ENGLISH_BRITISH: []}
TEXT = {
    deepl.Language.FRENCH: [
        "🇫🇷 Traduction en français 🇫🇷",
        "Demandée par",
        "Le message a déjà été traduit!",
        "Le message n'a pas pu être traduit!",
        "Message original",
    ],
    deepl.Language.ENGLISH_BRITISH: [
        "🇬🇧 Translation to english 🇬🇧",
        "Requested by",
        "The message has already been translated!",
        "The message could not be translated!",
        "Original message",
    ],
}


class Translator(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        if auth_key := os.getenv("DEEPL_TOKEN"):
            self.translator = deepl.Translator(auth_key)
        else:
            log("No DEEPL_TOKEN variable found!")

    @interactions.context_menu(
        name="Traduire en français", context_type=interactions.CommandType.MESSAGE
    )
    async def translate_french(self, ctx: interactions.ContextMenuContext):
        await self.translate(ctx, deepl.Language.FRENCH)

    @interactions.context_menu(
        name="Translate to english", context_type=interactions.CommandType.MESSAGE
    )
    async def translate_english(self, ctx: interactions.ContextMenuContext):
        await self.translate(ctx, deepl.Language.ENGLISH_BRITISH)

    async def translate(self, ctx: interactions.ContextMenuContext, language: str):
        if not hasattr(self, "translator"):
            return

        message: interactions.Message = ctx.target

        if int(message.id) in MESSAGES[language]:
            return await ctx.send(
                embeds=create_error_embed(TEXT[language][2]), ephemeral=True
            )
        if not message.content:
            return await ctx.send(
                embeds=create_error_embed(TEXT[language][3]), ephemeral=True
            )

        MESSAGES[language].append(int(message.id))
        translated_text = self.translator.translate_text(
            message.content, target_lang=language
        ).text

        embed = create_embed(
            title=TEXT[language][0],
            description=translated_text,
            color=0xA6A67A,
            footer_text=f"{TEXT[language][1]} {ctx.author.tag}",
            footer_image=ctx.member.avatar.url,
        )
        button = interactions.Button(
            style=interactions.ButtonStyle.LINK,
            label=TEXT[language][4],
            url=message.jump_url,
        )
        await ctx.send(embeds=embed, components=button)
