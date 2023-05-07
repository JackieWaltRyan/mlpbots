from asyncio import run, sleep
from datetime import datetime, timedelta
from functools import partial
from os import listdir, makedirs, execl
from os.path import exists
from random import choice
from subprocess import run as s_run
from sys import executable
from threading import Timer
from traceback import format_exc

from discord import Activity, Embed, Intents, Member
from discord.ext.commands import Bot, has_permissions, when_mentioned_or
from discord_components_mirror import Button, ButtonStyle, DiscordComponents
from discord_webhook import DiscordEmbed, AsyncDiscordWebhook
from fuzzywuzzy.fuzz import token_sort_ratio
from pymongo import MongoClient
from pytz import timezone

BOT, DB, LEVELS, TRIGGER = Bot(command_prefix=when_mentioned_or("!"),
                               help_command=None,
                               intents=Intents.all()), MongoClient()["mlpbots"], {"DEBUG": 0x0000FF,
                                                                                  "INFO": 0x008000,
                                                                                  "WARNING": 0xFFFF00,
                                                                                  "ERROR": 0xFFA500,
                                                                                  "CRITICAL": 0xFF0000}, {"Бот": False}
BOTS, FOOTER = DB["settings"].find_one(filter={"_id": "Боты"}), DB["settings"].find_one(filter={"_id": "Футер"})
TIME = str(datetime.now(tz=timezone(zone="Europe/Moscow")))[:-13].replace(" ", "_").replace("-", "_").replace(":", "_")


async def logs(level, message, file=None):
    try:
        db = DB["settings"].find_one(filter={"_id": "Логи"})
        if level == "DEBUG" and not db["Дебаг"]:
            return None
        print(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level}:\n{message}\n\n")
        if not exists(path="temp/logs"):
            makedirs(name="temp/logs")
        with open(file=f"temp/logs/{TIME}.log",
                  mode="a+",
                  encoding="UTF-8") as log_file:
            log_file.write(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level}:\n{message}\n\n")
        time, username, avatar_url = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S")), "", ""
        if 80000 <= time < 200000:
            username = BOTS["868148805722337320"]["Имя"]
            avatar_url = BOTS["868148805722337320"]["Аватар"]
        else:
            username = BOTS["868150460735971328"]["Имя"]
            avatar_url = BOTS["868150460735971328"]["Аватар"]
        try:
            username = str(BOT.user.name)
            avatar_url = str(BOT.user.avatar_url)
        except Exception:
            pass
        webhook = AsyncDiscordWebhook(username=username,
                                      avatar_url=avatar_url,
                                      url=db["Вебхук"])
        if len(message) <= 4096:
            webhook.add_embed(embed=DiscordEmbed(title=level,
                                                 description=message,
                                                 color=LEVELS[level]))
        else:
            webhook.add_file(file=message.encode(encoding="UTF-8",
                                                 errors="ignore"),
                             filename=f"{level}.log")
        if file is not None:
            with open(file=f"temp/db/{file}",
                      mode="rb") as backup_file:
                webhook.add_file(file=backup_file.read(),
                                 filename=file)
        await webhook.execute()
    except Exception:
        await logs(level="CRITICAL",
                   message=format_exc())


async def backup():
    try:
        date = str(datetime.now(tz=timezone(zone="Europe/Moscow")))[:-13]
        time = date.replace(" ", "_").replace("-", "_").replace(":", "_")
        if not exists(path=f"temp/db/{time}"):
            makedirs(name=f"temp/db/{time}")
        for collection in DB.list_collections():
            file = []
            for item in DB[collection["name"]].find():
                file.append(item)
            with open(file=f"temp/db/{time}/{collection['name']}.py",
                      mode="w",
                      encoding="UTF-8") as db_file:
                db_file.write(f"{collection['name']} = {file}\n")
        result = s_run(args=f"bin\\zip\\x64\\7za.exe a -mx9 temp\\db\\mlpbots_{time}.zip temp\\db\\{time}",
                       shell=True,
                       capture_output=True,
                       text=True,
                       encoding="UTF-8",
                       errors="ignore")
        try:
            result.check_returncode()
        except Exception:
            raise Exception(result.stderr)
        await logs(level="INFO",
                   message="Бэкап БД создан успешно!",
                   file=f"mlpbots_{time}.zip")
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


