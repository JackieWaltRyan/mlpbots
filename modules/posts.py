from asyncio import run
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from discord_components_mirror import Button, ButtonStyle, SelectOption, Select
from mlpbots import LEVELS, FOOTER, logs
from re import findall
from traceback import format_exc

RASES = [1007586334493388871, 1007586333394485288, 1007586331414773852, 1007586330198409356, 1007586329078542386,
         1007586327723786281, 1007586326469677131, 1007586323470749717, 1007586324993282069, 1007586322736746536,
         1007586321637855272, 1007586320517967872, 1007586318894776360, 1007586317598728262, 1007586315308638268,
         1007586316508217434, 1007586314201342055, 1007586311663792208, 1007586312901111838, 1007586310556495902,
         1007586309495345192, 1007586308425781298, 1007586306894856275, 1007586305850478613, 1007586305082937394,
         1007586303371653121, 1007586302520213585, 1007586301538750534, 1007586299311571044, 1007586300561477702,
         1007586298007146516, 1007586296329408535]
MINIS = [1007586295704457236, 1007586294530052217, 1007586293385019452, 1007586291954745386, 1007586290826485863,
         1007586290033774612]


class Posts(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.post_rules.start()
            self.post_roles.start()
            self.post_inactive.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(count=1)
    async def post_rules(self):
        try:
            await self.BOT.get_channel(id=1007577221541670982).purge()
            embed = Embed(title="Приветствуем тебя милая поняшка в нашем клубе!", color=0x008000,
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
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577221541670982).send(embed=embed, components=[[
                Button(label="Согласен!", id="rules_yes", style=ButtonStyle.green),
                Button(label="Не согласен!", id="rules_no", style=ButtonStyle.red)]])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def post_roles(self):
        try:
            await self.BOT.get_channel(id=1007577223110328330).purge()
            embed = Embed(title="На нашем сервере есть 5 основных ролей:", color=0xFFFF00,
                          description="<@&1007586359067803729> - пони, которые управляют сервером.\n\n"
                                      "<@&1007586288662216725> - основной табун, добрые пони сервера.\n\n"
                                      "<@&1007586287244562483> - кто несогласен с правилами, наблюдают.\n\n"
                                      "<@&1007586338238898187> - кто забыл об этом клубе, невидимы.\n\n"
                                      "<@&1007586285365502033> - открывает доступ в мир Дискорда. Чтобы получить "
                                      "эту роль, нажмите на кнопку под этим сообщением.")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021146958095712317/"
                                    "cheer.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577223110328330).send(embed=embed, components=[[
                Button(label="18+", id="roles_nsfw", style=ButtonStyle.gray)]])
            await self.post_rases.start()
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def post_rases(self):
        try:
            roles = {}
            for guild in self.BOT.guilds:
                for role in guild.roles:
                    if role.id in RASES:
                        roles.update({role.name: role.id})
            description, options, i = [], [[SelectOption(label="Без расы (убрать роль)", value="Без расы")]], 0
            roles_name = [x for x in roles]
            roles_name.sort()
            for role in roles_name:
                description.append(f"<@&{roles[role]}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=f"{role}", value=f"{roles[role]}"))
                else:
                    i += 1
                    options.append([SelectOption(label="Без расы (убрать роль)", value="Без расы"),
                                    SelectOption(label=f"{role}", value=f"{roles[role]}")])
            embed = Embed(title="А еще у нас есть расы:", color=0xFFA500, description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457483694161/"
                                    "chars.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577223110328330).send(embed=embed,
                                                                    components=[Select(options=x) for x in options])
            await self.post_minis.start()
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def post_minis(self):
        try:
            roles = {}
            for guild in self.BOT.guilds:
                for role in guild.roles:
                    if role.id in MINIS:
                        roles.update({role.name: role.id})
            description, i, roles_name = [], 0, [x for x in roles]
            options = [[SelectOption(label="Без министерства (убрать роль)", value="Без министерства")]]
            roles_name.sort()
            for role in roles_name:
                description.append(f"<@&{roles[role]}>\n\n")
                if len(options[i]) < 25:
                    options[i].append(SelectOption(label=f"{role}", value=f"{roles[role]}"))
                else:
                    i += 1
                    options.append([SelectOption(label="Без министерства (убрать роль)", value="Без министерства"),
                                    SelectOption(label=f"{role}", value=f"{roles[role]}")])
            embed = Embed(title="И министерства:", color=0xFF0000, description="".join([x for x in description]))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1021117457102016512/"
                                    "mine6.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577223110328330).send(embed=embed,
                                                                    components=[Select(options=x) for x in options])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def post_inactive(self):
        try:
            await self.BOT.get_channel(id=1007577224502837248).purge()
            embed = Embed(title="Актив и Неактив:", color=0x00BFFF,
                          description="Если вы не писали сообщения на сервере в течении 7 дней, вам автоматически "
                                      "дается роль <@&1007586338238898187> и скрывается доступ ко всем каналам "
                                      "сервера. Чтобы убрать эту роль, и снова получить полный доступ к серверу, "
                                      "достаточно написать одно любое сообщение!")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1021085537802649661/1048666697978101760/"
                                    "sleep.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            await self.BOT.get_channel(id=1007577224502837248).send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

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
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles, id=1007586288662216725))
                await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles, id=1007586287244562483))
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
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
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles, id=1007586287244562483))
                await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles, id=1007586288662216725))
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "roles_nsfw":
                role = get(iterable=interaction.user.guild.roles, id=1007586285365502033)
                if get(iterable=interaction.user.roles, id=1007586285365502033) is None:
                    await interaction.send(content=f"Поздравляем! Вам выдана роль <@&1007586285365502033>! Теперь у "
                                                   f"вас есть доступ к категории <#1007577254936719391>!")
                    await interaction.user.add_roles(role)
                else:
                    await interaction.send(content=f"Поздравляем! Вам убрана роль <@&1007586285365502033>!")
                    await interaction.user.remove_roles(role)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_select_option(self, interaction):
        try:
            if interaction.values[0] == "Без расы":
                await interaction.send(content="Поздравляем! Вам убраны все Расы!")
                for role in RASES:
                    try:
                        await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles, id=role))
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.values[0] == "Без министерства":
                await interaction.send(content="Поздравляем! Вам убраны все Министерства!")
                for role in MINIS:
                    try:
                        await interaction.user.remove_roles(get(iterable=interaction.user.guild.roles, id=role))
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.values[0] in str(RASES) or interaction.values[0] in str(MINIS):
                await interaction.send(content=f"Поздравляем! Вам выдана роль <@&{int(interaction.values[0])}>!")
                await interaction.user.add_roles(get(iterable=interaction.user.guild.roles,
                                                     id=int(interaction.values[0])))
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_member_update(self, before, after):
        try:
            after_roles, before_roles = [role.id for role in after.roles], [role.id for role in before.roles]
            if len(after_roles) > len(before_roles):
                for role in before_roles:
                    try:
                        after_roles.remove(role)
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
                if findall(pattern=str(after_roles[0]), string=str(RASES)):
                    for role in RASES:
                        if role == after_roles[0]:
                            continue
                        try:
                            await after.remove_roles(get(iterable=after.guild.roles, id=role))
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
                if findall(pattern=str(after_roles[0]), string=str(MINIS)):
                    for role in MINIS:
                        if role == after_roles[0]:
                            continue
                        try:
                            await after.remove_roles(get(iterable=after.guild.roles, id=role))
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Posts(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
