from asyncio import sleep, run
from random import choice, randint
from traceback import format_exc

from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord_components_mirror import Button, ButtonStyle
from pymongo import DESCENDING

from mlpbots import logs, DB, FOOTER


async def buttons(style, disabled):
    try:
        return [[Button(label="\u200b",
                        style=int(style[0][0]),
                        disabled=disabled[0][0]),
                 Button(label="\u200b",
                        style=int(style[0][1]),
                        disabled=disabled[0][1]),
                 Button(label="\u200b",
                        style=int(style[0][2]),
                        disabled=disabled[0][2]),
                 Button(label="\u200b",
                        style=int(style[0][3]),
                        disabled=disabled[0][3]),
                 Button(label="\u200b",
                        style=int(style[0][4]),
                        disabled=disabled[0][4])],
                [Button(label="\u200b",
                        style=int(style[1][0]),
                        disabled=disabled[1][0]),
                 Button(label="\u200b",
                        style=int(style[1][1]),
                        disabled=disabled[1][1]),
                 Button(label="\u200b",
                        style=int(style[1][2]),
                        disabled=disabled[1][2]),
                 Button(label="\u200b",
                        style=int(style[1][3]),
                        disabled=disabled[1][3]),
                 Button(label="\u200b",
                        style=int(style[1][4]),
                        disabled=disabled[1][4])],
                [Button(label="\u200b",
                        style=int(style[2][0]),
                        disabled=disabled[2][0]),
                 Button(label="\u200b",
                        style=int(style[2][1]),
                        disabled=disabled[2][1]),
                 Button(label="\u200b",
                        style=int(style[2][2]),
                        disabled=disabled[2][2]),
                 Button(label="\u200b",
                        style=int(style[2][3]),
                        disabled=disabled[2][3]),
                 Button(label="\u200b",
                        style=int(style[2][4]),
                        disabled=disabled[2][4])],
                [Button(label="\u200b",
                        style=int(style[3][0]),
                        disabled=disabled[3][0]),
                 Button(label="\u200b",
                        style=int(style[3][1]),
                        disabled=disabled[3][1]),
                 Button(label="\u200b",
                        style=int(style[3][2]),
                        disabled=disabled[3][2]),
                 Button(label="\u200b",
                        style=int(style[3][3]),
                        disabled=disabled[3][3]),
                 Button(label="\u200b",
                        style=int(style[3][4]),
                        disabled=disabled[3][4])],
                [Button(label="\u200b",
                        style=int(style[4][0]),
                        disabled=disabled[4][0]),
                 Button(label="\u200b",
                        style=int(style[4][1]),
                        disabled=disabled[4][1]),
                 Button(label="\u200b",
                        style=int(style[4][2]),
                        disabled=disabled[4][2]),
                 Button(label="\u200b",
                        style=int(style[4][3]),
                        disabled=disabled[4][3]),
                 Button(label="\u200b",
                        style=int(style[4][4]),
                        disabled=disabled[4][4])]]
    except Exception:
        await logs(level="ERROR",
                   message=format_exc())


