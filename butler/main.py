import discord
from config import setting
from butler.service import help


intents = discord.Intents.all()

bot = discord.Bot(intents=intents, activity=discord.Game(name='아가씨께 디코를 안내'))


@bot.event
async def on_message(message: discord.Message):
    if '끼얏호우' in message.content:  # 이스터에그
        file = discord.File('static/kkiyathou.png')
        await message.channel.send(file=file)

    elif '렛렝' == message.content:
        await message.channel.send("'렛렝'님은 '에이렛'님의 부캐릭터 '소생의찬가'의 전 닉네임이에요. 야레야레 정말 못말리는 아가씨인걸요?")

    elif '위하임' == message.content:
        await message.channel.send("我是魏海姆!")


@bot.slash_command(name='명령어', description='명령어 사용법을 알려줘요')
async def help_command(ctx: discord.commands.context.ApplicationContext):
    view = help.bot_help()
    await ctx.interaction.respond(view=view, ephemeral=True)

bot.run(setting.TOKEN)
