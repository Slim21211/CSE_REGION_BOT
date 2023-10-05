import telebot
import sqlite3
from decouple import config
from datetime import datetime

from telebot import types

telegram_bot_token = config('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(telegram_bot_token, parse_mode='html')
admin_ids = [349682954, 1793932185]
pending_message = {}

connect_users = sqlite3.connect('users.db')
cursor_users = connect_users.cursor()

# Создаем таблицу users_info, если она не существует
cursor_users.execute('''CREATE TABLE IF NOT EXISTS users_info(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    surname TEXT,
    city TEXT
)''')

# Фиксируем изменения в базе данных
connect_users.commit()

# Закрываем соединение с базой данных
connect_users.close()

def process_name_step(message, chat_id):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        name = message.text
        bot.send_message(chat_id, "Введите вашу фамилию:")
        bot.register_next_step_handler(message, process_surname_step, chat_id, name)
    except Exception as e:
        print(e)
    finally:
        connect.close()

def process_surname_step(message, chat_id, name):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        surname = message.text
        bot.send_message(chat_id, "Введите ваш город:")
        bot.register_next_step_handler(message, process_city_step, chat_id, name, surname)
    except Exception as e:
        print(e)
    finally:
        connect.close()

def process_city_step(message, chat_id, name, surname):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        city = message.text

        # Сохраняем информацию в базе данных
        cursor.execute("INSERT INTO users_info (user_id, name, surname, city) VALUES (?, ?, ?, ?)",
                        (chat_id, name, surname, city))
        connect.commit()

        bot.send_message(chat_id, f"Спасибо, {name} {surname}!\n"
                                  "\n"
                                  " Для начала обучения нажмите /home")
    except Exception as e:
        print(e)
    finally:
        connect.close()

def analytics(func: callable):
    def analytics_wrapper(message):
        try:
            chat_id = message.chat.id

            # Проверка существования записи в базе данных по chat_id
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM users_info WHERE user_id = ?", (chat_id,))
            existing_user = cursor.fetchone()

            if existing_user and message.text == '/start':
                # Запись уже существует
                id, user_id, name, surname, city = existing_user
                print(f"Пользователь с chat_id {chat_id} уже существует: {name} {surname}, город: {city}, id: {id}")
                bot.send_message(chat_id, f"Приветствуем, {name} {surname}!\n"
                                          "\n"
                                          " Для начала обучения нажмите /home")
            elif message.text == '/start':
                # Запрос данных у пользователя только при команде /start и отсутствии записи в базе
                bot.send_message(chat_id, "Добро пожаловать в команду компании <i>Курьер Сервис Экспресс!</i>\n"
                                          "\n"
                                          "Вы подписались на обучающий бот компании.\n"
                                          "\n"
                                          " Введите ваше имя:")
                bot.register_next_step_handler(message, process_name_step, chat_id)
        except Exception as e:
            print(e)
        finally:
            connect.close()

        try:
            # Создаем новый объект cursor для выполнения SQL-запросов
            message_date = datetime.fromtimestamp(message.date)
            message_date_formatted = message_date.strftime("%H:%M:%S %d.%m.%Y")
            connect_message = sqlite3.connect('message.db')
            cursor_message = connect_message.cursor()
            cursor_message.execute('''CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER,
                    name TEXT,
                    surname TEXT,
                    message TEXT,
                    time_sent TEXT
                )''')
            connect_message.commit()

            people_id = message.chat.id
            cursor_message.execute(f'SELECT id FROM messages WHERE id = {people_id}')
            user = (message.chat.id, message.from_user.first_name, message.from_user.last_name, message.text, message_date_formatted)
            print("Пользователь: ", user)
            cursor_message.execute('INSERT INTO messages VALUES(?,?,?,?,?);', user)
            connect_message.commit()
        except Exception as e:
            print(e)
        finally:
            connect_message.close()

        return func(message)

    return analytics_wrapper

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
    quiz = types.KeyboardButton('ТЕСТЫ')
    new_traces = types.KeyboardButton('НСТ')
    vympelcom = types.KeyboardButton('Вымпелком')
    netbynet = types.KeyboardButton('НэтБайНэт')
    trade_in = types.KeyboardButton('ТРЕЙД-ИН')
    self_collection = types.KeyboardButton('Самоинкассация')
    vsd = types.KeyboardButton("ВСД")
    casarte = types.KeyboardButton("Casarte")
    jamilco = types.KeyboardButton("МФК Джамилько/Монэкс трейдинг-им")
    best = types.KeyboardButton("Лучший из лучших")
    markup.row(interns, study)
    markup.row(cargo, post_office)
    markup.row(fast_pay, mentors)
    markup.row(vympelcom, new_traces)
    markup.row(trade_in, netbynet)
    markup.row(vsd, self_collection)
    markup.row(quiz, casarte)
    markup.row(jamilco, best)
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
@analytics
def send(message):
    if message.chat.id in admin_ids:
        bot.send_message(message.chat.id, 'Введите текст сообщения для рассылки:')
        bot.register_next_step_handler(message, confirm_message_step)
    else:
        bot.send_message(message.chat.id, 'Вы не можете делать рассылку в этом боте')

def confirm_message_step(message):
    text_to_send = message.text
    pending_message[message.chat.id] = text_to_send
    bot.send_message(message.chat.id, 'Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить рассылку.')

@bot.message_handler(commands=['confirm_send'])
@analytics
def confirm_send(message):
    text_to_send = pending_message.get(message.chat.id)
    if text_to_send:
        bot.send_message(message.chat.id, 'Рассылка начата. Это может занять некоторое время.')
        user_ids_to_send = set()  # Используем множество для хранения уникальных user_id

        # Считываем user_id из вашей базы данных users.db
        connect_users = sqlite3.connect('users.db')
        cursor_users = connect_users.cursor()
        cursor_users.execute("SELECT user_id FROM users_info")
        for row in cursor_users.fetchall():
            user_id = row[0]
            user_ids_to_send.add(user_id)

        # Отправляем сообщение каждому уникальному user_id
        for user_id in user_ids_to_send:
            try:
                bot.send_message(user_id, text_to_send)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

        connect_users.close()
        bot.send_message(message.chat.id, 'Рассылка завершена.')

    else:
        bot.send_message(message.chat.id, 'Отсутствует текст сообщения для рассылки.')

@bot.message_handler(commands=['cancel_send'])
@analytics
def cancel_send(message):
    if message.chat.id in admin_ids:
        pending_message.pop(message.chat.id, None)
        bot.send_message(message.chat.id, 'Рассылка отменена.')
    else:
        bot.send_message(message.chat.id, 'Вы не можете отменить рассылку в этом боте.')

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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/10hm8iQ8OyytR-phHhQmwh25Lr2BUtDpR/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Начало рабочего дня</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1c55YdtzeFyOfyQIQRVcqdFOTZYgnh7c6/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Расходные материалы</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1ddLAjq9t8mki7M-Dr33pv_Z4SkJ1H_Cq/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Накладная</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1dT0o7FTahiWOPKY3UmyBmHy4g-5xS7cE/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Доставка лично в руки</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1VA0TZDJV9cfCTiR93vHnOQ9U2mix0QR-/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Доставка с возвратом</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1595XApsVCMP6i1VHLLgwERVzSHapgyzN/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Забор за наличные деньги</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1zsgs04VACCAGVrQcRK1j6BlNopSBdwOb/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Международное отправление</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1dA_x8cU2_WElcrfJehb5uRgGJnsHo921/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Завершение рабочего дня</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://drive.google.com/file/d/1Bf6vn0BgSEtYXoV-TKXQkeWAHiWWE23Y/view?usp=drive_link'))
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1DpceGHOzdDcMh9f3-oUK5LW6GSzBx08z/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Видео урок ПВЗ</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Инструкция по работе с ПВЗ и почтоматами':
        bot.send_message(message.chat.id, 'Ознакомьтесь с инструкцией по закладке и изъятию отправлений в почтоматах Халва:')
        doc = open('Documents/halva.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html')

    elif message.text == 'СБП':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        reminder = types.KeyboardButton('Памятка по СБП')
        manual = types.KeyboardButton('Инструкция по СБП')
        script = types.KeyboardButton('Скрипт для курьеров по СБП')
        video = types.KeyboardButton('Видео урок СБП')
        markup.row(reminder, manual)
        markup.row(script, video)
        bot.send_message(message.chat.id, '<b><i>СБП</i></b>\n'
                                          '\n'
                                          'Выберите раздел:\n'
                                          '\n'
                                          'Для возврата назад нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка по СБП':
        doc = open('Documents/fast_pay_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Инструкция по СБП':
        doc = open('Documents/fast_pay_manual.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Скрипт для курьеров по СБП':
        doc = open('Documents/fast_pay_script.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Видео урок СБП':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/10LCh0FJMRv8Axt4Lyc3UzIXxpDllxPQA/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Видео урок СБП</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Для наставника':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Видео урок для наставников')
        chapter2 = types.KeyboardButton('Презентация для наставников')
        chapter3 = types.KeyboardButton('Памятка для наставников')
        chapter4 = types.KeyboardButton('Тест для наставников')
        markup.add(chapter1, chapter2, chapter3, chapter4)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок для наставников':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1MSDuS72YwKESSEI9FR08-HAGR5qCbMh-/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Видео урок для наставников</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Презентация для наставников':
        doc = open('Documents/mentors_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Памятка для наставников':
        doc = open('Documents/mentors_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Тест для наставников':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест для наставников', url='https://short.startexam.com/-491kseC'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

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
        chapter9 = types.KeyboardButton('НСТ курьеры')
        markup.add(chapter1, chapter2, chapter3, chapter9, chapter4, chapter5, chapter6, chapter7, chapter8)
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

    elif message.text == 'НСТ курьеры':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1qZLvNtgqUH1f8zUZEXb0hAexkvdPxYKP/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ для курьеров доставка</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1XhhmxLEwcDbjwSLs-93G5buUKOEkSs1v/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ для курьеров забор</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'НСТ диспетчеры':
        doc = open('Documents/disp_traces_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1Vfml-Iq-vE77Eru7ELcV8nGTI_twHWLf/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ для диспетчеров доставка</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1bEnEYRC_ADji69e6pSq-oUA_i7LPlWef/view?usp=drive_link'))
        bot.send_message(message.chat.id,
                         '<b>НСТ для диспетчеров забор</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/16qLMw3R54YOCVIvMTavlRdwvurQm5hz3/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ склад</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1-61HToxFxRZmtoXdUJd13WWhLHaViZ_x/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ склад</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1Tx3_Oqdtqlewk9dOz8YbXh7DGZyhd30S/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>НСТ склад</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Вымпелком':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкции Вымпелком')
        chapter2 = types.KeyboardButton('Видео инструкции Вымпелком')
        chapter3 = types.KeyboardButton('Презентация Вымпелком')
        chapter4 = types.KeyboardButton('ЭДО')
        markup.add(chapter1, chapter2, chapter3, chapter4)
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
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://drive.google.com/file/d/1ztSN0jADCDaoinVBHURomJIZU8GvAo-X/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Возврат АБО для смартфона</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://drive.google.com/file/d/1W6eXG-zhPcgUXO_y3MZAV7R30I9wLDig/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Доставка АБО</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1FENhWA1edTOhGiUEOzD7mpXoMQ3lAQzf/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Доставка СИМ</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1JLHyIaXicRpyolqdIRtQHsnulcjorUn_/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Замена АБО</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Презентация Вымпелком':
        doc = open('Documents/vympel_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'ЭДО':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Презентация ЭДО - Вымпелком')
        chapter2 = types.KeyboardButton('Видеоурок ЭДО - Вымпелком')
        chapter3 = types.KeyboardButton('Тест ЭДО - Вымпелком')
        markup.add(chapter1, chapter2, chapter3)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Презентация ЭДО - Вымпелком':
        doc = open('Documents/vympel_presentation_EDM.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Видеоурок ЭДО - Вымпелком':
        # video = open('', 'rb')
        # bot.send_document(message.chat.id, video)
        bot.send_message(message.chat.id, 'В этом разделе пока нет обучающих материалов, но они очень скоро появятся)\n'
                                          '\n'
                                          'Для возврата нажмите /home')

    elif message.text == 'Тест ЭДО - Вымпелком':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест ЭДО - Вымпелком', url='https://short.startexam.com/xICbjKBm'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тест:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'НэтБайНэт':
        doc1 = open('Documents/netbynet.pdf', 'rb')
        bot.send_document(message.chat.id, doc1)
        doc2 = open('Documents/netbynet_instruction.pdf', 'rb')
        bot.send_document(message.chat.id, doc2)

    elif message.text == 'ТРЕЙД-ИН':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Памятка ТРЕЙД_ИН')
        chapter2 = types.KeyboardButton('Презентация ТРЕЙД-ИН')
        chapter3 = types.KeyboardButton('Видео процесса проверки Б/У устройства')
        chapter4 = types.KeyboardButton('Тест по ТРЕЙД-ИН')
        markup.add(chapter1, chapter2)
        markup.add(chapter3, chapter4)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка ТРЕЙД_ИН':
        doc = open('Documents/instruction_trade-in.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Презентация ТРЕЙД-ИН':
        doc = open('Documents/presentation_trade-in.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Видео процесса проверки Б/У устройства':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://drive.google.com/file/d/1QMmoHXaZ1S_t8x_9JhWUDttDjiDNDaeY/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Проверка Б/У устройства</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Тест по ТРЕЙД-ИН':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест по ТРЕЙД-ИН', url='https://short.startexam.com/_9kcW1mf'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тест:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Самоинкассация':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Самоинкассация Москва и МО')
        chapter2 = types.KeyboardButton('Самоинкассация Регионы')
        markup.row(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Самоинкассация Москва и МО':
        doc = open('Documents/self_collection_region_msk_sber.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        doc = open('Documents/self_collection_MKB.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        doc = open('Documents/self_collection_eleksnet.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Самоинкассация Регионы':
        doc = open('Documents/self_collection_region_sber.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео',
                                              url='https://drive.google.com/file/d/1eUNFf6wzOsibqOHQFhpYj5OspkcgXPVy/view?usp=drive_link'))
        bot.send_message(message.chat.id, '<b>Самоинкассация Регионы</b>\nДля просмотра видео перейдите по ссылке:',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Casarte':
        doc = open('Documents/casarte_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        doc = open('Documents/casarte_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

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

    elif message.text == 'ТЕСТЫ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Тест Вымпелком')
        chapter2 = types.KeyboardButton('Тест Нетбайнет (Мегафон)')
        chapter3 = types.KeyboardButton('Тест ТРЕЙД-ИН')
        chapter4 = types.KeyboardButton('Аттестация сотрудников')
        chapter5 = types.KeyboardButton('Тест ЭДО - Вымпелком')
        markup.add(chapter1, chapter5, chapter2, chapter3, chapter4)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Тест Вымпелком':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Вымпелком', url='https://short.startexam.com/VmwNCt28'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Нетбайнет (Мегафон)':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Нетбайнет (Мегафон)', url='https://short.startexam.com/Yf4UbFTD'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест ТРЕЙД-ИН':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест ТРЕЙД-ИН', url='https://short.startexam.com/_9kcW1mf'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'ВСД':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Памятка по заполнению ВСД клиентов JTI, Нестле')
        chapter2 = types.KeyboardButton('Видео по заполнению ВСД клиентов JTI, Нестле')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка по заполнению ВСД клиентов JTI, Нестле':
        doc = open('Documents/VSD_reminder.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Видео по заполнению ВСД клиентов JTI, Нестле':
        # video = open('', 'rb')
        # bot.send_document(message.chat.id, video)
        bot.send_message(message.chat.id, 'В этом разделе пока нет обучающих материалов, но они очень скоро появятся)\n'
                                          '\n'
                                          'Для возврата нажмите /home')

    elif message.text == 'МФК Джамилько/Монэкс трейдинг-им':
        doc = open('Documents/jamilco_presentation.pdf', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == 'Лучший из лучших':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('1-й квартал 2023')
        chapter2 = types.KeyboardButton('2-й квартал 2023')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == '1-й квартал 2023':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://disk.yandex.ru/i/U0PNeSGWqubTpA'))
        bot.send_message(message.chat.id, '<b>Лучший из лучших за 1-й квартал 2023 года</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    elif message.text == '2-й квартал 2023':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Смотреть видео', url='https://disk.yandex.ru/i/XE3bkwNu4AhmEQ'))
        bot.send_message(message.chat.id, '<b>Лучший из лучших за 2-й квартал 2023 года</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home')

    else:
        bot.send_message(message.chat.id,'Для возврата в начало нажмите /home\n'
                                         '\n'
                                         'Если у Вас возникли вопросы, ответы на которые Вы не нашли в этом боте, обратитесь в Отдел обучения и развития\n'
                                         '\n'
                                         'Для продолжения работы переключите клавиатуру на кнопки и выберите один из разделов ниже:')


bot.infinity_polling()

