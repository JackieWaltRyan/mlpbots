from datetime import datetime
from functools import partial
from os import makedirs, execl
from os.path import exists
from re import match, IGNORECASE
from sys import executable
from threading import Timer
from traceback import format_exc

from discord_webhook import DiscordEmbed, DiscordWebhook
from pymongo import MongoClient
from pytz import timezone
from pywebio import config, start_server
from pywebio.input import URL, COLOR
from pywebio.output import put_html, put_text, put_scope, put_markdown, put_button, toast, clear, remove, put_row
from pywebio.pin import pin_on_change, put_select, put_input, put_textarea, put_checkbox
from pywebio.session import local
from pywebio_battery import get_query
from requests import post, get

DB, LEVELS = MongoClient()["mlpbots"], {"DEBUG": 0x0000FF,
                                        "INFO": 0x008000,
                                        "WARNING": 0xFFFF00,
                                        "ERROR": 0xFFA500,
                                        "CRITICAL": 0xFF0000}
BOTS = DB["settings"].find_one(filter={"_id": "Боты"})
TIME = str(datetime.now(tz=timezone(zone="Europe/Moscow")))[:-13].replace(" ", "_").replace("-", "_").replace(":", "_")


def logs(level, message):
    try:
        db = DB["settings"].find_one(filter={"_id": "Логи"})
        if level == "DEBUG" and not db["Дебаг"]:
            return None
        print(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level}:\n{message}\n\n")
        if not exists(path="temp/logs"):
            makedirs(name="temp/logs")
        with open(file=f"temp/logs/{TIME}.log",
                  mode="a+",
                  encoding="UTF-8") as log_file:
            log_file.write(f"{datetime.now(tz=timezone(zone='Europe/Moscow'))} {level}:\n{message}\n\n")
        time, username, avatar_url = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S")), "", ""
        if 80000 <= time < 200000:
            username = BOTS["868148805722337320"]["Имя"]
            avatar_url = BOTS["868148805722337320"]["Аватар"]
        else:
            username = BOTS["868150460735971328"]["Имя"]
            avatar_url = BOTS["868150460735971328"]["Аватар"]
        webhook = DiscordWebhook(username=username,
                                 avatar_url=avatar_url,
                                 url=db["Вебхук"])
        if len(message) <= 4096:
            webhook.add_embed(embed=DiscordEmbed(title=level,
                                                 description=message,
                                                 color=LEVELS[level]))
        else:
            webhook.add_file(file=message.encode(encoding="UTF-8",
                                                 errors="ignore"),
                             filename=f"{level}.log")
        webhook.execute()
    except Exception:
        logs(level="CRITICAL",
             message=format_exc())


