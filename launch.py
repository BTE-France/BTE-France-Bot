from utils.embed import create_info_embed
from argparse import ArgumentParser
from variables import server
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


@bot.command(name="load", description="Load all cogs or a specific one", scope=server, default_member_permissions=interactions.Permissions.ADMINISTRATOR)
@interactions.option("Cog to load", autocomplete=True)
async def load(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.load("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Loaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@load.autocomplete("cog")
async def load_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.command(name="unload", description="Unload all cogs or a specific one", scope=server, default_member_permissions=interactions.Permissions.ADMINISTRATOR)
@interactions.option("Cog to unload", autocomplete=True)
async def unload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.remove("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Unloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@unload.autocomplete("cog")
async def unload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.command(name="reload", description="Reload all cogs or a specific one", scope=server, default_member_permissions=interactions.Permissions.ADMINISTRATOR)
@interactions.option("Cog to reload", autocomplete=True)
async def reload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.reload("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Reloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@reload.autocomplete("cog")
async def reload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


def get_available_cogs() -> list[interactions.Choice]:
    return [interactions.Choice(name=cog, value=cog) for cog in cogs]


for cog in cogs:
    bot.load("cogs." + cog)
bot.start()
