import discord
from datetime import datetime
from division.util import create_id
from division.item_db import get_url
from division.database import Database


def input_division(item, members):
    id = create_id()
    created_at = datetime.now()
    status = "CREATED"

    with Database() as db:
        db.insert_division(id, item, created_at, status, members)

    embed = discord.Embed(title='입력 완료', description=f'{item}', color=0x8fce00)

    img_url = get_url(item)
    file = discord.File(f'static/{img_url}')
    embed.set_thumbnail(url=f'attachment://{file.filename}')

    return embed, file
