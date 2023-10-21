import urllib3
import os
import pandas as pd
import json
import datetime
import ydb
import string
import re
import requests

TG_TOKEN = os.environ.get("TG_TOKEN")
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"
http = urllib3.PoolManager()

driver_config = ydb.DriverConfig(
    endpoint=os.getenv("YDB_ENDPOINT"),
    database=os.getenv("YDB_DATABASE"),
    credentials=ydb.iam.MetadataUrlCredentials()
)

driver = ydb.Driver(driver_config)
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def get_quote():
    resp = requests.get("https://animechan.xyz/api/random")
    anime = resp.json()["anime"]
    character = resp.json()["character"]
    quote = resp.json()["quote"]
    return anime, character, quote


typechoiceText = "Выберите тип аниме (вы можете сменить его позже, но до тех пор вам будут показывать только аниме этого типа)."

recomRateText = "Как вам моя рекомендация?"

preftext = "О каком из параметров предпочтения вы хотите узнать?"

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


def get_users():
  text = f"SELECT `chat_id` FROM `myusers`;"
  user_ids = pool.retry_operation_sync(lambda s: s.transaction().execute(
    text,
    commit_tx=True,
    settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
  ))
  user_data = pd.DataFrame.from_records(user_ids[0].rows)
  return user_data

def set_genres(reply):
    reply_cut = reply[reply.find("/set genres ") + len("/set genres ") :]
    reply_lower = reply_cut.lower()
    # reply_punc = reply_lower.translate(str.maketrans('', '', string.punctuation))
    reply_space = re.sub(" +", " ", reply_lower)
    reply_list = list(reply_space.split(", "))
    genres_final = []
    for i in range(len(reply_list)):
        reply_list[i] = reply_list[i].strip()
        if reply_list[i] in genres:
            genres_final.append(reply_list[i])
        else:
            pass
    genres_final = ", ".join(genres_final)
    return genres_final


def set_exclude(reply):
    reply_cut = reply[reply.find("/set exclude") + len("/set exclude") :]
    reply_lower = reply_cut.lower()
    # reply_punc = reply_lower.translate(str.maketrans('', '', string.punctuation))
    reply_space = re.sub(" +", " ", reply_lower)
    reply_list = list(reply_space.split(", "))
    genres_final = []
    for i in range(len(reply_list)):
        reply_list[i] = reply_list[i].strip()
        if reply_list[i] in genres:
            genres_final.append(reply_list[i])
        else:
            pass
    genres_final = ", ".join(genres_final)
    return genres_final


def send_message(text, chat_id):
    final_text = text
    url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
    http.request("GET", url)


def type_choice():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Фильм", "callback_data": "Movie"},
                    {"text": "Сериал", "callback_data": "TV"},
                ],
                [
                    {"text": "OVA", "callback_data": "OVA"},
                    {"text": "Спец. выпуск", "callback_data": "Special"},
                ],
                [
                    {"text": "Музыкальный", "callback_data": "Music"},
                    {"text": "ONA", "callback_data": "ONA"},
                ],
                [{"text": "Любой", "callback_data": "All"}]
            ]
        }
    )


def pref_choice():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Жанры", "callback_data": "genres"},
                    {"text": "Исключаемые жанры", "callback_data": "exclude"}
                ],
                [
                    {"text": "Похожесть", "callback_data": "similarity"},
                    {"text": "Строгость", "callback_data": "strict"}
                ],
                [
                    {"text": "Общий рейтинг", "callback_data": "totalrate"},
                    {"text": "Собственный рейтинг", "callback_data": "myrate"}
                ],
                [
                    {"text": "Чужой рейтинг", "callback_data": "othersrate"},
                    {"text": "Тип", "callback_data": "type"}]
            ]
        }
    )

def rate_recom_chioce():
    return json.dumps(
        {
            "inline_keyboard": [
                [{"text": "Нравится", "callback_data": "Good"}],
                [{"text": "Не нравится", "callback_data": "Bad"}],
                [{"text": "Не знаю", "callback_data": "Don't know"}]
            ]
        }
    )

