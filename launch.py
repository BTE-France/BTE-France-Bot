import interactions
import logging
import os

logging.basicConfig(format='[%(levelname)s] %(message)s')

bot = interactions.Client(
    token=os.environ["DISCORD_TOKEN"],
    presence=interactions.ClientPresence(
        status=interactions.StatusType.ONLINE,
        activities=[interactions.PresenceActivity(
            type=interactions.PresenceActivityType.WATCHING,
            name="/help"
        )]
    ),
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.GUILD_MESSAGE_CONTENT
)

# Define all cogs
cogs = []
for filename in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs")):
    if filename.endswith(".py"):
        cogs.append(filename.replace(".py", ""))


@bot.event
async def on_start():
    print("Bot is ready!")


[bot.load("cogs." + cog) for cog in cogs]
bot.start()