async def restart():
    try:
        execl(executable, "python", "mlpbots.py")
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


async def autores():
    try:
        time = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S"))
        print(f"mlpbots: {time}")
        if 80000 <= time < 200000:
            try:
                if BOT.user.id != 868148805722337320:
                    await restart()
            except Exception:
                await logs(level="DEBUG",
                           message=format_exc())
        else:
            try:
                if BOT.user.id != 868150460735971328:
                    await restart()
            except Exception:
                await logs(level="DEBUG",
                           message=format_exc())
        Timer(interval=1,
              function=partial(run, main=autores())).start()
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


async def menu(button, menu_list, paginator):
    try:
        if button is None:
            return menu_list[paginator["Группа"]][paginator["Страница"]][0]
        if button == "previous_group":
            if paginator["Группа"] == 0:
                paginator.update({"Группа": len(menu_list) - 1, "Страница": 0})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
            else:
                paginator.update({"Группа": paginator["Группа"] - 1, "Страница": 0})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
        if button == "previous_page":
            if paginator["Страница"] == 0:
                paginator.update({"Страница": len(menu_list[paginator["Группа"]]) - 1})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
            else:
                paginator.update({"Страница": paginator["Страница"] - 1})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
        if button == "next_page":
            if paginator["Страница"] == len(menu_list[paginator["Группа"]]) - 1:
                paginator.update({"Страница": 0})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
            else:
                paginator.update({"Страница": paginator["Страница"] + 1})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
        if button == "next_group":
            if paginator["Группа"] == len(menu_list) - 1:
                paginator.update({"Группа": 0, "Страница": 0})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
            else:
                paginator.update({"Группа": paginator["Группа"] + 1, "Страница": 0})
                return menu_list[paginator["Группа"]][paginator["Страница"]][0]
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


