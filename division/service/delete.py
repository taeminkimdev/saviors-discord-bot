import discord
from database import Database
from division.service.distribution_status import update_distribut_status
from item_db import get_emoji
import logging

MAX_VALUES = 5


class DeleteOption(discord.SelectOption):
    def __init__(self, id, item, members):
        emoji = get_emoji(item)
        super().__init__(value=id, label=item, description=members, emoji=emoji)


class DeleteMenu(discord.ui.Select):
    def __init__(self, options, max_values):
        super().__init__(placeholder='❌ 삭제시킬 분배 목록을 선택해주세요', options=options, max_values=max_values)

    async def callback(self, interaction: discord.Interaction):
        saviors_logger = logging.getLogger('saviors')

        division_ids = [int(value) for value in self.values]
        with Database() as db:
            db.delete_division(division_ids)
        embed = discord.Embed(title='삭제 완료', color=0xFF0000)

        saviors_logger.info(msg=f'[분배 삭제] - {interaction.user.id}/{interaction.user.name} / division_ids : {division_ids}')

        await update_distribut_status(interaction.user.id, interaction.client)
        await interaction.respond(embed=embed, ephemeral=True, delete_after=10)


class DeleteView(discord.ui.View):
    def __init__(self, select_menu):
        super().__init__()
        self.add_item(select_menu)


def delete(user_id, member_ids):
    with Database() as db:
        divisions = db.find_divisions_by_member_ids(member_ids)

    options = []
    for i, division in enumerate(divisions):
        if i >= 25:
            break
        option = DeleteOption(id=str(division.id), item=division.item, members=division.get_members(user_id))
        options.append(option)

    if len(options) == 0:
        return None

    menu = DeleteMenu(options=options, max_values=len(options) if len(options) < MAX_VALUES else MAX_VALUES)
    view = DeleteView(menu)

    return view
