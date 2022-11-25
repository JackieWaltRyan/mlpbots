from asyncio import run
from discord import Embed
from discord.ext.commands import Cog, command
from discord.ext.tasks import loop
from discord.utils import get
from mlpbots import logs, LEVELS, FOOTER, save
from traceback import format_exc

ROLES = [1007586345042071633, 1007586344014454805, 1007586342634541057, 1007586341753724949, 1007586340663218206,
         1007586339572690984]


class Rainbow(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.members, self.a, self.b = bot, [], 1, 0
            from db.members import members
            for member in members:
                if members[member]["Радуга"]:
                    self.members.append(self.BOT.get_guild(id=798851582800035841).get_member(user_id=member))
            if len(self.members) > 0:
                self.rainbow.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.rainbow.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(seconds=3)
    async def rainbow(self):
        try:
            for member in self.members:
                try:
                    from db.members import members
                    if members[member.id]["Статус"]:
                        await member.add_roles(get(iterable=member.guild.roles, id=ROLES[self.a]))
                    await member.remove_roles(get(iterable=member.guild.roles, id=ROLES[self.b]))
                except Exception:
                    await logs(level=LEVELS[1], message=format_exc())
            self.a += 1
            self.b += 1
            if self.a == 6:
                self.a = 0
            if self.b == 6:
                self.b = 0
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 2", name="rainbow", help="Сделать себе радужный ник", brief="`On` / `Off`",
             usage="!rainbow on")
    async def command_rainbow(self, ctx, trigger: str = "on"):
        try:
            if str(ctx.channel.type) == "text":
                if trigger.lower() == "on" or trigger.lower() == "off":
                    await ctx.message.delete(delay=1)
                    embed = None
                    from db.members import members
                    if trigger.lower() == "on":
                        members[ctx.author.id]["Радуга"] = True
                        await save(file="members", content=members)
                        embed = Embed(title="Радужная роль:", color=ctx.author.color,
                                      description="Вы **включили** себе радужный ник!")
                    if trigger.lower() == "off":
                        members[ctx.author.id]["Радуга"] = False
                        await save(file="members", content=members)
                        embed = Embed(title="Радужная роль:", color=ctx.author.color,
                                      description="Вы **отключили** себе радужный ник!")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed, delete_after=60)
                    self.BOT.reload_extension(name="modules.rainbow")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Rainbow(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