async def mods(trigger, name, ok, error):
    try:
        if trigger == "on":
            try:
                BOT.load_extension(name=f"modules.{name.lower()}")
                ok.append(name.title())
                try:
                    DB["settings"].update_one(filter={"_id": "Разное"},
                                              update={"$pull": {"Отключенные модули": name.title()}})
                except Exception:
                    DB["settings"].update_one(filter={"_id": "Разное"},
                                              update={"$pull": {"Отключенные модули": name.lower()}})
            except Exception:
                error.append(name.title())
                await logs(level="DEBUG",
                           message=format_exc())
        if trigger == "off":
            try:
                BOT.unload_extension(name=f"modules.{name.lower()}")
                ok.append(name.title())
                try:
                    DB["settings"].update_one(filter={"_id": "Разное"},
                                              update={"$push": {"Отключенные модули": name.title()}})
                except Exception:
                    DB["settings"].update_one(filter={"_id": "Разное"},
                                              update={"$push": {"Отключенные модули": name.lower()}})
            except Exception:
                error.append(name.title())
                await logs(level="DEBUG",
                           message=format_exc())
        return ok, error
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.event
async def on_ready():
    try:
        try:
            DiscordComponents(bot=BOT)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            activity = DB["settings"].find_one(filter={"_id": "Боты"})[str(BOT.user.id)]["Статус"]
            await BOT.change_presence(activity=Activity(type=activity["Тип"],
                                                        name=activity["Название"]))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        if not TRIGGER["Бот"]:
            try:
                ok, error, modules = [], [], ""
                off = DB["settings"].find_one(filter={"_id": "Разное"})["Отключенные модули"]
                for filename in listdir("modules"):
                    if filename.endswith(".py"):
                        cog = filename[:-3]
                        if cog.lower() not in [x.lower() for x in off]:
                            try:
                                BOT.load_extension(name=f"modules.{cog.lower()}")
                                ok.append(cog.title())
                            except Exception:
                                error.append(cog.title())
                                await logs(level="DEBUG",
                                           message=format_exc())
                ok.sort()
                error.sort()
                off.sort()
                if len(ok) != 0:
                    modules += f"**Успешно:**\n" + "\n".join(x for x in ok)
                if len(error) != 0:
                    modules += "\n\n**Неудачно:**\n" + "\n".join(x for x in error)
                if len(off) > 0:
                    modules += "\n\n**Отключено:**\n" + "\n".join(x.title() for x in off)
                await logs(level="INFO",
                           message=modules)
            except Exception:
                await logs(level="ERROR",
                           message=format_exc())
            try:
                await backup()
            except Exception:
                await logs(level="ERROR",
                           message=format_exc())
            try:
                TRIGGER["Бот"] = True
            except Exception:
                await logs(level="ERROR",
                           message=format_exc())
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.event
async def on_message(message):
    try:
        await BOT.process_commands(message=message)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())
    try:
        db = DB["members"].find_one(filter={"_id": message.author.id})
        if db is not None:
            if db["Антиспам"]["Триггер"]:
                if message.created_at <= db["Антиспам"]["Блокировка"]:
                    try:
                        await message.delete()
                    except Exception:
                        await logs(level="DEBUG",
                                   message=format_exc())
                    DB["members"].update_one(filter={"_id": message.author.id},
                                             update={"$inc": {"Антиспам.Количество": 1}})
                    if db["Антиспам"]["Количество"] >= 3:
                        block = db["Антиспам"]["Блокировка"] + timedelta(minutes=1)
                        DB["members"].update_one(filter={"_id": message.author.id},
                                                 update={"$set": {"Антиспам.Блокировка": block,
                                                                  "Антиспам.Количество": 0}})
                        embed = Embed(title="Уведомление!",
                                      color=0xFFA500)
                        delta = (block - datetime.utcnow()).seconds
                        embed.add_field(name="Блокировка за спам!",
                                        value=f"Ваше время блокировки было увеличено на **60 секунд** за повторный "
                                              f"спам!\n\nОставшееся время блокировки: **{delta} секунд**.")
                        embed.set_thumbnail(url=BOT.user.avatar_url)
                        embed.set_footer(text=FOOTER["Текст"],
                                         icon_url=FOOTER["Ссылка"])
                        await message.author.send(embed=embed)
                else:
                    DB["members"].update_one(filter={"_id": message.author.id},
                                             update={"$set": {"Антиспам.Триггер": False}})
            else:
                if message.author.id not in [868148805722337320, 868150460735971328] and message.content != "":
                    messages = db["Антиспам"]["Сообщения"]
                    if (message.created_at - db["Антиспам"]["Время"]).seconds <= 15:
                        messages.insert(0, message.content)
                        if len(messages) == 4:
                            messages.pop()
                    else:
                        messages.clear()
                        messages.insert(0, message.content)
                    DB["members"].update_one(filter={"_id": message.author.id},
                                             update={"$set": {"Антиспам.Время": message.created_at,
                                                              "Антиспам.Сообщения": messages}})
                    if len(messages) >= 3:
                        messages = messages
                        messages_1 = [len(messages[1]) + 1, len(messages[1]), len(messages[1]) - 1]
                        messages_2 = [len(messages[2]) + 1, len(messages[2]), len(messages[2]) - 1]
                        if token_sort_ratio(messages[0], messages[1]) >= 90 or len(messages[0]) in messages_1:
                            if token_sort_ratio(messages[1], messages[2]) >= 90 or len(messages[1]) in messages_2:
                                try:
                                    await message.delete()
                                except Exception:
                                    await logs(level="DEBUG",
                                               message=format_exc())
                                block = message.created_at + timedelta(minutes=1)
                                messages.clear()
                                DB["members"].update_one(filter={"_id": message.author.id},
                                                         update={"$set": {"Антиспам.Триггер": True,
                                                                          "Антиспам.Сообщения": messages,
                                                                          "Антиспам.Блокировка": block,
                                                                          "Антиспам.Количество": 0}})
                                embed = Embed(title="Уведомление!",
                                              color=0xFFA500)
                                embed.add_field(name="Блокировка за спам!",
                                                value="Вы были заблокированы на **60 секунд** за спам!")
                                embed.set_thumbnail(url=BOT.user.avatar_url)
                                embed.set_footer(text=FOOTER["Текст"],
                                                 icon_url=FOOTER["Ссылка"])
                                await message.author.send(embed=embed)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())
    try:
        if message.author.id not in [868148805722337320, 868150460735971328]:
            if "пон" in message.content or "pon" in message.content:
                await message.reply(content=choice(seq=DB["settings"].find_one(filter={"_id": "Разное"})["Пони"]))
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.event
async def on_raw_reaction_add(payload):
    try:
        post, like, dlike = await BOT.get_channel(id=payload.channel_id).fetch_message(id=payload.message_id), 0, 0
        for reaction in post.reactions:
            if reaction.emoji == "👍":
                like = int(reaction.count)
            if reaction.emoji == "👎":
                dlike = int(reaction.count)
            try:
                await post.add_reaction(emoji=reaction)
            except Exception:
                await logs(level="DEBUG",
                           message=format_exc())
        if like - dlike >= int(BOT.guilds[0].member_count / 3):
            await post.pin()
        if dlike - like >= int(BOT.guilds[0].member_count / 3):
            await post.delete()
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.event
async def on_member_join(member):
    try:
        embed = Embed(title="В наш клуб присоединилась милая поняшка!",
                      color=0xBA55D3,
                      description=f"Поприветствуем: {member.mention}!")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_image(url=choice(seq=DB["settings"].find_one(filter={"_id": "Разное"})["Арты приветствия"]))
        embed.set_footer(text=FOOTER["Текст"],
                         icon_url=FOOTER["Ссылка"])
        await BOT.get_channel(id=DB["channels"].find_one(filter={"Категория": "Главный"})["_id"]).send(embed=embed)
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


