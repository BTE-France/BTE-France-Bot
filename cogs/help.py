import interactions
from interactions.ext.paginators import Paginator

from utils import create_embed


class Help(interactions.Extension):
    @interactions.listen(interactions.events.Startup)
    async def on_start(self):
        # lookup all commands (and subcommands) using the interaction tree
        self.help_commands: list[interactions.InteractionCommand] = []
        for interaction_command in self.bot.interaction_tree.values():
            self.create_commands_recursive(interaction_command)

    @interactions.slash_command(name="help")
    async def help(self, ctx: interactions.SlashContext):
        "Montre toutes les commandes du bot"
        fields_list = []

        for command in self.help_commands:
            if command.is_enabled(ctx):
                if isinstance(command, interactions.SlashCommand):
                    name = str(command.name)
                    if command.group_name:
                        name += " " + str(command.group_name)
                    if command.sub_cmd_name:
                        name += " " + str(command.sub_cmd_name)

                    desc = str(command.description)
                    if command.group_name:
                        desc = str(command.group_description)
                    if command.sub_cmd_name:
                        desc = str(command.sub_cmd_description)

                    fields_list.append(interactions.EmbedField(name=f"/{name}", value=desc))
                else:
                    fields_list.append(
                        interactions.EmbedField(name=f"{command.name}", value="Clic droit sur un utilisateur/message")
                    )

        # divide embed fields into lists of maximum N size
        chunked_fields_list = [fields_list[i : i + 10] for i in range(0, len(fields_list), 10)]  # noqa
        embeds = []
        for i, fields_list in enumerate(chunked_fields_list):
            embed = create_embed(
                title=f"Help! Page {i+1}/{len(chunked_fields_list)}",
                color=0xFF0000,
                footer_text="Contacte @maxyolo01 si tu trouves des bugs / suggestions!",
                include_thumbnail=True,
            )
            embed.add_fields(*fields_list)
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.send(ctx)

    def create_commands_recursive(self, interaction_command):
        if isinstance(interaction_command, interactions.InteractionCommand):
            self.help_commands.append(interaction_command)
        elif isinstance(interaction_command, dict):
            for interaction_subcommand in interaction_command.values():
                self.create_commands_recursive(interaction_subcommand)
        else:
            raise Exception(f"Unknown interaction command type in /help: {type(interaction_command)}")
