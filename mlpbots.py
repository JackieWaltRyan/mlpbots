from sys import executable

from asyncio import run, sleep
from datetime import datetime
from discord import Activity, Embed, Intents, Member
from discord.ext.commands import Bot, has_permissions, when_mentioned_or
from discord_components_mirror import Button, ButtonStyle, DiscordComponents
from discord_webhook import DiscordEmbed, DiscordWebhook
from fuzzywuzzy.fuzz import token_sort_ratio
from os import listdir, makedirs, system, execl
from os.path import exists
from pytz import timezone
from random import choice
from threading import Timer
from traceback import format_exc

BOT, SPAM, BLOCK = Bot(command_prefix=when_mentioned_or("!"), help_command=None, intents=Intents.all()), {}, []
FOOTER = {"Текст": "Все права принадлежат пони! Весь мир принадлежит пони!",
          "Ссылка": "https://cdn.discordapp.com/attachments/1021085537802649661/1021092052487909458/NoDRM.png"}
LEVELS, TRIGGER = {1: {"Название": "DEBUG", "Цвет": 0x0000FF}, 2: {"Название": "INFO", "Цвет": 0x008000},
                   3: {"Название": "WARNING", "Цвет": 0xFFFF00}, 4: {"Название": "ERROR", "Цвет": 0xFFA500},
                   5: {"Название": "CRITICAL", "Цвет": 0xFF0000}}, {"Сохранение": False, "Бэкап": False}
TIME = str(datetime.now(tz=timezone(zone="Europe/Moscow")))[:-13].replace(" ", "_").replace("-", "_").replace(":", "_")


async def logs(level, message, file=None):
    try:
        if level == LEVELS[1]:
            from db.settings import settings
            if not settings["Дебаг"]:
                return None
        print(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level['Название']}\n{message}")
        if not exists(path="temp/logs"):
            makedirs(name="temp/logs")
        with open(file=f"temp/logs/{TIME}.log", mode="a+", encoding="UTF-8") as log_file:
            log_file.write(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level['Название']}:\n{message}\n\n")
        time, username, avatar_url = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S")), "", ""
        if 80000 <= time < 200000:
            username = "Принцесса Селестия"
            avatar_url = "https://cdn.discordapp.com/attachments/1021085537802649661/1021090387030462585/celestia.jpg"
        else:
            username = "Принцесса Луна"
            avatar_url = "https://cdn.discordapp.com/attachments/1021085537802649661/1021090386753634454/luna.jpg"
        try:
            username = str(BOT.user.name)
            avatar_url = str(BOT.user.avatar_url)
        except Exception:
            pass
        webhook = DiscordWebhook(username=username, avatar_url=avatar_url, url="")
        webhook.add_embed(embed=DiscordEmbed(title=level["Название"], description=str(message), color=level["Цвет"]))
        if file is not None:
            with open(file=f"temp/backups/{file}", mode="rb") as backup_file:
                webhook.add_file(file=backup_file.read(), filename=file)
        webhook.execute()
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


async def save(file, content):
    try:
        while True:
            if not TRIGGER["Сохранение"]:
                TRIGGER["Сохранение"] = True
                if not exists(path="db"):
                    makedirs(name="db")
                if file in ["members"]:
                    with open(file=f"db/{file}.py", mode="w", encoding="UTF-8") as db_file:
                        db_file.write(f"import datetime\n\n{file} = {content}\n")
                else:
                    with open(file=f"db/{file}.py", mode="w", encoding="UTF-8") as db_file:
                        db_file.write(f"{file} = {content}\n")
                TRIGGER["Сохранение"] = False
                break
            else:
                print("Идет сохранение...")
                await sleep(delay=1)
    except Exception:
        TRIGGER["Сохранение"] = False
        await logs(level=LEVELS[4], message=format_exc())


async def backup():
    try:
        if not TRIGGER["Бэкап"]:
            TRIGGER["Бэкап"] = True
            if not exists(path="temp/backups"):
                makedirs(name="temp/backups")
            date = str(datetime.now(tz=timezone(zone="Europe/Moscow")))[:-13]
            time = date.replace(" ", "_").replace("-", "_").replace(":", "_")
            system(command=f"bin\\zip\\x64\\7za.exe a -mx9 temp\\backups\\mlpbots_{time}.zip db")
            await logs(level=LEVELS[2], message=f"Бэкап БД создан успешно!", file=f"mlpbots_{time}.zip")
            TRIGGER["Бэкап"] = False
    except Exception:
        TRIGGER["Бэкап"] = False
        await logs(level=LEVELS[4], message=format_exc())


