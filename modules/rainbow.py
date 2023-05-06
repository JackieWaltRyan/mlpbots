from asyncio import run
from traceback import format_exc

from discord import Embed
from discord.ext.commands import Cog, command
from discord.ext.tasks import loop
from discord.utils import get

from mlpbots import DB, logs, FOOTER


class Rainbow(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.start, self.stop = bot, 1, 0
            self.roles = [x["_id"] for x in DB["roles"].find({"Категория": "Радуга"})]
            self.rainbow.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.rainbow.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(seconds=3)
    async def rainbow(self):
        try:
            for user in DB["members"].find({"Радуга": True}):
                try:
                    member = self.BOT.guilds[0].get_member(user_id=user["_id"])
                    await member.add_roles(get(iterable=member.guild.roles,
                                               id=self.roles[self.start]))
                    await member.remove_roles(get(iterable=member.guild.roles,
                                                  id=self.roles[self.stop]))
                except Exception:
                    await logs(level="DEBUG",
                               message=format_exc())
            self.start += 1
            self.stop += 1
            if self.start == 9:
                self.start = 0
            if self.stop == 9:
                self.stop = 0
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @command(description="Все 2",
             name="rainbow",
             help="Сделать себе радужный ник",
             brief="`On` / `Off`",
             usage="!rainbow on")
    async def command_rainbow(self, ctx, trigger: str = "on"):
        try:
            if str(ctx.channel.type) == "text":
                if trigger.lower() == "on" or trigger.lower() == "off":
                    await ctx.message.delete(delay=1)
                    embed = None
                    if trigger.lower() == "on":
                        DB["members"].update_one(filter={"_id": ctx.author.id},
                                                 update={"$set": {"Радуга": True}})
                        embed = Embed(title="Радужная роль:",
                                      color=ctx.author.color,
                                      description="Вы **включили** себе радужный ник!")
                    if trigger.lower() == "off":
                        DB["members"].update_one(filter={"_id": ctx.author.id},
                                                 update={"$set": {"Радуга": False}})
                        embed = Embed(title="Радужная роль:",
                                      color=ctx.author.color,
                                      description="Вы **отключили** себе радужный ник!")
                    embed.set_footer(text=FOOTER["Текст"],
                                     icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed,
                                   delete_after=60)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Rainbow(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
