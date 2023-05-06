from asyncio import run
from datetime import datetime, timedelta
from hashlib import sha256
from json import loads
from random import randint
from time import time
from traceback import format_exc

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from discord_components_mirror import Button, ButtonStyle
from pytz import timezone
from requests import post

from mlpbots import DB, logs, FOOTER


class Raffle(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.channel_notice = DB["channels"].find_one(filter={"Категория": "Обьявления"})["_id"]
            self.role_gamer = DB["roles"].find_one(filter={"Категория": "Игрок"})["_id"]
            self.member_jwr = [x["_id"] for x in DB["members"].find({"Категория": "JWR"})]
            self.time_mon = DB["settings"].find_one(filter={"_id": "Розыгрыш"})["Денежный Мод"]
            self.time_max = DB["settings"].find_one(filter={"_id": "Розыгрыш"})["Максимальный Мод"]
            self.raffle.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    async def post_win(self, user, mod):
        try:
            embed = Embed(title="Результаты розыгрыша",
                          color=0x0000FF,
                          description=f"Поздравляем победителя розыгрыша <@{user}>! Чтобы получить свой приз, нажми "
                                      f"на кнопку под этим сообщением. У тебя есть 24 часа, чтобы забрать приз, или "
                                      f"будет выбран новый победитель.")
            embed.add_field(name="Победитель:",
                            value=f"<@{user}>")
            embed.add_field(name="Приз:",
                            value=mod)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457819250829/"
                                    "PinkiePieWannaHugYou.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            mod_id = {"Денежный Мод": "3467418",
                      "Максимальный Мод": "3468896"}
            await self.BOT.get_channel(id=self.channel_notice).send(content=f"@here Поздравляем победителя розыгрыша "
                                                                            f"<@{user}>!",
                                                                    embed=embed,
                                                                    components=[[Button(label="Получить приз",
                                                                                        id=f"raffle_win_{mod_id[mod]}",
                                                                                        style=ButtonStyle.blue)]])
            DB["settings"].update_one(filter={"_id": "Розыгрыш"},
                                      update={"$set": {"Денежный Мод": self.time_mon + timedelta(hours=24),
                                                       "Максимальный Мод": self.time_max + timedelta(hours=24),
                                                       f"Победители.{user}": {"Время": datetime.utcnow(),
                                                                              "Мод": mod,
                                                                              "Триггер": False}}})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    async def win(self, mod):
        try:
            self.member_jwr.extend([868148805722337320, 868150460735971328])
            parts, ints, seq, tab, per = {}, 0, 0, {}, 0
            for guild in self.BOT.guilds:
                for channel in guild.channels:
                    if str(channel.type) == "text":
                        async for message in channel.history(after=datetime.utcnow() - timedelta(days=7)):
                            if len(message.reactions) > 0:
                                for reaction in message.reactions:
                                    async for user in reaction.users():
                                        try:
                                            if get(iterable=user.roles,
                                                   id=self.role_gamer) is not None:
                                                if user.id not in self.member_jwr:
                                                    if user.id not in parts:
                                                        parts.update({user.id: {"int": 1, "%": 0}})
                                                    else:
                                                        parts[user.id]["int"] += 1
                                        except Exception:
                                            await logs(level="DEBUG",
                                                       message=format_exc())
            for part in parts:
                ints += parts[part]["int"]
            for part in parts:
                parts[part]["%"] = int((100 / len(parts)) + ((parts[part]["int"] / (ints / 100)) / 10))
                seq += parts[part]["%"]
            for part in parts:
                parts[part]["%"] -= int((seq - 100) / len(parts))
                tab.update({per + parts[part]["%"]: part})
                per += parts[part]["%"]
            win = randint(a=1,
                          b=per)
            for item in tab:
                if win < item + 1:
                    for part in parts:
                        if part == tab[item]:
                            await self.post_win(user=part,
                                                mod=mod)
                            break
                    break
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def raffle(self):
        try:
            if (datetime.utcnow() - self.time_max).days >= 28:
                await self.win(mod="Максимальный Мод")
            else:
                if (datetime.utcnow() - self.time_mon).days >= 7:
                    await self.win(mod="Денежный Мод")
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if "raffle_win" in interaction.component.id:
                winners = DB["settings"].find_one(filter={"_id": "Розыгрыш"})["Победители"]
                if str(interaction.user.id) in winners:
                    if (datetime.utcnow() - winners[str(interaction.user.id)]["Время"]).days < 1:
                        if not winners[str(interaction.user.id)]["Триггер"]:
                            sha = sha256(str(interaction.user.id).encode(encoding="UTF-8",
                                                                         errors="ignore")).hexdigest()
                            user, i = f"{int(time())}".join(x for x in sha if x.isdigit()), 0
                            while len(user) > 10:
                                if i + 1 >= len(user):
                                    i = 0
                                if i + 1 < len(user):
                                    temp = [int(x) for x in user]
                                    temp[i] += temp.pop(i + 1)
                                    i += 1
                                    user = "".join(str(x) for x in temp)
                            response = loads(s=post(url="",
                                                    json={"id": interaction.component.id[11:],
                                                          "inv": int(user),
                                                          "friend": f"discord_{interaction.user.id}"}).text)
                            str_ok = str(f"Спасибо за участие! Приятной игры!\n\nЧтобы получить ваш мод перейдите "
                                         f"пожалуйста по ссылке: http://jwrshop.tk/users/{user}\n\nНи в коем случае "
                                         f"не сообщайте посторонним людям адрес этой страницы или ваш ID!")
                            str_er = str(f"На сервере обработки данных произошла ошибка! Пожалуйста, свяжитесь с "
                                         f"<@496139824500178964> для решения проблемы.\n\nИ сообщите мне эти данные:"
                                         f"\n\nID: {user}\nTime: {datetime.now(tz=timezone(zone='Europe/Moscow'))}\n\n"
                                         f"Извините за неудобства! Ни в коем случае не сообщайте посторонним людям "
                                         f"адрес этой страницы или ваш ID!")
                            await interaction.send(content=str_ok if "goods" in response else str_er)
                            winners[str(interaction.user.id)]["Триггер"] = True
                            mod = "Денежный Мод" if interaction.component.id[11:] == "3467418" else "Максимальный Мод"
                            DB["settings"].update_one(filter={"_id": "Розыгрыш"},
                                                      update={"$set": {mod: datetime.utcnow() + timedelta(hours=24),
                                                                       "Победители": winners}})
                        else:
                            await interaction.send(content="Вы уже забрали свой приз.")
                    else:
                        await interaction.send(content="Ваше время вышло! 24 часа прошли...")
                else:
                    await interaction.send(content="Забрать приз может только победитель!")
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Raffle(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
