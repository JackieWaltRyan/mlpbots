from asyncio import run
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord_components_mirror import Button, ButtonStyle
from mlpbots import DB, logs, FOOTER
from pymongo import DESCENDING
from re import findall
from traceback import format_exc


async def paginator(interaction, page):
    try:
        components, i, db = [[]], 0, DB["game"].find_one(filter={"_id": page})
        member = DB["members"].find_one(filter={"_id": interaction.user.id})["Похищенная пони"]["Концовки"]
        embed = Embed(title="Похищенная пони",
                      color=db["Цвет"],
                      description=db["Текст"].replace("\\n", "\n"))
        if "Изображение" in db:
            embed.set_image(url=db["Изображение"])
        if "Скрытые кнопки" in db and len(member) >= 17:
            for button in db["Скрытые кнопки"]:
                if len(components[i]) < 5:
                    components[i].append(Button(label=button["Название"],
                                                id=button["Страница"]))
                else:
                    i += 1
                    components.append([Button(label=button["Название"],
                                              id=button["Страница"])])
        else:
            for button in db["Кнопки"]:
                if len(components[i]) < 5:
                    components[i].append(Button(label=button["Название"],
                                                id=button["Страница"]))
                else:
                    i += 1
                    components.append([Button(label=button["Название"],
                                              id=button["Страница"])])
        await interaction.send(embed=embed,
                               components=components)
        DB["members"].update_one(filter={"_id": interaction.user.id},
                                 update={"$set": {"Похищенная пони.Страница": page}})
        if "Концовка" in db:
            if db["Концовка"] not in member:
                DB["members"].update_one(filter={"_id": interaction.user.id},
                                         update={"$push": {"Похищенная пони.Концовки": db["Концовка"]}})
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


class Game(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.post.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(count=1)
    async def post(self):
        try:
            channel = DB["channels"].find_one(filter={"Категория": "Игра"})["_id"]
            await self.BOT.get_channel(id=channel).purge()
            embed = Embed(title="Похищенная пони: интерактивная игра-новелла",
                          color=0xFF8C00,
                          description="Привет! Если ты первый раз сталкиваешься с такой игрой, обязательно прочитай "
                                      "этот раздел. Ну а если тебе не впервой, то можешь сразу начинать игру и "
                                      "отправляться в путешествие!\n\nТо, как будет развиваться сюжет игры, "
                                      "зависит только от тебя. В этой истории тебе предстоит посмотреть на мир "
                                      "глазами Кэррот Топ, молодой земной пони, живущей на окраине Понивилля. По мере "
                                      "чтения тебе придётся время от времени принимать решения.\n\nИногда мелкие, "
                                      "иногда - важные, все они, так или иначе, повлияют на сюжет. Каждый раз в "
                                      "момент выбора тебе будет предложено два или больше вариантов. Просто щёлкай по "
                                      "кнопке и читай, что случилось дальше. В книге есть 19 различных концовок, "
                                      "некоторые - счастливые, некоторые - не очень, но каждая уникальна. Историю "
                                      "можно проходить несколько раз, и сюжет ни разу не повторится!\n\nТеперь, "
                                      "когда ты знаешь, как играть, смело жми на кнопку \"Начать новую игру\" и "
                                      "начинай свое приключение. Удачи!\n\nИгра сохраняется автоматически после "
                                      "каждого действия!\n\n**Автор**: Chris **Перевод**: Многорукий Удав "
                                      "**Вычитка**: Orhideous, Hariester, Haveglory **Оформление**: ponyPharmacist")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1021085537802649661/1064578890338680973/"
                                "pp000.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=channel).send(embed=embed,
                                                        components=[[Button(label="Начать новую игру",
                                                                            id="pp_newgame",
                                                                            style=ButtonStyle.green),
                                                                     Button(label="Продолжить игру",
                                                                            id="pp_continue",
                                                                            style=ButtonStyle.blue),
                                                                     Button(label="Статистика",
                                                                            id="pp_stats",
                                                                            style=ButtonStyle.gray)]])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "pp_newgame":
                if DB["members"].find_one(filter={"_id": interaction.user.id})["Похищенная пони"]["Страница"] == "p0":
                    await paginator(interaction=interaction,
                                    page="p1")
                else:
                    await interaction.send(content=f"У вас обнаружена сохраненная игра!"
                                                   f"Хотите удалить ее и начать заново, или продолжить?",
                                           components=[[Button(label="Продолжить игру",
                                                               id="pp_continue",
                                                               style=ButtonStyle.green),
                                                        Button(label="Начать заново",
                                                               id="p1",
                                                               style=ButtonStyle.red)]])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "pp_continue":
                page = DB["members"].find_one(filter={"_id": interaction.user.id})["Похищенная пони"]["Страница"]
                if page != "p0":
                    await paginator(interaction=interaction,
                                    page=page)
                else:
                    await interaction.send(content=f"У вас нет сохраненной игры! Хотите начать новую?",
                                           components=[Button(label="Начать новую игру",
                                                              id="pp_newgame",
                                                              style=ButtonStyle.green)])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "pp_stats":
                stats = []
                for member in DB["members"].find().sort(key_or_list="Похищенная пони.Концовки",
                                                        direction=DESCENDING):
                    if len(member["Похищенная пони"]["Концовки"]) > 0:
                        stats.append(f"<@{member['_id']}>: "
                                     f"Пройдено {len(member['Похищенная пони']['Концовки'])} из 19 концовок.")
                if len(stats) == 0:
                    stats.append("Сейчас нет пони, которые прошли хотя бы одну концовку.")
                embed = Embed(title="Статистика прохождения:",
                              color=interaction.user.color,
                              description="\n\n".join([x for x in stats]))
                embed.set_footer(text=FOOTER["Текст"],
                                 icon_url=FOOTER["Ссылка"])
                await interaction.send(embed=embed)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if len(findall(pattern=r"p\d+",
                           string=interaction.component.id)) != 0:
                await paginator(interaction=interaction,
                                page=interaction.component.id)
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Game(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
