from asyncio import run
from traceback import format_exc

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop

from mlpbots import logs, DB


class Embeds(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            DB["embeds"].update_one(filter={"_id": "Embeds"},
                                    update={"$set": {"Бот": self.BOT.user.id}})
            self.update_data.start()
            self.check_embeds.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.update_data.cancel()
            self.check_embeds.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(minutes=1)
    async def update_data(self):
        try:
            admins, channels, positions, temp = [], [], [], {}
            for guild in self.BOT.guilds:
                for member in guild.members:
                    if member.guild_permissions.administrator:
                        admins.append(member.id)
                for channel in guild.channels:
                    if str(channel.type) == "text":
                        positions.append(channel.position)
                        temp.update({channel.position: {"name": channel.name,
                                                        "id": str(channel.id)}})
                positions.sort()
                for pos in positions:
                    channels.append({"label": temp[pos]["name"],
                                     "value": temp[pos]["id"]})
            DB["embeds"].update_one(filter={"_id": "Embeds"},
                                    update={"$set": {"Админы": admins,
                                                     "Каналы": channels}})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(seconds=1)
    async def check_embeds(self):
        try:
            embeds = DB["embeds"].find_one(filter={"_id": "Embeds"})["Ембеды"]
            if len(embeds) > 0:
                for embed in embeds:
                    e = Embed(title=embed["title"])
                    if "description" in embed:
                        e.description = embed["description"]
                    if "color" in embed:
                        e.colour = embed["color"]
                    if "url" in embed:
                        e.url = embed["url"]
                    if "thumbnail" in embed:
                        e.set_thumbnail(url=embed["thumbnail"])
                    if "image" in embed:
                        e.set_image(url=embed["image"])
                    if "author" in embed:
                        e.set_author(name=embed["author"]["name"],
                                     url=embed["author"]["url"],
                                     icon_url=embed["author"]["icon_url"])
                    if "fields" in embed:
                        for field in embed["fields"]:
                            e.add_field(name=embed["fields"][field]["name"],
                                        value=embed["fields"][field]["value"],
                                        inline=embed["fields"][field]["inline"])
                    if "footer" in embed:
                        e.set_footer(text=embed["footer"]["text"],
                                     icon_url=embed["footer"]["icon_url"])
                    member = self.BOT.guilds[0].get_member(user_id=embed["Пользователь"])
                    webhook = await self.BOT.get_channel(id=embed["Канал"]).create_webhook(name=member.display_name)
                    await webhook.send(username=member.display_name,
                                       avatar_url=member.avatar_url,
                                       embed=e)
                    await webhook.delete()
                    DB["embeds"].update_one(filter={"_id": "Embeds"},
                                            update={"$pull": {"Ембеды": embed}})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Embeds(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