def restart():
    try:
        execl(executable, "python", "embeds.py")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def autores():
    try:
        time = int(datetime.now(tz=timezone(zone="Europe/Moscow")).strftime("%H%M%S"))
        print(f"embeds: {time}")
        Timer(interval=1,
              function=partial(autores)).start()
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def change_channel(channel):
    try:
        local["Embed"]["Канал"] = int(channel)
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def change_embed(content, value):
    try:
        if value == "title":
            local["Embed"]["title"] = content
            if local["Embed"]["title"] == "":
                local["Embed"].pop("title")
                toast(content="Значение \"Название\" не может быть пустым!",
                      duration=5,
                      color="error")
        if value == "description":
            local["Embed"]["description"] = content
            if local["Embed"]["description"] == "":
                local["Embed"].pop("description")
        if value == "color":
            local["Embed"]["color"] = int(content[1:], 16)
            if local["Embed"]["color"] == "":
                local["Embed"].pop("color")
                toast(content="Значение \"Цвет\" не может быть пустым!",
                      duration=5,
                      color="error")
        if value in ["url", "thumbnail", "image"]:
            local["Embed"][value] = content
            if local["Embed"][value] == "":
                local["Embed"].pop(value)
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def change_author(content, value):
    try:
        if "author" not in local["Embed"]:
            local["Embed"]["author"] = {}
        if value == "add":
            clear(scope="author")
            put_markdown(mdcontent="## Блок \"Автор\":",
                         scope="author")
            put_textarea(name="author_name",
                         label="Имя (обязательно) [текст]:",
                         rows=1,
                         maxlength=256,
                         help_text="Максимум 256 символов.",
                         scope="author")
            pin_on_change(name="author_name",
                          clear=True,
                          onchange=partial(change_author,
                                           value="name"))
            put_input(name="author_url",
                      type=URL,
                      label="Ссылка (не обязательно) [ссылка]:",
                      scope="author")
            pin_on_change(name="author_url",
                          clear=True,
                          onchange=partial(change_author,
                                           value="url"))
            put_input(name="author_icon_url",
                      type=URL,
                      label="Аватар (не обязательно) [ссылка]:",
                      scope="author")
            pin_on_change(name="author_icon_url",
                          clear=True,
                          onchange=partial(change_author,
                                           value="icon_url"))
            put_button(label="Удалить блок \"Автор\"",
                       onclick=partial(change_author,
                                       content=None,
                                       value="del"),
                       color="danger",
                       scope="author")
        if value == "del":
            clear(scope="author")
            put_button(label="Добавить блок \"Автор\"",
                       onclick=partial(change_author,
                                       content=None,
                                       value="add"),
                       color="primary",
                       scope="author")
            local["Embed"].pop("author")
        if value == "name":
            local["Embed"]["author"]["name"] = content
            if local["Embed"]["author"]["name"] == "":
                local["Embed"]["author"].pop("name")
                toast(content="Значение \"Имя\" не может быть пустым!",
                      duration=5,
                      color="error")
        if value in ["url", "icon_url"]:
            local["Embed"]["author"][value] = content
            if local["Embed"]["author"][value] == "":
                local["Embed"]["author"].pop(value)
        if "author" in local["Embed"]:
            if len(local["Embed"]["author"]) == 0:
                local["Embed"].pop("author")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def change_field(content, value):
    try:
        if "fields" not in local["Embed"]:
            local["Embed"]["fields"] = {}
        if value == "add":
            i = len(local["Embed"]["fields"]) + 1
            if i <= 25:
                if f"{i}" not in local["Embed"]["fields"]:
                    local["Embed"]["fields"][f"{i}"] = {}
                put_scope(name=f"field_{i}",
                          content=[],
                          scope="fields")
                put_markdown(mdcontent=f"## Блок \"Филд\" {i}:",
                             scope=f"field_{i}")
                put_textarea(name=f"field_name_{i}",
                             label="Название (обязательно) [текст]:",
                             rows=1,
                             maxlength=256,
                             help_text="Максимум 256 символов.",
                             scope=f"field_{i}")
                pin_on_change(name=f"field_name_{i}",
                              clear=True,
                              onchange=partial(change_field,
                                               value=f"name_{i}"))
                put_textarea(name=f"field_value_{i}",
                             label="Значение (обязательно) [текст]:",
                             rows=3,
                             maxlength=1024,
                             help_text="Максимум 1024 символа.",
                             scope=f"field_{i}")
                pin_on_change(name=f"field_value_{i}",
                              clear=True,
                              onchange=partial(change_field,
                                               value=f"value_{i}"))
                put_checkbox(name=f"field_inline_{i}", options=[{"label": "В строку",
                                                                 "value": True}],
                             scope=f"field_{i}")
                pin_on_change(name=f"field_inline_{i}",
                              clear=True,
                              onchange=partial(change_field,
                                               value=f"inline_{i}"))
                put_button(label=f"Удалить блок \"Филд\" {i}",
                           onclick=partial(change_field,
                                           content=f"field_{i}",
                                           value="del"),
                           color="danger",
                           scope=f"field_{i}")
            else:
                toast(content="Максимум 25 филдов!",
                      duration=5,
                      color="error")
        if value == "del":
            remove(scope=content)
            local["Embed"]["fields"].pop(content[6:])
        if "name" in value:
            local["Embed"]["fields"][value[5:]]["name"] = content
            if local["Embed"]["fields"][value[5:]]["name"] == "":
                local["Embed"]["fields"][value[5:]].pop("name")
                toast(content="Значение \"Название\" не может быть пустым!",
                      duration=5,
                      color="error")
        if "value" in value:
            local["Embed"]["fields"][value[6:]]["value"] = content
            if local["Embed"]["fields"][value[6:]]["value"] == "":
                local["Embed"]["fields"][value[6:]].pop("value")
                toast(content="Значение \"Значение\" не может быть пустым!",
                      duration=5,
                      color="error")
        if "inline" in value:
            if content:
                local["Embed"]["fields"][value[7:]]["inline"] = True
            else:
                local["Embed"]["fields"][value[7:]].pop("inline")
        if "fields" in local["Embed"]:
            if len(local["Embed"]["fields"]) == 0:
                local["Embed"].pop("fields")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def change_footer(content, value):
    try:
        if "footer" not in local["Embed"]:
            local["Embed"]["footer"] = {}
        if value == "add":
            clear(scope="footer")
            put_markdown(mdcontent="## Блок \"Футер\":",
                         scope="footer")
            put_textarea(name="footer_text",
                         label="Текст (не обязательно) [текст]:",
                         rows=6,
                         maxlength=2048,
                         help_text="Максимум 2048 символов.",
                         scope="footer")
            pin_on_change(name="footer_text",
                          clear=True,
                          onchange=partial(change_footer,
                                           value="text"))
            put_input(name="footer_icon_url",
                      type=URL,
                      label="Иконка (не обязательно) [ссылка]:",
                      scope="footer")
            pin_on_change(name="footer_icon_url",
                          clear=True,
                          onchange=partial(change_footer,
                                           value="icon_url"))
            put_button(label="Удалить блок \"Футер\"",
                       onclick=partial(change_footer,
                                       content=None,
                                       value="del"),
                       color="danger",
                       scope="footer")
        if value == "del":
            clear(scope="footer")
            put_button(label="Добавить блок \"Футер\"",
                       onclick=partial(change_footer,
                                       content=None,
                                       value="add"),
                       color="primary",
                       scope="footer")
            local["Embed"].pop("footer")
        if value == "text":
            local["Embed"]["footer"]["text"] = content
            if local["Embed"]["footer"]["text"] == "":
                local["Embed"]["footer"].pop("text")
        if value == "icon_url":
            local["Embed"]["footer"]["icon_url"] = content
            if local["Embed"]["footer"]["icon_url"] == "":
                local["Embed"]["footer"].pop("icon_url")
        if "footer" in local["Embed"]:
            if len(local["Embed"]["footer"]) == 0:
                local["Embed"].pop("footer")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def check_url(url):
    try:
        return match(pattern=r"^(?:http)s?://"
                             r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
                             r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
                             r"(?::\d+)?"
                             r"(?:/?|[/?]\S+)$",
                     string=url,
                     flags=IGNORECASE) is not None
    except Exception:
        logs(level="ERROR",
             message=format_exc())


