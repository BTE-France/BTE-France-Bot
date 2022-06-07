from utils.embed import create_info_embed
from argparse import ArgumentParser
from variables import server
import interactions
import os


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
    )
)
bot.load('interactions.ext.files')

# Define all cogs
cogs = []
for filename in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs")):
    if filename.endswith(".py"):
        cogs.append(filename.replace(".py", ""))


@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.command(
    name="load",
    description="Load all cogs or a specific one",
    scope=server,
    options=[
        interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to load", required=False, autocomplete=True)
    ],
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def load(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.load("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Loaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.command(
    name="unload",
    description="Unload all cogs or a specific one",
    scope=server,
    options=[
        interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to unload", required=False, autocomplete=True)
    ],
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def unload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.remove("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Unloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.command(
    name="reload",
    description="Reload all cogs or a specific one",
    scope=server,
    options=[
        interactions.Option(type=interactions.OptionType.STRING, name="cog", description="Cog to reload", required=False, autocomplete=True)
    ],
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def reload(ctx: interactions.CommandContext, cog: str = None):
    cog_list = [cog] if cog else cogs
    for cog in cog_list:
        bot.reload("cogs." + cog)
    await ctx.send(embeds=create_info_embed("**Reloaded:**\n" + "\n".join([f"- {cog_name}" for cog_name in cog_list])), ephemeral=True)


@bot.autocomplete("load", "cog")
async def load_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.autocomplete("unload", "cog")
async def unload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


@bot.autocomplete("reload", "cog")
async def reload_autocomplete(ctx: interactions.CommandContext, user_input: str = ""):
    await ctx.populate(get_available_cogs())


def get_available_cogs() -> list[interactions.Choice]:
    return [interactions.Choice(name=cog, value=cog) for cog in cogs]


try:
    for cog in cogs:
        bot.load("cogs." + cog)
    bot.start()
except KeyboardInterrupt:
    print("Shutting down bot...")