def send_question_infopref(chat_id):
    # Create data dict
    data = {
        "text": (None, preftext),
        "chat_id": (None, chat_id),
        "parse_mode": (None, "Markdown"),
        "reply_markup": (None, pref_choice())
    }
    url = URL + "sendMessage"
    http.request("POST", url, fields=data)

def send_question_recomrate(chat_id):
    # Create data dict
    data = {
        "text": (None, recomRateText),
        "chat_id": (None, chat_id),
        "parse_mode": (None, "Markdown"),
        "reply_markup": (None, rate_recom_chioce())
    }
    url = URL + "sendMessage"
    http.request("POST", url, fields=data)


def rate_choice():
    return json.dumps(
        {
            "inline_keyboard": [
                [{"text": "Не смотрел(-а)", "callback_data": "0"}],
                [
                    {"text": "1", "callback_data": "1"},
                    {"text": "2", "callback_data": "2"},
                    {"text": "3", "callback_data": "3"},
                    {"text": "4", "callback_data": "4"},
                    {"text": "5", "callback_data": "5"},
                ],
                [
                    {"text": "6", "callback_data": "6"},
                    {"text": "7", "callback_data": "7"},
                    {"text": "8", "callback_data": "8"},
                    {"text": "9", "callback_data": "9"},
                    {"text": "10", "callback_data": "10"},
                ]
            ]
        }
    )


def ratechoiceText(anime_id):
    rateText = f"Вы смотрели это аниме? Как вам? Ссылочка: https://myanimelist.net/anime/{anime_id}"
    return rateText


def send_question_type(chat_id):
    # Create data dict
    data = {
        "text": (None, typechoiceText),
        "chat_id": (None, chat_id),
        "parse_mode": (None, "Markdown"),
        "reply_markup": (None, type_choice())
    }
    url = URL + "sendMessage"
    http.request("POST", url, fields=data)


def send_question_rate(anime_id, chat_id):
    # Create data dict
    data = {
        "text": (None, ratechoiceText(anime_id)),
        "chat_id": (None, chat_id),
        "parse_mode": (None, "Markdown"),
        "reply_markup": (None, rate_choice())
    }
    url = URL + "sendMessage"
    http.request("POST", url, fields=data)


def rate_recom(username, reply, chat_id):
    count_rates = rate_count("animerate", username)[0].rows[0]["r_count"]
    answ = "Спасибо за отзыв!"
    moment_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    send_message(answ, chat_id)
    upsert_rate_recom(username, moment_now, count_rates, reply)


def upsert_rate_recom(username, moment_now, count_rates, reply):
    text = f"UPSERT INTO recomrate (`id`, `rate`, `rate_count`, `time_rated`, `username`) VALUES ( RandomNumber(1), '{reply}', '{count_rates}', '{moment_now}', '{username}') ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

def upsert_myusers(username, chat_id):
    text = f"UPSERT INTO myusers (`username`, `chat_id`) VALUES ( '{username}', '{chat_id}') ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def rate_anime(message, username, reply, chat_id):
    anime_id = message["callback_query"]["message"]["text"].split("anime/", 1)[1]
    answ = username + ", вы оценили " + anime_id + " на " + reply
    row_id = username + "_" + anime_id
    moment_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    send_message(answ, chat_id)
    upsert_rating("animerate", username, anime_id, row_id, moment_now, reply)


def rate_specific(chat_id, anime_id):
    send_question_rate(anime_id, chat_id)


def send_anime_for_rate(chat_id, username):
    top_anime = pd.read_csv(
        f"https://storage.yandexcloud.net/module-task/anime_top.csv",
        encoding="unicode_escape"
    )
    watched_ani = watched(username)
    non_watched = top_anime[
        ~top_anime["anime_id"].isin(list(watched_ani["animeid"].astype(int)))
    ]
    random_anime = non_watched.sample(1)
    anime_name = random_anime.name.iloc[0]
    anime_id = random_anime.anime_id.iloc[0]
    send_message(anime_name, chat_id)
    send_question_rate(anime_id, chat_id)


def rate_specific(chat_id, anime_id):
    send_question_rate(anime_id, chat_id)


