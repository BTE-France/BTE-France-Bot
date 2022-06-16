from utils.embed import create_embed, create_info_embed, create_error_embed
from variables import server
import interactions


# Dictionary of polls (resets when the bot is reloaded), one poll per user
polls = {}
numbers = [
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
end_poll = "🔴"


class Poll(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client

    @interactions.extension_command(
        name="poll",
        description="Setup a poll",
        scope=server,
        options=[
            interactions.Option(type=interactions.OptionType.SUB_COMMAND, name="create", description="Create the poll", options=[
                interactions.Option(type=interactions.OptionType.STRING, name="poll_name", description="Name of the poll", required=True)
            ]),
            interactions.Option(type=interactions.OptionType.SUB_COMMAND, name="add", description="Add a choice to the poll", options=[
                interactions.Option(type=interactions.OptionType.STRING, name="choice", description="Choice", required=True)
            ]),
            interactions.Option(type=interactions.OptionType.SUB_COMMAND, name="show", description="Show the poll")
        ]
    )
    async def poll(self, ctx: interactions.CommandContext, sub_command: str, poll_name=None, choice=None):
        user_id: int = int(ctx.author.id)
        if sub_command == "create":
            if polls.get(user_id) is not None:
                await ctx.send(embeds=create_info_embed(
                    f"Replaced the poll called `{polls[user_id]['title']}` with `{poll_name}`"
                ), ephemeral=True)
            else:
                await ctx.send(embeds=create_info_embed(
                    f"Created the poll called `{poll_name}`"
                ), ephemeral=True)
            polls[user_id] = {"title": poll_name, "choices": []}

        elif sub_command == "add":
            if polls.get(user_id) is None:
                await ctx.send(embeds=create_error_embed(
                    "You have not created any poll yet! Please create one using `/poll create <name>`"
                ), ephemeral=True)
            elif len(polls[user_id]["choices"]) >= len(numbers):
                await ctx.send(embeds=create_error_embed(
                    "You have reached the maximum number of choices!"
                ), ephemeral=True)
            else:
                await ctx.send(embeds=create_info_embed(
                    f"Added `{choice}` as a choice to the poll `{polls[user_id]['title']}`"
                ), ephemeral=True)
                polls[user_id]["choices"].append(choice)

        elif sub_command == "show":
            if polls.get(user_id) is None:
                await ctx.send(embeds=create_error_embed(
                    "You have not created any poll yet! Please create one using `/poll create <name>`"
                ), ephemeral=True)
            elif len(polls[user_id]["choices"]) < 2:
                await ctx.send(embeds=create_error_embed(
                    f"Your poll is missing at least {2 - len(polls[user_id]['choices'])} choice(s)! Please create them using `/poll add <choice>`"
                ), ephemeral=True)
            else:
                polls[user_id]["votes"] = {}
                menu = interactions.SelectMenu(
                    custom_id=str(user_id),
                    options=[interactions.SelectOption(
                        label=choice, value=str(i),
                        emoji={"name": numbers[i]}
                    ) for i, choice in enumerate(polls[user_id]["choices"])],
                    placeholder=polls[user_id]["title"]
                )

                channel = interactions.Channel(**await self.client._http.get_channel(ctx.channel_id), _client=self.client._http)
                message: interactions.Message = await channel.send("*Generating poll...*", components=menu)
                polls[user_id]["message"] = message
                await self.send_poll(user_id)
                await ctx.send(embeds=create_info_embed(
                    f"Your poll named `{polls[user_id]['title']}` has successfully been created. React to it with {end_poll} to close the poll!"
                ), ephemeral=True)

                # Register menu's callbacks
                self.client.component(menu)(self.on_poll_select)

    async def on_poll_select(self, ctx: interactions.ComponentContext, options: list):
        option: int = int(options[0])  # This poll will only have one selectable option possible
        voter_id: int = int(ctx.author.id)

        # Find correct poll_id
        poll_id = None
        for _poll_id, poll in polls.items():
            if poll.get("message") is not None and int(poll["message"].id) == int(ctx.message.id):
                poll_id = _poll_id
                break
        if not poll_id:
            await ctx.send(embeds=create_error_embed(
                "Unable to find this poll. Is it still active?"
            ), ephemeral=True)
            return

        polls[poll_id]["votes"][voter_id] = option
        await ctx.send(embeds=create_info_embed(
            f"You selected the option {numbers[option]} `{polls[poll_id]['choices'][option]}`"
        ), ephemeral=True)
        await self.send_poll(poll_id)

    async def send_poll(self, poll_id: int) -> interactions.Message:
        # Create list of percentages for each choice
        votes = [0 for _ in range(len(polls[poll_id]["choices"]))]
        for voter_id, option in polls[poll_id]["votes"].items():
            votes[option] += 1

        num_votes = len(polls[poll_id]["votes"])
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
            f"{numbers[i]} {choice}",
            f"{bars[i]} **{round(percentages[i] * 100)}%** ({votes[i]})",
            False
        ) for i, choice in enumerate(polls[poll_id]["choices"])]
        embed: interactions.Embed = create_embed(
            title=f"Sondage: {polls[poll_id]['title']}",
            fields=fields
        )

        message: interactions.Message = polls[poll_id]["message"]
        await message.edit("", embeds=embed)

    @interactions.extension_listener()
    async def on_message_reaction_add(self, message_reaction: interactions.MessageReaction):
        if message_reaction.emoji.name != end_poll:
            return

        # Find correct poll_id
        poll_id = None
        for _poll_id, poll in polls.items():
            if poll.get("message") is not None and int(poll["message"].id) == int(message_reaction.message_id):
                poll_id = _poll_id
                break
        if not poll_id:
            return

        if poll_id != int(message_reaction.member.id):
            return

        message = interactions.Message(**await self.client._http.get_message(message_reaction.channel_id, message_reaction.message_id), _client=self.client._http)
        embed: interactions.Embed = message.embeds[0]
        embed.set_footer(text="Sondage terminé")
        await message.edit("", embeds=embed, components=[])
        await message.remove_reaction_from(end_poll, poll_id)
        del polls[poll_id]


def setup(client: interactions.Client):
    Poll(client)