# команды пользователей
@BOT.command(description="Все 1",
             name="help",
             help="Показать список всех команд бота",
             brief="Не применимо",
             usage="!help")
async def command_help(ctx):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            raw_commands, commands, i = [[x.description for x in BOT.commands], [x.name for x in BOT.commands],
                                         [x.help for x in BOT.commands], [x.brief for x in BOT.commands],
                                         [x.usage for x in BOT.commands]], [], 0
            while i < len(raw_commands[0]):
                list_sort = [raw_commands[0][i], raw_commands[1][i], raw_commands[2][i], raw_commands[3][i],
                             raw_commands[4][i]]
                commands.append(list_sort)
                i += 1
            commands.sort()
            menu_list = []
            if "Все 1" in [x[0] for x in commands]:
                try:
                    menu_list[0]
                except Exception:
                    menu_list.append([])
                menu_list[0].append([])
            if "Все 2" in [x[0] for x in commands]:
                try:
                    menu_list[0]
                except Exception:
                    menu_list.append([])
                menu_list[0].append([])
            if "Все 3" in [x[0] for x in commands]:
                try:
                    menu_list[0]
                except Exception:
                    menu_list.append([])
                menu_list[0].append([])
            if ctx.author.permissions_in(channel=ctx.channel).manage_messages:
                if "Модераторы 1" in [x[0] for x in commands]:
                    menu_list.append([[]])
            if ctx.author.guild_permissions.administrator:
                if "Админы 1" in [x[0] for x in commands]:
                    menu_list.append([[]])
            if ctx.author.id == 496139824500178964:
                if "Создатель 1" in [x[0] for x in commands]:
                    menu_list.append([[]])
            group, page = 0, 0
            if "Все 1" in [x[0] for x in commands]:
                menu_list[group][page].append(Embed(title="Список всех команд:",
                                                    color=ctx.author.color,
                                                    description=f"⏮️ Переключение группы ({group + 1} из "
                                                                f"{len(menu_list)}) ⏭️\n"
                                                                f"**Команды пользователей:** "
                                                                f"Общедоступные команды бота.\n"
                                                                f"⏪ Переключение страницы ({page + 1} из "
                                                                f"{len(menu_list[group])}) ⏩\n"
                                                                f"**Команды информации:** "
                                                                f"Команды для получение какой либо информации."))
                i = 0
                while i < len(commands):
                    command = commands[i][0].split(" ")
                    if command[0] == "Все":
                        if command[1] == "1":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
            if "Все 2" in [x[0] for x in commands]:
                page += 1
                menu_list[group][page].append(Embed(title="Список всех команд:",
                                                    color=ctx.author.color,
                                                    description=f"⏮️ Переключение группы ({group + 1} из "
                                                                f"{len(menu_list)}) ⏭️\n"
                                                                f"**Команды пользователей:** "
                                                                f"Общедоступные команды бота.\n"
                                                                f"⏪ Переключение страницы ({page + 1} из "
                                                                f"{len(menu_list[group])}) ⏩\n"
                                                                f"**Команды управления:** "
                                                                f"Команды для управления чем либо."))
                i = 0
                while i < len(commands):
                    command = commands[i][0].split(" ")
                    if command[0] == "Все":
                        if command[1] == "2":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
            if "Все 3" in [x[0] for x in commands]:
                page += 1
                menu_list[group][page].append(Embed(title="Список всех команд:",
                                                    color=ctx.author.color,
                                                    description=f"⏮️ Переключение группы ({group + 1} из "
                                                                f"{len(menu_list)}) ⏭️\n"
                                                                f"**Команды пользователей:** "
                                                                f"Общедоступные команды бота.\n"
                                                                f"⏪ Переключение страницы ({page + 1} из "
                                                                f"{len(menu_list[group])}) ⏩\n"
                                                                f"**Команды развлечений:** "
                                                                f"Команды для развлекательных целей."))
                i = 0
                while i < len(commands):
                    command = commands[i][0].split(" ")
                    if command[0] == "Все":
                        if command[1] == "3":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
            if ctx.author.permissions_in(channel=ctx.channel).manage_messages:
                if "Модераторы 1" in [x[0] for x in commands]:
                    group += 1
                    page = 0
                    menu_list[group][page].append(Embed(title="Список всех команд:",
                                                        color=ctx.author.color,
                                                        description=f"⏮️ Переключение группы ({group + 1} из "
                                                                    f"{len(menu_list)}) ⏭️\n"
                                                                    f"**Команды модераторов:** "
                                                                    f"Специальные команды только для модераторов.\n"
                                                                    f"⏪ Переключение страницы ({page + 1} из "
                                                                    f"{len(menu_list[group])}) ⏩\n"))
                    i = 0
                    while i < len(commands):
                        command = commands[i][0].split(" ")
                        if command[0] == "Модераторы":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
            if ctx.author.guild_permissions.administrator:
                if "Админы 1" in [x[0] for x in commands]:
                    group += 1
                    page = 0
                    menu_list[group][page].append(Embed(title="Список всех команд:",
                                                        color=ctx.author.color,
                                                        description=f"⏮️ Переключение группы ({group + 1} из "
                                                                    f"{len(menu_list)}) ⏭️\n"
                                                                    f"**Команды администраторов:** "
                                                                    f"Специальные команды только для администраторов.\n"
                                                                    f"⏪ Переключение страницы ({page + 1} из "
                                                                    f"{len(menu_list[group])}) ⏩\n"))
                    i = 0
                    while i < len(commands):
                        command5 = commands[i][0].split(" ")
                        if command5[0] == "Админы":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
            if ctx.author.id == 496139824500178964:
                if "Создатель 1" in [x[0] for x in commands]:
                    group += 1
                    page = 0
                    menu_list[group][page].append(Embed(title="Список всех команд:",
                                                        color=ctx.author.color,
                                                        description=f"⏮️ Переключение группы ({group + 1} из "
                                                                    f"{len(menu_list)}) ⏭️\n"
                                                                    f"**Команды создателя бота:** "
                                                                    f"Специальные команды только для создателя бота.\n"
                                                                    f"⏪ Переключение страницы ({page + 1} из "
                                                                    f"{len(menu_list[group])}) ⏩\n"))
                    i = 0
                    while i < len(commands):
                        command6 = commands[i][0].split(" ")
                        if command6[0] == "Создатель":
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}",
                                                                inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
            paginator = {"Группа": 0,
                         "Страница": 0}
            components, post = [[Button(emoji="⏮️",
                                        style=ButtonStyle.blue,
                                        id="previous_group"),
                                 Button(emoji="⏪",
                                        style=ButtonStyle.blue,
                                        id="previous_page"),
                                 Button(emoji="⏩",
                                        style=ButtonStyle.blue,
                                        id="next_page"),
                                 Button(emoji="⏭️",
                                        style=ButtonStyle.blue,
                                        id="next_group")]], None
            if post is None:
                post = await ctx.send(embed=await menu(button=None,
                                                       menu_list=menu_list,
                                                       paginator=paginator),
                                      delete_after=60,
                                      components=components)
            while True:
                interaction = await BOT.wait_for(event="button_click")
                try:
                    await BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                except Exception:
                    break
                if interaction.message.id == post.id:
                    if interaction.user.id == ctx.author.id:
                        await post.edit(embed=await menu(button=interaction.component.id,
                                                         menu_list=menu_list,
                                                         paginator=paginator),
                                        delete_after=60,
                                        components=components)
                try:
                    await interaction.respond()
                except Exception:
                    pass
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.command(description="Все 1",
             name="ava",
             help="Прислать аватарку пользователя",
             brief="Ничего / `Упоминание пользователя`",
             usage="!ava <@918687493577121884>")