def upsert_type(user, an_type):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `type`) VALUES ( '{user}', '{an_type}') ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_genres(user, genres):
    # create the transaction and execute query.
    text = f'UPSERT INTO preferences (`user`, `genre`) VALUES ( "{user}", "{genres}") ;'
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_exclude(user, genres):
    # create the transaction and execute query.
    text = f'UPSERT INTO preferences (`user`, `exclude`) VALUES ( "{user}", "{genres}") ;'
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_similarity(user, similarity):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `similarity`) VALUES ( '{user}', {similarity}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_strict(user, strict):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `strict`) VALUES ( '{user}', {strict}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_myrate(user, myrate):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `rating_self`) VALUES ( '{user}', {myrate}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

def upsert_othersrate(user, othersrate):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `rating_others`) VALUES ( '{user}', {othersrate}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_totalrate(user, totalrate):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `rating_total`) VALUES ( '{user}', {totalrate}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_rating_total(user, rating_total):
    # create the transaction and execute query.
    text = f"UPSERT INTO preferences (`user`, `rating_total`) VALUES ( '{user}', {rating_total}) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def upsert_rating(tablename, user, anime_id, row_id, moment_now, rate_value):
    # create the transaction and execute query.
    text = f"UPSERT INTO {tablename} (`id`, `animeid`, `rating`, `updated`, `username`) VALUES ( '{row_id}', '{anime_id}',  {rate_value}, '{moment_now}', '{user}') ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def rate_count(tablename, user):
    text = f"SELECT COUNT(*) as r_count FROM {tablename} WHERE username == '{user}';"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def watched(user):
    text = f"SELECT `animeid`, `rating`, `username` FROM animerate WHERE `username` == '{user}' AND `rating` != 0;"
    user_data_ydb = pool.retry_operation_sync(
        lambda s: s.transaction().execute(
            text,
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )
    )
    user_data = pd.DataFrame.from_records(user_data_ydb[0].rows)
    return user_data


def get_prefs(user):
    text = f"SELECT * FROM preferences WHERE `user` == '{user}';"
    user_data_ydb = pool.retry_operation_sync(
        lambda s: s.transaction().execute(
            text,
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )
    )
    user_prefs = pd.DataFrame.from_records(user_data_ydb[0].rows)
    return user_prefs


def smart_filter(username):
    ratingdata = pd.read_csv(
        f"https://storage.yandexcloud.net/module-task/rating_only.csv",
        encoding="unicode_escape"
    )
    all_data = pd.read_csv(
        f"https://storage.yandexcloud.net/module-task/anime_only.csv",
        encoding="unicode_escape"
    )
    userdata = watched(username)

    user_prefs = get_prefs(username)

    if user_prefs.empty:
        anime_type = "None"
        similar = "None"
        rating_others = "nan"
        rating_self = "nan"
        rating_total = "nan"
        exclude = "None"
        genres = "None"
        strict = "None"
    else:
        anime_type = user_prefs["type"][0]
        similar = user_prefs["similarity"][0]
        rating_others = user_prefs["rating_others"][0]
        rating_self = user_prefs["rating_self"][0]
        rating_total = user_prefs["rating_total"][0]
        exclude = user_prefs["exclude"][0]
        genres = user_prefs["genre"][0]
        strict = user_prefs["strict"][0]

    if str(anime_type) in ["nan", "None", 'All']:
        anime_type = list(all_data["type"].unique())
    else:
        anime_type = [anime_type]

    if str(similar) in ["nan", "None"]:
        similar = False
    else:
        similar = similar

    if str(strict) in ["nan", "None"]:
        strict = False
    else:
        strict = strict

    if str(genres) in ["nan", "None"]:
        genres = []
    else:
        genres = genres.split(", ")

    if str(exclude) in ["nan", "None"]:
        exclude = []
    else:
        exclude = exclude.split(", ")

    if str(rating_others) in ["nan", "None"]:
        rating_others = 1
    else:
        rating_others = rating_others

    if str(rating_self) in ["nan", "None"]:
        rating_self = 1
    else:
        rating_self = rating_self

    if str(rating_total) in ["nan", "None"]:
        rating_total = 1
    else:
        rating_total = rating_total

    if userdata.empty:
        not_watched = ratingdata
    else:
        # пользователь поставил оценку выше rating_self
        userdata_rating = userdata.loc[userdata.rating >= rating_self]

        # ТАБЛИЦА С ОЦЕНКАМИ ПОЛЬЗОВАТЕЛЯ
        # забираем названия просмотренных текущим пользователем аниме
        watched_list = userdata["animeid"].astype(int)
        watched_rating = userdata_rating["animeid"].astype(int)

        # ТАБЛИЦА С ОЦЕНКАМИ ДРУГИХ
        # исключаем текущего пользователя из наших данных
        other_users = ratingdata.loc[ratingdata.user_id != username]

        # поиск по похожим
        if similar == True:
            # ищем пользователей, которые смотрели просмотренное текущим пользователем
            similar_users = other_users.loc[
                other_users["anime_id"].isin(watched_rating)
            ]
            # сохраняем id этих пользователей
            similar_users_id = similar_users["user_id"].unique()
            # оставляем только записи о том, что смотрели похожие пользователи
            similar_data = other_users.loc[
                other_users["user_id"].isin(similar_users_id)
            ]
            # исключаем просмотренное текущим пользователем
            not_watched = similar_data.loc[~similar_data["anime_id"].isin(watched_list)]

        # поиск по всем
        else:
            # исключаем просмотренное текущим пользователем
            not_watched = other_users.loc[~other_users["anime_id"].isin(watched_list)]

    not_watched = not_watched.loc[not_watched.rating_user > rating_others]

    # оставляем только аниме с средним рейтингом выше указанного пользователем

    recom_id = list(not_watched["anime_id"].unique())

    all_data_cut = all_data.loc[all_data["anime_id"].isin(recom_id)]

    all_data_cut = all_data_cut.loc[all_data_cut.rating_total > rating_total]

    if len(genres) > 0:
        # строгий поиск
        if strict == True:
            recom = all_data_cut
            # отфильтровываем то, что не просмотрено, чтобы оставить только аниме со всеми перечисленными жанрами
            for genre in genres:
                recom = recom[recom[genre] == 1]
        # не строгий поиск
        else:
            recom = pd.DataFrame()
            # добавляем в итоговую выдачу все аниме, имеющие хоть один жанр из списка желаемых
            for genre in genres:
                temp = all_data_cut[all_data_cut[genre] == 1]
                recom = pd.concat([recom, temp])
    else:

        recom = all_data_cut

    # исключаем жанры, которые пользователь не хочет видеть
    if len(exclude) > 0:
        for excl in exclude:
            recom = recom[recom[excl] == 0]
            recom3 = recom[recom[excl] == 0]
    else:
        recom = recom

    recom = recom.drop_duplicates()

    names_genres = recom.columns[6:]
    # создаем колонку с жанрами
    recom["genre"] = ""

    # для каждого аниме в итоговой выдаче наполняем колонку жанров перечислением всех жанров одной строкой через точку
    # так таблица станет более читабельной
    for i in recom.index:
        for j in names_genres:
            if recom.at[i, j] == 1:
                recom.at[i, "genre"] += j + ". "
            else:
                recom.at[i, "genre"] += ""

    # удаляем старые колонки с жанрами
    recom = recom.drop(names_genres, axis=1)

    recom = recom.loc[recom["type"].isin(anime_type)]
    recom = recom.drop(["Unnamed: 0"], axis=1)

    return recom


def report_prefs(prefs_data):
    ani_type = str(prefs_data["type"][0])
    similarity = str(prefs_data["similarity"][0])
    rating_others = str(prefs_data["rating_others"][0])
    rating_self = str(prefs_data["rating_self"][0])
    rating_total = str(prefs_data["rating_total"][0])
    exclude_genre = str(prefs_data["exclude"][0])
    include_genre = str(prefs_data["genre"][0])
    strict = str(prefs_data["strict"][0])

    answ = f"Ваши предпочтения: \nТип аниме: {ani_type} \nСтрогость: {strict} \nПохожесть: {similarity} \nИсключить жанры: {exclude_genre} \nВключить жанры: {include_genre} \nРейтинг (мой): {rating_self} \nРейтинг (чужой): {rating_others} \nРейтинг (общий): {rating_total} "
    return answ


def clean_pref(user, pref):
    text = f"UPSERT INTO preferences (`user`, {pref}) VALUES ( '{user}', null) ;"
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        text,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))
