from asyncio import run
from io import BytesIO
from re import findall
from traceback import format_exc

from PIL.Image import open
from discord import File
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from pymongo import ASCENDING
from requests import get

from mlpbots import DB, logs


class Arts(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.check_arts.start()
            self.send_arts.start()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    def cog_unload(self):
        try:
            self.check_arts.cancel()
            self.send_arts.cancel()
        except Exception:
            run(main=logs(level="ERROR",
                          message=format_exc()))

    @loop(hours=1)
    async def check_arts(self):
        try:
            request = get(url="https://4pda.to/forum/index.php?showtopic=403239&view=getnewpost").content
            url, formats = "//4pda.to/forum/dl/post/", "jpg|png|gif|jpeg"
            counts = len(findall(pattern=rf"{url}(\d*)/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats})",
                                 string=f"{request}"))
            if counts > 0:
                news = int(findall(pattern=rf"{url}(\d*)/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:{formats})",
                                   string=f"{request}")[-1][:-3])
                posts_1 = findall(pattern=rf"{url}((?:{news - 1}\d{{3}})/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:"
                                          rf"{formats}))",
                                  string=f"{request}")
                posts_2 = findall(pattern=rf"{url}((?:{news}\d{{3}})/(?:[_\-]*\w+[_\-]+){{2,}}\w+[(\d+)%]*\.(?:"
                                          rf"{formats}))",
                                  string=f"{request}")
                if int(news) > DB["settings"].find_one(filter={"_id": "Арты"})["Триггер"]:
                    DB["settings"].update_one(filter={"_id": "Арты"},
                                              update={"$set": {"Триггер": news}})
                    for art in posts_1 + posts_2:
                        try:
                            DB["arts"].insert_one(document={"_id": art})
                        except Exception:
                            await logs(level="DEBUG",
                                       message=format_exc())
                    await logs(level="INFO",
                               message=f"**{len(posts_1) + len(posts_2)}** артов загружены в БД!\n"
                                       f"На данный момент в базе данных "
                                       f"**{DB['arts'].count_documents(filter={})}** артов!")
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())

    @loop(minutes=30)
    async def send_arts(self):
        try:
            art = DB["arts"].find().sort(key_or_list="_id",
                                         direction=ASCENDING)[0]["_id"]
            while True:
                request = get(url=f"https://4pda.to/forum/dl/post/{art}").content
                if b"html" not in request:
                    if len(request) > 8000000:
                        while True:
                            img = open(fp=BytesIO(request))
                            new_size_ratio = 1 - ((len(request) / 8000000) / 10)
                            img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)))
                            out = BytesIO()
                            img.save(fp=out,
                                     format="PNG")
                            request = out.getvalue()
                            if len(request) < 8000000:
                                break
                    break
                else:
                    DB["arts"].delete_one(filter={"_id": art})
            channel = DB["channels"].find_one(filter={"Категория": "Арты"})["_id"]
            await self.BOT.get_channel(id=channel).send(file=File(fp=BytesIO(request),
                                                                  filename="img.png"))
            DB["arts"].delete_one(filter={"_id": art})
        except Exception:
            await logs(level="ERROR",
                       message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Arts(bot=bot))
    except Exception:
        run(main=logs(level="ERROR",
                      message=format_exc()))
