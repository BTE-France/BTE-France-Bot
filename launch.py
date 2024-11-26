import logging
import os
from pathlib import Path

import interactions
from dotenv import load_dotenv

from utils import get_env, log

load_dotenv()
logging.basicConfig(format="[%(levelname)s] %(message)s")

bot = interactions.Client(
    activity=interactions.Activity(type=interactions.ActivityType.WATCHING, name="/help"),
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.MESSAGE_CONTENT,
)

for filename in os.listdir(Path(__file__).parent / "cogs"):
    if filename.endswith(".py"):
        bot.load_extension("cogs." + filename.replace(".py", ""))


@interactions.listen(interactions.events.Startup)
async def on_start():
    log("Bot is ready!")


bot.start(get_env("DISCORD_TOKEN"))
