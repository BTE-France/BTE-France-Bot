from utils.embed import create_embed, create_info_embed, create_error_embed
from variables import server
import interactions


# Dictionary of polls (resets when the bot is reloaded), one poll per user
POLLS = {}
NUMBERS = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
]
END_POLL_EMOJI = "🔴"


class Poll(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="poll", description="Setup a poll", scope=server)
    async def poll(self, ctx: interactions.CommandContext):
        pass

    @poll.subcommand(name="create", description="Create the poll")
    @interactions.option("Name of the poll")
    async def create_poll(self, ctx: interactions.CommandContext, poll_name: str):
        user_id = int(ctx.author.id)

        if POLLS.get(user_id) is not None:
            await ctx.send(embeds=create_info_embed(
                f"Replaced the poll called `{POLLS[user_id]['title']}` with `{poll_name}`"
            ), ephemeral=True)
        else:
            await ctx.send(embeds=create_info_embed(
                f"Created the poll called `{poll_name}`"
            ), ephemeral=True)
        POLLS[user_id] = {"title": poll_name, "choices": []}

    @poll.subcommand(name="add", description="Add a choice to the poll")
    @interactions.option("Choice")
    async def add_poll(self, ctx: interactions.CommandContext, choice: str):
        user_id = int(ctx.author.id)

        if POLLS.get(user_id) is None:
            await ctx.send(embeds=create_error_embed(
                "You have not created any poll yet! Please create one using `/poll create <name>`"
            ), ephemeral=True)
        elif len(POLLS[user_id]["choices"]) >= len(NUMBERS):
            await ctx.send(embeds=create_error_embed(
                "You have reached the maximum number of choices!"
            ), ephemeral=True)
        else:
            await ctx.send(embeds=create_info_embed(
                f"Added `{choice}` as a choice to the poll `{POLLS[user_id]['title']}`"
            ), ephemeral=True)
            POLLS[user_id]["choices"].append(choice)

    @poll.subcommand(name="show", description="Show the poll")
    async def show_poll(self, ctx: interactions.CommandContext):
        user_id = int(ctx.author.id)

        if POLLS.get(user_id) is None:
            await ctx.send(embeds=create_error_embed(
                "You have not created any poll yet! Please create one using `/poll create <name>`"
            ), ephemeral=True)
        elif len(POLLS[user_id]["choices"]) < 2:
            await ctx.send(embeds=create_error_embed(
                f"Your poll is missing at least {2 - len(POLLS[user_id]['choices'])} choice(s)! Please create them using `/poll add <choice>`"
            ), ephemeral=True)
        else:
            POLLS[user_id]["votes"] = {}
            menu = interactions.SelectMenu(
                custom_id=str(user_id),
                options=[interactions.SelectOption(
                    label=choice, value=str(i),
                    emoji=interactions.Emoji(name=NUMBERS[i])
                ) for i, choice in enumerate(POLLS[user_id]["choices"])],
                placeholder=POLLS[user_id]["title"]
            )

            channel = await ctx.get_channel()
            message: interactions.Message = await channel.send(embeds=await self.create_embed(user_id), components=menu)
            POLLS[user_id]["message"] = message
            await ctx.send(embeds=create_info_embed(
                f"Your poll named `{POLLS[user_id]['title']}` has successfully been created. React to it with {END_POLL_EMOJI} to close the poll!"
            ), ephemeral=True)

            # Register menu's callbacks
            self.client.component(menu)(self.on_poll_select)

    async def on_poll_select(self, ctx: interactions.ComponentContext, options: list):
        option = int(options[0])  # This poll will only have one selectable option possible
        voter_id = int(ctx.author.id)

        # Find correct poll_id
        poll_id = None
        for _poll_id, poll in POLLS.items():
            if poll.get("message") is not None and int(poll["message"].id) == int(ctx.message.id):
                poll_id = _poll_id
                break
        if not poll_id:
            await ctx.send(embeds=create_error_embed(
                "Unable to find this poll. Is it still active?"
            ), ephemeral=True)
            return

        POLLS[poll_id]["votes"][voter_id] = option
        await ctx.message.edit(embeds=await self.create_embed(poll_id), components=ctx.message.components)
        await ctx.send(embeds=create_info_embed(
            f"You selected the option {NUMBERS[option]} `{POLLS[poll_id]['choices'][option]}`"
        ), ephemeral=True)

    async def create_embed(self, poll_id: int) -> interactions.Embed:
        # Create list of percentages for each choice
        votes = [0 for _ in range(len(POLLS[poll_id]["choices"]))]
        for voter_id, option in POLLS[poll_id]["votes"].items():
            votes[option] += 1

        num_votes = len(POLLS[poll_id]["votes"])
        if num_votes == 0:
            percentages = [0 for _ in range(len(votes))]
        else:
            percentages = [vote / num_votes for vote in votes]

        # Create a bar to represent the percentage visually
        bars = []
        for percentage in percentages:
            num: int = round(percentage * 10)
            bars.append("█" * num)

        # Create message to send and return
        fields = [(
            f"{NUMBERS[i]} {choice}",
            f"{bars[i]} **{round(percentages[i] * 100)}%** ({votes[i]})",
            False
        ) for i, choice in enumerate(POLLS[poll_id]["choices"])]
        embed: interactions.Embed = create_embed(
            title=f"Sondage: {POLLS[poll_id]['title']}",
            fields=fields
        )

        return embed

    @interactions.extension_listener()
    async def on_message_reaction_add(self, message_reaction: interactions.MessageReaction):
        if message_reaction.emoji.name != END_POLL_EMOJI:
            return

        # Find correct poll_id
        poll_id = None
        for _poll_id, poll in POLLS.items():
            if poll.get("message") is not None and int(poll["message"].id) == int(message_reaction.message_id):
                poll_id = _poll_id
                break
        if not poll_id:
            return

        if poll_id != int(message_reaction.member.id):
            return

        message = await interactions.get(self.client, interactions.Message, object_id=message_reaction.message_id, parent_id=message_reaction.channel_id)
        embed = message.embeds[0]
        embed.set_footer(text="Sondage terminé")
        await message.edit("", embeds=embed, components=[])
        await message.remove_reaction_from(END_POLL_EMOJI, poll_id)
        del POLLS[poll_id]


def setup(client: interactions.Client):
    Poll(client)