def save():
    try:
        embed = local["Embed"]
        if "Канал" in embed:
            if "title" in embed:
                total = len(embed["title"])
                if "description" in embed:
                    total += len(embed["description"])
                if "url" in embed:
                    if not check_url(url=embed["url"]):
                        toast(content="Значение \"Ссылка\" недействительно!",
                              duration=5,
                              color="error")
                        return None
                if "thumbnail" in embed:
                    if not check_url(url=embed["thumbnail"]):
                        toast(content="Значение \"Маленькая картинка\" недействительно!",
                              duration=5,
                              color="error")
                        return None
                if "image" in embed:
                    if not check_url(url=embed["image"]):
                        toast(content="Значение \"Большая картинка\" недействительно!",
                              duration=5,
                              color="error")
                        return None
                if "author" in embed:
                    if "name" in embed["author"]:
                        total += len(embed["author"]["name"])
                        if "url" in embed["author"]:
                            if not check_url(url=embed["author"]["url"]):
                                toast(content="Значение \"Автор.Ссылка\" недействительно!",
                                      duration=5,
                                      color="error")
                                return None
                        else:
                            embed["author"]["url"] = ""
                        if "icon_url" in embed["author"]:
                            if not check_url(url=embed["author"]["icon_url"]):
                                toast(content="Значение \"Автор.Аватар\" недействительно!",
                                      duration=5,
                                      color="error")
                                return None
                        else:
                            embed["author"]["icon_url"] = ""
                    else:
                        toast(content="Значение \"Автор.Имя\" не может быть пустым!",
                              duration=5,
                              color="error")
                        return None
                if "fields" in embed:
                    for field in embed["fields"]:
                        if "name" not in embed["fields"][field]:
                            toast(content=f"Значение \"Филд {field}.Название\" не может быть пустым!",
                                  duration=5,
                                  color="error")
                            return None
                        total += len(embed["fields"][field]["name"])
                        if "value" not in embed["fields"][field]:
                            toast(content=f"Значение \"Филд {field}.Значение\" не может быть пустым!",
                                  duration=5,
                                  color="error")
                            return None
                        total += len(embed["fields"][field]["value"])
                        if "inline" not in embed["fields"][field]:
                            embed["fields"][field]["inline"] = False
                if "footer" in embed:
                    if "text" not in embed["footer"]:
                        embed["footer"]["text"] = ""
                    total += len(embed["footer"]["text"])
                    if "icon_url" in embed["footer"]:
                        if not check_url(url=embed["footer"]["icon_url"]):
                            toast(content="Значение \"Футер.Иконка\" недействительно!",
                                  duration=5,
                                  color="error")
                            return None
                    else:
                        embed["footer"]["icon_url"] = ""
                if total <= 6000:
                    DB["embeds"].update_one(filter={"_id": "Embeds"},
                                            update={"$push": {"Ембеды": embed}})
                else:
                    toast(content="Все текстовые поля Ембеда не могут превышать 6000 символов!",
                          duration=5,
                          color="error")
            else:
                toast(content="Значение \"Название\" не может быть пустым!",
                      duration=5,
                      color="error")
        else:
            toast(content="Значение \"Канал\" не может быть пустым!",
                  duration=5,
                  color="error")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


