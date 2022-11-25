from asyncio import run
from discord import File, Member
from discord.ext.commands import Cog, command
from discord.ext.tasks import loop
from mlpbots import logs, LEVELS, save
from traceback import format_exc


class Achievements(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.achievements.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.achievements.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    async def send_achievements(self, member, file):
        try:
            await self.BOT.get_channel(id=1007577280643604571).send(
                content=f"**Ей! <@{member.id}> только что получил достижение!**",
                file=File(f"images/achievements/{file}.png"))
            from db.members import members
            members[member.id]["Достижения"].append(file)
            await save(file="members", content=members)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(hours=1)
    async def achievements(self):
        try:
            from db.members import members
            for guild in self.BOT.guilds:
                for member in guild.members:
                    if members[member.id]["Дни"] >= 30:
                        if "d30" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="d30")
                    if members[member.id]["Дни"] >= 90:
                        if "d90" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="d90")
                    if members[member.id]["Дни"] >= 180:
                        if "d180" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="d180")
                    if members[member.id]["Дни"] >= 365:
                        if "d365" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="d365")
                    if members[member.id]["Дни"] >= 1095:
                        if "d1095" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="d1095")
                    if int(members[member.id]["Сообщения"]) >= 500:
                        if "m500" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="m500")
                    if int(members[member.id]["Сообщения"]) >= 1000:
                        if "m1000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="m1000")
                    if int(members[member.id]["Сообщения"]) >= 2000:
                        if "m2000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="m2000")
                    if int(members[member.id]["Сообщения"]) >= 5000:
                        if "m5000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="m5000")
                    if int(members[member.id]["Сообщения"]) >= 10000:
                        if "m10000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="m10000")
                    if int(members[member.id]["Упоминания"]) >= 50:
                        if "mt50" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="mt50")
                    if int(members[member.id]["Упоминания"]) >= 100:
                        if "mt100" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="mt100")
                    if int(members[member.id]["Упоминания"]) >= 300:
                        if "mt300" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="mt300")
                    if int(members[member.id]["Упоминания"]) >= 1000:
                        if "mt1000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="mt1000")
                    if int(members[member.id]["Упоминания"]) >= 5000:
                        if "mt5000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="mt5000")
                    if int(members[member.id]["Лайки"]) >= 10:
                        if "l10" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="l10")
                    if int(members[member.id]["Лайки"]) >= 50:
                        if "l50" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="l50")
                    if int(members[member.id]["Лайки"]) >= 100:
                        if "l100" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="l100")
                    if int(members[member.id]["Лайки"]) >= 300:
                        if "l300" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="l300")
                    if int(members[member.id]["Лайки"]) >= 1000:
                        if "l1000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="l1000")
                    if int(members[member.id]["Дизлайки"]) >= 10:
                        if "dl10" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="dl10")
                    if int(members[member.id]["Дизлайки"]) >= 50:
                        if "dl50" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="dl50")
                    if int(members[member.id]["Дизлайки"]) >= 100:
                        if "dl100" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="dl100")
                    if int(members[member.id]["Дизлайки"]) >= 300:
                        if "dl300" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="dl300")
                    if int(members[member.id]["Дизлайки"]) >= 1000:
                        if "dl1000" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="dl1000")
                    if len(members[member.id]["Похищенная пони"]["Концовки"]) == 19:
                        if "pp" not in members[member.id]["Достижения"]:
                            await self.send_achievements(member=member, file="pp")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_message(self, message):
        try:
            if message.content.startswith("!ban"):
                from db.members import members
                if "ban" not in members[message.author.id]["Достижения"]:
                    await self.send_achievements(member=message.author, file="ban")
                if str(message.content) == "!ban <@496139824500178964>":
                    if "banowner" not in members[message.author.id]["Достижения"]:
                        await self.send_achievements(member=message.author, file="banowner")
                if str(message.content) == "!ban @everyone":
                    if "baneveryone" not in members[message.author.id]["Достижения"]:
                        await self.send_achievements(member=message.author, file="baneveryone")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 1", name="achieve", help="Показать достижения пользователя",
             brief="Ничего / `Упоминание пользователя`", usage="!achieve <@918687493577121884>")
    async def achieve(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if not member:
                    member = ctx.message.author
                from db.members import members
                if len(members[member.id]["Достижения"]) == 0:
                    await ctx.send(content=f"Сейчас у {member.mention} нет достижений...", delete_after=60)
                else:
                    files, i = [[]], 0
                    for file in members[member.id]["Достижения"]:
                        if len(files[i]) < 10:
                            files[i].append(File(fp=f"images/achievements/{file}.png"))
                        else:
                            i += 1
                            files.append([File(fp=f"images/achievements/{file}.png")])
                    for lists in files:
                        await ctx.send(content=f"Текущие достижения {member.mention}:", files=lists, delete_after=60)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Achievements(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
