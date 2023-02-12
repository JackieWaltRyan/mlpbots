from asyncio import run
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from discord_components_mirror import Button, ButtonStyle, SelectOption, Select
from mlpbots import DB, logs, FOOTER
from pymongo import ASCENDING
from traceback import format_exc


class Posts(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.rases = [x["_id"] for x in DB["roles"].find({"Категория": "Расы"})]
            self.minis = [x["_id"] for x in DB["roles"].find({"Категория": "Министерства"})]
            self.post_rules.start()
            self.post_roles.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(count=1)
    async def post_rules(self):
        try:
            channel = DB["channels"].find_one(filter={"Категория": "Правила"})["_id"]
            await self.BOT.get_channel(id=channel).purge()
            embed = Embed(title="Приветствуем тебя милая поняшка в нашем клубе!",
                          color=0x008000,
                          description="Несмотря на название, этот клуб создан для простого и дружественного общения "
                                      "всех участников на любые возможные темы. Но тем не менее, для поддержания "
                                      "уютной и комфортной атмосферы, у нас есть несколько правил:")
            embed.add_field(name="Правила:",
                            value=":one: Не оскорблять других участников! Не обсуждать и не указывать на внешность, "
                                  "голос, и подобные особенности других участников!\n\n"
                                  ":two: Не обсуждать религию, политику, расовые особенности, и другие подобные темы, "
                                  "которые могут задеть и оскорбить чувства других участников!\n\n"
                                  ":three: В нашем клубе действует главный закон Эквестрии: Дружба - это чудо! И мы "
                                  "искренне надеемся на поддержание этого всеми участниками клуба!")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457819250829/"
                                    "PinkiePieWannaHugYou.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=channel).send(embed=embed,
                                                        components=[[Button(label="Согласен!",
                                                                            id="rules_yes",
                                                                            style=ButtonStyle.green),
                                                                     Button(label="Не согласен!",
                                                                            id="rules_no",
                                                                            style=ButtonStyle.red)]])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def post_roles(self):
        try:
            channel = DB["channels"].find_one(filter={"Категория": "Роли"})["_id"]
            await self.BOT.get_channel(id=channel).purge()
            embed = Embed(title="На нашем сервере есть 4 основных роли:",
                          color=0xFFFF00,
                          description="<@&1007586359067803729> - пони, которые управляют сервером.\n\n"
                                      "<@&1007586288662216725> - основной табун, добрые пони сервера.\n\n"
                                      "<@&1007586287244562483> - кто несогласен с правилами, наблюдают.\n\n"
                                      "<@&1007586285365502033> - открывает доступ в мир Дискорда. Чтобы получить "
                                      "эту роль, нажмите на кнопку под этим сообщением.")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021146958095712317/"
                                    "cheer.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=channel).send(embed=embed,
                                                        components=[[Button(label="18+",
                                                                            id="roles_nsfw",
                                                                            style=ButtonStyle.gray)]])
            await self.post_rases.start()
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def post_rases(self):
        try:
            channel = DB["channels"].find_one(filter={"Категория": "Роли"})["_id"]
            description, options, i = [], [[SelectOption(label="Без расы (убрать роль)",
                                                         value="Без расы")]], 0
            for role in DB["roles"].find({"Категория": "Расы"}).sort(key_or_list="Название",
                                                                     direction=ASCENDING):
                description.append(f"<@&{role['_id']}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=role["Название"],
                                                   value=str(role["_id"])))
                else:
                    i += 1
                    options.append([SelectOption(label="Без расы (убрать роль)",
                                                 value="Без расы"),
                                    SelectOption(label=role["Название"],
                                                 value=str(role["_id"]))])
            embed = Embed(title="А еще у нас есть расы:",
                          color=0xFFA500,
                          description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457483694161/"
                                    "chars.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=channel).send(embed=embed,
                                                        components=[Select(options=x) for x in options])
            await self.post_minis.start()
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def post_minis(self):
        try:
            channel = DB["channels"].find_one(filter={"Категория": "Роли"})["_id"]
            description, options, i = [], [[SelectOption(label="Без министерства (убрать роль)",
                                                         value="Без министерства")]], 0
            for role in DB["roles"].find({"Категория": "Министерства"}).sort(key_or_list="Название",
                                                                             direction=ASCENDING):
                description.append(f"<@&{role['_id']}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=role["Название"],
                                                   value=str(role["_id"])))
                else:
                    i += 1
                    options.append([SelectOption(label="Без министерства (убрать роль)",
                                                 value="Без министерства"),
                                    SelectOption(label=role["Название"],
                                                 value=str(role["_id"]))])
            embed = Embed(title="И министерства:",
                          color=0xFF0000,
                          description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457102016512/"
                                    "mine6.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=channel).send(embed=embed,
                                                        components=[Select(options=x) for x in options])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "rules_yes":
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&1007586288662216725>! Теперь у вас "
                                               f"есть полный доступ ко всем каналам сервера!\n\nВ канале "
                                               f"<#1007577223110328330> вы можете выбрать себе Рассу и Министерство, "
                                               f"а также получить роль 18+ для доступа к соответствующей "
                                               f"категории.\nВ канале <#1007585194863251468> вы можете послушать "
                                               f"пони-радио или свои любимые треки из YouTube.\nВ канале "
                                               f"<#1007577229691207773> вы можете поиграть в интерактивную игру "
                                               f"\"Похищенная пони\".\n\nТак же у нас есть <@&1007586346178707516>. "
                                               f"Посмотреть все доступные вам команды бота вы можете командой "
                                               f"**!help**.")
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                     id=DB["roles"].find_one(filter={"Категория": "Пони"})["_id"]))
                await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                        id=DB["roles"].find_one(filter={"Категория": "Духи"})["_id"]))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "rules_no":
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&1007586287244562483>! Теперь у вас "
                                               f"есть доступ ко всем каналам сервера, но только в режиме \"**Только "
                                               f"чтение**\"!\n\nВ канале <#1007577223110328330> вы можете выбрать "
                                               f"себе Рассу и Министерство, а также получить роль 18+ для доступа к "
                                               f"соответствующей категории.\nВ канале <#1007585194863251468> вы "
                                               f"можете послушать пони-радио или свои любимые треки из YouTube.\nВ "
                                               f"канале <#1007577229691207773> вы можете поиграть в интерактивную "
                                               f"игру \"Похищенная пони\".\n\nТак же у нас есть "
                                               f"<@&1007586346178707516>. Посмотреть все доступные вам команды бота "
                                               f"вы можете командой **!help**.")
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                     id=DB["roles"].find_one(filter={"Категория": "Духи"})["_id"]))
                await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                        id=DB["roles"].find_one(filter={"Категория": "Пони"})["_id"]))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "roles_nsfw":
                role = DB["roles"].find_one(filter={"Категория": "18+"})["_id"]
                if get(iterable=interaction.user.roles,
                       id=role) is None:
                    await interaction.send(content=f"Поздравляем! Вам выдана роль <@&1007586285365502033>! "
                                                   f"Теперь у вас есть доступ к категории <#1007577254936719391>!")
                    await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                         id=role))
                else:
                    await interaction.send(content=f"Поздравляем! Вам убрана роль <@&1007586285365502033>!")
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=role))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_select_option(self, interaction):
        try:
            if interaction.values[0] == "Без расы":
                await interaction.send(content="Поздравляем! Вам убраны все Расы!")
                for role in self.rases:
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=role))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.values[0] == "Без министерства":
                await interaction.send(content="Поздравляем! Вам убраны все Министерства!")
                for role in self.minis:
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=role))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.values[0] in str(self.rases) or interaction.values[0] in str(self.minis):
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{int(interaction.values[0])}>!")
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                     id=int(interaction.values[0])))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Posts(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
