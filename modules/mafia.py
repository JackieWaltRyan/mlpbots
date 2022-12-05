from asyncio import sleep, run
from datetime import timedelta
from db.mafia import mafia
from discord import Embed, PermissionOverwrite
from discord.ext.commands import Cog, command
from discord_components_mirror import Button, ButtonStyle, Select, SelectOption
from mlpbots import logs, LEVELS, FOOTER
from random import choice, randint
from traceback import format_exc


# https://ru.wikipedia.org/wiki/%D0%9C%D0%B0%D1%84%D0%B8%D1%8F_(%D0%B8%D0%B3%D1%80%D0%B0)#Городская_мафия


class Mafia(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.trigger, self.time, self.selector = bot, None, None, []
            self.players, self.vote = {"Люди": {}, "Боты": {}}, {"Старт": {}, "Конец": {}, "Убить": []}
            self.minutes = {"Пользователь": None, "Триггер": False}
            for guild in self.BOT.guilds:
                for role in guild.roles:
                    if role.id == 1007586288662216725:
                        self.ponies = role
                    if role.id == 1007586338238898187:
                        self.inactive = role
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    async def bots(self):
        pass

    async def mafia(self):
        pass

    async def doctor(self):
        pass

    async def mineyak(self):
        pass

    async def putana(self):
        pass

    async def days(self, tier, post, kill=None):
        time = 60
        if kill is not None:
            if type(kill) is str:
                await post.channel.send(content=f"Игрок **{kill}** убит!")
            else:
                self.minutes = {"Пользователь": kill.id, "Триггер": False}
                await post.channel.send(content=f"Игрок {kill.mention} убит!")
                await post.channel.edit(overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                                    self.ponies: PermissionOverwrite(send_messages=False),
                                                    kill: PermissionOverwrite(send_messages=True)})

                def e(t):
                    embed = Embed(title=f"День {tier}:", color=self.BOT.user.color,
                                  description=f"Текущая стадия: **Последняя минута**\n\nДо окончания: {t} секунд")
                    embed.add_field(name="Описание:", value=f"Игрок {kill.mention} может сказать последние слова.")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    return embed

                await post.edit(embed=e(t=time),
                                components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green),
                                             Button(label="Завершить минуту", id="maf_endminute",
                                                    style=ButtonStyle.red)]])
                while True:
                    if time == 0:
                        await post.channel.edit(overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                                            self.ponies: PermissionOverwrite(send_messages=False)})
                        self.players["Люди"][kill]["Жив"] = False
                        time = 60
                        break
                    else:
                        if self.minutes["Триггер"]:
                            break
                        await sleep(delay=1)
                        time -= 1
                        await post.edit(embed=e(t=time),
                                        components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green),
                                                     Button(label="Завершить минуту", id="maf_endminute",
                                                            style=ButtonStyle.red)]])
        for player in self.players["Люди"]:
            if self.players["Люди"][player]["Жив"]:
                self.minutes = {"Пользователь": player.id, "Триггер": False}
                await post.channel.edit(overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                                    self.ponies: PermissionOverwrite(send_messages=False),
                                                    player: PermissionOverwrite(send_messages=True)})

                def e(t):
                    embed = Embed(title=f"День {tier}:", color=self.BOT.user.color,
                                  description=f"Текущая стадия: **Минута речи**\n\nДо окончания: {t} секунд")
                    embed.add_field(name="Сейчас говорит:", value=f"{player.mention}")
                    embed.add_field(name="Описание:", value=mafia["День"])
                    if len(self.vote["Убить"]) > 0:
                        for vote in self.vote["Убить"]:
                            for user in self.players["Люди"]:
                                if vote == user.name:
                                    self.vote["Убить"].remove(vote)
                                    self.vote["Убить"].append(user.mention)
                        embed.add_field(name="Голосование:", value="\n".join(self.vote["Убить"]))
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    return embed

                await post.edit(embed=e(t=time),
                                components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green),
                                             Button(label="Завершить минуту", id="maf_endminute",
                                                    style=ButtonStyle.red)],
                                            [Select(options=x) for x in self.selector]])
                while True:
                    if time == 0:
                        await post.channel.edit(overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                                            self.ponies: PermissionOverwrite(send_messages=False)})
                        time = 60
                        break
                    else:
                        if self.minutes["Триггер"]:
                            break
                        await sleep(delay=1)
                        time -= 1
                        await post.edit(embed=e(t=time),
                                        components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green),
                                                     Button(label="Завершить минуту", id="maf_endminute",
                                                            style=ButtonStyle.red)],
                                                    [Select(options=x) for x in self.selector]])

    async def game(self, channel):
        try:
            bots, time = 12 - len(self.players["Люди"]), 60
            if bots < 12:
                while True:
                    if len(self.players["Боты"]) < bots:
                        bot = choice(seq=mafia["Боты"])
                        self.players["Боты"].update({bot: {}})
                        self.selector.append([SelectOption(label=f"{bot}", value=f"{bot}")])
                    else:
                        break
            else:
                self.trigger = None
            roles = ["Мирные жители", "Мирные жители", "Мирные жители", "Мирные жители", "Мирные жители", "Доктор",
                     "Маньяк", "Шериф", "Дон", "Мафия", "Мафия", "Путана"]
            if randint(a=1, b=100) == 1:
                roles.remove("Дон")
                roles.append("Дорондондон :)")
            for user in self.players["Люди"]:
                role = choice(seq=roles)
                self.players["Люди"][user].update({"Роль": role, "Жив": True})
                roles.remove(role)
            if len(self.players["Боты"]) != 0:
                for bot in self.players["Боты"]:
                    role = choice(seq=roles)
                    self.players["Боты"][bot].update({"Роль": role, "Жив": True})
                    roles.remove(role)
            await channel.send(content=f"{', '.join([user.mention for user in self.players['Люди']])} игра началась!")
            await channel.edit(overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                           self.ponies: PermissionOverwrite(send_messages=False)})
            await self.BOT.get_channel(id=1032292505938579497).purge()
            overwrites = {self.inactive: PermissionOverwrite(view_channel=False),
                          self.ponies: PermissionOverwrite(view_channel=False)}
            for player in self.players["Люди"]:
                if self.players["Люди"][player]["Роль"] in ["Дон", "Мафия", "Путана", "Дорондондон :)"]:
                    overwrites.update({player: PermissionOverwrite(read_message_history=True, send_messages=True,
                                                                   view_channel=True)})
            await self.BOT.get_channel(id=1032292505938579497).edit(overwrites=overwrites)

            def e(t):
                embed = Embed(title="Нулевая ночь:", color=self.BOT.user.color,
                              description=f"Текущая стадия: **Минута мафии**\n\nДо окончания: {t} секунд")
                embed.add_field(name="Описание:", value=mafia["Нулевая ночь"])
                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                return embed

            post = await channel.send(embed=e(t=time),
                                      components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green)]])
            while True:
                if time == 0:
                    await self.BOT.get_channel(id=1032292505938579497).edit(
                        overwrites={self.inactive: PermissionOverwrite(view_channel=False),
                                    self.ponies: PermissionOverwrite(view_channel=False)})
                    break
                else:
                    await sleep(delay=1)
                    time -= 1
                    await post.edit(embed=e(t=time),
                                    components=[[Button(label="Моя роль", id="maf_myrole", style=ButtonStyle.green)]])
            await self.days(tier=0, post=post)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 3", name="maf", help="Сыграть в Мафию", brief="Ничего", usage="!maf")
    async def maf(self, ctx):
        try:
            if ctx.channel.id == 1032292431405781083:
                await ctx.message.delete(delay=1)
                if self.trigger is None:
                    self.trigger = "Набор игроков"
                    self.players = {"Люди": {}, "Боты": {}}
                    self.vote = {"Старт": {}, "Конец": {}}
                    embed, time = Embed(title="Мафия:", color=ctx.author.color, description=mafia["Описание"]), 60
                    embed.add_field(name="Текущая стадия:", value=self.trigger)
                    embed.add_field(name="До начала игры:", value=f"{str(timedelta(seconds=time))[2:]}")
                    users1 = [user.mention for user in self.players["Люди"]]
                    embed.add_field(name=f"Текущие игроки {len(self.players['Люди'])}/12:",
                                    value="\n".join(users1) + "\nПосле окончания таймера недостающие игроки будут "
                                                              "заменены ботами.")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    post = await ctx.send(embed=embed,
                                          components=[[Button(label="Участвовать", id="maf_admember",
                                                              style=ButtonStyle.green)]])
                    await ctx.send(content=f"@everyone {ctx.author.mention} приглашает сыграть в Мафию! "
                                           f"Присоединяйтесь!")
                    while True:
                        try:
                            await self.BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                        except Exception:
                            break
                        embed = Embed(title="Мафия:", color=ctx.author.color, description=mafia["Описание"])
                        embed.add_field(name="Текущая стадия:", value=self.trigger)
                        embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                        users2 = [user.mention for user in self.players["Люди"]]
                        bots1 = [bot for bot in self.players["Боты"]]
                        if self.trigger == "Набор игроков":
                            embed.add_field(name="До начала игры:", value=f"{str(timedelta(seconds=time))[2:]}")
                            embed.add_field(name=f"Текущие игроки {len(self.players['Люди'])}/12:",
                                            value="\n".join(users2) + "\nПосле окончания времени недостающие игроки "
                                                                      "будут заменены ботами.")
                        if self.trigger == "Идет игра":
                            embed.add_field(name=f"Текущие игроки "
                                                 f"{len(self.players['Люди']) + len(self.players['Боты'])}/12:",
                                            value="\n".join(users2) + "\n" + "\n".join(bots1))
                            await post.edit(embed=embed, delete_after=60, components=[[
                                Button(label="Завершить игру", id="maf_endgame", style=ButtonStyle.red)]])
                            break
                        if time == 0:
                            if len(self.players["Люди"]) == 0:
                                try:
                                    await post.delete()
                                except Exception:
                                    pass
                                self.trigger = None
                                break
                            else:
                                self.trigger = "Идет игра"
                                embed.add_field(name=f"Текущие игроки "
                                                     f"{len(self.players['Люди']) + len(self.players['Боты'])}/12:",
                                                value="\n".join(users2) + "\n" + "\n".join(bots1))
                                await post.edit(embed=embed, delete_after=60, components=[[
                                    Button(label="Завершить игру", id="maf_endgame", style=ButtonStyle.red)]])
                                await self.game(channel=post.channel)
                                break
                        if len(self.players["Люди"]) != 0:
                            await post.edit(embed=embed, components=[[
                                Button(label="Участвовать", id="maf_admember", style=ButtonStyle.green),
                                Button(label="Принудительный старт", id="maf_startgame", style=ButtonStyle.blue)]])
                        else:
                            await post.edit(embed=embed, components=[[
                                Button(label="Участвовать", id="maf_admember", style=ButtonStyle.green)]])
                        time -= 1
                        await sleep(delay=1)
                else:
                    embed = Embed(title="Мафия:", color=ctx.author.color, description=mafia["Описание"])
                    embed.add_field(name="Текущая стадия:",
                                    value="Сейчас уже проводится другая игра, подождите ее окончания, или попросите "
                                          "участников завершить игру...")
                    users = [user.mention for user in self.players["Люди"]]
                    bots2 = [bot for bot in self.players["Боты"]]
                    if len(self.players["Люди"]) + len(self.players["Боты"]) != 0:
                        embed.add_field(name=f"Текущие игроки "
                                             f"{len(self.players['Люди']) + len(self.players['Боты'])}/12:",
                                        value="\n ".join(users) + "\n " + "\n ".join(bots2))
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    if ctx.author in self.players["Люди"]:
                        await ctx.send(embed=embed, delete_after=60, components=[[
                            Button(label="Завершить игру", id="maf_endgame", style=ButtonStyle.red)]])
                    else:
                        await ctx.send(embed=embed, delete_after=60)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "maf_admember":
                if interaction.user not in self.players["Люди"]:
                    self.players["Люди"].update({interaction.user: {}})
                    self.selector.append([SelectOption(label=f"{interaction.user.name}",
                                                       value=f"{interaction.user.name}")])
                else:
                    self.players["Люди"].pop(interaction.user)
                    self.selector.remove([SelectOption(label=f"{interaction.user.name}",
                                                       value=f"{interaction.user.name}")])
                try:
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "maf_startgame":
                if interaction.user in self.players["Люди"]:
                    self.vote["Старт"].update({interaction.user: {}})
                    post1 = await self.BOT.get_channel(id=interaction.channel.id).send(embed=Embed(
                        title="Принудительный старт:", color=0xFFA500,
                        description=f"{interaction.user.mention} голосует за принудительный старт!\n\nДля принятия "
                                    f"решения ВСЕ участники ({len(self.vote['Старт'])} из {len(self.players['Люди'])}) "
                                    f"должны проголосовать!"),
                        components=[[Button(label="Проголосовать", id="maf_votes", style=ButtonStyle.green)]],
                        delete_after=60)
                    try:
                        await interaction.respond()
                    except Exception:
                        pass
                    while True:
                        if len(self.vote["Старт"]) == len(self.players["Люди"]):
                            self.trigger = "Идет игра"
                            await self.BOT.get_channel(id=interaction.channel.id).send(delete_after=60, embed=Embed(
                                title="Принудительный старт:", color=0xFFA500,
                                description=f"Игра принудительно начата!"))
                            await self.game(channel=post1.channel)
                            break
                        interaction = await self.BOT.wait_for(event="button_click")
                        try:
                            await self.BOT.get_channel(id=post1.channel.id).fetch_message(id=post1.id)
                        except Exception:
                            break
                        if interaction.message.id == post1.id:
                            if interaction.user in self.players["Люди"]:
                                self.vote["Старт"].update({interaction.user: {}})
                        try:
                            await interaction.respond()
                        except Exception:
                            pass
                try:
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "maf_endgame":
                if interaction.user in self.players["Люди"]:
                    self.vote["Конец"].update({interaction.user: {}})
                    under = len(self.vote['Конец']) + len(self.players['Боты'])
                    upon = len(self.players['Люди']) + len(self.players['Боты'])
                    post2 = await self.BOT.get_channel(id=interaction.channel.id).send(embed=Embed(
                        title="Завершить игру:", color=0xFF0000,
                        description=f"{interaction.user.mention} голосует за принудительное завершение игры!\n\nДля "
                                    f"принятия решения ПОЛОВИНА участников ({under} из {upon}) должны проголосовать! "
                                    f"Боты всегда голосуют!"),
                        components=[[Button(label="Проголосовать", id="maf_votes", style=ButtonStyle.red)]],
                        delete_after=60)
                    try:
                        await interaction.respond()
                    except Exception:
                        pass
                    while True:
                        vote = len(self.vote["Конец"]) + len(self.players["Боты"])
                        users = len(self.players["Люди"]) + len(self.players["Боты"])
                        if vote >= users / 2:
                            self.trigger = None
                            await self.BOT.get_channel(id=interaction.channel.id).send(delete_after=60, embed=Embed(
                                title="Завершить игру:", color=0xFF0000, description=f"Игра принудительно завершена!"))
                            break
                        interaction = await self.BOT.wait_for(event="button_click")
                        try:
                            await self.BOT.get_channel(id=post2.channel.id).fetch_message(id=post2.id)
                        except Exception:
                            break
                        if interaction.message.id == post2.id:
                            if interaction.user in self.players["Люди"]:
                                self.vote["Конец"].update({interaction.user: {}})
                        try:
                            await interaction.respond()
                        except Exception:
                            pass
                try:
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "maf_myrole":
                if interaction.user in self.players["Люди"]:
                    await interaction.send(content=f"Ваша роль: **{self.players['Люди'][interaction.user]['Роль']}**")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "maf_endminute":
                if interaction.user.id == self.minutes["Пользователь"]:
                    self.minutes["Триггер"] = True
                else:
                    await interaction.send(content="Завершить минуту может только ее автор!")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_select_option(self, interaction):
        try:
            if interaction.user.id == self.minutes["Пользователь"]:
                await interaction.send(content="Поздравляем! Вам убраны все Расы!")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Mafia(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
