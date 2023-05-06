from asyncio import run
from datetime import datetime
from traceback import format_exc

from discord.ext.commands import Cog
from discord.ext.tasks import loop

from mlpbots import DB, logs


class Activity(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.update_members.start()
            self.update_channels.start()
            self.update_roles.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.update_members.cancel()
            self.update_channels.cancel()
            self.update_roles.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(hours=1)
    async def update_members(self):
        try:
            for guild in self.BOT.guilds:
                for member in guild.members:
                    if DB["members"].find_one(filter={"_id": member.id}) is None:
                        DB["members"].insert_one(document={"_id": member.id,
                                                           "Имя": f"{member.name}#{member.discriminator}",
                                                           "Уведомления": False,
                                                           "Радуга": False,
                                                           "Похищенная пони": {"Страница": "p0",
                                                                               "Концовки": []},
                                                           "Антиспам": {"Триггер": False,
                                                                        "Сообщения": [],
                                                                        "Время": datetime.utcnow(),
                                                                        "Блокировка": datetime.utcnow(),
                                                                        "Количество": 0}})
                    else:
                        DB["members"].update_one(filter={"_id": member.id},
                                                 update={"$set": {"Имя": f"{member.name}#{member.discriminator}"}})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(hours=1)
    async def update_channels(self):
        try:
            channel_type = {"text": "Текстовый",
                            "voice": "Голосовой",
                            "category": "Категория"}
            for guild in self.BOT.guilds:
                for channel in guild.channels:
                    DB["channels"].update_one(filter={"_id": channel.id},
                                              update={"$set": {"Название": channel.name,
                                                               "Тип": channel_type[str(channel.type)],
                                                               "Позиция": channel.position}},
                                              upsert=True)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(hours=1)
    async def update_roles(self):
        try:
            for guild in self.BOT.guilds:
                for role in guild.roles:
                    DB["roles"].update_one(filter={"_id": role.id},
                                           update={"$set": {"Название": role.name,
                                                            "Цвет": role.color.value,
                                                            "Позиция": role.position}},
                                           upsert=True)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Activity(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
