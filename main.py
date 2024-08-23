import discord
import os
from discord.commands.options import Option
from discord.ext import commands
from database import Database
from config import setting
from item_db import emoji_db
from util import convert_members, convert_external_members
from division.service import compete, delete, get_list, input
from division.service.distribution_status import update_distribut_status


import logging
from config import log
from logging.handlers import TimedRotatingFileHandler


def set_handler(logger, level):
    filename = log.INFO_LOG_FILENAME
    if level == logging.WARNING:
        filename = log.WARNING_LOG_FILENAME

    handler = TimedRotatingFileHandler(filename=filename, when='d', interval=1, backupCount=90, encoding='utf-8')
    handler.suffix = log.SUFFIX
    formatter = logging.Formatter(log.LOG_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)


saviors_logger = logging.getLogger('saviors')
saviors_logger.setLevel(logging.INFO)

set_handler(saviors_logger, logging.INFO)
set_handler(saviors_logger, logging.WARNING)


intents = discord.Intents.all()

bot = discord.Bot(intents=intents, activity=discord.Game(name='섬멸자 여신님을 숭배'))


@bot.event
async def on_ready():
    guild = bot.get_guild(setting.guild_id)

    members = []
    for member in guild.members:
        nickname = member.name
        if member.display_name is not None:
            nickname = member.display_name
        elif member.global_name is not None:
            nickname = member.global_name

        members.append({
            'id': member.id,
            'nickname': str(nickname)
        })

    with Database() as db:
        db.update_members(members)
    print('finish')


@bot.event
async def on_member_join(member):
    nickname = member.name
    if member.display_name is not None:
        nickname = member.display_name
    elif member.global_name is not None:
        nickname = member.global_name

    member = [{
        'id': member.id,
        'nickname': str(nickname)
    }]

    with Database() as db:
        db.update_members(member)


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == setting.channel_id and not message.author.bot:
        await message.delete()

    elif '끼얏호우' in message.content:  # 이스터에그
        file = discord.File(f'static/kkiyathou.png')
        await message.channel.send(file=file)

    elif '렛렝' == message.content:
        await message.channel.send("'렛렝'님은 '에이렛'님의 부캐릭터 '소생의찬가'의 전 닉네임이에요. 정말 독특하고 멋진 닉네임이네요!")

    elif '위하임' == message.content:
        await message.channel.send("我是魏海姆!")

division = bot.create_group(name='분배', description='분배합니다')


class CommandNotValidLocation(commands.CommandError):
    pass


@division.before_invoke
async def check_valid_channel(ctx: discord.commands.context.ApplicationContext):
    if ctx.selected_options[0]['name'] == '초기화':
        pass

    elif ctx.channel_id != setting.channel_id:
        raise CommandNotValidLocation


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, CommandNotValidLocation):
        await ctx.respond(f"'{ctx.channel.name}' 채널은 분배 명령어를 사용할 수 없는 채널입니다", ephemeral=True, delete_after=10)
    elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.respond(f"명령어를 사용할 권한이 부족합니다", ephemeral=True, delete_after=10)
    else:
        msg = f'{ctx.command.name}'
        saviors_logger.exception(msg=msg, exc_info=error)
        raise error  # Here we raise other errors to ensure they aren't ignored


@division.command(name='초기화', description='명령어를 입력할 채널 세팅을 지정합니다')
@commands.has_permissions(administrator=True)
async def division_init(ctx: discord.commands.context.ApplicationContext):
    with open('channel_id', 'w') as f:
        f.write(str(ctx.channel_id))

    try:
        os.remove('distribute_message_id')
    except FileNotFoundError:
        pass

    setting.channel_id = ctx.channel_id
    await ctx.respond(f"'{ctx.channel.name}' 채널을 분배 채널로 지정합니다")


@division.command(name='목록', description='내가 받을 수 있는 분배 목록을 검색합니다')
async def get_division_list(ctx: discord.commands.context.ApplicationContext,
                            members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @꼬장@찰봉@에이렛') = ''):
    member_ids = convert_members(members, ctx.user.id)
    embed = get_list.get_division(ctx.user.id, member_ids)

    await ctx.respond(embed=embed, ephemeral=True, delete_after=60)


@division.command(name='완료', description='분배된 항목을 완료합니다')
async def complete_division(ctx: discord.Interaction,
                            members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @꼬장@찰봉@에이렛') = ''):
    member_ids = convert_members(members, ctx.user.id)

    embed = get_list.get_division(ctx.user.id, member_ids)
    view = compete.complete(ctx.user.id, member_ids)

    await ctx.respond(embed=embed, view=view, ephemeral=True, delete_after=120)


@division.command(name='삭제', description='분배 항목을 삭제합니다')
async def delete_division(ctx: discord.Interaction,
                          members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @꼬장@찰봉@에이렛') = ''):
    member_ids = convert_members(members, ctx.user.id)

    embed = get_list.get_division(ctx.user.id, member_ids)
    view = delete.delete(ctx.user.id, member_ids)

    await ctx.respond(embed=embed, view=view, ephemeral=True, delete_after=120)


@division.command(name='등록', description='분배 항목을 등록합니다')
async def input_division(ctx: discord.Interaction,
                         item: Option(str, name='아이템이름', min_length=1, max_length=30, description='분배할 아이템 이름을 입력합니다. 인챈트, 강화권 아이템은 해당 단어를 포함시켜주세요 ex. 인챈트 - 가두는, 강화권 - 스매시'),
                         members: Option(str, name='분배참여자', description='분배할 유저를 모두 멘션해주세요 ex. @꼬장@찰봉@에이렛 / 외부 인원의 경우 tab키를 눌러 옵션을 추가해주세요'),
                         external_members: Option(str, name='외부인원', description='외부 인원의 닉네임을 입력해주세요. 띄어쓰기로 구분합니다. ex. 외부꼬장 외부찰봉 외부에이렛') = ''):
    external_members = convert_external_members(external_members)
    with Database() as db:
        db.update_members(external_members)
        external_member_ids = db.find_external_members([member['nickname'] for member in external_members])
    member_ids = convert_members(members, ctx.user.id)
    embed, file = input.input_division(item, member_ids + external_member_ids)

    saviors_logger.info(msg=f'[분배 등록] - {ctx.user.id}/{ctx.user.name}')
    await ctx.respond(embed=embed, file=file, ephemeral=True, delete_after=10)
    await update_distribut_status(ctx.user.id, bot)


bot.run(setting.TOKEN)