async def autores():
    try:
        time = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S"))
        print(f"mlpbots: {time}")
        if 80000 <= time < 200000:
            try:
                if BOT.user.id != 868148805722337320:
                    try:
                        execl(executable, executable, "mlpbots.py")
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
                        execl("bin/python/python.exe", "bin/python/python.exe", "mlpbots.py")
            except Exception:
                await logs(level=LEVELS[1], message=format_exc())
        else:
            try:
                if BOT.user.id != 868150460735971328:
                    try:
                        execl(executable, executable, "mlpbots.py")
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
                        execl("bin/python/python.exe", "bin/python/python.exe", "mlpbots.py")
            except Exception:
                await logs(level=LEVELS[1], message=format_exc())
        Timer(interval=1, function=lambda: run(main=autores())).start()
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


@BOT.event
async def on_ready():
    try:
        DiscordComponents(bot=BOT)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())
    try:
        bots = {868148805722337320: {"Тип": 3, "Название": "за Эквестрией..."},
                868150460735971328: {"Тип": 2, "Название": "тишину ночи..."}}
        await BOT.change_presence(activity=Activity(type=bots[BOT.user.id]["Тип"], name=bots[BOT.user.id]["Название"]))
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())
    try:
        from db.settings import settings
        ok, error, modules = [], [], ""
        for filename in listdir("modules"):
            if filename.endswith(".py"):
                cog = filename[:-3]
                if cog.lower() not in [x.lower() for x in settings["Отключенные модули"]]:
                    try:
                        BOT.load_extension(name=f"modules.{cog.lower()}")
                        ok.append(cog.title())
                    except Exception:
                        error.append(cog.title())
                        await logs(level=LEVELS[1], message=format_exc())
        ok.sort()
        error.sort()
        settings["Отключенные модули"].sort()
        if len(ok) != 0:
            modules += f"**Успешно:**\n" + "\n".join(x for x in ok)
        if len(error) != 0:
            modules += "\n\n**Неудачно:**\n" + "\n".join(x for x in error)
        if len(settings["Отключенные модули"]) > 0:
            modules += "\n\n**Отключено:**\n" + "\n".join(x.title() for x in settings["Отключенные модули"])
        await logs(level=LEVELS[2], message=modules)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())
    try:
        await backup()
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


@BOT.event
async def on_message(message):
    try:
        await BOT.process_commands(message=message)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())
    try:
        if message.author.id in BLOCK:
            try:
                await message.delete()
            except Exception:
                pass
        else:
            if message.author.id not in [868148805722337320, 868150460735971328]:
                if message.content != "":
                    if SPAM.get(message.author.id) is None:
                        SPAM.update({message.author.id: {"Время": message.created_at, "Сообщения": [message.content]}})
                    else:
                        delta = message.created_at - SPAM[message.author.id]["Время"]
                        SPAM[message.author.id].update({"Время": message.created_at})
                        if int(delta.total_seconds()) <= 15:
                            SPAM[message.author.id]["Сообщения"].insert(0, message.content)
                        else:
                            SPAM[message.author.id]["Сообщения"].clear()
                            SPAM[message.author.id]["Сообщения"].insert(0, message.content)
                    if len(SPAM[message.author.id]["Сообщения"]) >= 3:
                        mes = SPAM[message.author.id]["Сообщения"]
                        mes_1 = [len(mes[1]) + 1, len(mes[1]), len(mes[1]) - 1]
                        mes_2 = [len(mes[2]) + 1, len(mes[2]), len(mes[2]) - 1]
                        if token_sort_ratio(mes[0], mes[1]) >= 95 or len(mes[0]) in mes_1:
                            if token_sort_ratio(mes[1], mes[2]) >= 95 or len(mes[1]) in mes_2:
                                try:
                                    await message.delete()
                                except Exception:
                                    pass
                                embed = Embed(title="Уведомление!", color=0xFFA500)
                                embed.add_field(name="Блокировка за спам!",
                                                value="Вы были заблокированы на **60 секунд** за спам!")
                                embed.set_thumbnail(url=BOT.user.avatar_url)
                                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                                await message.author.send(embed=embed)
                                BLOCK.append(message.author.id)
                                SPAM[message.author.id]["Сообщения"].clear()
                                await sleep(delay=60)
                                BLOCK.remove(message.author.id)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())
    try:
        if message.author.id not in [868148805722337320, 868150460735971328]:
            if "пон" in message.content or "pon" in message.content:
                from db.mafia import mafia
                await message.reply(content=choice(seq=mafia["Боты"]))
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


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
                await logs(level=LEVELS[1], message=format_exc())
        from db.members import members
        actives, bots = 0, 0
        for member in members.values():
            if member["Статус"]:
                actives += 1
            if member["Бот"]:
                bots += 1
        if like - dlike >= int((actives - bots) / 3):
            await post.pin()
        if dlike - like >= int((actives - bots) / 3):
            await post.delete()
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


