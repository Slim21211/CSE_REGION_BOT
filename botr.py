import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot("5415445247:AAHg_cDaH1q1rSlkMP4tRE8wfbBmX3TOl_A", parse_mode='html')
admin_id = 349682954

def analytics(func: callable):
    def analytics_wrapper(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS login_id(
            id INTEGER,
            name TEXT,
            surname TEXT
        )''')
        connect.commit()

        people_id = message.chat.id
        cursor.execute(f'SELECT id FROM login_id WHERE id = {people_id}')
        data = cursor.fetchone()
        if data is None:
            user = (message.chat.id, message.from_user.first_name, message.from_user.last_name)
            print("Новый пользователь: ", user, "Сообщение: ", message.text)
            cursor.execute('INSERT INTO login_id VALUES(?,?,?);', user)
            connect.commit()

        connect = sqlite3.connect('message.db')
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER,
                    name TEXT,
                    surname TEXT,
                    message TEXT
                )''')
        connect.commit()

        people_id = message.chat.id
        cursor.execute(f'SELECT id FROM messages WHERE id = {people_id}')
        user = (message.chat.id, message.from_user.first_name, message.from_user.last_name, message.text)
        print("Пользователь: ", user)
        cursor.execute('INSERT INTO messages VALUES(?,?,?,?);', user)
        connect.commit()
        return func(message)
    return analytics_wrapper

@bot.message_handler(commands=['start'])
@analytics
def start(message):
    with open('users.txt', 'a+') as usersids:
        print(message.chat.id, file=usersids)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    interns = types.KeyboardButton('Для стажеров')
    study = types.KeyboardButton('Базовое обучение')
    cargo = types.KeyboardButton('КАРГО')
    post_office = types.KeyboardButton('ПВЗ и почтоматы')
    fast_pay = types.KeyboardButton('СБП')
    mentors = types.KeyboardButton('Для наставника')
    traces = types.KeyboardButton('Трейсы для диспетчера')
    vympelcom = types.KeyboardButton('Вымпелком')
    netbynet = types.KeyboardButton('НэтБайНэт')
    quiz = types.KeyboardButton('Аттестация сотрудников')
    new_traces = types.KeyboardButton('НСТ')
    markup.row(interns, study)
    markup.row(cargo, post_office)
    markup.row(fast_pay, mentors)
    markup.row(traces, new_traces)
    markup.row(vympelcom, netbynet)
    markup.row(quiz)
    bot.send_message(message.chat.id,f'{message.from_user.first_name}, добро пожаловать в команду компании <i>Курьер Сервис Экспресс!</i>\n'
                                 '\n'
                                 'Вы подписались на обучающий бот компании.\n'
                                 '\n'
                                 'Выберите раздел:', parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['home'])
@analytics
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    interns = types.KeyboardButton('Для стажеров')
    study = types.KeyboardButton('Базовое обучение')
    cargo = types.KeyboardButton('КАРГО')
    post_office = types.KeyboardButton('ПВЗ и почтоматы')
    fast_pay = types.KeyboardButton('СБП')
    mentors = types.KeyboardButton('Для наставника')
    traces = types.KeyboardButton('Трейсы для диспетчера')
    quiz = types.KeyboardButton('Аттестация сотрудников')
    new_traces = types.KeyboardButton('НСТ')
    vympelcom = types.KeyboardButton('Вымпелком')
    netbynet = types.KeyboardButton('НэтБайНэт')
    markup.row(interns, study)
    markup.row(cargo, post_office)
    markup.row(fast_pay, mentors)
    markup.row(traces, new_traces)
    markup.row(vympelcom, netbynet)
    markup.row(quiz)
    bot.send_message(message.chat.id,'Выберите раздел:', parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['back'])
@analytics
def back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    chapter1 = types.KeyboardButton('Программа Базового обучения')
    chapter2 = types.KeyboardButton('Начало рабочего дня')
    chapter3 = types.KeyboardButton('Расходные материалы')
    chapter4 = types.KeyboardButton('Накладная')
    chapter5 = types.KeyboardButton('Доставка лично в руки')
    chapter6 = types.KeyboardButton('Доставка с возвратом')
    chapter7 = types.KeyboardButton('Забор за наличные деньги')
    chapter8 = types.KeyboardButton('Международное отправление')
    chapter9 = types.KeyboardButton('Завершение рабочего дня')
    markup.row(chapter1)
    markup.add(chapter2, chapter3, chapter4, chapter5, chapter6, chapter7, chapter8, chapter9)
    bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                      '\n'
                                      'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['send'])
