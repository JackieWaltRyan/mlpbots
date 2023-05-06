from asyncio import run
from traceback import format_exc

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from discord_components_mirror import Button, ButtonStyle, SelectOption, Select
from pymongo import ASCENDING

from mlpbots import DB, logs, FOOTER


class Posts(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.channel_rules = DB["channels"].find_one(filter={"Категория": "Правила"})["_id"]
            self.channel_roles = DB["channels"].find_one(filter={"Категория": "Роли"})["_id"]
            self.channel_player = DB["channels"].find_one(filter={"Категория": "Плеер 1"})["_id"]
            self.channel_game = DB["channels"].find_one(filter={"Категория": "Игра"})["_id"]
            self.role_pony = DB["roles"].find_one(filter={"Категория": "Пони"})["_id"]
            self.role_bots = DB["roles"].find_one(filter={"Категория": "Принцессы"})["_id"]
            self.role_gamer = DB["roles"].find_one(filter={"Категория": "Игрок"})["_id"]
            self.role_nsfw = DB["roles"].find_one(filter={"Категория": "18+"})["_id"]
            self.role_rases = [x["_id"] for x in DB["roles"].find({"Категория": "Расы"})]
            self.role_minis = [x["_id"] for x in DB["roles"].find({"Категория": "Министерства"})]
            self.posts.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    async def post_rules(self):
        try:
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
            await self.BOT.get_channel(id=self.channel_rules).send(embed=embed,
                                                                   components=[[Button(label="Согласен!",
                                                                                       id="rules_yes",
                                                                                       style=ButtonStyle.green),
                                                                                Button(label="Не согласен!",
                                                                                       id="rules_no",
                                                                                       style=ButtonStyle.red)]])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    async def post_rases(self):
        try:
            description, options, i = [], [[SelectOption(label="🚫 Без расы (убрать роль)",
                                                         value="Без расы")]], 0
            for role in DB["roles"].find({"Категория": "Расы"}).sort(key_or_list="Название",
                                                                     direction=ASCENDING):
                description.append(f"<@&{role['_id']}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=role["Название"],
                                                   value=str(role["_id"])))
                else:
                    i += 1
                    options.append([SelectOption(label="🚫 Без расы (убрать роль)",
                                                 value="Без расы"),
                                    SelectOption(label=role["Название"],
                                                 value=str(role["_id"]))])
            embed = Embed(title="Расы:",
                          color=0xFFA500,
                          description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457483694161/"
                                    "chars.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=self.channel_roles).send(embed=embed,
                                                                   components=[Select(options=x) for x in options])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    async def post_minis(self):
        try:
            description, options, i = [], [[SelectOption(label="🚫 Без министерства (убрать роль)",
                                                         value="Без министерства")]], 0
            for role in DB["roles"].find({"Категория": "Министерства"}).sort(key_or_list="Название",
                                                                             direction=ASCENDING):
                description.append(f"<@&{role['_id']}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=role["Название"],
                                                   value=str(role["_id"])))
                else:
                    i += 1
                    options.append([SelectOption(label="🚫 Без министерства (убрать роль)",
                                                 value="Без министерства"),
                                    SelectOption(label=role["Название"],
                                                 value=str(role["_id"]))])
            embed = Embed(title="Министерства:",
                          color=0xFF0000,
                          description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457102016512/"
                                    "mine6.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=self.channel_roles).send(embed=embed,
                                                                   components=[Select(options=x) for x in options])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    async def post_roles(self):
        try:
            embed = Embed(title="Разное:",
                          color=0xFFFF00,
                          description=f"<@&{self.role_gamer}> - для тех, кто активно играет в игру.\n\n"
                                      f"<@&{self.role_nsfw}> - для тех, кто старше 18 и не боится R34.\n\n"
                                      f"Чтобы получить или убрать роль, нажмите на кнопку под сообщением.")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021146958095712317/"
                                    "cheer.png")
            embed.set_footer(text=FOOTER["Текст"],
                             icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=self.channel_roles).send(embed=embed,
                                                                   components=[[Button(label="🦄 Игроки",
                                                                                       id="roles_gamer",
                                                                                       style=ButtonStyle.gray),
                                                                                Button(label="🦄 18+",
                                                                                       id="roles_nsfw",
                                                                                       style=ButtonStyle.gray)]])
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(count=1)
    async def posts(self):
        try:
            await self.BOT.get_channel(id=self.channel_rules).purge()
            await self.post_rules()
            await self.BOT.get_channel(id=self.channel_roles).purge()
            await self.post_rases()
            await self.post_minis()
            await self.post_roles()
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "rules_yes":
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{self.role_pony}>! Теперь у вас "
                                               f"есть полный доступ ко всем каналам сервера!\n\nВ канале "
                                               f"<#{self.channel_roles}> вы можете выбрать себе Рассу, Министерство, "
                                               f"или получить другие роли.\nВ канале <#{self.channel_player}> вы "
                                               f"можете послушать пони-радио.\nВ канале <#{self.channel_game}> вы "
                                               f"можете поиграть в интерактивную игру \"Похищенная пони\".\n\nТак же "
                                               f"у нас есть <@&{self.role_bots}>. Посмотреть все доступные вам "
                                               f"команды бота вы можете командой **!help**.")
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                     id=self.role_pony))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "rules_no":
                await interaction.send(content=f"Извините, но если вы не согласны с правилами, то вы не можете "
                                               f"получить доступ к серверу!")
                await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                        id=self.role_pony))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "roles_gamer":
                if get(iterable=interaction.user.roles,
                       id=self.role_gamer) is None:
                    await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{self.role_gamer}>!")
                    await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                         id=self.role_gamer))
                else:
                    await interaction.send(content=f"Поздравляем! Вам убрана роль <@&{self.role_gamer}>!")
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=self.role_gamer))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.component.id == "roles_nsfw":
                if get(iterable=interaction.user.roles,
                       id=self.role_nsfw) is None:
                    await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{self.role_nsfw}>! "
                                                   f"Теперь у вас есть доступ к категории <#1007577254936719391>!")
                    await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                         id=self.role_nsfw))
                else:
                    await interaction.send(content=f"Поздравляем! Вам убрана роль <@&{self.role_nsfw}>!")
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=self.role_nsfw))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @Cog.listener()
    async def on_select_option(self, interaction):
        try:
            if interaction.values[0] == "Без расы":
                await interaction.send(content="Поздравляем! Вам убраны все Расы!")
                for role in self.role_rases:
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=role))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.values[0] == "Без министерства":
                await interaction.send(content="Поздравляем! Вам убраны все Министерства!")
                for role in self.role_minis:
                    await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles,
                                                            id=role))
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())
        try:
            if interaction.values[0] in str(self.role_rases) or interaction.values[0] in str(self.role_minis):
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{interaction.values[0]}>!")
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
