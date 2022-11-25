from asyncio import sleep, run
from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord_components_mirror import Button, ButtonStyle
from mlpbots import logs, LEVELS, FOOTER, save
from random import choice, randint
from traceback import format_exc


class Tetris(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.posts, self.styles, self.positions, self.members = bot, {}, {}, {}, {}
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "tetris_left" or interaction.component.id == "tetris_right":
                post_id = self.posts[interaction.message.id]
                position, member, style = self.positions[post_id], self.members[post_id], self.styles[post_id]
                if position is not None:
                    if interaction.component.id == "tetris_left":
                        if member is None:
                            member = interaction.user
                        if interaction.user == member:
                            if position[1] > 0:
                                if style[position[0] + 1][position[1] - 1] == ButtonStyle.gray:
                                    style[position[0]][position[1]] = ButtonStyle.gray
                                    position[1] = position[1] - 1
                            self.styles.update([(post_id, style)])
                            self.members.update([(post_id, member)])
                            self.positions.update([(post_id, position)])
                            try:
                                await interaction.respond()
                            except Exception:
                                pass
                    if interaction.component.id == "tetris_right":
                        if member is None:
                            member = interaction.user
                        if interaction.user == member:
                            if position[1] < 4:
                                if style[position[0] + 1][position[1] + 1] == ButtonStyle.gray:
                                    style[position[0]][position[1]] = ButtonStyle.gray
                                    position[1] = position[1] + 1
                            self.styles.update([(post_id, style)])
                            self.members.update([(post_id, member)])
                            self.positions.update([(post_id, position)])
                            try:
                                await interaction.respond()
                            except Exception:
                                pass
                else:
                    try:
                        await interaction.respond()
                    except Exception:
                        pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 3", name="tet", help="Сыграть в Тетрис", brief="Ничего / `Упоминание пользователя`",
             usage="!tet <@918687493577121884>")
    async def command_tet(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if member is not None:
                    from db.members import members
                    embed = Embed(title="Статистика игры \"Тетрис\":", color=ctx.author.color,
                                  description=f"**Пользователь {member.mention}:**\n"
                                              f"Сыграно игр: **{members[member.id]['Тетрис']['Сыграно']}**\n"
                                              f"Лучший счет: **{members[member.id]['Тетрис']['Лучший счет']}**")
                    top, i, top_1, top_2 = "", 1, {}, []
                    for member in members:
                        if members[member]["Тетрис"]["Лучший счет"] > 0:
                            top_1.update({members[member]["Тетрис"]["Лучший счет"]: member})
                            top_2.append(members[member]["Тетрис"]["Лучший счет"])
                    top_2.sort()
                    for item in top_2:
                        if i <= 10:
                            top += f"<@{top_1[item]}>: {item}\n"
                        i += 1
                    if top == "":
                        top = "Сейчас нет пони, которые играли в Тетрис."
                    embed.add_field(name="Таблица лидеров:", value=top)
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed, delete_after=60)
                else:
                    style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]
                    disabled = [[False, False, False, False, False],
                                [False, False, False, False, False],
                                [False, False, False, False, False],
                                [False, False, False, False, False],
                                [False, False, False, False, False]]
                    score, time = 0, 1

                    def button(st, ds):
                        buttons = [[Button(label="\u200b", style=int(st[0][0]), disabled=ds[0][0]),
                                    Button(label="\u200b", style=int(st[0][1]), disabled=ds[0][1]),
                                    Button(label="\u200b", style=int(st[0][2]), disabled=ds[0][2]),
                                    Button(label="\u200b", style=int(st[0][3]), disabled=ds[0][3]),
                                    Button(label="\u200b", style=int(st[0][4]), disabled=ds[0][4])],
                                   [Button(label="\u200b", style=int(st[1][0]), disabled=ds[1][0]),
                                    Button(label="\u200b", style=int(st[1][1]), disabled=ds[1][1]),
                                    Button(label="\u200b", style=int(st[1][2]), disabled=ds[1][2]),
                                    Button(label="\u200b", style=int(st[1][3]), disabled=ds[1][3]),
                                    Button(label="\u200b", style=int(st[1][4]), disabled=ds[1][4])],
                                   [Button(label="\u200b", style=int(st[2][0]), disabled=ds[2][0]),
                                    Button(label="\u200b", style=int(st[2][1]), disabled=ds[2][1]),
                                    Button(label="\u200b", style=int(st[2][2]), disabled=ds[2][2]),
                                    Button(label="\u200b", style=int(st[2][3]), disabled=ds[2][3]),
                                    Button(label="\u200b", style=int(st[2][4]), disabled=ds[2][4])],
                                   [Button(label="\u200b", style=int(st[3][0]), disabled=ds[3][0]),
                                    Button(label="\u200b", style=int(st[3][1]), disabled=ds[3][1]),
                                    Button(label="\u200b", style=int(st[3][2]), disabled=ds[3][2]),
                                    Button(label="\u200b", style=int(st[3][3]), disabled=ds[3][3]),
                                    Button(label="\u200b", style=int(st[3][4]), disabled=ds[3][4])],
                                   [Button(label="\u200b", style=int(st[4][0]), disabled=ds[4][0]),
                                    Button(label="\u200b", style=int(st[4][1]), disabled=ds[4][1]),
                                    Button(label="\u200b", style=int(st[4][2]), disabled=ds[4][2]),
                                    Button(label="\u200b", style=int(st[4][3]), disabled=ds[4][3]),
                                    Button(label="\u200b", style=int(st[4][4]), disabled=ds[4][4])]]
                        return buttons

                    embed_2 = Embed(title="Тетрис:", color=ctx.author.color)
                    post = await ctx.send(embed=embed_2, components=button(st=style, ds=disabled))
                    control = await ctx.send(components=[[Button(emoji="⬅️", id="tetris_left"),
                                                          Button(emoji="➡️", id="tetris_right")]])
                    self.posts.update([(control.id, post.id)])
                    self.styles.update([(post.id, style)])
                    self.members.update([(post.id, None)])
                    self.positions.update([(post.id, None)])
                    try:
                        while True:
                            try:
                                await self.BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                            except Exception:
                                break
                            style_2 = self.styles[post.id]
                            position = self.positions[post.id]
                            member = self.members[post.id]
                            if style_2[4].count(ButtonStyle.gray) == 0:
                                style_2[4].clear()
                                style_2[4].extend(style_2[3])
                                style_2[3].clear()
                                style_2[3].extend(style_2[2])
                                style_2[2].clear()
                                style_2[2].extend(style_2[1])
                                style_2[1].clear()
                                style_2[1].extend(style_2[0])
                                style_2[0].clear()
                                style_2[0].extend([ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray,
                                                   ButtonStyle.gray, ButtonStyle.gray])
                                score += 10
                                time -= 0.1
                            if member is not None:
                                embed_2 = Embed(title="Тетрис:", color=ctx.author.color,
                                                description=f"Сейчас играет: {member.mention}\nCчет: **{score}**")
                            for x in range(5):
                                column = 5
                                for line in style_2:
                                    if line[x] != ButtonStyle.gray:
                                        column -= 1
                                if column == 0:
                                    if member is not None:
                                        embed_2 = Embed(title="Тетрис:", color=ctx.author.color,
                                                        description=f"Играл: {member.mention}\n"
                                                                    f"Финальный счет: **{score}**")
                                    else:
                                        embed_2 = Embed(title="Тетрис:", color=ctx.author.color,
                                                        description=f"Играл: {self.BOT.user.mention}\n"
                                                                    f"Финальный счет: **{score}**")
                                        member = self.BOT.user
                                    await control.delete()
                                    from db.members import members
                                    members[member.id]["Тетрис"]["Сыграно"] += 1
                                    if score > members[member.id]["Тетрис"]["Лучший счет"]:
                                        members[member.id]["Тетрис"]["Лучший счет"] = score
                                    await save(file="members", content=members)
                                    for xx in range(5):
                                        for xxx in range(5):
                                            disabled[xx][xxx] = True
                            if position is None:
                                button_1, color = randint(0, 4), choice([ButtonStyle.green, ButtonStyle.red,
                                                                         ButtonStyle.blue])
                                if style_2[0][button_1] == ButtonStyle.gray:
                                    style_2[0][button_1] = color
                                    position = [0, button_1, color]
                            else:
                                if style_2[position[0] + 1][position[1]] == ButtonStyle.gray:
                                    style_2[position[0] + 1][position[1]] = position[2]
                                    style_2[position[0]][position[1]] = ButtonStyle.gray
                                    position[0] = position[0] + 1
                                    if position[0] == 4:
                                        position = None
                                else:
                                    position = None
                            await post.edit(embed=embed_2, components=button(st=style_2, ds=disabled))
                            self.styles.update([(post.id, style_2)])
                            self.members.update([(post.id, member)])
                            self.positions.update([(post.id, position)])
                            await sleep(delay=time)
                    except Exception:
                        await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Tetris(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
