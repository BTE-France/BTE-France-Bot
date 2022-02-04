from utils.embed import create_info_embed
from argparse import ArgumentParser
from variables import server
import interactions
import os


parser = ArgumentParser()
parser.add_argument('-s', '--sync', action='store_true')
args = parser.parse_args()
disable_sync = False if args.sync else True

bot = interactions.Client(token=os.environ["DISCORD_TOKEN"], disable_sync=disable_sync)

# Define all cogs
cogs = []
for filename in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs2")):
    if filename.endswith(".py"):
        cogs.append(filename.replace(".py", ""))


@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.command(name="load", description="Load all cogs or a specific one", scope=server, options=[
    interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to load", required=False, autocomplete=True)
])
async def load(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.load("cogs2." + cog)
    await ctx.send(embeds=create_info_embed("**Loaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.command(name="unload", description="Unload all cogs or a specific one", scope=server, options=[
    interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to unload", required=False, autocomplete=True)
])
async def unload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.remove("cogs2." + cog)
    await ctx.send(embeds=create_info_embed("**Unloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.command(name="reload", description="Reload all cogs or a specific one", scope=server, options=[
    interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to reload", required=False, autocomplete=True)
])
async def reload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.reload("cogs2." + cog)
    await ctx.send(embeds=create_info_embed("**Reloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.autocomplete("cog", command=bot._http.cache.interactions.get("load").id)
async def load_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.autocomplete("cog", command=bot._http.cache.interactions.get("unload").id)
async def unload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.autocomplete("cog", command=bot._http.cache.interactions.get("reload").id)
async def reload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


def get_available_cogs() -> list[interactions.Choice]:
    return [interactions.Choice(name=cog, value=cog) for cog in cogs]


try:
    for cog in cogs:
        bot.load("cogs2." + cog)
    bot.start()
except KeyboardInterrupt:
    print("Shutting down bot...")