async def command_ava(ctx, member: Member = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            if not member:
                member = ctx.message.author
            await ctx.send(content=member.avatar_url)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


# команды модераторов
@BOT.command(description="Модераторы 1",
             name="mute",
             help="Просмотр заблокированных пользователей",
             brief="Не применимо",
             usage="!mute")
@has_permissions(manage_messages=True)
async def command_mute(ctx):
    try:
        if str(ctx.channel.type) == "text":
            if DB["members"].count_documents(filter={"Антиспам.Триггер": True}) > 0:
                embed = Embed(title="Заблокированные пользователи:",
                              color=ctx.author.color)
                i = 1
                for member in DB["members"].find({"Антиспам.Триггер": True}):
                    delta = (member["Антиспам"]["Блокировка"] - datetime.utcnow()).seconds
                    embed.add_field(name=f"Пользователь {i}:",
                                    value=f"**Имя:** <@{member['_id']}>\n"
                                          f"**Оставшееся время:** {delta} секунд.")
            else:
                embed = Embed(title="Заблокированные пользователи:",
                              color=ctx.author.color,
                              description="Сейчас нет заблокированных пользователей.")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed,
                           delete_after=60)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.command(description="Модераторы 1",
             name="del",
             help="Удалить указанное количество сообщений",
             brief="`Количество сообщений` / `Упоминание пользователя`",
             usage="!del 10 <@918687493577121884>")