class Tetris(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.posts, self.styles, self.positions, self.members = bot, {}, {}, {}, {}
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

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
                                    position[1] -= 1
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
                                    position[1] += 1
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
            await logs(level="ERROR",
                       message=format_exc())

    @command(description="Все 3",
             name="tet",
             help="Сыграть в Тетрис",
             brief="Ничего / `Упоминание пользователя`",
             usage="!tet <@918687493577121884>")
    async def command_tet(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if member is not None:
                    score, db = 0, DB["members"].find_one(filter={"_id": member.id})
                    if "Тетрис" in db:
                        score = db["Тетрис"]
                    embed = Embed(title="Статистика игры \"Тетрис\":",
                                  color=ctx.author.color,
                                  description=f"**Пользователь {member.mention}:**\n"
                                              f"Лучший счет: **{score}**")
                    top, i = "", 1
                    for user in DB["members"].find().sort(key_or_list="Тетрис",
                                                          direction=DESCENDING):
                        if "Тетрис" in user:
                            if i <= 10:
                                top += f"<@{user['_id']}>: {user['Тетрис']}\n"
                            i += 1
                    embed.add_field(name="Таблица лидеров:",
                                    value=top)
                    embed.set_footer(text=FOOTER["Текст"],
                                     icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed,
                                   delete_after=60)
                else:
                    style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                             [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]
                    disabled, score, time = [[False, False, False, False, False],
                                             [False, False, False, False, False],
                                             [False, False, False, False, False],
                                             [False, False, False, False, False],
                                             [False, False, False, False, False]], 0, 1
                    embed = Embed(title="Тетрис:",
                                  color=ctx.author.color)
                    post = await ctx.send(embed=embed,
                                          components=await buttons(style=style,
                                                                   disabled=disabled))
                    control = await ctx.send(components=[[Button(emoji="⬅️",
                                                                 id="tetris_left"),
                                                          Button(emoji="➡️",
                                                                 id="tetris_right")]])
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
                            style, position = self.styles[post.id], self.positions[post.id]
                            member = self.members[post.id]
                            if style[4].count(ButtonStyle.gray) == 0:
                                style[4].clear()
                                style[4].extend(style[3])
                                style[3].clear()
                                style[3].extend(style[2])
                                style[2].clear()
                                style[2].extend(style[1])
                                style[1].clear()
                                style[1].extend(style[0])
                                style[0].clear()
                                style[0].extend([ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray,
                                                 ButtonStyle.gray])
                                score += 10
                                time -= 0.1
                            if member is not None:
                                embed = Embed(title="Тетрис:",
                                              color=ctx.author.color,
                                              description=f"Сейчас играет: {member.mention}\n"
                                                          f"Cчет: **{score}**")
                            for x in range(5):
                                column = 5
                                for line in style:
                                    if line[x] != ButtonStyle.gray:
                                        column -= 1
                                if column == 0:
                                    if member is not None:
                                        embed = Embed(title="Тетрис:",
                                                      color=ctx.author.color,
                                                      description=f"Играл: {member.mention}\n"
                                                                  f"Финальный счет: **{score}**")
                                    else:
                                        embed = Embed(title="Тетрис:",
                                                      color=ctx.author.color,
                                                      description=f"Играл: {self.BOT.user.mention}\n"
                                                                  f"Финальный счет: **{score}**")
                                        member = self.BOT.user
                                    await control.delete()
                                    db = DB["members"].find_one(filter={"_id": member.id})
                                    if "Тетрис" in db:
                                        if score > int(db["Тетрис"]):
                                            DB["members"].update_one(filter={"_id": member.id},
                                                                     update={"$set": {"Тетрис": score}})
                                    else:
                                        DB["members"].update_one(filter={"_id": member.id},
                                                                 update={"$set": {"Тетрис": score}})
                                    for xx in range(5):
                                        for xxx in range(5):
                                            disabled[xx][xxx] = True
                            if position is None:
                                button, color = randint(0, 4), choice([ButtonStyle.green, ButtonStyle.red,
                                                                       ButtonStyle.blue])
                                if style[0][button] == ButtonStyle.gray:
                                    style[0][button], position = color, [0, button, color]
                            else:
                                if style[position[0] + 1][position[1]] == ButtonStyle.gray:
                                    style[position[0] + 1][position[1]] = position[2]
                                    style[position[0]][position[1]] = ButtonStyle.gray
                                    position[0] += 1
                                    if position[0] == 4:
                                        position = None
                                else:
                                    position = None
                            await post.edit(embed=embed,
                                            components=await buttons(style=style,
                                                                     disabled=disabled))
                            self.styles.update([(post.id, style)])
                            self.members.update([(post.id, member)])
                            self.positions.update([(post.id, position)])
                            await sleep(time)
                    except Exception:
                        await logs(level="DEBUG",
                                   message=format_exc())
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Tetris(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
