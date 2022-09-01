from argparse import ArgumentParser
import interactions
import logging
import os

logging.basicConfig(format='[%(levelname)s] %(message)s')

parser = ArgumentParser()
parser.add_argument('-s', '--sync', action='store_true', help="synchronize slash commands on the Discord API")
args = parser.parse_args()
disable_sync = False if args.sync else True

bot = interactions.Client(
    token=os.environ["DISCORD_TOKEN"],
    disable_sync=disable_sync,
    presence=interactions.ClientPresence(
        status=interactions.StatusType.ONLINE,
        activities=[interactions.PresenceActivity(
            type=interactions.PresenceActivityType.WATCHING,
            name="/help"
        )]
    ),
    intents=interactions.Intents.ALL
)
bot.load('interactions.ext.files')

# Define all cogs
cogs = []
for filename in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs")):
    if filename.endswith(".py"):
        cogs.append(filename.replace(".py", ""))


@bot.event
async def on_start():
    print("Bot is ready!")


for cog in cogs:
    bot.load("cogs." + cog)
bot.start()
