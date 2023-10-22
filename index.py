import json
import urllib3
import os
import pandas as pd
import ydb
import datetime
from mf import *

driver_config = ydb.DriverConfig(
    endpoint=os.getenv("YDB_ENDPOINT"),
    database=os.getenv("YDB_DATABASE"),
    credentials=ydb.iam.MetadataUrlCredentials()
)

ani_types = ["Movie", "TV", "OVA", "Special", "Music", "ONA", "All"]

pref_list = ["genres", "exclude", "similarity", "strict", "totalrate", "myrate", "othersrate", "type"]

genres = [
    "action",
    "adventure",
    "comedy",
    "drama",
    "sci-fi",
    "space",
    "mystery",
    "magic",
    "police",
    "supernatural",
    "fantasy",
    "shounen",
    "sports",
    "josei",
    "romance",
    "slice of life",
    "cars",
    "seinen",
    "horror",
    "psychological",
    "thriller",
    "martial arts",
    "super power",
    "school",
    "ecchi",
    "vampire",
    "historical",
    "military",
    "dementia",
    "mecha",
    "demons",
    "samurai",
    "game",
    "shoujo",
    "harem",
    "music",
    "shoujo ai",
    "shounen ai",
    "kids",
    "hentai",
    "parody",
    "yuri",
    "yaoi"
]

rate_recom_answ = ["Dont know", "Good", "Bad"]

