import logging
import os
from pathlib import Path

import interactions

logging.basicConfig(format="[%(levelname)s] %(message)s")

bot = interactions.Client(
    activity=interactions.Activity(
        type=interactions.ActivityType.WATCHING, name="/help"
    ),
    intents=interactions.Intents.ALL,
)

for filename in os.listdir(Path(__file__).parent / "cogs"):
    if filename.endswith(".py"):
        bot.load_extension("cogs." + filename.replace(".py", ""))


@interactions.listen(interactions.events.Startup)
async def on_start():
    print("Bot is ready!")


bot.start(os.environ["DISCORD_TOKEN"])