@has_permissions(manage_messages=True)
async def command_del(ctx, amount: int = 0, member: Member = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            if not member:
                await ctx.channel.purge(limit=amount)
                embed = Embed(title="Сообщения удалены успешно:",
                              color=ctx.author.color,
                              description=f"Количество: **{amount}**\n"
                                          f"Пользователь: **Все**")
            else:
                messages = []
                async for message in ctx.channel.history():
                    if len(messages) == amount:
                        break
                    if message.author == member:
                        messages.append(message)
                await ctx.channel.delete_messages(messages=messages)
                embed = Embed(title="Сообщения удалены успешно:",
                              color=ctx.author.color,
                              description=f"Количество: **{len(messages)}**\n"
                                          f"Пользователь: **{member.mention}**")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed,
                           delete_after=60)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


# команды администраторов
@BOT.command(description="Админы 1",
             name="mods",
             help="Управление модулями",
             brief="Ничего / `Параметр` / `Название модуля`",
             usage="!mods on commands")
@has_permissions(administrator=True)
async def command_mods(ctx, trigger: str = None, name: str = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            embed = None
            if trigger is None and name is None:
                on, off = [], []
                for filename in listdir("modules"):
                    if filename.endswith(".py"):
                        cog = filename[:-3]
                        if cog.title() in [x.title() for x in BOT.cogs]:
                            on.append(cog.title())
                        else:
                            off.append(cog.title())
                on.sort()
                off.sort()
                embed = Embed(title="Список всех модулей:",
                              color=ctx.author.color)
                embed.add_field(name="Команды управления:",
                                inline=False,
                                value="Включить модуль: **!mods on `название модуля`**\n"
                                      "Отключить модуль: **!mods off `название модуля`**\n"
                                      "Перезагрузить модуль: **!mods res `название модуля`**")
                if len(on) != 0:
                    embed.add_field(name="Включено:",
                                    inline=False,
                                    value=f"\n".join(x for x in on))
                if len(off) != 0:
                    embed.add_field(name="Отключено:",
                                    inline=False,
                                    value=f"\n".join(x for x in off))
            if trigger is not None:
                ok, error, alert = [], [], []
                if trigger == "on":
                    if name is not None:
                        if name.title() in [x.title() for x in BOT.cogs]:
                            alert.append(name.title())
                        else:
                            ok, error = await mods(trigger=trigger,
                                                   name=name,
                                                   ok=ok,
                                                   error=error)
                    else:
                        for filename in listdir("modules"):
                            if filename.endswith(".py"):
                                name = filename[:-3]
                                if name.title() in [x.title() for x in BOT.cogs]:
                                    alert.append(name.title())
                                else:
                                    ok, error = await mods(trigger=trigger,
                                                           name=name,
                                                           ok=ok,
                                                           error=error)
                    ok.sort()
                    error.sort()
                    alert.sort()
                    embed = Embed(title="Подключение модулей:",
                                  color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:",
                                        inline=False,
                                        value=f"\n".join(cog for cog in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:",
                                        inline=False,
                                        value=f"\n".join(cog for cog in error))
                    if len(alert) != 0:
                        embed.add_field(name="Ошибка:",
                                        inline=False,
                                        value="\n".join(f"Модуль \"{cog}\" уже включен!" for cog in alert))
                if trigger == "off":
                    if name is not None:
                        if name.title() not in [x.title() for x in BOT.cogs]:
                            alert.append(name.title())
                        else:
                            ok, error = await mods(trigger=trigger,
                                                   name=name,
                                                   ok=ok,
                                                   error=error)
                    else:
                        for filename in listdir("modules"):
                            if filename.endswith(".py"):
                                name = filename[:-3]
                                if name.title() not in [x.title() for x in BOT.cogs]:
                                    alert.append(name.title())
                                else:
                                    ok, error = await mods(trigger=trigger,
                                                           name=name,
                                                           ok=ok,
                                                           error=error)
                    ok.sort()
                    error.sort()
                    alert.sort()
                    embed = Embed(title="Отключение модулей:",
                                  color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:",
                                        inline=False,
                                        value=f"\n".join(x for x in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:",
                                        inline=False,
                                        value=f"\n".join(x for x in error))
                    if len(alert) != 0:
                        embed.add_field(name="Ошибка:",
                                        inline=False,
                                        value="\n".join(f"Модуль \"{x}\" уже отключен!" for x in alert))
                if trigger == "res":
                    if name is not None:
                        try:
                            BOT.unload_extension(name=f"modules.{name.lower()}")
                            BOT.load_extension(name=f"modules.{name.lower()}")
                            ok.append(name.title())
                        except Exception:
                            error.append(name.title())
                            await logs(level="DEBUG",
                                       message=format_exc())
                    else:
                        for filename in listdir("modules"):
                            if filename.endswith(".py"):
                                cog = filename[:-3]
                                try:
                                    BOT.unload_extension(name=f"modules.{cog.lower()}")
                                    BOT.load_extension(name=f"modules.{cog.lower()}")
                                    ok.append(cog.title())
                                except Exception:
                                    error.append(cog.title())
                                    await logs(level="DEBUG",
                                               message=format_exc())
                    ok.sort()
                    error.sort()
                    embed = Embed(title="Перезагрузка модулей:",
                                  color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:",
                                        inline=False,
                                        value=f"\n".join(x for x in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:",
                                        inline=False,
                                        value=f"\n".join(x for x in error))
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed,
                           delete_after=60)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


@BOT.command(description="Админы 1",
             name="res",
             help="Полная перезагрузка бота",
             brief="Не применимо",
             usage="!res")
@has_permissions(administrator=True)
async def command_res(ctx):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            await sleep(delay=1)
            await restart()
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


# команды создателя
@BOT.command(description="Создатель 1",
             name="debug",
             help="Вывод дебаг сообщений в лог",
             brief="`On` / `Off`",
             usage="!debug on")
async def command_debug(ctx, trigger: str = "on"):
    try:
        if str(ctx.channel.type) == "text":
            if ctx.author.id == 496139824500178964:
                if trigger.lower() == "on" or trigger.lower() == "off":
                    await ctx.message.delete(delay=1)
                    embed = None
                    if trigger.lower() == "on":
                        DB["settings"].update_one(filter={"_id": "Логи"},
                                                  update={"$set": {"Дебаг": True}})
                        embed = Embed(title="Дебаг:",
                                      color=ctx.author.color,
                                      description="Дебаг **включен**!")
                    if trigger.lower() == "off":
                        DB["settings"].update_one(filter={"_id": "Логи"},
                                                  update={"$set": {"Дебаг": False}})
                        embed = Embed(title="Дебаг:",
                                      color=ctx.author.color,
                                      description="Дебаг **отключен**!")
                    embed.set_footer(text=FOOTER["Текст"],
                                     icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed,
                                   delete_after=60)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


# скрытые команды
@BOT.command(description="Скрыто 1",
             name="ban",
             help="",
             brief="",
             usage="")
async def command_ban(ctx, member: Member = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            if member is not None:
                embed = Embed(title="Бан пользователей:",
                              color=ctx.author.color,
                              description=f"Пользователь {member.mention} успешно забанен!")
            else:
                users = [user.mention for user in BOT.users]
                embed = Embed(title="Бан пользователей:",
                              color=ctx.author.color,
                              description=f"Пользователи {', '.join(users)} успешно забанены!")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed)
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


if __name__ == "__main__":
    try:
        run(main=autores())
        if 80000 <= int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S")) < 200000:
            BOT.run(BOTS["868148805722337320"]["Токен"])
        else:
            BOT.run(BOTS["868150460735971328"]["Токен"])
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