@BOT.event
async def on_member_join(member):
    try:
        arts = ["https://cdn.discordapp.com/attachments/1021085537802649661/1044627897136205914/hoodie_cloud.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627897832443924/skittles.jpg",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627898151227482/smug_pipp_petals.jpg",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627898654531674/sunset_in_raincoat.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627899094945792/coloratura.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627899514359860/commission_bizuni.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627900189659217/cute_pony.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627900831371374/filly_coco_pomme.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627901288566784/fluttershy.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627901628293220/fluttershy_waited.jpg",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627902685253733/shortcut_twi.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627903117271171/pegabrushies.png",
                "https://cdn.discordapp.com/attachments/1021085537802649661/1044627903775785091/princess_luna.png"]
        embed = Embed(title="В наш клуб присоединилась милая поняшка!", color=0xBA55D3,
                      description=f"Поприветствуем: {member.mention}!")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_image(url=choice(seq=arts))
        embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
        await BOT.get_channel(id=1007577226037968986).send(embed=embed)
        from db.members import members
        members.update({member.id: {"Имя аккаунта": f"{member.name}#{member.discriminator}",
                                    "Статус": True,
                                    "Время последнего сообщения": datetime.utcnow(),
                                    "Уведомления": False,
                                    "Радуга": False,
                                    "Бот": member.bot,
                                    "Достижения": [],
                                    "Дни": 0,
                                    "Сообщения": 0,
                                    "Упоминания": 0,
                                    "Лайки": 0,
                                    "Дизлайки": 0,
                                    "Дата добавления на сервер": member.joined_at,
                                    "Роли": [],
                                    "Похищенная пони": {"Страница": "p0", "Концовки": []},
                                    "Крестики-нолики": {"Сыграно": 0, "Побед": 0, "Поражений": 0, "Процент": 0},
                                    "Тетрис": {"Сыграно": 0, "Лучший счет": 0}}})
        await save(file="members", content=members)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


