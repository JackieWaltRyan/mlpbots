from asyncio import run
from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord_components_mirror import Button, ButtonStyle
from mlpbots import logs, LEVELS, FOOTER, save
from traceback import format_exc


class TicTacToe(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @command(description="Все 3", name="tic", help="Сыграть в Крестики-нолики",
             brief="Ничего / `Упоминание пользователя`", usage="!tic <@918687493577121884>")
    async def command_tic(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if member is not None:
                    from db.members import members
                    top_1, top_2 = {}, []
                    for member_1 in members:
                        wins = int(members[member_1]["Крестики-нолики"]["Побед"])
                        defeats = int(members[member_1]["Крестики-нолики"]["Поражений"])
                        games = int(members[member_1]["Крестики-нолики"]["Сыграно"])
                        if games > 0:
                            percent = int(((wins - defeats) / games) * 100)
                        else:
                            percent = 0
                        members[member_1]["Крестики-нолики"]["Процент"] = percent
                        top_1.update({percent: member_1})
                        top_2.append(percent)
                    await save(file="members", content=members)
                    embed = Embed(title="Статистика игры \"Крестики-нолики\":", color=ctx.author.color,
                                  description=f"**Пользователь {member.mention}:**\n"
                                              f"Сыграно игр: **{members[member.id]['Крестики-нолики']['Сыграно']}**\n"
                                              f"Побед: **{members[member.id]['Крестики-нолики']['Побед']}**\n"
                                              f"Поражений: **{members[member.id]['Крестики-нолики']['Поражений']}**\n"
                                              f"Процент побед: **{members[member.id]['Крестики-нолики']['Процент']}%**")
                    top, i = "", 1
                    top_2.sort(reverse=True)
                    for item in top_2:
                        if item != 0:
                            if i <= 10:
                                top += f"<@{top_1[item]}>: {item}%\n"
                            i += 1
                    if top == "":
                        top = "Сейчас нет пони, которые играли в Крестики-нолики."
                    embed.add_field(name="Таблица лидеров:", value=top)
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed, delete_after=60)
                else:
                    label = [["\u200b", "\u200b", "\u200b"],
                             ["\u200b", "\u200b", "\u200b"],
                             ["\u200b", "\u200b", "\u200b"]]
                    style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]
                    disabled = [[False, False, False],
                                [False, False, False],
                                [False, False, False]]
                    tick, gamer_1, gamer_2 = "Крестики", None, None

                    def button(lb, st, ds):
                        buttons = [[Button(label=lb[0][0], style=st[0][0], id="0 0", disabled=ds[0][0]),
                                    Button(label=lb[0][1], style=st[0][1], id="0 1", disabled=ds[0][1]),
                                    Button(label=lb[0][2], style=st[0][2], id="0 2", disabled=ds[0][2])],
                                   [Button(label=lb[1][0], style=st[1][0], id="1 0", disabled=ds[1][0]),
                                    Button(label=lb[1][1], style=st[1][1], id="1 1", disabled=ds[1][1]),
                                    Button(label=lb[1][2], style=st[1][2], id="1 2", disabled=ds[1][2])],
                                   [Button(label=lb[2][0], style=st[2][0], id="2 0", disabled=ds[2][0]),
                                    Button(label=lb[2][1], style=st[2][1], id="2 1", disabled=ds[2][1]),
                                    Button(label=lb[2][2], style=st[2][2], id="2 2", disabled=ds[2][2])]]
                        return buttons

                    embed_2 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                    description="Первые ходят **крестики**:")
                    post = await ctx.send(embed=embed_2, components=button(lb=label, st=style, ds=disabled))
                    try:
                        while True:
                            interaction = await self.BOT.wait_for("button_click")
                            try:
                                await self.BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                            except Exception:
                                break
                            if interaction.message.id == post.id:
                                button_id = interaction.component.id
                                position = button_id.split(" ")
                                if tick == "Крестики":
                                    if gamer_1 is None:
                                        gamer_1 = interaction.user
                                    if gamer_1 is not None and interaction.user != gamer_1:
                                        continue
                                    label[int(position[0])][int(position[1])] = "X"
                                    style[int(position[0])][int(position[1])] = ButtonStyle.red
                                    disabled[int(position[0])][int(position[1])] = True
                                    tick = "Нолики"
                                else:
                                    if gamer_2 is None and interaction.user != gamer_1:
                                        gamer_2 = interaction.user
                                    if gamer_2 is None and interaction.user == gamer_1:
                                        continue
                                    if gamer_2 is not None and interaction.user != gamer_2:
                                        continue
                                    label[int(position[0])][int(position[1])] = "O"
                                    style[int(position[0])][int(position[1])] = ButtonStyle.green
                                    disabled[int(position[0])][int(position[1])] = True
                                    tick = "Крестики"
                                embed_2 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                description=f"Сейчас ходят **{tick}**:")
                                if gamer_1 is not None:
                                    embed_2 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                    description=f"За крестиков играет: {gamer_1.mention}\n\n"
                                                                f"Сейчас ходят **{tick}**:")
                                    if gamer_2 is not None:
                                        embed_2 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                        description=f"За крестиков играет: {gamer_1.mention}\n"
                                                                    f"За ноликов играет: {gamer_2.mention}\n\n"
                                                                    f"Сейчас ходят **{tick}**:")

                                def winners(player):
                                    embed_3 = None
                                    from db.members import members
                                    if player == "X":
                                        embed_3 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                        description=f"За крестиков играл: {gamer_1.mention}\n"
                                                                    f"За ноликов играл: {gamer_2.mention}\n\n"
                                                                    f"Победили **крестики**!")
                                        members[gamer_1.id]["Крестики-нолики"]["Сыграно"] += 1
                                        members[gamer_1.id]["Крестики-нолики"]["Побед"] += 1
                                        members[gamer_2.id]["Крестики-нолики"]["Сыграно"] += 1
                                        members[gamer_2.id]["Крестики-нолики"]["Поражений"] += 1
                                    if player == "O":
                                        embed_3 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                        description=f"За крестиков играл: {gamer_1.mention}\n"
                                                                    f"За ноликов играл: {gamer_2.mention}\n\n"
                                                                    f"Победили **нолики**!")
                                        members[gamer_1.id]["Крестики-нолики"]["Сыграно"] += 1
                                        members[gamer_1.id]["Крестики-нолики"]["Поражений"] += 1
                                        members[gamer_2.id]["Крестики-нолики"]["Сыграно"] += 1
                                        members[gamer_2.id]["Крестики-нолики"]["Побед"] += 1
                                    if player == "XO":
                                        embed_3 = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                                        description=f"За крестиков играл: {gamer_1.mention}\n"
                                                                    f"За ноликов играл: {gamer_2.mention}\n\n"
                                                                    f"У нас **ничья**!")
                                        members[gamer_1.id]["Крестики-нолики"]["Сыграно"] += 1
                                        members[gamer_2.id]["Крестики-нолики"]["Сыграно"] += 1
                                    for x in range(3):
                                        for xx in range(3):
                                            disabled[x][xx] = True
                                    return embed_3, members

                                count, mem = 0, None
                                for line in label:
                                    count += line.count("\u200b")
                                if count == 0:
                                    embed_2, mem = winners(player="XO")
                                for line in label:
                                    if line.count("X") == 3:
                                        embed_2, mem = winners(player="X")
                                    if line.count("O") == 3:
                                        embed_2, mem = winners(player="O")
                                for line in range(3):
                                    value = label[0][line] + label[1][line] + label[2][line]
                                    if value == "XXX":
                                        embed_2, mem = winners(player="X")
                                    if value == "OOO":
                                        embed_2, mem = winners(player="O")
                                diagonal_1 = label[0][2] + label[1][1] + label[2][0]
                                diagonal_2 = label[0][0] + label[1][1] + label[2][2]
                                if diagonal_1 == "XXX" or diagonal_2 == "XXX":
                                    embed_2, mem = winners(player="X")
                                if diagonal_1 == "OOO" or diagonal_2 == "OOO":
                                    embed_2, mem = winners(player="O")
                                if mem is not None:
                                    await save(file="members", content=mem)
                                await post.edit(embed=embed_2, components=button(lb=label, st=style, ds=disabled))
                                if count != 0:
                                    try:
                                        await interaction.respond()
                                    except Exception:
                                        pass
                                else:
                                    await interaction.respond()
                    except Exception:
                        await logs(level=LEVELS[4], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=TicTacToe(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
