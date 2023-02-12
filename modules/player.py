from time import time

from asyncio import sleep, run
from datetime import timedelta
from discord import Embed, FFmpegPCMAudio
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord_components_mirror import Button, ButtonStyle
from json import loads
from mlpbots import DB, logs, FOOTER
from requests import get
from traceback import format_exc


async def subscribe(interaction):
    try:
        if DB["members"].find_one(filter={"_id": interaction.user.id})["Уведомления"]:
            status = "Подписан"
        else:
            status = "Не подписан"
        embed = Embed(title="Настройки:",
                      color=0x00FFFF,
                      description="Подписатся на уведомления о прямых эфирах?")
        embed.add_field(name="Текущий статус:",
                        value=f"{status}")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1074324409201995857/"
                                "set.png")
        embed.set_footer(text=FOOTER["Текст"],
                         icon_url=FOOTER["Ссылка"])
        await interaction.send(embed=embed,
                               components=[[Button(emoji="🔔",
                                                   id="subscribe_on"),
                                            Button(emoji="🔕",
                                                   id="subscribe_off")]])
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


class Player(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.online.start()
            self.player.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.online.cancel()
            self.player.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(seconds=60)
    async def online(self):
        try:
            params = {"operationName": "",
                      "variables": {},
                      "query": "{getCalendarEvents {summary startsAt endsAt}}"}
            data = loads(s=get(url="https://everhoof.ru/api/graphql",
                               params=params).text)["data"]
            if len(data["getCalendarEvents"]) > 0:
                start = int(str(data["getCalendarEvents"][0]["startsAt"])[:10])
                if start < int(time()) < start + 3600:
                    if DB["settings"].find_one(filter={"_id": "Плеер"})["Триггер"] < start:
                        notice = ""
                        for member in DB["members"].find({"Уведомления": True}):
                            notice += f"<@{member['_id']}>, "
                        channel = DB["channels"].find_one(filter={"Категория": "Плеер 1"})["_id"]
                        content = f"{notice}\nСейчас в прямом эфире **\"{data['getCalendarEvents'][0]['summary']}\"**!"
                        await self.BOT.get_channel(id=channel).send(content=content)
                        DB["settings"].update_one(filter={"_id": "Плеер"},
                                                  update={"$set": {"Триггер": start}})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def player(self):
        try:
            while True:
                try:
                    for vc in self.BOT.voice_clients:
                        vc.cleanup()
                        await vc.disconnect(force=True)
                except Exception:
                    await logs(level="DEBUG",
                               message=format_exc())
                try:
                    voise = DB["channels"].find_one(filter={"Категория": "Плеер 2"})["_id"]
                    vc = await self.BOT.get_channel(id=voise).connect()
                    try:
                        vc.play(FFmpegPCMAudio(source="https://everhoof.ru/320",
                                               executable="bin/ffmpeg/bin/ffmpeg.exe"))
                    except Exception:
                        await logs(level="DEBUG",
                                   message=format_exc())
                        vc.play(FFmpegPCMAudio(source="https://everhoof.ru/320"))
                except Exception:
                    await logs(level="DEBUG",
                               message=format_exc())
                artist, title, duration = "Everhoof Radio", "Everhoof Radio", 60
                art, delta = "https://everhoof.ru/favicon.png", 60
                try:
                    params = {"operationName": "",
                              "variables": {},
                              "query": "{getCurrentPlaying {live {isLive} "
                                       "current {artist title endsAt duration art}} "
                                       "getCalendarEvents {summary startsAt endsAt}}"}
                    content = loads(s=get(url="https://everhoof.ru/api/graphql",
                                          params=params).text)["data"]
                    current = content["getCurrentPlaying"]["current"]
                    if content["getCurrentPlaying"]["live"]["isLive"]:
                        start = int(str(content["getCalendarEvents"][0]["startsAt"])[:10])
                        if int(time()) > start:
                            artist, title, delta = "В эфире", content["getCalendarEvents"][0]["summary"], 60
                    else:
                        artist, title = current["artist"], current["title"]
                        duration, art = current["duration"], current["art"]
                        try:
                            delta = int(str(current["endsAt"])[:10]) - int(time())
                            if delta == 0:
                                delta = 60
                        except Exception:
                            delta = 60
                            await logs(level="DEBUG",
                                       message=format_exc())
                except Exception:
                    artist, title, duration = "Everhoof Radio", "Everhoof Radio", 60
                    art, delta = "https://everhoof.ru/favicon.png", 60
                    await logs(level="DEBUG",
                               message=format_exc())
                channel = DB["channels"].find_one(filter={"Категория": "Плеер 1"})["_id"]
                post_id = DB["settings"].find_one(filter={"_id": "Плеер"})["Пост"]
                try:
                    post = await self.BOT.get_channel(id=channel).fetch_message(id=post_id)
                    await post.delete()
                except Exception:
                    await logs(level="DEBUG",
                               message=format_exc())
                embed = Embed(title="Сейчас играет:",
                              color=0x00FFFF)
                embed.set_thumbnail(url=art)
                embed.add_field(name=title,
                                inline=False,
                                value=f"Исполнитель: {artist}\n"
                                      f"Длительность: {str(timedelta(seconds=duration))[2:]}\n"
                                      f"Ссылка: https://everhoof.ru")
                embed.set_footer(text=FOOTER["Текст"],
                                 icon_url=FOOTER["Ссылка"])
                try:
                    post = await self.BOT.get_channel(id=channel).send(embed=embed,
                                                                       components=[[Button(label="История",
                                                                                           id="player_history",
                                                                                           style=ButtonStyle.green),
                                                                                    Button(emoji="⚙",
                                                                                           id="player_settings",
                                                                                           style=ButtonStyle.blue)]])
                    DB["settings"].update_one(filter={"_id": "Плеер"},
                                              update={"$set": {"Пост": post.id}})
                except Exception:
                    await logs(level="DEBUG",
                               message=format_exc())
                await sleep(delay=delta)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "player_history":
                embed = Embed(title="История:",
                              color=interaction.user.color)
                try:
                    params = {"operationName": "",
                              "variables": {},
                              "query": "{getTracksHistory {track {text}}}"}
                    content, i = loads(s=get(url="https://everhoof.ru/api/graphql",
                                             params=params).text)["data"], 1
                    for track in content["getTracksHistory"]:
                        info = track["track"]["text"].split(" - ")
                        embed.add_field(name=f"{i}. {info[1]}",
                                        value=f"Исполнитель: {info[0]}",
                                        inline=False)
                        i += 1
                except Exception:
                    embed.add_field(name="Ошибка!",
                                    value="Не удалось получить список, попробуйте позже...",
                                    inline=False)
                    await logs(level="DEBUG",
                               message=format_exc())
                embed.set_footer(text=FOOTER["Текст"],
                                 icon_url=FOOTER["Ссылка"])
                await interaction.send(embed=embed)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "player_settings":
                await subscribe(interaction=interaction)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "subscribe_on":
                DB["members"].update_one(filter={"_id": interaction.user.id},
                                         update={"$set": {"Уведомления": True}})
                await subscribe(interaction=interaction)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "subscribe_off":
                DB["members"].update_one(filter={"_id": interaction.user.id},
                                         update={"$set": {"Уведомления": False}})
                await subscribe(interaction=interaction)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Player(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