driver = ydb.Driver(driver_config)
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def handler(event, context):
    try:
        message = json.loads(event["body"])
        if "callback_query" in message.keys():
            reply = message["callback_query"]["data"]
            chat_id = message["callback_query"]["message"]["chat"]["id"]
            username = message["callback_query"]["message"]["chat"]["username"]
        else:
            chat_id = message["message"]["chat"]["id"]
            reply = message["message"]["text"]
            username = message["message"]["chat"]["username"]
            upsert_myusers(username, chat_id)

        if "callback_query" in message.keys():
            if reply in ani_types:
                answ = username + ", вы выбрали " + reply
                send_message(answ, chat_id)
                upsert_type(username, reply)
            elif reply in rate_recom_answ:
                rate_recom(username, reply, chat_id)

            elif reply in pref_list:
                if reply == 'genres':
                    answ = "Жанры – какие жанры вы хотите видеть в рекомендованных аниме. Чтобы установить предпочтение по жанрам, нужно набрать команду /set genres и после пробела через запятую и пробел указать предпочитаемые жанры. Например: /set genres action, comedy ."
                    send_message(answ, chat_id)
                elif reply == 'exclude':
                    answ = "Исключаемые жанры – жанры, которые вы хотите исключить из рекомендаций. Чтобы исключить какие-либо жанры, нужно набрать /set exclude и после пробела через запятую и пробел указать ислючаемые жанры. Например: /set exclude action, comedy ."
                    send_message(answ, chat_id)
                elif reply == 'similarity':
                    answ = "Похожесть – параметр, имеющий значение True или False. Если вы установите этот параметр на True, то рекомендация будет строиться с помощью оценок пользователей, которые оценили те же аниме, что и вы. Если этот параметр установлен на False, то при расчете рекомендации будут просто использованы аниме, которые вы не смотрели. Чтобы установить параметр, необходимо набрать команду /set similarity и после пробела True или False. Например: /set similarity True ."
                    send_message(answ, chat_id)
                elif reply == 'strict':
                    answ = "Строгость - параметр, имеющий значение True или False. Если вы установите этот параметр на True, то при составлении рекомендации в результате будут только аниме, которые содержат все перечисленные вами предпочитаемые жанры. Если этот параметр установлен на False, то в рекомендациях будут все аниме, в которых есть хоть один из перечисленных вами предпочитаемых жанров. Чтобы установить параметр, необходимо набрать команду /set strict и после пробела True или False. Например: /set strict True ."
                    send_message(answ, chat_id)
                elif reply == 'totalrate':
                    answ = "Общий рейтинг – средняя оценка аниме за всю историю оценивания. Вы можете установить минимальный общий рейтинг для рекомендуемых вам аниме. Чтобы установить предпочтение общего рейтинга, наберите команду /set totalrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set totalrate 8 ."
                    send_message(answ, chat_id)
                elif reply == 'myrate':
                    answ = "Собственный рейтинг – оценка, которую поставили вы. Этот параметр используется для того, чтобы не использовать в алгоритме подбора рекомендаций аниме, которые вы оценили ниже указанного значения. Эти аниме исключаются из списка оцененных, будто вы их вообще никогда не оценивали. Чтобы установить предпочтение по собственному рейтингу, наберите команду /set myrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set myrate 8 ."
                    send_message(answ, chat_id)
                elif reply == 'othersrate':
                    answ = "Чужой рейтинг – оценка, которую поставил другой пользователь. Этот параметр используется для того, чтобы исключить из алгоритма подбора рекомендации аниме, которые все из отдельно рассматриваемых пользователей оценили ниже указанного значения. Чтобы установить предпочтение по чужому рейтингу, наберите команду /set othersrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set othersrate 8 ."
                    send_message(answ, chat_id)
                elif reply == 'type':
                    answ = "Тип аниме – какой тип аниме вы хотите получить в рекомендациях. Чтобы установить тип, наберите /set type и в появившемся меню выберите нужный вариант."
                    send_message(answ, chat_id)

            else:
                rate_anime(message, username, reply, chat_id)
                send_anime_for_rate(chat_id, username)
                send_message(
                    "Если хотите закончить оценивание, напишите в чат /stoprate .", chat_id
                )
        elif reply == '/infopref':
            send_question_infopref(chat_id)
        elif reply == "/set type":
            send_question_type(chat_id)
        elif reply == "/stoprate":
            send_message("Чем займемся дальше?", chat_id)
        elif reply.startswith("/rate"):
            if len(reply.split(" ")) == 2:
                if reply == "/rate count":
                    counts = rate_count("animerate", username)[0].rows[0]["r_count"]
                    send_message(counts, chat_id)
                else:
                    anime_id = reply.split(" ")[1]
                    send_message("Если аниме с таким ID нет, то по ссылке будет страница с ошибкой.", chat_id)
                    rate_specific(chat_id, anime_id)
            elif reply == "/rate":
                send_anime_for_rate(chat_id, username)
            else:
                send_message(
                    "Что-то пошло не так. Для оценки рандомных аниме напишите просто /rate, для оценки конкретного аниме напишите /rate id, где id - это идентификатор аниме",
                    chat_id
                )

        elif reply == "/quote":
            anime, character, quote = get_quote()
            answ = f"В аниме {anime} персонажем {character} было сказано: \n{quote}"
            send_message(answ, chat_id)

        elif reply.startswith("/set similarity"):
            if len(reply.split(" ")) == 3:
                similarity = reply.split(" ")[2]
                if similarity in ["true", "TRUE", "True", "false", "FALSE", "False"]:
                    upsert_similarity(username, similarity)
                    send_message(f"Вы установили похожесть на {similarity}", chat_id)

                else:
                    send_message(
                        "Что-то пошло не так! Вам нужно написать команду /set similarity и через один пробел True или False, чтобы установить предпочтение похожести для фильтра",
                        chat_id
                    )

        elif reply.startswith("/set strict"):
            if len(reply.split(" ")) == 3:
                strict = reply.split(" ")[2]
                if strict in ["true", "TRUE", "True", "false", "FALSE", "False"]:
                    upsert_strict(username, strict)
                    send_message(f"Вы установили строгость на {strict}", chat_id)

                else:
                    send_message(
                        "Что-то пошло не так! Вам нужно написать команду /set strict и через один пробел True или False, чтобы установить предпочтение строгости для фильтра",
                        chat_id
                    )

        elif reply.startswith("/set myrate"):
            if len(reply.split(" ")) == 3:
                try:
                    myrate = int(reply.split(" ")[2])
                    if 1 <= myrate <= 10:
                        upsert_myrate(username, myrate)
                        send_message(
                            f"Вы установили собственный рейтинг на {myrate}", chat_id
                        )

                    else:
                        send_message(
                            "Что-то пошло не так! Вам нужно написать команду /set myrate и через один пробел число от 1 до 10, чтобы установить предпочтение вашей оценки для фильтра",
                            chat_id
                        )

                except:
                    send_message(
                        "Что-то пошло не так! Вам нужно написать команду /set myrate и через один пробел число от 1 до 10, чтобы установить предпочтение вашей оценки для фильтра",
                        chat_id
                    )
            else:
                send_message(
                    "Что-то пошло не так! Вам нужно написать команду /set myrate и через один пробел число от 1 до 10, чтобы установить предпочтение вашей оценки для фильтра",
                    chat_id
                )

        elif reply.startswith("/set othersrate"):
            if len(reply.split(" ")) == 3:
                try:
                    othersrate = int(reply.split(" ")[2])
                    if 1 <= othersrate <= 10:
                        upsert_othersrate(username, othersrate)
                        send_message(
                            f"Вы установили собственный рейтинг на {othersrate}", chat_id
                        )

                    else:
                        send_message(
                            "Что-то пошло не так! Вам нужно написать команду /set othersrate и через один пробел число от 1 до 10, чтобы установить предпочтение оценки других пользователей для фильтра",
                            chat_id
                        )

                except:
                    send_message(
                        "Что-то пошло не так! Вам нужно написать команду /set othersrate и через один пробел число от 1 до 10, чтобы установить предпочтение оценки других пользователей для фильтра",
                        chat_id
                    )
            else:
                send_message(
                    "Что-то пошло не так! Вам нужно написать команду /set othersrate и через один пробел число от 1 до 10, чтобы установить предпочтение оценки других пользователей для фильтра",
                    chat_id
                )

        elif reply.startswith("/set totalrate"):
            if len(reply.split(" ")) == 3:
                try:
                    totalrate = int(reply.split(" ")[2])
                    if 1 <= totalrate <= 10:
                        upsert_totalrate(username, totalrate)
                        send_message(
                            f"Вы установили собственный рейтинг на {totalrate}", chat_id
                        )

                    else:
                        send_message(
                            "Что-то пошло не так! Вам нужно написать команду /set totalrate и через один пробел число от 1 до 10, чтобы установить предпочтение общей оценки для фильтра",
                            chat_id
                        )

                except:
                    send_message(
                        "Что-то пошло не так! Вам нужно написать команду /set totalrate и через один пробел число от 1 до 10, чтобы установить предпочтение общей оценки для фильтра",
                        chat_id
                    )
            else:
                send_message(
                    "Что-то пошло не так! Вам нужно написать команду /set totalrate и через один пробел число от 1 до 10, чтобы установить предпочтение общей оценки для фильтра",
                    chat_id
                )

        elif reply == "/get genres":
            send_message("Вот такие жанры у нас есть:", chat_id)
            send_message(genres, chat_id)

        elif reply.startswith("/set genres"):
            genres_list = set_genres(reply)
            upsert_genres(username, genres_list)
            send_message(
                "Вы установили предпочтение таких жанров: " + str(genres_list), chat_id
            )

        elif reply.startswith("/set exclude"):
            genres_list = set_exclude(reply)
            upsert_exclude(username, genres_list)
            send_message(
                "Вы установили исключение таких жанров: " + str(genres_list), chat_id
            )

        elif reply == "/get preferences":
            prefs = get_prefs(username)
            if prefs.empty:
                answ = "У вас еще нет предпочтений."
                send_message(answ, chat_id)
                print({answ})
            else:
                answ = report_prefs(prefs)
                send_message(answ, chat_id)
                print({answ})

        elif reply == "/recommend":
            watched_ani = watched(username)
            user_prefs = get_prefs(username)

            if watched_ani.empty:
                if user_prefs.empty:
                    send_message(
                        "У вас отсутствуют оценки аниме и предпочтения. Рекомендация будет построена практически рандомно.",
                        chat_id
                    )
                    recom_data = smart_filter(username=username)
                    if recom_data.empty:
                        answ = "Не могу подобрать вам рекомендацию. Попробуйте поменять предпочтения."
                        send_message(answ, chat_id)
                        print({answ})
                    else:
                        recom_raw = recom_data.sample(1)
                        name = recom_raw.iloc[0]["name"]
                        ani_type = recom_raw.iloc[0]["type"]
                        episodes = recom_raw.iloc[0]["episodes"]
                        rating_total = recom_raw.iloc[0]["rating_total"]
                        genre = recom_raw.iloc[0]["genre"]
                        ani_id = recom_raw.iloc[0]["anime_id"]
                        answ = f"""Дорогой пользователь! Вот моя рекомендация: \n
Название аниме: {name}\n
Тип: {ani_type}\n
Количество эпизодов: {episodes}\n
Средний рейтинг: {rating_total}\n
Жанр: {genre}\n
Ссылочка: https://myanimelist.net/anime/{ani_id}
"""
                        send_message(answ, chat_id)
                        send_question_recomrate(chat_id)
                        print({answ})
                else:

                    send_message(
                        "У вас отсутствуют оценки аниме. Рекомендация будет построена только с учетом предпочтений.",
                        chat_id
                    )
                    recom_data = smart_filter(username=username)
                    if recom_data.empty:
                        answ = "Не могу подобрать вам рекомендацию. Попробуйте поменять предпочтения."
                        send_message(answ, chat_id)
                        print({answ})
                    else:
                        recom_raw = recom_data.sample(1)
                        name = recom_raw.iloc[0]["name"]
                        ani_type = recom_raw.iloc[0]["type"]
                        episodes = recom_raw.iloc[0]["episodes"]
                        rating_total = recom_raw.iloc[0]["rating_total"]
                        genre = recom_raw.iloc[0]["genre"]
                        ani_id = recom_raw.iloc[0]["anime_id"]
                        answ = f"""Дорогой пользователь! Вот моя рекомендация: \n
Название аниме: {name}\n
Тип: {ani_type}\n
Количество эпизодов: {episodes}\n
Средний рейтинг: {rating_total}\n
Жанр: {genre}\n
Ссылочка: https://myanimelist.net/anime/{ani_id}
"""

                        send_message(answ, chat_id)
                        send_question_recomrate(chat_id)
                        print({answ})
            else:
                if user_prefs.empty:
                    send_message(
                        "У вас отсутствуют предпочтения. Рекомендация будет построена с учетом ваших оценок аниме.",
                        chat_id
                    )
                    ani_type = "None"
                    similarity = "None"
                    rating_others = "nan"
                    rating_self = "nan"
                    rating_total = "nan"
                    exclude_genre = "None"
                    include_genre = "None"
                    strict = "None"
                    recom_data = smart_filter(username=username)
                    if recom_data.empty:
                        answ = "Не могу подобрать вам рекомендацию. Попробуйте поменять предпочтения."
                        send_message(answ, chat_id)
                        print({answ})
                    else:
                        recom_raw = recom_data.sample(1)
                        name = recom_raw.iloc[0]["name"]
                        ani_type = recom_raw.iloc[0]["type"]
                        episodes = recom_raw.iloc[0]["episodes"]
                        rating_total = recom_raw.iloc[0]["rating_total"]
                        genre = recom_raw.iloc[0]["genre"]
                        ani_id = recom_raw.iloc[0]["anime_id"]
                        answ = f"""Дорогой пользователь! Вот моя рекомендация: \n
Название аниме: {name}\n
Тип: {ani_type}\n
Количество эпизодов: {episodes}\n
Средний рейтинг: {rating_total}\n
Жанр: {genre}\n
Ссылочка: https://myanimelist.net/anime/{ani_id}
"""

                        send_message(answ, chat_id)
                        send_question_recomrate(chat_id)
                        print({answ})
                else:
                    send_message(
                        "Рекомендация будет построена с учетом предпочтений и ваших оценок аниме.",
                        chat_id
                    )

                    recom_data = smart_filter(username=username)
                    if recom_data.empty:
                        answ = "Не могу подобрать вам рекомендацию. Попробуйте поменять предпочтения."
                        send_message(answ, chat_id)
                        print({answ})
                    else:
                        recom_raw = recom_data.sample(1)
                        name = recom_raw.iloc[0]["name"]
                        ani_type = recom_raw.iloc[0]["type"]
                        episodes = recom_raw.iloc[0]["episodes"]
                        rating_total = recom_raw.iloc[0]["rating_total"]
                        genre = recom_raw.iloc[0]["genre"]
                        ani_id = recom_raw.iloc[0]["anime_id"]
                        amount = len(recom_data)
                        answ = f"""Дорогой пользователь! Вот моя рекомендация из {amount} подходящих аниме: \n
Название аниме: {name}\n
Тип: {ani_type}\n
Количество эпизодов: {episodes}\n
Средний рейтинг: {rating_total}\n
Жанр: {genre}\n
Ссылочка: https://myanimelist.net/anime/{ani_id}
"""

                    send_message(answ, chat_id)
                    send_question_recomrate(chat_id)
                    print({answ})

        elif reply == "/commands":
            answ = """/get preferences – Получить сохраненные предпочтения \n
/get genres – Получить список всех жанров аниме в базе \n
/recommend – Получить рекомендацию аниме \n
\n
/infopref – Получить информацию и инструкции к предпочтениям \n
/set exclude – Установить предпочтение исключаемых жанров \n
/set genres - Установить предпочтение жанров \n
/set totalrate - Установить предпочтение общего рейтинга \n
/set othersrate - Установить предпочтение рейтинга других пользователей \n
/set myrate - Установить предпочтение собственного рейтинга \n
/set strict - Установить предпочтение строгости фильтрации \n
/set similarity - Установить предпочтение похожести \n
/set type - Установить предпочтение типа аниме \n
/clean genres - Очистить предпочтение жанров \n
/clean exclude - Очистить предпочтение исключаемых жанров \n
/clean totalrate - Очистить предпочтение общего рейтинга \n
/clean othersrate - Очистить предпочтение рейтинга других пользователей \n
/clean myrate - Очистить предпочтение собственного рейтинга \n
/clean strict - Очистить предпочтение строгости фильтрации \n
/clean similarity - Очистить предпочтение похожести \n
/clean type - Очистить предпочтение типа аниме \n
\n
/rate count – Получить количество оцененных аниме \n
/quote – Получить случайную цитату (задействовано внешнее API) \n
/rate – Оценить аниме \n
/rate {id} – Оценить конкретное аниме. Для этого необходимо знать его id на myanimelist.net . id аниме пишется в ссылке после 'anime/'. Например: ссылка на аниме - https://myanimelist.net/anime/666 , id этого аниме - 666 \n
/stoprate – Прекратить оценивание аниме \n
"""
            send_message(answ, chat_id)
        elif reply.startswith("/clean"):
            if len(reply.split(" ")) == 2:
                if reply.split(" ")[1] in ["genre", "genres"]:
                    pref = "genre"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение жанра"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] == "type":
                    pref = "type"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение типа аниме"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] in ["except", "exclude"]:
                    pref = "exclude"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение исключаемых жанров"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] == "myrate":
                    pref = "rating_self"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение собственного рейтинга"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] == "totalrate":
                    pref = "rating_total"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение обшего рейтинга"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] == "othersrate":
                    pref = "rating_others"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение чужого рейтинга"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] == "strict":
                    pref = "strict"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение строгости"
                    send_message(answ, chat_id)
                elif reply.split(" ")[1] in ["similarity", "similar"]:
                    pref = "similarity"
                    clean_pref(username, pref)
                    answ = "Вы очистили предпочтение похожести"
                    send_message(answ, chat_id)
            else:
                send_message("Что-то не так! Проверьте свою команду.", chat_id)

        elif reply == '/start':
            answ = f"""Привет! Я – бот-советчик для рекомендации аниме. \n
С моей помощью ты можешь оценить просмотренные и рандомные аниме, установить свои предпочтения (а также посмотреть и поменять их), и получить рекомендацию аниме на основе того, что уже было просмотрено и оценено, и твоих сохраненных предпочтений. А еще я могу скинуть тебе рандомную аниме-цитатку! И если меня не остановить, я буду присылать тебе цитатку дня каждый день!\n
Весь список команд можно узнать, набрав /commands . """
            send_message(answ, chat_id)
            print({answ})
        else:
            anime, character, quote = get_quote()
            answ = f"В аниме {anime} персонажем {character} было сказано: \n{quote}"
            send_message(answ, chat_id)
            print({answ})
    except:
        message = json.loads(json.dumps(event))
        try:
            text = message['messages'][0]['details']['payload']
            myusers = get_users()
            for user in range(len(myusers)):
                try:
                    chat_id = int(myusers.chat_id[user])
                    anime, character, quote = get_quote()
                    answ = text + "\n" + f"В аниме {anime} персонажем {character} было сказано: \n{quote}"
                    send_message(answ, chat_id)
                except:
                    pass
        except:
            pass

    print(json.dumps(event))
    return {"statusCode": 200}
