import discord
from database import Database
from item_db import get_emoji


def get_division(member_ids):
    with Database() as db:
        divisions = db.find_divisions_by_member_ids(member_ids)

    embed = discord.Embed(title='📜 분배 목록', description='미분배 목록입니다', color=0x62c1cc)
    if len(divisions) == 0:
        embed.description = '분배할 아이템이 없습니다'
        return embed

    for i, division in enumerate(divisions):
        if i >= 25:
            break
        emoji = get_emoji(division.item)
        embed.add_field(name=f'{emoji} {division.item} - {division.created_at.strftime("%m/%d")}', value=division.get_members_string, inline=False)

    return embed