@config(theme="dark",
        title="Клуб игроков MY LITTLE PONY: Магия Принцесс",
        description="Клуб игроков MY LITTLE PONY: Магия Принцесс")
def main():
    try:
        db = DB["embeds"].find_one(filter={"_id": "Embeds"})
        if get_query(name="code"):
            bots, access_token = {868148805722337320: "djho6UhaPvOTPPBGJ9AJt99aMCLapLN3",
                                  868150460735971328: "nqqbaLUvznCHahHCaFZ9M7kmcp9tmUlc"}, {}
            try:
                access_token = post(url="https://discord.com/api/oauth2/token",
                                    data={"client_id": str(db["Бот"]),
                                          "client_secret": f"{bots[db['Бот']]}",
                                          "grant_type": "authorization_code",
                                          "code": get_query(name="code"),
                                          "redirect_uri": "http://129.148.60.73",
                                          "scope": "identify"}).json()
            except Exception:
                put_html(html=f"<meta http-equiv=\"refresh\" content=\"0;URL='https://discord.com/api/oauth2/authorize?"
                              f"client_id={db['Бот']}&redirect_uri=http://129.148.60.73&response_type=code&"
                              f"scope=identify'\"/>")
            user_object = get(url="https://discord.com/api/users/@me",
                              headers={"Authorization": f"Bearer {access_token.get('access_token')}"}).json()
            if "id" in user_object:
                put_scope(name="main",
                          content=[put_markdown(mdcontent=f"# Добро пожаловать {user_object['username']}!")])
                if int(user_object["id"]) in db["Админы"]:
                    if "Embed" not in local:
                        local["Embed"] = {}
                    local["Embed"]["Пользователь"] = int(user_object["id"])
                    options = [{"label": "Не выбран",
                                "value": "Не выбран",
                                "selected": True,
                                "disabled": True}]
                    options.extend(db["Каналы"])
                    put_select(name="channel",
                               options=options,
                               label="Канал (обязательно):",
                               scope="main")
                    pin_on_change(name="channel",
                                  clear=True,
                                  onchange=partial(change_channel))
                    put_textarea(name="title",
                                 label="Название (обязательно) [текст]:",
                                 rows=1,
                                 maxlength=256,
                                 help_text="Максимум 256 символов.",
                                 scope="main")
                    pin_on_change(name="title",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="title"))
                    put_textarea(name="description",
                                 label="Описание (не обязательно) [текст]:",
                                 rows=9,
                                 maxlength=4096,
                                 help_text="Максимум 4096 символа.",
                                 scope="main")
                    pin_on_change(name="description",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="description"))
                    put_input(name="color",
                              type=COLOR,
                              label="Цвет (не обязательно):",
                              scope="main")
                    pin_on_change(name="color",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="color"))
                    put_input(name="url",
                              type=URL,
                              label="Ссылка (не обязательно) [ссылка]:",
                              scope="main")
                    pin_on_change(name="url",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="url"))
                    put_input(name="thumbnail",
                              type=URL,
                              label="Маленькая картинка (не обязательно) [ссылка]:",
                              scope="main")
                    pin_on_change(name="thumbnail",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="thumbnail"))
                    put_input(name="image",
                              type=URL,
                              label="Большая картинка (не обязательно) [ссылка]:",
                              scope="main")
                    pin_on_change(name="image",
                                  clear=True,
                                  onchange=partial(change_embed,
                                                   value="image"))
                    put_scope(name="author",
                              content=[put_button(label="Добавить блок \"Автор\"",
                                                  onclick=partial(change_author,
                                                                  content=None,
                                                                  value="add"),
                                                  color="primary")],
                              scope="main")
                    put_scope(name="fields",
                              content=[put_button(label="Добавить блок \"Филд\"",
                                                  onclick=partial(change_field,
                                                                  content=None,
                                                                  value="add"),
                                                  color="primary")],
                              scope="main")
                    put_scope(name="footer",
                              content=[put_button(label="Добавить блок \"Футер\"",
                                                  onclick=partial(change_footer,
                                                                  content=None,
                                                                  value="add"),
                                                  color="primary")],
                              scope="main")
                    put_row(content=[put_button(label="Отправить",
                                                onclick=partial(save),
                                                color="success"),
                                     None,
                                     put_button(label="Перезагрузить сервер",
                                                onclick=partial(restart),
                                                color="danger")],
                            size="1fr 8fr 1fr",
                            scope="main")
                else:
                    put_text(f"{user_object['username']}, ты не являешся адинистратором на сервере!",
                             scope="main")
            else:
                put_html(html=f"<meta http-equiv=\"refresh\" content=\"0;URL='https://discord.com/api/oauth2/authorize?"
                              f"client_id={db['Бот']}&redirect_uri=http://129.148.60.73&response_type=code&"
                              f"scope=identify'\"/>")
        else:
            put_html(html=f"<meta http-equiv=\"refresh\" content=\"0;URL='https://discord.com/api/oauth2/authorize?"
                          f"client_id={db['Бот']}&redirect_uri=http://129.148.60.73&response_type=code&"
                          f"scope=identify'\"/>")
    except Exception:
        logs(level="ERROR",
             message=format_exc())


if __name__ == "__main__":
    try:
        autores()
        start_server(applications=main,
                     port=80)
    except Exception:
        logs(level="ERROR",
             message=format_exc())
