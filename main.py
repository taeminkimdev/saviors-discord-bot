import discord
import os
from discord.commands.options import Option

from database import Database
from config import setting
from util import convert_members, convert_external_members
from division.service import compete, delete, get_list, input
from division.service.distribution_status import update_distribut_status

intents = discord.Intents.all()

bot = discord.Bot(intents=intents, activity=discord.Game(name='여신님을 숭배'))


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

division = bot.create_group(name='분배', description='분배합니다')


class CommandNotValidLocation(Exception):
    pass


@division.before_invoke
async def check_valid_channel(ctx: discord.commands.context.ApplicationContext):
    if ctx.channel_id != setting.channel_id:
        raise discord.ApplicationCommandInvokeError(e=CommandNotValidLocation())


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.ApplicationCommandInvokeError):
    if isinstance(error, discord.ApplicationCommandInvokeError):
        await ctx.respond(f"'{ctx.channel.name}' 채널은 분배 명령어를 사용할 수 없는 채널입니다")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


@division.command(name='초기화', description='명령어를 입력할 채널 세팅을 지정합니다')
async def division_init(ctx: discord.commands.context.ApplicationContext):
    with open('channel_id', 'w') as f:
        f.write(str(ctx.channel_id))
    os.remove('distribute_message_id')

    setting.channel_id = ctx.channel_id
    await ctx.respond(f"'{ctx.channel.name}' 채널을 분배 채널로 지정합니다")


@division.command(name='목록', description='내가 받을 수 있는 분배 목록을 검색합니다')
async def get_division_list(ctx: discord.commands.context.ApplicationContext,
                            members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @찰봉@찰봇@붕괴의파동') = ''):
    member_ids = convert_members(members, ctx.user.id)
    embed, file = get_list.get_division(member_ids)

    await ctx.respond(embed=embed, file=file, ephemeral=True, delete_after=60)


@division.command(name='완료', description='분배된 항목을 완료합니다')
async def complete_division(ctx: discord.Interaction,
                            members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @찰봉@찰봇@붕괴의파동') = ''):
    member_ids = convert_members(members, ctx.user.id)

    embed, file = get_list.get_division(member_ids)
    view = compete.complete(member_ids)

    await ctx.respond(embed=embed, file=file, view=view, ephemeral=True, delete_after=120)


@division.command(name='삭제', description='분배 항목을 삭제합니다')
async def delete_division(ctx: discord.Interaction,
                          members: Option(str, name='필터유저', description='함께 검색하고 싶은 유저를 멘션해주세요 ex. @찰봉@찰봇@붕괴의파동') = ''):
    member_ids = convert_members(members, ctx.user.id)

    embed, file = get_list.get_division(member_ids)
    view = delete.delete(member_ids)

    await ctx.respond(embed=embed, file=file, view=view, ephemeral=True, delete_after=120)


@division.command(name='등록', description='분배 항목을 등록합니다')
async def input_division(ctx: discord.Interaction,
                         item: Option(str, name='아이템이름', min_length=1, max_length=30, description='분배할 아이템 이름을 입력합니다. 인챈트, 강화권 아이템은 해당 단어를 포함시켜주세요 ex. 인챈트 - 가두는, 강화권 - 스매시'),
                         members: Option(str, name='분배참여자', description='분배할 유저를 모두 멘션해주세요 ex. @찰봉@찰봇@붕괴의파동'),
                         external_members: Option(str, name='외부인원', description='외부 인원의 닉네임을 입력해주세요. 띄어쓰기로 구분합니다. ex. 외부찰봉 외부찰봇 외부붕괴') = ''):
    external_members = convert_external_members(external_members)
    with Database() as db:
        db.update_members(external_members)
        external_member_ids = db.find_external_members([member['nickname'] for member in external_members])
    member_ids = convert_members(members, ctx.user.id)
    embed, file = input.input_division(item, member_ids + external_member_ids)

    await ctx.respond(embed=embed, file=file, ephemeral=True, delete_after=10)
    await update_distribut_status(bot)


bot.run(setting.TOKEN)
