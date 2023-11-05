# ChatBot AniRec (бот для модульного задания по курсу Системный анализ и проектирование сложных систем)


А вот и сам бот: https://t.me/module_task_bot


  ### Какой вопрос решает бот:

  Какое аниме мне (пользователю) посмотреть?

  ### Возможная исследовательская гипотеза на основе полученных от бота данных:

  Чем больше аниме оценил пользователь, тем более вероятно, что рекомендация бота его удовлетворит.

  ### Сбор предпочтений:

  В боте реализованы несколько вариантов сбора предпочтений в зависимости от конкретного предпочтения.

  **Ниже приведен список предпочтений и способы получения данных:**

  * Оценка просмотренных и рандомных аниме. Это ключевой элемент в дальнейшем построении рекомендации. Для оценки рандомного аниме можно ввести команду /rate. Будет предложено рандомное аниме из базы базы данных, которое можно оценить с помощью клавиатуры в интерфейсе. Для оценки конкретного аниме нужно ввести команду /rate и через пробел написать id этого аниме согласно базе данных сайта myanimelist.net . id аниме пишется в ссылке после 'anime/'. Например: ссылка на аниме - https://myanimelist.net/anime/666 , id этого аниме - 666. В результате вызова обеих команд запускается алгоритм повторения отправки рандомного аниме на оценку - пользователю будет предлагаться оценивать аниме до того, как он не введет другую команду (либо команду остановки).

  * Жанры – какие жанры вы хотите видеть в рекомендованных аниме. Чтобы установить предпочтение по жанрам, нужно набрать команду /set genres и после пробела через запятую и пробел указать предпочитаемые жанры. Например: /set genres action, comedy .

  * Тип аниме – какой тип аниме вы хотите получить в рекомендациях. Чтобы установить тип, наберите /set type и в появившемся меню выберите нужный вариант.

  * Исключаемые жанры – жанры, которые вы хотите исключить из рекомендаций. Чтобы исключить какие-либо жанры, нужно набрать /set exclude и после пробела через запятую и пробел указать ислючаемые жанры. Например: /set exclude action, comedy .

  * Общий рейтинг – средняя оценка аниме за всю историю оценивания. Вы можете установить минимальный общий рейтинг для рекомендуемых вам аниме. Чтобы установить предпочтение общего рейтинга, наберите команду /set totalrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set totalrate 8 .

  * Чужой рейтинг – оценка, которую поставил другой пользователь. Этот параметр используется для того, чтобы исключить из алгоритма подбора рекомендации аниме, которые все из отдельно рассматриваемых пользователей оценили ниже указанного значения. Чтобы установить предпочтение по чужому рейтингу, наберите команду /set othersrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set othersrate 8 .

  * Собственный рейтинг – оценка, которую поставили вы. Этот параметр используется для того, чтобы не использовать в алгоритме подбора рекомендаций аниме, которые вы оценили ниже указанного значения. Эти аниме исключаются из списка оцененных, будто вы их вообще никогда не оценивали. Чтобы установить предпочтение по собственному рейтингу, наберите команду /set myrate и после пробела укажите целым числом от 1 до 9 желаемое значение. Например: /set myrate 8 .

  * Похожесть – параметр, имеющий значение True или False. Если вы установите этот параметр на True, то рекомендация будет строиться с помощью оценок пользователей, которые оценили те же аниме, что и вы. Если этот параметр установлен на False, то при расчете рекомендации будут просто использованы аниме, которые вы не смотрели. Чтобы установить параметр, необходимо набрать команду /set similarity и после пробела True или False. Например: /set similarity True .

  * Строгость - параметр, имеющий значение True или False. Если вы установите этот параметр на True, то при составлении рекомендации в результате будут только аниме, которые содержат все перечисленные вами предпочитаемые жанры. Если этот параметр установлен на False, то в рекомендациях будут все аниме, в которых есть хоть один из перечисленных вами предпочитаемых жанров. Чтобы установить параметр, необходимо набрать команду /set strict и после пробела True или False. Например: /set strict True .

  Каждый из элементов предпочтений (кроме оценки аниме) можно очистить с помощью команды /clean \{название предпочтения\}. Например: /clean genres очистит предпочтения жанров аниме.

  ### Способ генерации вопроса:

  Вопрос пользователю состоит из двух частей: итоговая рекомендация аниме и вопрос “Как вам моя рекомендация?” с вариантами ответа “Понравилась” / “ Не понравилась” / “Не знаю”.

  Рекомендация составляется с помощью функции smart_filter() , которая принимает на вход имя пользователя, а на выходе дает датасет с подходящими по критериям аниме. Код функции доступен в файле mf , по ссылке https://github.com/meremuta/ChatBot .

  **Функция действует согласно следующему алгоритму:**

  * Загрузка датасетов об аниме и оценках других пользователей из облачного хранилища.

  * Загрузка оценок текущего пользователя из подключенной базы данных YDB.

  * Загрузка предпочтений текущего пользователя из подключенной базы данных YDB.

  * Обработка данных о предпочтениях: использовать дефолтные значения, если данных нет.

  * Обработка данных об оценках текущего пользователя: если оценок нет, использовать весь датасет аниме в качестве непросмотренного.

  * Если оценки аниме есть, то отфильтровать их список по предпочтению “собственный рейтинг”.

  * Проверка по предпочтению похожести:

    * Если значение True,  тогда берется датасет с оценками других пользователей, из него выбираются только те пользователи, которые оценивали аниме, просмотренные текущим пользователем и оцененные им выше параметра “собственный рейтинг”.  Выделяется список уникальных пользователей. Общий датасет с оценками всех пользователей фильтруется по списку пользователей, полученному в предыдущем шаге. Исключаются аниме, уже просмотренные текущим пользователем.  Таким образом мы находим “похожих” пользователей и аниме, которые они просмотрели и оценили.

    * Если значение False, из общего списка оценок других пользователей исключаются аниме, уже просмотренные текущим пользователем.

  * Фильтрация полученного датасета оценок других пользователей по предпочтению “чужой рейтинг”.

  * Извлечение уникальных аниме (удаление дублирующихся строк)

  * Фильтр аниме по предпочтению “общий рейтинг”.

  * Проверка по предпочтению строгости:

    * Если значение True,  датасет с аниме фильтруется таким образом, что в нем остаются только те аниме, в которых есть все жанры, указанные пользователем в предпочтениях.

    * Если значение False, датасет с аниме фильтруется таким образом, что в нем остаются аниме, в которых есть хоть один жанр из указанных в предпочтениях пользователя.

  * Фильтрация по исключаемым жанрам. Остаются только те аниме, в которых нет жанров, указанных в предпочтении “исключаемые жанры”.

  * Приведение данных о жанрах из вида дамми-переменных в читаемую строку.

  * Фильтрация датасета по предпочитаемому типу аниме.




  ### Функционал бота

  Список команд:

  * /start - Вступительная речь

  * /commands - Список доступных команд

  * /get preferences – Получить сохраненные предпочтения из базы данных

  * /get genres – Получить список всех жанров аниме в базе

  * /recommend – Получить рекомендацию аниме

  * /infopref – Получить информацию и инструкции к предпочтениям

  * /set exclude – Установить предпочтение исключаемых жанров

  * /set genres - Установить предпочтение жанров

  * /set totalrate - Установить предпочтение общего рейтинга

  * /set othersrate - Установить предпочтение рейтинга других пользователей

  * /set myrate - Установить предпочтение собственного рейтинга

  * /set strict - Установить предпочтение строгости фильтрации

  * /set similarity - Установить предпочтение похожести

  * /set type - Установить предпочтение типа аниме

  * /clean genres - Очистить предпочтение жанров

  * /clean exclude - Очистить предпочтение исключаемых жанров

  * /clean totalrate - Очистить предпочтение общего рейтинга

  * /clean othersrate - Очистить предпочтение рейтинга других пользователей

  * /clean myrate - Очистить предпочтение собственного рейтинга

  * /clean strict - Очистить предпочтение строгости фильтрации

  * /clean similarity - Очистить предпочтение похожести

  * /clean type - Очистить предпочтение типа аниме

  * /rate count – Получить количество оцененных аниме из базы данных

  * /quote – Получить случайную цитату (задействовано внешнее API) https://animechan.xyz/

  * /rate – Оценить аниме

  * /rate \{id\} – Оценить конкретное аниме. Для этого необходимо знать его id на myanimelist.net . id аниме пишется в ссылке после 'anime/'. Например: ссылка на аниме - https://myanimelist.net/anime/666 , id этого аниме - 666

  * /stoprate – Прекратить оценивание аниме

  
  ### Реализация функции с кроном

 Помимо вызываемых напрямую пользователем команд, также настроен триггер, отправляющий пользователю раз в день рандомную “Цитату дня” с помощью вызова API.

  Бот запрашивает цитату через API и отправляет пользователю с сообщением “Ваша цитатка дня:”

  ### Ресурсы

  Для выполнения задания были использованы данные с  [Kaggle ](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database?resource=download) (это ссылка на данные).

  Данные были изменены и обработаны мной с помощью R, вот код - https://github.com/meremuta/ChatBot/blob/master/anime_data.Rmd

  Также, был использован API Animechan - https://animechan.xyz/

  Весь код чат-бота можно найти по ссылке - https://github.com/meremuta/ChatBot/tree/master . В проекте, помимо кода обработки данных, также основной файл с кодом бота (index) и файл с написанными мной функциями (mf).
