import discord


class HelpOption(discord.SelectOption):
    def __init__(self, id, command, description):
        super().__init__(value=id, label=command, description=description)


class HelpMenu(discord.ui.Select):
    def __init__(self, options, max_values):
        super().__init__(placeholder='명령어를 선택해주세요', options=options, max_values=max_values)

    async def callback(self, interaction: discord.Interaction):
        command_id = self.values[0]
        if command_id == 'division':
            file = discord.File('static/help/division-help.png')
            await interaction.respond(file=file, ephemeral=True)

        elif command_id == 'song':
            file = discord.File('static/help/song-help.png')
            await interaction.respond(file=file, ephemeral=True)


class HelpView(discord.ui.View):
    def __init__(self, select_menu):
        super().__init__()
        self.add_item(select_menu)


def bot_help():
    options = [
        HelpOption(id='division', command='분배봇', description='분배 항목을 관리하는 봇'),
        HelpOption(id='song', command='노래봇', description='노래를 재생하는 봇')
    ]

    menu = HelpMenu(options=options, max_values=1)
    view = HelpView(menu)

    return view