def send(message):
    if message.chat.id == admin_id:
        bot.send_message(message.chat.id, 'Start')
        for i in open('users.txt', 'r').readlines():
            try:
                bot.send_message(i, 'ОБЪЯВЛЕНИЕ!!!\n\n'
                                    'Коллеги, сегодня в боте пройдут небольшие обновления. Какое-то непродолжительное время он работать не будет.\n\n'
                                    'Вы получите оповещение, когда всё будет восстановлено.\n\n'
                                    'Приносим извинения за временные неудобства!')
            except:
                continue
        bot.send_message(message.chat.id, 'Stop')
    else:
        bot.send_message(message.chat.id, 'Вы не можете делать рассылку в этом боте')



@bot.message_handler(content_types=['text'])
@analytics
def get_user_text(message):
    if message.text == 'Для стажеров':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        part1 = types.KeyboardButton('Памятка стажера')
        part2 = types.KeyboardButton('Контакты МСК')
        markup.add(part1, part2)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка стажера':
        bot.send_message(message.chat.id, 'Ознакомьтесь с памяткой для стажеров:')
        doc = open('Documents/interns_guide.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html')

    elif message.text == 'Контакты МСК':
        bot.send_message(message.chat.id, 'Здесь Вы можете посмотреть контакты сотрудников подразделений Москвы и Московской области:')
        doc = open('Documents/contacts.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html')

    elif message.text == 'Базовое обучение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Программа Базового обучения')
        chapter2 = types.KeyboardButton('Начало рабочего дня')
        chapter3 = types.KeyboardButton('Расходные материалы')
        chapter4 = types.KeyboardButton('Накладная')
        chapter5 = types.KeyboardButton('Доставка лично в руки')
        chapter6 = types.KeyboardButton('Доставка с возвратом')
        chapter7 = types.KeyboardButton('Забор за наличные деньги')
        chapter8 = types.KeyboardButton('Международное отправление')
        chapter9 = types.KeyboardButton('Завершение рабочего дня')
        chapter10 = types.KeyboardButton('Тест по базовому обучению')
        markup.row(chapter1)
        markup.add(chapter2, chapter3, chapter4, chapter5, chapter6, chapter7, chapter8, chapter9)
        markup.row(chapter10)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Программа Базового обучения':
        doc = open('Documents/study_program.pdf', 'rb')
        bot.send_message(message.chat.id, 'Ознакомьтесь с программой обучения стажера:')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Начало рабочего дня':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Начало рабочего дня (текст)')
        video = types.KeyboardButton('Начало рабочего дня (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Начало рабочего дня</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Начало рабочего дня (текст)':
        doc = open('Documents/start_day.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Начало рабочего дня (видео)':
        video = open('Video/start_day.MP4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Расходные материалы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Расходные материалы (текст)')
        video = types.KeyboardButton('Расходные материалы (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Расходные материалы</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Расходные материалы (текст)':
        doc = open('Documents/expend_materials.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Расходные материалы (видео)':
        video = open('Video/expend_materials.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Накладная':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Накладная (текст)')
        video = types.KeyboardButton('Накладная (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Накладная</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Накладная (текст)':
        doc = open('Documents/invoice.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Накладная (видео)':
        video = open('Video/invoice.MP4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Доставка лично в руки':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Доставка лично в руки (текст)')
        video = types.KeyboardButton('Доставка лично в руки (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Доставка лично в руки</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Доставка лично в руки (текст)':
        doc = open('Documents/deliv_person.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Доставка лично в руки (видео)':
        video = open('Video/deliv_person.MP4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Доставка с возвратом':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Доставка с возвратом (текст)')
        video = types.KeyboardButton('Доставка с возвратом (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Доставка с возвратом</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)
    elif message.text == 'Доставка с возвратом (текст)':
        doc = open('Documents/return_shipping.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Доставка с возвратом (видео)':
        video = open('Video/return_shipping.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Забор за наличные деньги':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Забор за наличные деньги (текст)')
        video = types.KeyboardButton('Забор за наличные деньги (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Забор за наличные деньги</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Забор за наличные деньги (текст)':
        doc = open('Documents/reception_cash.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Забор за наличные деньги (видео)':
        video = open('Video/reception_cash.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Международное отправление':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Международное отправление (текст)')
        video = types.KeyboardButton('Международное отправление (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Международное отправление</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Международное отправление (текст)':
        doc = open('Documents/international_shipping.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Международное отправление (видео)':
        video = open('Video/international_shipping.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Завершение рабочего дня':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        text = types.KeyboardButton('Завершение рабочего дня (текст)')
        video = types.KeyboardButton('Завершение рабочего дня (видео)')
        markup.add(text, video)
        bot.send_message(message.chat.id, '<b><i>Завершение рабочего дня</i></b>\n'
                                          '\n'
                                          'Выберите формат обучающего материала:\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html', reply_markup=markup)

    elif message.text == 'Завершение рабочего дня (текст)':
        doc = open('Documents/end_day.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Завершение рабочего дня (видео)':
        video = open('Video/end_day.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /back')

    elif message.text == 'Тест по базовому обучению':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Базовое тестирование', url='https://short.startexam.com/B6HL1SHQ'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'КАРГО':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Видео урок Карго')
        chapter2 = types.KeyboardButton('Памятка Карго')
        chapter3 = types.KeyboardButton('Схема трейсов')
        chapter4 = types.KeyboardButton('Презентация Карго')
        chapter5 = types.KeyboardButton('Электронные чеки')
        markup.add(chapter1, chapter2, chapter3, chapter4, chapter5)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок Карго':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://disk.yandex.ru/i/ltovAU8b255-DQ'))
        bot.send_message(message.chat.id, 'Для просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Памятка Карго':
        doc = open('Documents/cargo_manual.pdf', 'rb')
        bot.send_message(message.chat.id, 'Ознакомьтесь с инструкцией по работе с мобильным приложением Cargo5:')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Схема трейсов':
        doc = open('Documents/traces_scheme.pdf', 'rb')
        bot.send_message(message.chat.id, 'Ознакомьтесь со схемой трейсов:')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Презентация Карго':
        doc = open('Documents/cargo-presentation.pdf', 'rb')
        bot.send_message(message.chat.id, 'Ознакомьтесь с презентацией по работе в мобильном приложении:')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Электронные чеки':
        doc = open('Documents/e_chek.pdf', 'rb')
        bot.send_message(message.chat.id, 'Ознакомьтесь с инструкцией по работе с интернет-магазинами (электронные чеки):')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'ПВЗ и почтоматы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        chapter1 = types.KeyboardButton('Видео урок ПВЗ')
        chapter2 = types.KeyboardButton('Инструкция по работе с ПВЗ и почтоматами')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок ПВЗ':
        video = open('Video/halva_video.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Инструкция по работе с ПВЗ и почтоматами':
        bot.send_message(message.chat.id, 'Ознакомьтесь с инструкцией по закладке и изъятию отправлений в почтоматах Халва:')
        doc = open('Documents/halva.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html')

    elif message.text == 'СБП':
        connect = sqlite3.connect('users_sbp.db')
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS login_sbp_id(
                        id INTEGER,
                        name TEXT,
                        surname TEXT
                    )''')
        connect.commit()

        people_id = message.chat.id
        cursor.execute(f'SELECT id FROM login_sbp_id WHERE id = {people_id}')
        data = cursor.fetchone()
        if data is None:
            user_sbp = (message.chat.id, message.from_user.first_name, message.from_user.last_name)
            print("Обучение СБП: ", user_sbp)
            cursor.execute('INSERT INTO login_sbp_id VALUES(?,?,?);', user_sbp)
            connect.commit()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        manual = types.KeyboardButton('Инструкция по СБП')
        script = types.KeyboardButton('Скрипт для курьеров по СБП')
        video = types.KeyboardButton('Видео урок СБП')
        markup.row(manual, script)
        markup.row(video)
        bot.send_message(message.chat.id, '<b><i>СБП</i></b>\n'
                                          '\n'
                                          'Выберите раздел:\n'
                                          '\n'
                                          'Для возврата назад нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Инструкция по СБП':
        doc = open('Documents/fast_pay_manual.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Скрипт для курьеров по СБП':
        doc = open('Documents/fast_pay_script.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Видео урок СБП':
        video = open('Video/fast_pay.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Для наставника':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Видео урок для наставников')
        chapter2 = types.KeyboardButton('Презентация для наставников')
        chapter3 = types.KeyboardButton('Памятка для наставников')
        markup.row(chapter1)
        markup.row(chapter2)
        markup.row(chapter3)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок для наставников':
        video = open('Video/mentoring.mp4', 'rb')
        bot.send_video(message.chat.id, video, width=1920, height=1080, timeout=10000)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Презентация для наставников':
        doc = open('Documents/mentors_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Памятка для наставников':
        # doc = open('', 'rb')
        # bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'В этом разделе пока нет обучающих материалов, но они очень скоро появятся)\n'
                                          '\n'
                                          'Для возврата нажмите /home')

    elif message.text == 'Трейсы для диспетчера':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Презентация трейсы для диспетчера')
        chapter2 = types.KeyboardButton('Памятка трейсы для диспетчера')
        markup.row(chapter1)
        markup.row(chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Презентация трейсы для диспетчера':
        doc = open('Documents/disp_traces_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Памятка трейсы для диспетчера':
        doc = open('Documents/disp_traces_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Новая система трейсов')
        chapter2 = types.KeyboardButton('Памятка НСТ')
        chapter3 = types.KeyboardButton('Схема НСТ')
        chapter4 = types.KeyboardButton('НСТ диспетчеры')
        chapter5 = types.KeyboardButton('Работа с трейсами ПВЗ')
        chapter6 = types.KeyboardButton('НСТ логист')
        chapter7 = types.KeyboardButton('НСТ склад хранения')
        chapter8 = types.KeyboardButton('НСТ склад')
        markup.add(chapter1, chapter2, chapter3, chapter4, chapter5, chapter6, chapter7, chapter8)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Новая система трейсов':
        doc = open('Documents/traces_new_system.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Памятка НСТ':
        doc = open('Documents/traces_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Схема НСТ':
        doc = open('Documents/traces_scheme.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ диспетчеры':
        doc = open('Documents/disp_traces_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Работа с трейсами ПВЗ':
        doc = open('Documents/traces_work.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ логист':
        doc = open('Documents/traces_logist.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ склад хранения':
        doc = open('Documents/traces_storage.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ склад':
        doc = open('Documents/traces_storehouse.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Вымпелком':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкции Вымпелком')
        chapter2 = types.KeyboardButton('Видео инструкции Вымпелком')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)
    elif message.text == 'Инструкции Вымпелком':
        doc1 = open('Documents/return ABO.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция для курьера (Возврат АБО):')
        bot.send_document(message.chat.id, doc1)
        doc2 = open('Documents/change ABO.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция для курьера (Замена АБО):')
        bot.send_document(message.chat.id, doc2)
        doc3 = open('Documents/delivery ABO.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция для курьера (Доставка АБО):')
        bot.send_document(message.chat.id, doc3)
        doc4 = open('Documents/delivery SIM.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция для курьера (Доставка СИМ):')
        bot.send_document(message.chat.id, doc4)
        doc5 = open('Documents/delivery lite.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция для курьера (Доставка Lite):')
        bot.send_document(message.chat.id, doc5)
        doc6 = open('Documents/damage ABO.pdf', 'rb')
        bot.send_message(message.chat.id, 'Инструкция ВК ШПД Порченное АБО:')
        bot.send_document(message.chat.id, doc6)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')
    elif message.text == 'Видео инструкции Вымпелком':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://disk.yandex.ru/i/Yx1yyB0HaHnAPg'))
        bot.send_message(message.chat.id, '<b>Возврат АБО для смартфона</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://disk.yandex.ru/i/mXWbmfAOPkyDow'))
        bot.send_message(message.chat.id, '<b>Доставка АБО</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НэтБайНэт':
        doc1 = open('Documents/netbynet.pdf', 'rb')
        bot.send_document(message.chat.id, doc1)

    elif message.text == 'Аттестация сотрудников':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкция по аттестации')
        chapter2 = types.KeyboardButton('Тест для ОСиД, АФС, Регионы')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Инструкция по аттестации':
        doc = open('Documents/attestation_instruction.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Тест для ОСиД, АФС, Регионы':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Аттестация', url='https://short.startexam.com/-9RVOBVF'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти аттестацию:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    else:
        bot.send_message(message.chat.id,'Для возврата в начало нажмите /home\n'
                                         '\n'
                                         'Если у Вас возникли вопросы, ответы на которые Вы не нашли в этом боте, обратитесь в Отдел обучения и развития\n'
                                         '\n'
                                         'Для продолжения работы переключите клавиатуру на кнопки и выберите один из разделов ниже:')





bot.infinity_polling()

