from dataclasses import dataclass, field

import interactions

from utils import create_embed, create_error_embed, create_info_embed


@dataclass
class Poll:
    title: str
    options: list[str]
    owner_id: int
    votes: dict[int, int] = field(default_factory=dict)


POLLS: dict[int, Poll] = {}
NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
END_POLL_EMOJI = "🔴"
POLL_MODAL = interactions.Modal(
    interactions.InputText(
        style=interactions.TextStyles.SHORT,
        label="Titre du sondage",
        custom_id="title",
        max_length=150,
    ),
    interactions.InputText(
        style=interactions.TextStyles.PARAGRAPH,
        label="Options du sondage (min: 2, max: 10)",
        custom_id="options",
        placeholder="Une option par ligne",
    ),
    title="Création d'un sondage",
    custom_id="modal_poll",
)


class Polls(interactions.Extension):
    @interactions.slash_command(name="poll")
    async def poll(self, ctx: interactions.SlashContext):
        "Créer un sondage"
        await ctx.send_modal(POLL_MODAL)

        modal_ctx = await self.bot.wait_for_modal(POLL_MODAL)
        title = modal_ctx.responses["title"]
        options = [
            option.strip() for option in modal_ctx.responses["options"].split("\n") if option.strip()
        ]  # Remove empty options
        num = len(options)

        if num > len(NUMBERS):
            await modal_ctx.send(
                embeds=create_error_embed(f"Le sondage a trop d'options ({num}, maximum: {len(NUMBERS)})."),
                ephemeral=True,
            )
        elif num < 2:
            await modal_ctx.send(
                embeds=create_error_embed(f"Le sondage n'a pas assez d'options ({num}, minimum: 2)."),
                ephemeral=True,
            )
        else:
            poll = Poll(title=title, options=options, owner_id=int(modal_ctx.author.id))
            message = await modal_ctx.send("_Chargement..._")
            POLLS[int(message.id)] = poll
            menu = interactions.StringSelectMenu(
                *[
                    interactions.StringSelectOption(label=choice, value=str(i), emoji=NUMBERS[i])
                    for i, choice in enumerate(poll.options)
                ],
                custom_id="select_poll",
                placeholder=poll.title,
            )
            await message.edit(content="", embeds=self.create_embed(poll), components=menu)
            await modal_ctx.send(
                embeds=create_info_embed(
                    f"Le sondage nommé `{poll.title}` a été créé. Réagis avec {END_POLL_EMOJI} pour le fermer!"
                ),
                ephemeral=True,
            )

    @interactions.component_callback("select_poll")
    async def on_poll_select(self, ctx: interactions.ComponentContext):
        option = int(ctx.values[0])  # This poll will only have one selectable option possible
        voter_id = int(ctx.author.id)

        poll = POLLS.get(int(ctx.message.id))
        if not poll:  # Close poll if not active anymore
            await self.close_poll(ctx.message)
        else:
            poll.votes[voter_id] = option
            await ctx.message.edit(embeds=self.create_embed(poll), components=ctx.message.components)
            await ctx.send(
                embeds=create_info_embed(f"Vous avez sélectionné l'option {NUMBERS[option]} `{poll.options[option]}`"),
                ephemeral=True,
            )

    def create_embed(self, poll: Poll) -> interactions.Embed:
        # Create list of percentages for each choice
        votes = [0 for _ in range(len(poll.options))]
        for option in poll.votes.values():
            votes[option] += 1

        num_votes = len(poll.votes)
        if num_votes == 0:
            percentages = [0 for _ in range(len(votes))]
        else:
            percentages = [vote / num_votes for vote in votes]

        # Create a bar to represent the percentage visually
        bars = []
        for percentage in percentages:
            num: int = round(percentage * 20)
            bars.append("█" * num)

        # Create message to send and return
        fields = [
            (
                f"{NUMBERS[i]} {choice}",
                f"{bars[i]} **{round(percentages[i] * 100)}%** ({votes[i]})",
                False,
            )
            for i, choice in enumerate(poll.options)
        ]
        embed: interactions.Embed = create_embed(title=poll.title, fields=fields)

        return embed

    async def close_poll(self, message: interactions.Message):
        embed = message.embeds[0]
        embed.set_footer(text="Sondage terminé")
        await message.edit(embeds=embed, components=[])

    @interactions.listen(interactions.events.MessageReactionAdd)
    async def on_message_reaction_add(self, message_reaction: interactions.events.MessageReactionAdd):
        if message_reaction.emoji.name != END_POLL_EMOJI:
            return

        poll_id = int(message_reaction.message.id)
        poll = POLLS.get(poll_id)
        if not poll:
            return

        if poll.owner_id != int(message_reaction.author.id):
            return

        await self.close_poll(message_reaction.message)
        await message_reaction.message.remove_reaction(END_POLL_EMOJI, message_reaction.author)
        del POLLS[poll_id]
