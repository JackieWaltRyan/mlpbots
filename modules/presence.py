from asyncio import run
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from mlpbots import logs, BOTS
from pypresence import AioPresence
from traceback import format_exc


class Presence(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.presence.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.presence.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(minutes=1)
    async def presence(self):
        try:
            rpc = AioPresence(str(self.BOT.user.id))
            await rpc.connect()
            await rpc.update(large_text=BOTS[str(self.BOT.user.id)]["Имя"],
                             large_image=BOTS[str(self.BOT.user.id)]["Присутствие"]["Аватар"],
                             details=BOTS[str(self.BOT.user.id)]["Присутствие"]["Статус"],
                             start=1000000000)
        except Exception:
            await logs(level="DEBUG",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Presence(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
