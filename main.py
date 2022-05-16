# Телеграм-бот v.004
from io import BytesIO

import telebot  # pyTelegramBotAPI 4.3.1
from telebot import types
import requests
import bs4
import botGames  # бот-игры, файл botGames.py
from menuBot import Menu, Users  # в этом модуле есть код, создающий экземпляры классов описывающих моё меню
import DZ  # домашнее задание от первого урока

api_key = '5105972662:AAG24fr382U1_hosO4Zrb-tv_BTakAV1MPk'

bot = telebot.TeleBot(api_key)  # Создаем экземпляр бота


# -----------------------------------------------------------------------
# Функция, обрабатывающая команды
@bot.message_handler(commands=['start'])
def command(message, res=False):
    chat_id = message.chat.id
    bot.send_sticker(chat_id, "CAACAgIAAxkBAAIaeWJEeEmCvnsIzz36cM0oHU96QOn7AAJUAANBtVYMarf4xwiNAfojBA")
    txt_message = f"Привет, {message.from_user.first_name}! Я тестовый бот для курса программирования на языке Python"
    bot.send_message(chat_id, text=txt_message, reply_markup=Menu.getMenu(chat_id, "Главное меню").markup)


# -----------------------------------------------------------------------
# Получение стикеров от юзера
@bot.message_handler(content_types=['sticker'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    sticker = message.sticker
    bot.send_message(message.chat.id, sticker)

    # глубокая инспекция объекта
    # import inspect,pprint
    # i = inspect.getmembers(sticker)
    # pprint.pprint(i)


# -----------------------------------------------------------------------
# Получение аудио от юзера
@bot.message_handler(content_types=['audio'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    audio = message.audio
    bot.send_message(chat_id, audio)


# -----------------------------------------------------------------------
# Получение голосовухи от юзера
@bot.message_handler(content_types=['voice'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    voice = message.voice
    bot.send_message(message.chat.id, voice)


# -----------------------------------------------------------------------
# Получение фото от юзера
@bot.message_handler(content_types=['photo'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    photo = message.photo
    bot.send_message(message.chat.id, photo)


# -----------------------------------------------------------------------
# Получение видео от юзера
@bot.message_handler(content_types=['video'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    video = message.video
    bot.send_message(message.chat.id, video)


# -----------------------------------------------------------------------
# Получение документов от юзера
@bot.message_handler(content_types=['document'])
def get_messages(message):
    chat_id = message.chat.id
    mime_type = message.document.mime_type
    bot.send_message(chat_id, "Это " + message.content_type + " (" + mime_type + ")")

    document = message.document
    bot.send_message(message.chat.id, document)
    if message.document.mime_type == "video/mp4":
        bot.send_message(message.chat.id, "This is a GIF!")


# -----------------------------------------------------------------------
# Получение координат от юзера
@bot.message_handler(content_types=['location'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    location = message.location
    bot.send_message(message.chat.id, location)


# -----------------------------------------------------------------------
# Получение контактов от юзера
@bot.message_handler(content_types=['contact'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    contact = message.contact
    bot.send_message(message.chat.id, contact)


# -----------------------------------------------------------------------
# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    ms_text = message.text

    cur_user = Users.getUser(chat_id)
    if cur_user == None:
        cur_user = Users(chat_id, message.json["from"])

    result = goto_menu(chat_id, ms_text)  # попытаемся использовать текст как команду меню, и войти в него
    if result:
        return  # мы вошли в подменю, и дальнейшая обработка не требуется

    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu is not None and ms_text in cur_menu.buttons:  # проверим, что команда относится к текущему меню

        if ms_text == "Помощь":
            send_help(chat_id)

        elif ms_text == "Прислать собаку":
            bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

        elif ms_text == "Прислать анекдот":
            # bot.send_message(chat_id, text=get_anekdot())
            bot.send_message(chat_id, text=get_news())

        elif ms_text == "Прислать фильм":
            send_film(chat_id)

        elif ms_text == 'Прислать картину':
            get_randomArt()

        elif ms_text == "Новая игра":
            text_game = "❌ Игрок\n" \
                        "⭕ Компьютер"

            markup = types.InlineKeyboardMarkup()

            for i in range(3):
                btn1 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{1 + i * 3}')
                btn2 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{2 + i * 3}')
                btn3 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{3 + i * 3}')

                markup.add(btn1, btn2, btn3)

            sended_message = bot.send_message(chat_id, text=text_game, reply_markup=markup)

            gameTicTacToe = botGames.newGame(chat_id, botGames.gameTicTacToe(chat_id, sended_message.id))

        elif ms_text == "Угадай кто?":
            get_ManOrNot(chat_id)

        elif ms_text == "Карту!":
            game21 = botGames.getGame(chat_id)

            if game21 is None:  # если мы случайно попали в это меню, а объекта с игрой нет
                goto_menu(chat_id, "Выход")
                return

            text_game = game21.get_cards(1)
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

            if game21.status is not None:  # выход, если игра закончена
                botGames.stopGame(chat_id)
                goto_menu(chat_id, "Выход")
                return

        elif ms_text == "Стоп!":
            botGames.stopGame(chat_id)
            goto_menu(chat_id, "Выход")
            return

        # elif ms_text in botGames.GameRPS.values:  # реализация игры Камень-ножницы-бумага
        #     gameRSP = botGames.getGame(chat_id)
        #
        #     if gameRSP is None:  # если мы случайно попали в это меню, а объекта с игрой нет
        #         goto_menu(chat_id, "Выход")
        #         return
        #
        #     text_game = gameRSP.playerChoice(ms_text)
        #     bot.send_message(chat_id, text=text_game)
        #     gameRSP.newGame()

        elif ms_text == "Задание-1":
            DZ.dz1(bot, chat_id)

        elif ms_text == "Задание-2":
            DZ.dz2(bot, chat_id)

        elif ms_text == "Задание-3":
            DZ.dz3(bot, chat_id)

        elif ms_text == "Задание-4":
            DZ.dz4(bot, chat_id)

        elif ms_text == "Задание-5":
            DZ.dz5(bot, chat_id)

        elif ms_text == "Задание-6":
            DZ.dz6(bot, chat_id)

    else:  # ...........................................................................................................
        bot.send_message(chat_id, text="Мне жаль, я не понимаю вашу команду: " + ms_text)
        goto_menu(chat_id, "Главное меню")


# -----------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # если требуется передать параметр или несколько параметров в обработчик кнопки,
    # использовать методы Menu.getExtPar() и Menu.setExtPar()

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Камень, ножницы, бумага
    if call.data == 'cb_rock':
        rsp_game_result(chat_id, message_id, 'Камень')

    elif call.data == 'cb_scissors':
        rsp_game_result(chat_id, message_id, 'Ножницы')

    elif call.data == 'cb_paper':
        rsp_game_result(chat_id, message_id, 'Бумага')

    # Крестики-нолики
    # print(call.message.reply_markup.inline_keyboard[0][0].text)
    # print(dir(call.message.reply_markup))
    # print(call.message)
    keyboard = call.message.reply_markup.keyboard

    if call.data[:-2] == 'field':
        field_number = int(call.data[-1]) - 1
        button = keyboard[field_number // 3][field_number % 3]

        # tic_tac_toe_player_choice(chat_id, keyboard[field_number // 3][field_number % 3])
        tic_tac_toe_player_choice(chat_id, message_id, field_number, button)


    # if call.data == "ManOrNot_GoToSite": #call.data это callback_data, которую мы указали при объявлении InLine-кнопки
    #
    #     # После обработки каждого запроса нужно вызвать метод answer_callback_query, чтобы Telegram понял, что запрос обработан.
    #     bot.answer_callback_query(call.id)


def tic_tac_toe_player_choice(chat_id, message_id, field_number, button):
    gameTicTacToe = botGames.getGame(chat_id)

    if gameTicTacToe is None:  # если мы случайно попали в это меню, а объекта с игрой нет
        goto_menu(chat_id, "Выход")
        return

    if Menu.getCurMenuName(chat_id) == 'Крестики-нолики':
        if button.text == '⬜':
            game_end = gameTicTacToe.gameEndCheck(chat_id, message_id)

            if game_end == 0:
                # Ход игрока
                gameTicTacToe.playerChoice(chat_id, message_id, field_number)
                ttt_refresh_markup(chat_id, message_id, gameTicTacToe.getField(chat_id, message_id))

                # Проверка конца игры
                game_end = gameTicTacToe.gameEndCheck(chat_id, message_id)

                if game_end == 0:
                    # Ход компьютера
                    gameTicTacToe.computerChoice(chat_id, message_id)
                    ttt_refresh_markup(chat_id, message_id, gameTicTacToe.getField(chat_id, message_id))

                    game_end = gameTicTacToe.gameEndCheck(chat_id, message_id)

                if game_end != 0:
                    ttt_game_end_refresh(chat_id, message_id, game_end, gameTicTacToe.getField(chat_id, message_id))
    else:
        text_game = "❌ Игрок\n" \
                    "⭕ Компьютер"

        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=text_game, parse_mode='HTML', reply_markup=None)


def ttt_game_end_refresh(chat_id, message_id, win_side, field):
    if win_side == 1:
        text_game = "⠀⠀⠀⠀<b>Победа игрока</b>\n" \
                    "❌ Игрок⠀⠀⠀⠀⠀⠀🏆\n" \
                    "⭕ Компьютер⠀⠀😭"
    elif win_side == 2:
        text_game = "⠀⠀⠀⠀<b>Победа компьютера</b>\n" \
                    "❌ Игрок⠀⠀⠀⠀⠀⠀😭\n" \
                    "⭕ Компьютер⠀⠀🏆"
    else:
        text_game = "⠀⠀⠀⠀<b>Ничья</b>\n" \
                    "❌ Игрок⠀⠀⠀⠀⠀⠀😐\n" \
                    "⭕ Компьютер⠀⠀😐"

    markup = types.InlineKeyboardMarkup()
    markup_row = []

    for i in range(9):
        if field[i] == 0:
            markup_row.append(types.InlineKeyboardButton(text="⬜", callback_data=f'field_{i + 1}'))

        elif field[i] == 1:
            markup_row.append(types.InlineKeyboardButton(text="❌", callback_data=f'field_{i + 1}'))

        else:
            markup_row.append(types.InlineKeyboardButton(text="⭕", callback_data=f'field_{i + 1}'))

        if i % 3 == 2:
            markup.add(*markup_row)
            markup_row = []

    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=text_game, parse_mode='HTML', reply_markup=markup)


def ttt_refresh_markup(chat_id, message_id, field):
    markup = types.InlineKeyboardMarkup()
    markup_row = []

    for i in range(9):
        if field[i] == 0:
            markup_row.append(types.InlineKeyboardButton(text="⬜", callback_data=f'field_{i + 1}'))

        elif field[i] == 1:
            markup_row.append(types.InlineKeyboardButton(text="❌", callback_data=f'field_{i + 1}'))

        else:
            markup_row.append(types.InlineKeyboardButton(text="⭕", callback_data=f'field_{i + 1}'))

        if i % 3 == 2:
            markup.add(*markup_row)
            markup_row = []

    text_game = "❌ Игрок\n" \
                "⭕ Компьютер"

    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=text_game, parse_mode='HTML', reply_markup=markup)


def rsp_game_result(chat_id, message_id, player_choice=None):
    gameRSP = botGames.getGame(chat_id)

    if gameRSP is None:  # если мы случайно попали в это меню, а объекта с игрой нет
        goto_menu(chat_id, "Выход")
        return

    if Menu.getCurMenuName(chat_id) == 'Камень, ножницы, бумага':
        victory_text = gameRSP.playerChoice(player_choice)

        round_result_text = f'⠀⠀⠀⠀<b>Игровой⠀раунд</b>' + '\n\n' + \
                            f'Игрок:    <b>{player_choice}</b>' + '\n' + \
                            f'Компьютер:    <b>{gameRSP.computerChoice}</b>'

        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=round_result_text, parse_mode='HTML', reply_markup=None)

        bot.send_message(chat_id, text=victory_text)
        gameRSP.newGame()

        rsp_game_start(chat_id)
    else:
        round_text = '⠀⠀⠀⠀<b>Игровой⠀раунд</b>' + '\n\n' + \
                     'Игрок:    <b>???</b>' + '\n' + \
                     'Компьютер:    <b>???</b>'

        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=round_text, parse_mode='HTML', reply_markup=None)


def rsp_game_start(chat_id):
    round_start_text = '⠀⠀⠀⠀<b>Игровой⠀раунд</b>' + '\n\n' + \
                       'Игрок:    <b>???</b>' + '\n' + \
                       'Компьютер:    <b>???</b>'

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton(text="Камень", callback_data='cb_rock')
    btn2 = types.InlineKeyboardButton(text="Ножницы", callback_data='cb_scissors')
    btn3 = types.InlineKeyboardButton(text="Бумага", callback_data='cb_paper')

    markup.add(btn1, btn2, btn3)

    bot.send_message(chat_id, text=round_start_text, parse_mode='HTML', reply_markup=markup)


# -----------------------------------------------------------------------
def goto_menu(chat_id, name_menu):
    # получение нужного элемента меню
    cur_menu = Menu.getCurMenu(chat_id)
    if name_menu == "Выход" and cur_menu is not None and cur_menu.parent is not None:
        target_menu = Menu.getMenu(chat_id, cur_menu.parent.name)
    else:
        target_menu = Menu.getMenu(chat_id, name_menu)

    if target_menu is not None:
        bot.send_message(chat_id, text=target_menu.name, reply_markup=target_menu.markup)

        # Проверим, нет ли обработчика для самого меню. Если есть - выполним нужные команды
        if target_menu.name == "Игра в 21":
            game21 = botGames.newGame(chat_id, botGames.Game21(jokers_enabled=True))  # создаём новый экземпляр игры
            text_game = game21.get_cards(2)  # просим 2 карты в начале игры
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

        elif target_menu.name == "Камень, ножницы, бумага":
            gameRSP = botGames.newGame(chat_id, botGames.GameRPS())  # создаём новый экземпляр игры

            text_game = "<b>Победитель определяется по следующим правилам:</b>\n" \
                        "1. Камень побеждает ножницы\n" \
                        "2. Бумага побеждает камень\n" \
                        "3. Ножницы побеждают бумагу"

            bot.send_photo(chat_id, photo="https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg",
                           caption=text_game, parse_mode='HTML')

            rsp_game_start(chat_id)

        elif target_menu.name == "Крестики-нолики":
            text_game = "❌ Игрок\n" \
                        "⭕ Компьютер"

            markup = types.InlineKeyboardMarkup()

            for i in range(3):
                btn1 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{1 + i * 3}')
                btn2 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{2 + i * 3}')
                btn3 = types.InlineKeyboardButton(text="⬜", callback_data=f'field_{3 + i * 3}')

                markup.add(btn1, btn2, btn3)

            sended_message = bot.send_message(chat_id, text=text_game, reply_markup=markup)

            gameTicTacToe = botGames.newGame(chat_id, botGames.gameTicTacToe(chat_id, sended_message.id))

        return True
    else:
        return False


# -----------------------------------------------------------------------
def getMediaCards(game21):
    medias = []
    for url in game21.arr_cards_URL:
        medias.append(types.InputMediaPhoto(url))
    return medias


# -----------------------------------------------------------------------
def send_help(chat_id):
    global bot
    bot.send_message(chat_id, "Автор: Панасенко Софья, 1-МД-5")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Напишите автору", url="https://t.me/goto_menuave_satanas_bitch")
    markup.add(btn1)
    img = open('author.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=markup)

    bot.send_message(chat_id, "Активные пользователи чат-бота:")
    for el in Users.activeUsers:
        bot.send_message(chat_id, Users.activeUsers[el].getUserHTML(), parse_mode='HTML')


# -----------------------------------------------------------------------
def send_film(chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n\n" \
               f"<b>Год:</b> {film['Год']}\n" \
               f"<b>Страна:</b> {film['Страна']}\n" \
               f"<b>Жанр:</b> {film['Жанр']}\n" \
               f"<b>Режисёр:</b> {film['Режиссёр']}\n" \
               f"<b>Актёры:</b> {film['Актёры']}"
    # f"Продолжительность: {film['Продолжительность']}" \

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="СМОТРЕТЬ онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML', reply_markup=markup)


# -----------------------------------------------------------------------
def get_anekdot():
    array_anekdots = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""


# -----------------------------------------------------------------------
def get_news():
    array_anekdots = []
    req_anek = requests.get('https://www.banki.ru/news/lenta')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.doFpcq')
        for result in result_find:
            print(result)

            # array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""


# -----------------------------------------------------------------------
def get_foxURL():
    url = ""
    req = requests.get('https://randomfox.ca/floof/')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['image']
        # url.split("/")[-1]
    return url


# -----------------------------------------------------------------------
def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
        # url.split("/")[-1]
    return url


# -----------------------------------------------------------------------
def get_ManOrNot(chat_id):
    global bot

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text="Проверить",
        url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")

    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")


# ---------------------------------------------------------------------
def get_randomFilm():
    url = 'https://randomfilm.ru/'
    infoFilm = {}
    req_film = requests.get(url)
    soup = bs4.BeautifulSoup(req_film.text, "html.parser")
    result_find = soup.find('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]

    details = result_find.findAll('td')

    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm


# ---------------------------------------------------------------------
def get_randomArt():
    #from translate import Translator
    #translator = Translator(from_lang="english", to_lang="russian")

    infoArt = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }

    url = 'https://random-ize.com/random-art-gallery/'

    req_art = requests.get(url, headers=headers)

    soup = bs4.BeautifulSoup(req_art.text, "html.parser")

    #print(soup)
    result_find = soup.find(id='Container')

    img = result_find.find_all('img')[0]
    infoArt['Картина_url'] = url + img.get('src').replace('/random-art-gallery/', '')

    print(infoArt['Картина_url'])

   # url = 'https://random-ize.com/random-art-gallery/'

    print(result_find)


# ---------------------------------------------------------------------
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)  # Запускаем бота

    except Exception as e:
        print(e)
