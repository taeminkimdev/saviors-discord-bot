from database import Database
import discord
from config import setting


async def update_distribut_status(client: discord.Client):
    channel = client.get_channel(setting.channel_id)

    with Database() as db:
        divisions = db.find_divisions_by_member_ids([])
    embed = discord.Embed(title='📜 Saviors 미분배 목록', description='', color=0x62c1cc)

    if len(divisions) == 0:
        embed.description = '분배할 아이템이 없습니다'

    for i, division in enumerate(divisions):
        embed.add_field(name=f'[{i + 1}] {division.item} - {division.created_at.strftime("%m/%d")}',
                        value=division.get_members_string, inline=False)

    try:
        with open('distribute_message_id', 'r') as f:
            message_id = int(f.readline().strip())
    except FileNotFoundError:
        pass
    else:
        message = channel.get_partial_message(message_id)
        await message.delete()

    message = await channel.send(embed=embed)
    with open('distribute_message_id', 'w') as f:
        f.write(str(message.id))
