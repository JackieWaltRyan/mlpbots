from asyncio import run
from db.game import game
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord_components_mirror import Button, ButtonStyle
from mlpbots import logs, LEVELS, FOOTER, save
from re import findall
from traceback import format_exc


class Game(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.post.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    async def paginator(self, interaction, page):
        try:
            embed = Embed(title="Похищенная пони", color=game[page]["Цвет"], description=game[page]["Текст"])
            if "Изображение" in game[page]:
                embed.set_image(url=game[page]["Изображение"])
            from db.members import members
            ends = len(members[interaction.user.id]["Похищенная пони"]["Концовки"])
            if "Скрытые кнопки" in game[page] and ends >= 17:
                await interaction.send(embed=embed, components=game[page]["Скрытые кнопки"])
            else:
                await interaction.send(embed=embed, components=game[page]["Кнопки"])
            members[interaction.user.id]["Похищенная пони"]["Страница"] = page
            if "Концовка" in game[page]:
                if game[page]["Концовка"] not in members[interaction.user.id]["Похищенная пони"]["Концовки"]:
                    members[interaction.user.id]["Похищенная пони"]["Концовки"].append(game[page]["Концовка"])
            await save(file="members", content=members)
            if ends == 19:
                self.BOT.reload_extension(name="modules.achievements")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def post(self):
        try:
            await self.BOT.get_channel(id=1007577229691207773).purge()
            embed = Embed(title="Похищенная пони: интерактивная игра-новелла", color=0xFF8C00,
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
            embed.set_image(url="https://projects.everypony.ru/purloined-pony/pics/pp000.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577229691207773).send(embed=embed, components=[[
                Button(label="Начать новую игру", id="pp_newgame", style=ButtonStyle.green),
                Button(label="Продолжить игру", id="pp_continue", style=ButtonStyle.blue),
                Button(label="Статистика", id="pp_stats", style=ButtonStyle.gray)]])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "pp_newgame":
                from db.members import members
                if members[interaction.user.id]["Похищенная пони"]["Страница"] == "p0":
                    await self.paginator(interaction=interaction, page="p1")
                else:
                    await interaction.send(
                        f"У вас обнаружена сохраненная игра! Хотите удалить ее и начать заново, или продолжить?",
                        components=[[Button(label="Продолжить игру", id="pp_continue", style=ButtonStyle.green),
                                     Button(label="Начать заново", id="p1", style=ButtonStyle.red)]])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "pp_continue":
                from db.members import members
                if members[interaction.user.id]["Похищенная пони"]["Страница"] != "p0":
                    await self.paginator(interaction=interaction,
                                         page=members[interaction.user.id]["Похищенная пони"]["Страница"])
                else:
                    await interaction.send(f"У вас нет сохраненной игры! Хотите начать новую?",
                                           components=[Button(label="Начать новую игру", id="pp_newgame",
                                                              style=ButtonStyle.green)])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "pp_stats":
                stats = []
                from db.members import members
                for member in members:
                    if len(members[member]["Похищенная пони"]["Концовки"]) > 0:
                        stats.append(f"<@{member}>: Пройдено {len(members[member]['Похищенная пони']['Концовки'])} "
                                     f"из 19 концовок.")
                if len(stats) == 0:
                    stats.append("Сейчас нет пони, которые прошли хотя бы одну концовку.")
                embed = Embed(title="Статистика прохождения:", color=interaction.user.color,
                              description="\n\n".join([x for x in stats]))
                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                await interaction.send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if len(findall(pattern=r"p\d+", string=interaction.component.id)) != 0:
                await self.paginator(interaction=interaction, page=interaction.component.id)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Game(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