# команды пользователей
@BOT.command(description="Все 1", name="help", help="Показать список всех команд бота", brief="Не применимо",
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
                menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
                page += 1
            if "Все 2" in [x[0] for x in commands]:
                menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
                page += 1
            if "Все 3" in [x[0] for x in commands]:
                menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                    i += 1
                page = 0
                group += 1
            if ctx.author.permissions_in(channel=ctx.channel).manage_messages:
                if "Модераторы 1" in [x[0] for x in commands]:
                    menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
                page = 0
                group += 1
            if ctx.author.guild_permissions.administrator:
                if "Админы 1" in [x[0] for x in commands]:
                    menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
                page = 0
                group += 1
            if ctx.author.id == 496139824500178964:
                if "Создатель 1" in [x[0] for x in commands]:
                    menu_list[group][page].append(Embed(title="Список всех команд:", color=ctx.author.color,
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
                            menu_list[group][page][0].add_field(name=f"{commands[i][1]}", inline=False,
                                                                value=f"Описание: {commands[i][2]}\n"
                                                                      f"Параметр: {commands[i][3]}\n"
                                                                      f"Пример: {commands[i][4]}")
                        i += 1
            paginator = {"Группа": 0, "Страница": 0}

            def menu(button):
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

            components, post = [[Button(emoji="⏮️", style=ButtonStyle.blue, id="previous_group"),
                                 Button(emoji="⏪", style=ButtonStyle.blue, id="previous_page"),
                                 Button(emoji="⏩", style=ButtonStyle.blue, id="next_page"),
                                 Button(emoji="⏭️", style=ButtonStyle.blue, id="next_group")]], None
            if post is None:
                post = await ctx.send(embed=menu(button=None), delete_after=60, components=components)
            while True:
                interaction = await BOT.wait_for(event="button_click")
                try:
                    await BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                except Exception:
                    break
                if interaction.message.id == post.id:
                    if interaction.user.id == ctx.author.id:
                        await post.edit(embed=menu(button=interaction.component.id), delete_after=60,
                                        components=components)
                try:
                    await interaction.respond()
                except Exception:
                    pass
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


# команды администраторов
@BOT.command(description="Админы 1", name="mods", help="Управление модулями",
             brief="Ничего / `Параметр` / `Название модуля`", usage="!mods on commands")
@has_permissions(administrator=True)
async def command_mods(ctx, trigger: str = None, name: str = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            descriptions = {"achievements": "Модуль отвечает за все достижения и все что с ними связано.\n\nКоманды в "
                                            "модуле: !achievements",
                            "activity": "Модуль отвечает за обновление БД, подсчет статистики, и управление "
                                        "неактивными пользователями.",
                            "arts": f"Модуль отвечает за публикацию новых артов в канале <#1007577227380146267> и "
                                    f"<#1007577232975339551>.\n\nКоманды в модуле: !arts",
                            "commands": "Модуль отвечает за все команды бота кроме административных. Даже если модуль "
                                        "отключен, команда \"!help\", команды управления модулями (!mods), и команда "
                                        "перезагрузки бота (!res) по прежнему будут работать.",
                            "game": "Модуль отвечает за игру \"Похищенная пони\" и все что с ней связанно.",
                            "player": f"Модуль отвечает за музыкальный плеер в канале <#1007585194863251468> и все "
                                      f"что с ним связанно.",
                            "posts": "Модуль отвечает за обновление всех постов в категории \"Добро Пожаловать!\" и "
                                     "обработку их кнопок и селекторов.",
                            "rainbow": "Модуль отвечает за динамическое изменение цвета ников. Проще говоря \"Радужная "
                                       "роль\".\n\nКоманды в модуле: !rainbow",
                            "tetris": "Модуль отвечает за мини-игру \"Тетрис\" и все что с ней связанно.\n\nКоманды в "
                                      "модуле: !tet",
                            "tictactoe": "Модуль отвечает за мини-игру \"Крестики-нолики\" и все что с ней связанно."
                                         "\n\nКоманды в модуле: !tic"}
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
                embed = Embed(title="Список всех модулей:", color=ctx.author.color)
                embed.add_field(name="Команды управления:", inline=False,
                                value="Подробное описание модуля: **!mods `название модуля`**\n"
                                      "Включить модуль: **!mods on `название модуля`**\n"
                                      "Отключить модуль: **!mods off `название модуля`**\n"
                                      "Перезагрузить модуль: **!mods res `название модуля`**")
                if len(on) != 0:
                    embed.add_field(name="Включено:", inline=False, value=f"\n".join(x for x in on))
                if len(off) != 0:
                    embed.add_field(name="Отключено:", inline=False, value=f"\n".join(x for x in off))
            from db.settings import settings
            if trigger is not None:
                ok, error, alert = [], [], []
                if trigger == "on":
                    if name is not None:
                        if name.title() in [x.title() for x in BOT.cogs]:
                            alert.append(name.title())
                        else:
                            try:
                                BOT.load_extension(name=f"modules.{name.lower()}")
                                ok.append(name.title())
                                try:
                                    settings["Отключенные модули"].remove(name.lower())
                                except Exception:
                                    settings["Отключенные модули"].remove(name.title())
                                await save(file="settings", content=settings)
                            except Exception:
                                error.append(name.title())
                                await logs(level=LEVELS[1], message=format_exc())
                    else:
                        for filename in listdir("modules"):
                            if filename.endswith(".py"):
                                cog = filename[:-3]
                                if cog.title() in [x.title() for x in BOT.cogs]:
                                    alert.append(cog.title())
                                else:
                                    try:
                                        BOT.load_extension(name=f"modules.{cog.lower()}")
                                        ok.append(cog.title())
                                        try:
                                            settings["Отключенные модули"].remove(cog.lower())
                                        except Exception:
                                            settings["Отключенные модули"].remove(cog.title())
                                        await save(file="settings", content=settings)
                                    except Exception:
                                        error.append(cog.title())
                                        await logs(level=LEVELS[1], message=format_exc())
                    ok.sort()
                    error.sort()
                    alert.sort()
                    embed = Embed(title="Подключение модулей:", color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:", inline=False, value=f"\n".join(cog for cog in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:", inline=False, value=f"\n".join(cog for cog in error))
                    if len(alert) != 0:
                        embed.add_field(name="Ошибка:", inline=False,
                                        value="\n".join(f"Модуль \"{cog}\" уже включен!" for cog in alert))
                elif trigger == "off":
                    if name is not None:
                        if name.title() not in [x.title() for x in BOT.cogs]:
                            alert.append(name.title())
                        else:
                            try:
                                BOT.unload_extension(name=f"modules.{name.lower()}")
                                ok.append(name.title())
                                try:
                                    settings["Отключенные модули"].append(name.lower())
                                except Exception:
                                    settings["Отключенные модули"].append(name.title())
                                await save(file="settings", content=settings)
                            except Exception:
                                error.append(name.title())
                                await logs(level=LEVELS[1], message=format_exc())
                    else:
                        for filename in listdir("modules"):
                            if filename.endswith(".py"):
                                cog = filename[:-3]
                                if cog.title() not in [x.title() for x in BOT.cogs]:
                                    alert.append(cog.title())
                                else:
                                    try:
                                        BOT.unload_extension(name=f"modules.{cog.lower()}")
                                        ok.append(cog.title())
                                        try:
                                            settings["Отключенные модули"].append(cog.lower())
                                        except Exception:
                                            settings["Отключенные модули"].append(cog.title())
                                        await save(file="settings", content=settings)
                                    except Exception:
                                        error.append(cog.title())
                                        await logs(level=LEVELS[1], message=format_exc())
                    ok.sort()
                    error.sort()
                    alert.sort()
                    embed = Embed(title="Отключение модулей:", color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:", inline=False, value=f"\n".join(x for x in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:", inline=False, value=f"\n".join(x for x in error))
                    if len(alert) != 0:
                        embed.add_field(name="Ошибка:", inline=False,
                                        value="\n".join(f"Модуль \"{x}\" уже отключен!" for x in alert))
                elif trigger == "res":
                    if name is not None:
                        try:
                            BOT.unload_extension(name=f"modules.{name.lower()}")
                            BOT.load_extension(name=f"modules.{name.lower()}")
                            ok.append(name.title())
                        except Exception:
                            error.append(name.title())
                            await logs(level=LEVELS[1], message=format_exc())
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
                                    await logs(level=LEVELS[1], message=format_exc())
                    ok.sort()
                    error.sort()
                    embed = Embed(title="Перезагрузка модулей:", color=ctx.author.color)
                    if len(ok) != 0:
                        embed.add_field(name="Успешно:", inline=False, value=f"\n".join(x for x in ok))
                    if len(error) != 0:
                        embed.add_field(name="Неудачно:", inline=False, value=f"\n".join(x for x in error))
                else:
                    embed = Embed(title=f"Модуль \"{trigger.title()}\":", color=ctx.author.color)
                    embed.add_field(name="Описание:", inline=False, value=descriptions[trigger.lower()])
                    if trigger.title() in [x.title() for x in BOT.cogs]:
                        status = "Включен"
                    else:
                        status = "Отключен"
                    embed.add_field(name="Текущий статус:", inline=False, value=status)
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed, delete_after=60)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


@BOT.command(description="Админы 1", name="res", help="Полная перезагрузка бота", brief="Не применимо", usage="!res")
@has_permissions(administrator=True)
async def command_res(ctx):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            await sleep(delay=1)
            try:
                execl(executable, executable, "mlpbots.py")
            except Exception:
                await logs(level=LEVELS[1], message=format_exc())
                execl("bin/python/python.exe", "bin/python/python.exe", "mlpbots.py")
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


# команды создателя
@BOT.command(description="Создатель 1", name="debug", help="Вывод дебаг сообщений в лог", brief="`On` / `Off`",
             usage="!debug on")
async def command_debug(ctx, trigger: str = "on"):
    try:
        if str(ctx.channel.type) == "text":
            if ctx.author.id == 496139824500178964:
                if trigger.lower() == "on" or trigger.lower() == "off":
                    await ctx.message.delete(delay=1)
                    embed = None
                    from db.settings import settings
                    if trigger.lower() == "on":
                        settings["Дебаг"] = True
                        await save(file="settings", content=settings)
                        embed = Embed(title="Дебаг:", color=ctx.author.color, description="Дебаг **включен**!")
                    if trigger.lower() == "off":
                        settings["Дебаг"] = False
                        await save(file="settings", content=settings)
                        embed = Embed(title="Дебаг:", color=ctx.author.color, description="Дебаг **отключен**!")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed, delete_after=60)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


# скрытые команды
@BOT.command(description="Скрыто 1", name="ban", help="", brief="", usage="")
async def command_ban(ctx, member: Member = None):
    try:
        if str(ctx.channel.type) == "text":
            await ctx.message.delete(delay=1)
            if member is not None:
                embed = Embed(title="Бан пользователей:", color=ctx.author.color,
                              description=f"Пользователь {member.mention} успешно забанен!")
            else:
                users = [user.mention for user in BOT.users]
                embed = Embed(title="Бан пользователей:", color=ctx.author.color,
                              description=f"Пользователи {', '.join(users)} успешно забанены!")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await ctx.send(embed=embed)
    except Exception:
        await logs(level=LEVELS[4], message=format_exc())


if __name__ == "__main__":
    try:
        run(main=autores())
        if 80000 <= int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S")) < 200000:
            BOT.run("")
        else:
            BOT.run("")
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
