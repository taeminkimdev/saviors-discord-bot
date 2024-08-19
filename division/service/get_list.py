import discord
from database import Database
from item_db import get_url


def get_division(member_ids):
    with Database() as db:
        divisions = db.find_divisions_by_member_ids(member_ids)

    embed = discord.Embed(title='📜 분배 목록', description='미분배 목록입니다', color=0x62c1cc)
    if len(divisions) == 0:
        embed.description = '분배할 아이템이 없습니다'
        return embed, None

    represent_division = divisions[0]
    img_url = get_url(represent_division.item)
    file = discord.File(f'static/{img_url}')
    embed.set_thumbnail(url=f'attachment://{file.filename}')
    for i, division in enumerate(divisions):
        embed.add_field(name=f'[{i + 1}] {division.item} - {division.created_at.strftime("%m/%d")}', value=division.get_members_string, inline=False)

    return embed, file

