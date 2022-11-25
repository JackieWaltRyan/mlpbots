from PIL.Image import open
from asyncio import run
from discord import Embed, File
from discord.ext.commands import command, has_permissions, Cog
from discord.ext.tasks import loop
from io import BytesIO
from json import loads
from mlpbots import logs, LEVELS, FOOTER, save
from random import randint
from re import findall
from requests import get
from traceback import format_exc


class Arts(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.check_arts.start()
            self.send_arts.start()
            self.send_dark_arts.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.send_arts.cancel()
            self.send_dark_arts.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(hours=1)
    async def check_arts(self):
        try:
            request = get(url="https://4pda.to/forum/index.php?showtopic=403239&view=getnewpost").content
            url, formats = "//4pda.to/forum/dl/post/", "jpg|png|gif|jpeg"
            counts = len(findall(pattern=rf"{url}(\d*)/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats})",
                                 string=f"{request}"))
            if counts > 0:
                news = int(findall(pattern=rf"{url}(\d*)/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats})",
                                   string=f"{request}")[-1][:-3])
                posts_1 = findall(
                    pattern=rf"{url}((?:{news - 1}\d{{3}})/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats}))",
                    string=f"{request}")
                posts_2 = findall(
                    pattern=rf"{url}((?:{news}\d{{3}})/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats}))",
                    string=f"{request}")
                from db.settings import settings
                if int(news) > settings["Арты"]["ID"]:
                    settings["Арты"]["ID"] = news
                    await save(file="settings", content=settings)
                    from db.arts import arts  # type: ignore
                    arts.extend(posts_1 + posts_2)
                    await save(file="arts", content=arts)
                    await logs(level=LEVELS[2], message=f"**{len(posts_1) + len(posts_2)}** артов загружены в БД!\n"
                                                        f"На данный момент в базе данных **{len(arts)}** артов!")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop()
    async def send_arts(self):
        try:
            from db.settings import settings
            self.send_arts.change_interval(minutes=settings["Арты"]["Таймер_1"])
            from db.arts import arts  # type: ignore
            while True:
                request = get(url=f"https://4pda.to/forum/dl/post/{arts[-1]}").content
                if b"html" not in request:
                    if len(request) > 8000000:
                        while True:
                            img = open(fp=BytesIO(request))
                            new_size_ratio = 1 - ((len(request) / 8000000) / 10)
                            img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)))
                            out = BytesIO()
                            img.save(fp=out, format="PNG")
                            request = out.getvalue()
                            if len(request) < 8000000:
                                break
                    break
                else:
                    arts.pop()
            await self.BOT.get_channel(id=1007577227380146267).send(file=File(fp=BytesIO(request), filename="img.png"))
            arts.pop()
            await save(file="arts", content=arts)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop()
    async def send_dark_arts(self):
        try:
            from db.settings import settings
            self.send_dark_arts.change_interval(minutes=settings["Арты"]["Таймер_2"])
            from db.settings import settings
            for tag in settings["Арты"]["Теги"]:
                try:
                    request = loads(s=get(url=f"https://derpibooru.org/api/v1/json/search/images?page=1&per_page=50&"
                                              f"filter_id=2&q={tag}").text)["images"]
                    await self.BOT.get_channel(id=1007577232975339551).send(
                        content=f"{request[randint(1, 50)]['view_url']}")
                except Exception:
                    await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Админы 1", name="arts", help="Настройки модуля Arts",
             brief="Ничего / `Параметр` / `Время в минутах`", usage="!arts dark 60")
    @has_permissions(administrator=True)
    async def command_arts(self, ctx, trigger: str = None, timetag: str = None):
        try:
            if str(ctx.channel.type) == "text":
                if ctx.channel.id in [1007577227380146267, 1007577232975339551]:
                    await ctx.message.delete(delay=1)
                    from db.settings import settings
                    from db.arts import arts  # type: ignore
                    embed, res = None, 0
                    if trigger is None and timetag is None:
                        embed = Embed(title="Настройки модуля \"Arts\":", color=ctx.author.color)
                        embed.add_field(name="Команды канала \"Арты\":", inline=False,
                                        value="Изменить частоту публикации: **!arts `время в минутах`**")
                        embed.add_field(name="Команды канала \"Темные Арты\":", inline=False,
                                        value="Изменить частоту публикации: **!arts dark `время в минутах`**\n"
                                              "Добавить тег для поиска: **!arts +tag `название тега`**\n"
                                              "Удалить тег из поиска: **!arts -tag `название тега`**")
                        embed.add_field(name="Настройки канала \"Арты\":", inline=False,
                                        value=f"Артов в базе данных: {len(arts)}\n"
                                              f"Частота публикации артов: {settings['Арты']['Таймер_1']} минут")
                        embed.add_field(name="Настройки канала \"Темные Арты\":", inline=False,
                                        value=f"Теги для поиска: {', '.join(settings['Арты']['Теги'])}\n"
                                              f"Частота публикации артов: {settings['Арты']['Таймер_2']} минут")
                    if trigger is not None:
                        if trigger == "+tag":
                            if timetag is not None:
                                embed = Embed(title="Добавление тега:", color=ctx.author.color)
                                check = loads(s=get(url=f"https://derpibooru.org/api/v1/json/search/images?per_page=50&"
                                                        f"filter_id=2&q={timetag.lower()}").text)["images"]
                                if len(check) == 50:
                                    if timetag.lower() not in settings["Арты"]["Теги"]:
                                        settings["Арты"]["Теги"].append(timetag.lower())
                                        await save(file="settings", content=settings)
                                        embed.add_field(name="Успешно:", inline=False, value=f"{timetag.lower()}")
                                    else:
                                        embed.add_field(name="Ошибка:", inline=False,
                                                        value=f"Тег **{timetag.lower()}** уже есть в списке!")
                                else:
                                    embed.add_field(name="Ошибка:", inline=False,
                                                    value=f"По тегу **{timetag.lower()}** слишком мало результатов!")
                        elif trigger == "-tag":
                            if timetag is not None:
                                embed = Embed(title="Удаление тега:", color=ctx.author.color)
                                try:
                                    settings["Арты"]["Теги"].remove(timetag.lower())
                                    await save(file="settings", content=settings)
                                    embed.add_field(name="Успешно:", inline=False, value=f"{timetag.lower()}")
                                except Exception:
                                    embed.add_field(name="Ошибка:", inline=False,
                                                    value=f"Тег **{timetag.lower()}** не найден в списке добавленных!")
                                    await logs(level=LEVELS[1], message=format_exc())
                        elif trigger == "dark":
                            if timetag is not None:
                                if len(findall(pattern=r"\d+", string=timetag)) != 0:
                                    time = int("".join(findall(pattern=r"\d+", string=timetag)))
                                    settings["Арты"]["Таймер_2"] = time
                                    await save(file="settings", content=settings)
                                    embed = Embed(title="Изменение времени:", color=ctx.author.color,
                                                  description=f"Частота публикации в канале \"Темные Арты\" изменена "
                                                              f"на **{time}** минут!")
                                    res = 1
                        else:
                            if len(findall(pattern=r"\d+", string=trigger)) != 0:
                                time = int("".join(findall(pattern=r"\d+", string=trigger)))
                                settings["Арты"]["Таймер_1"] = time
                                await save(file="settings", content=settings)
                                embed = Embed(title="Изменение времени:", color=ctx.author.color,
                                              description=f"Частота публикации в канале \"Арты\" изменена на "
                                                          f"**{time}** минут!")
                                res = 1
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed, delete_after=60)
                    if res == 1:
                        self.BOT.reload_extension(name="modules.arts")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Arts(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
