from utils.embed import create_embed
import interactions
import deepl
import os

LANGUAGES = {
    "🇫🇷": deepl.Language.FRENCH,
    "🇩🇪": deepl.Language.GERMAN,
    "🇬🇧": deepl.Language.ENGLISH_BRITISH,
    "🇺🇸": deepl.Language.ENGLISH_AMERICAN,
    "🇪🇸": deepl.Language.SPANISH,
    "🇮🇹": deepl.Language.ITALIAN,
    "🇯🇵": deepl.Language.JAPANESE,
    "🇳🇱": deepl.Language.DUTCH,
    "🇧🇷": deepl.Language.PORTUGUESE_BRAZILIAN,
    "🇵🇹": deepl.Language.PORTUGUESE_EUROPEAN,
    "🇷🇺": deepl.Language.RUSSIAN,
    "🇨🇳": deepl.Language.CHINESE,
}


class Translator(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client
        try:
            self.translator = deepl.Translator(os.environ["DEEPL_TOKEN"])
        except KeyError:
            print("Deepl API key has not been found!")

    @interactions.extension_listener()
    async def on_message_reaction_add(self, message_reaction: interactions.MessageReaction):
        language = LANGUAGES.get(message_reaction.emoji.name)
        if not language:
            return

        count = len(await self.client._http.get_reactions_of_emoji(
            message_reaction.channel_id,
            message_reaction.message_id,
            message_reaction.emoji.name
        ))
        if count > 1:
            return

        message = await interactions.get(self.client, interactions.Message, object_id=message_reaction.message_id, parent_id=message_reaction.channel_id)
        user = await interactions.get(self.client, interactions.User, object_id=message_reaction.user_id)

        if not message.content:
            return
        translated_text = self.translator.translate_text(message.content, target_lang=language).text

        embed = create_embed(
            title=f"Translation to {message_reaction.emoji.name}",
            description=translated_text,
            color=0xA6A67A,
            footer_text=f"Requested by @{user.username}#{user.discriminator}",
            footer_image=user.avatar_url
        )
        await message.reply(embeds=embed)


def setup(client: interactions.Client):
    Translator(client)
