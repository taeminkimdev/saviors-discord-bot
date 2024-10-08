import discord
from division.database import Database
from division.service.distribution_status import update_distribut_status
from division.item_db import get_emoji
import logging

MAX_VALUES = 5


class PartitionOption(discord.SelectOption):
    def __init__(self, id, nickname):
        super().__init__(value=id, label=nickname)


class PartitionMenu(discord.ui.Select):
    def __init__(self, options, max_values):
        super().__init__(placeholder="분배가 완료된 멤버를 선택해주세요", options=options, max_values=max_values)

    async def callback(self, interaction: discord.Interaction):
        division_ids, member_id = self.values[0].split('/')
        division_ids = list(map(int, division_ids.split(',')))

        member_ids = [int(value.split('/')[1]) for value in self.values]
        with Database() as db:
            divided = db.update_partition_complete(division_ids, member_ids)

        saviors_logger = logging.getLogger('saviors')
        saviors_logger.info(msg=f'[분배 완료] - {interaction.user.id}/{interaction.user.name} / division_ids : {division_ids} / member_ids : {member_ids}')

        if len(divided) > 0:
            embed = discord.Embed(title='분배 완료', color=0x8fce00)
            with Database() as db:
                divisions = db.find_divisions_by_ids(divided)

            for i, division in enumerate(divisions):
                emoji = get_emoji(division.item)
                embed.add_field(name=f'{emoji} {division.item} - {division.created_at.strftime("%m/%d")}',
                                value=division.get_members(interaction.user.id), inline=False)

            await interaction.respond(embed=embed)

        if len(divided) != len(division_ids):
            embed = discord.Embed(title='부분 분배 완료', color=0x8fce00)
            with Database() as db:
                divisions = db.find_divisions_by_ids(division_ids)

            for i, division in enumerate(divisions):
                emoji = get_emoji(division.item)
                embed.add_field(name=f'{emoji} {division.item} - {division.created_at.strftime("%m/%d")}',
                                value=division.get_members(interaction.user.id), inline=False)

            await interaction.respond(embed=embed, ephemeral=True, delete_after=10)

        await update_distribut_status(interaction.user.id, interaction.client)


class PartitionView(discord.ui.View):
    def __init__(self, select_menu):
        super().__init__()
        self.add_item(select_menu)


def complete_partition(division_ids):
    with Database() as db:
        members = db.find_members_by_division_ids(division_ids)

    options = []
    for member_id, nickname in members:
        option = PartitionOption(id=str(f'{",".join([str(division_id) for division_id in division_ids])}/{member_id}'), nickname=nickname)
        options.append(option)

    menu = PartitionMenu(options=options, max_values=len(options))
    view = PartitionView(menu)

    return view


class CompleteOption(discord.SelectOption):
    def __init__(self, id, item, members):
        emoji = get_emoji(item)
        super().__init__(value=id, label=item, description=members, emoji=emoji)


class CompleteMenu(discord.ui.Select):
    def __init__(self, options, max_values):
        super().__init__(placeholder="✅ 분배 항목을 선택해주세요", options=options, max_values=max_values)

    async def callback(self, interaction: discord.Interaction):
        division_ids = [int(value) for value in self.values]
        view = complete_partition(division_ids)
        await interaction.respond(view=view, ephemeral=True, delete_after=120)


class CompleteView(discord.ui.View):
    def __init__(self, select_menu):
        super().__init__()
        self.add_item(select_menu)


def complete(user_id, member_ids):
    with Database() as db:
        divisions = db.find_divisions_by_member_ids(member_ids)
    options = []
    for i, division in enumerate(divisions):
        if i >= 25:
            break
        option = CompleteOption(id=str(division.id), item=division.item, members=division.get_members(user_id))
        options.append(option)

    if len(options) == 0:
        return None

    menu = CompleteMenu(options=options, max_values=len(options) if len(options) < MAX_VALUES else MAX_VALUES)
    view = CompleteView(menu)

    return view
