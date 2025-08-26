import sqlite3
from decouple import config
import time
import datetime
from telebot.apihelper import ApiTelegramException
import json

from telebot import types
from webhook_app import bot

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

telegram_bot_token = config('TELEGRAM_BOT_TOKEN')
admin_ids = [349682954, 223737494]
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

# Создаем таблицу для очереди рассылки
cursor_users.execute('''
    CREATE TABLE IF NOT EXISTS broadcast_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        content TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_users INTEGER DEFAULT 0,
        sent_count INTEGER DEFAULT 0,
        failed_count INTEGER DEFAULT 0,
        blocked_count INTEGER DEFAULT 0
    )
''')

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
            message_date = datetime.datetime.fromtimestamp(message.date)
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


@bot.message_handler(commands=['send'])
@analytics
def send(message):
    if message.chat.id in admin_ids:
        bot.send_message(message.chat.id, 'Отправьте сообщение для рассылки: текст или картинку с подписью.')
        bot.register_next_step_handler(message, confirm_message_step)
    else:
        bot.send_message(message.chat.id, 'Вы не можете делать рассылку в этом боте')


def confirm_message_step(message):
    if message.photo:
        file_id = message.photo[-1].file_id
        caption = message.caption or ''
        pending_message[message.chat.id] = {'type': 'photo', 'file_id': file_id, 'caption': caption}
    else:
        text = message.text
        pending_message[message.chat.id] = {'type': 'text', 'text': text}

    bot.send_message(
        message.chat.id,
        'Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить.'
    )


@bot.message_handler(commands=['confirm_send'])
@analytics
def confirm_send(message):
    content = pending_message.get(message.chat.id)
    if not content:
        bot.send_message(message.chat.id, 'Отсутствует сообщение для рассылки.')
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users_info')
    total_users = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO broadcast_queue (admin_id, content, total_users)
        VALUES (?, ?, ?)
    ''', (message.chat.id, json.dumps(content), total_users))
    broadcast_id = cursor.lastrowid
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, f'Рассылка запущена для {total_users} пользователей.')

    # Запускаем рассылку
    run_broadcast(broadcast_id)


def run_broadcast(broadcast_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Получаем данные рассылки
    cursor.execute('SELECT admin_id, content FROM broadcast_queue WHERE id = ?', (broadcast_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    admin_id, content_json = row
    content = json.loads(content_json)

    # Обновляем статус
    cursor.execute('UPDATE broadcast_queue SET status = "processing" WHERE id = ?', (broadcast_id,))
    conn.commit()

    # Получаем пользователей
    cursor.execute('SELECT user_id FROM users_info')
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    success = 0
    failed = 0
    blocked = 0

    # Отправляем сообщение о начале
    progress_msg = bot.send_message(admin_id, f"Начинаю рассылку для {len(user_ids)} пользователей...")

    for i, user_id in enumerate(user_ids, 1):
        try:
            if content['type'] == 'text':
                bot.send_message(user_id, content['text'])
            elif content['type'] == 'photo':
                bot.send_photo(user_id, content['file_id'], caption=content['caption'])
            success += 1

        except ApiTelegramException as e:
            if 'bot was blocked by the user' in str(e):
                blocked += 1
                # Удаляем заблокировавшего пользователя
                conn = sqlite3.connect('users.db')
                cur = conn.cursor()
                cur.execute("DELETE FROM users_info WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
            failed += 1

        except Exception as e:
            failed += 1

        # Обновляем прогресс каждые 50 пользователей
        if i % 50 == 0:
            try:
                bot.edit_message_text(
                    f"Отправлено {i}/{len(user_ids)} ({(i / len(user_ids) * 100):.1f}%)\n"
                    f"Успешно: {success}\nОшибок: {failed}\nЗаблокировали: {blocked}",
                    admin_id, progress_msg.message_id
                )
            except:
                pass

            # Обновляем в базе
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE broadcast_queue 
                SET sent_count = ?, failed_count = ?, blocked_count = ?
                WHERE id = ?
            ''', (success, failed, blocked, broadcast_id))
            conn.commit()
            conn.close()

        # Задержка для избежания rate limit
        time.sleep(0.05)  # 50ms между сообщениями

    # Завершаем рассылку
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE broadcast_queue 
        SET status = "completed", sent_count = ?, failed_count = ?, blocked_count = ?
        WHERE id = ?
    ''', (success, failed, blocked, broadcast_id))
    conn.commit()
    conn.close()

    # Удаляем прогресс и отправляем итоги
    try:
        bot.delete_message(admin_id, progress_msg.message_id)
    except:
        pass

    bot.send_message(admin_id,
                     f'✅ Рассылка завершена.\n\n'
                     f'Всего пользователей: {len(user_ids)}\n'
                     f'Успешно: {success}\n'
                     f'Ошибок: {failed}\n'
                     f'Заблокировали бота: {blocked}\n'
                     f'/home'
                     )


@bot.message_handler(commands=['cancel_send'])
@analytics
def cancel_send(message):
    if message.chat.id in admin_ids:
        pending_message.pop(message.chat.id, None)
        bot.send_message(message.chat.id, 'Рассылка отменена.')
    else:
        bot.send_message(message.chat.id, 'Вы не можете отменить рассылку в этом боте.')


@bot.message_handler(commands=['broadcast_status'])
@analytics
def broadcast_status(message):
    if message.chat.id not in admin_ids:
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT status, total_users, sent_count, failed_count, blocked_count 
        FROM broadcast_queue 
        ORDER BY created_at DESC 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()

    if not row:
        bot.send_message(message.chat.id, 'Нет данных о рассылках.')
        return

    status, total, sent, failed, blocked = row

    if status == 'processing':
        bot.send_message(message.chat.id,
                         f'🔄 Рассылка в процессе:\n'
                         f'Отправлено: {sent}/{total}\n'
                         f'Ошибок: {failed}\n'
                         f'Заблокировали: {blocked}'
                         )
    elif status == 'completed':
        bot.send_message(message.chat.id,
                         f'✅ Последняя рассылка завершена:\n'
                         f'Всего: {total}\n'
                         f'Успешно: {sent}\n'
                         f'Ошибок: {failed}\n'
                         f'Заблокировали: {blocked}'
                         )
    else:
        bot.send_message(message.chat.id, f'Статус рассылки: {status}')
def count_active_users(message):
    bot.send_message(message.chat.id, 'Подсчёт активных пользователей начат. Пожалуйста, подождите...')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users_info")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    total_users = len(user_ids)
    active_count = 0
    inactive_users = []

    progress_msg = bot.send_message(message.chat.id, f"Проверено 0 из {total_users} пользователей...")

    for i, user_id in enumerate(user_ids, start=1):
        try:
            bot.send_chat_action(user_id, 'typing')
            active_count += 1
        except ApiTelegramException:
            inactive_users.append(user_id)
        except Exception:
            inactive_users.append(user_id)

        # Обновляем прогресс каждые 50
        if i % 50 == 0 or i == total_users:
            try:
                bot.edit_message_text(
                    chat_id=progress_msg.chat.id,
                    message_id=progress_msg.message_id,
                    text=f"Проверено {i} из {total_users} пользователей..."
                )
            except:
                pass

        time.sleep(0.03)  # Короткий таймаут, чтобы избежать Rate Limit

    # Удаляем неактивных
    if inactive_users:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM users_info WHERE user_id = ?", [(uid,) for uid in inactive_users])
        conn.commit()
        conn.close()

    bot.send_message(
        message.chat.id,
        f'Подсчёт завершён!\n\n'
        f'Всего пользователей: {total_users}\n'
        f'Активных: {active_count}\n'
        f'Удалено неактивных: {len(inactive_users)}\n/home'
    )

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
    new_traces = types.KeyboardButton('Система трейсов')
    self_collection = types.KeyboardButton('Самоинкассация')
    vsd = types.KeyboardButton("ВСД / ВПД / Просвещение")
    casarte = types.KeyboardButton("Casarte")
    jamilco = types.KeyboardButton("Джамилько")
    best = types.KeyboardButton('Программа "Лучший сотрудник"')
    temperature = types.KeyboardButton("Температурные грузы")
    damage_fix = types.KeyboardButton("Акт осмотра/Акт несоответствия")
    restor = types.KeyboardButton("РЕСТОР")
    stops = types.KeyboardButton('СТОПы')
    dispatch = types.KeyboardButton('Диспетчер')
    mistakes = types.KeyboardButton('Обучение по ошибкам')
    labor_protection = types.KeyboardButton('Охрана труда')
    parking = types.KeyboardButton('Правила парковки')
    binding = types.KeyboardButton('Привязка грузовых мест при сборе. Сдача в ячейку')
    avito = types.KeyboardButton('ПВЗ Авито')
    updateApp = types.KeyboardButton('Обновление МПК')
    wb = types.KeyboardButton('Доставка WB')
    admin = types.KeyboardButton("Функции для администраторов")
    markup.row(interns, study)
    markup.row(cargo, post_office)
    markup.row(fast_pay, mentors)
    markup.row(vsd, self_collection)
    markup.row(quiz, casarte)
    markup.row(new_traces, jamilco)
    markup.row(temperature, best)
    markup.row(damage_fix, restor)
    markup.row(dispatch, stops)
    markup.row(parking, mistakes)
    markup.row(avito, labor_protection)
    markup.row(wb)
    markup.row(binding, updateApp)
    if message.from_user.id in admin_ids:
        markup.add(admin)
    bot.send_message(message.chat.id,'Выберите раздел:', parse_mode='html', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Функции для администраторов")
def choose_command(message):
    keyboard = types.InlineKeyboardMarkup()
    command1_button = types.InlineKeyboardButton(text="Отправить сообщение в бот", callback_data="command1")
    command2_button = types.InlineKeyboardButton(text="Посчитать активных пользователей", callback_data="command2")

    keyboard.add(command1_button)
    keyboard.add(command2_button)

    bot.send_message(message.chat.id, "Выберите команду:\n\nДля возврата нажмите /home", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "command1":
        send(call.message)
    elif call.data == "command2":
        count_active_users(call.message)

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


def send_document_with_message(bot, chat_id, message_text, document_path, final_text=True, start_text=True ):
    if start_text:
        bot.send_message(chat_id, message_text)

    with open(document_path, 'rb') as doc:
        bot.send_document(chat_id, doc)
    if final_text:
        bot.send_message(chat_id, 'Для возврата нажмите /home', parse_mode='html')

def send_video_link(bot, chat_id, title, video_url, back_button=False, final_text=True):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Смотреть видео', url=video_url))

    bot.send_message(chat_id, f'<b>{title}</b>\nДля просмотра видео перейдите по ссылке:', reply_markup=markup, parse_mode='html')

    if final_text:
        bot.send_message(chat_id, 'Для возврата нажмите /home', parse_mode='html')

    if back_button:
        bot.send_message(chat_id, 'Для возврата нажмите /back')

@bot.message_handler(content_types=['text'])
@analytics
def get_user_text(message):
    if message.text == 'Для стажеров':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        part1 = types.KeyboardButton('Памятка стажера')
        markup.add(part1)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка стажера':
        send_document_with_message(bot, message.chat.id, 'Ознакомьтесь с памяткой для стажеров:', 'Documents/Памятка для курьеров и водителей.pdf')

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с программой базового обучения:',
                                   'Documents/study_program.pdf')

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком действий в начале рабочего дня:',
                                   'Documents/start_day.pdf')

    elif message.text == 'Начало рабочего дня (видео)':
        send_video_link(bot, message.chat.id, 'Начало рабочего дня',
                        'https://drive.google.com/file/d/10hm8iQ8OyytR-phHhQmwh25Lr2BUtDpR/view?usp=drive_link', True, False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы с расхоными материалами:',
                                   'Documents/expend_materials.pdf')

    elif message.text == 'Расходные материалы (видео)':
        send_video_link(bot, message.chat.id, 'Расходные материалы',
                        'https://drive.google.com/file/d/1c55YdtzeFyOfyQIQRVcqdFOTZYgnh7c6/view?usp=drive_link', True,
                        False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы с накладными:',
                                   'Documents/invoice.pdf')

    elif message.text == 'Накладная (видео)':
        send_video_link(bot, message.chat.id, 'Накладная',
                        'https://drive.google.com/file/d/1ddLAjq9t8mki7M-Dr33pv_Z4SkJ1H_Cq/view?usp=drive_link', True,
                        False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы при доставке лично в руки:',
                                   'Documents/deliv_person.pdf')

    elif message.text == 'Доставка лично в руки (видео)':
        send_video_link(bot, message.chat.id, 'Доставка лично в руки',
                        'https://drive.google.com/file/d/1dT0o7FTahiWOPKY3UmyBmHy4g-5xS7cE/view?usp=drive_link', True,
                        False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы при доставке с возвратом:',
                                   'Documents/return_shipping.pdf')

    elif message.text == 'Доставка с возвратом (видео)':
        send_video_link(bot, message.chat.id, 'Доставка с возвратом',
                        'https://drive.google.com/file/d/1VA0TZDJV9cfCTiR93vHnOQ9U2mix0QR-/view?usp=drive_link', True,
                        False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы при заборе за наличные деньги:',
                                   'Documents/reception_cash.pdf')

    elif message.text == 'Забор за наличные деньги (видео)':
        # send_video_link(bot, message.chat.id, 'Забор за наличные деньги',
        #                 'https://drive.google.com/file/d/1595XApsVCMP6i1VHLLgwERVzSHapgyzN/view?usp=drive_link', True,
        #                 False)
        bot.send_message(message.chat.id, 'Материал на доработке...\n'
                                          '\n'
                                          'Для возврата в начало нажмите /home\n'
                                          '\n'
                                          'Для возврата к списку разделов нажмите /back', parse_mode='html')

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы при международном отправлении:',
                                   'Documents/international_shipping.pdf')

    elif message.text == 'Международное отправление (видео)':
        send_video_link(bot, message.chat.id, 'Международное отправление',
                        'https://drive.google.com/file/d/1zsgs04VACCAGVrQcRK1j6BlNopSBdwOb/view?usp=drive_link', True,
                        False)

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком работы при завершении рабочего дня:',
                                   'Documents/end_day.pdf')

    elif message.text == 'Завершение рабочего дня (видео)':
        send_video_link(bot, message.chat.id, 'Завершение рабочего дня',
                        'https://drive.google.com/file/d/1dA_x8cU2_WElcrfJehb5uRgGJnsHo921/view?usp=drive_link', True,
                        False)

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
        send_video_link(bot, message.chat.id, 'Карго. Основные операции',
                        'https://drive.google.com/file/d/1Bf6vn0BgSEtYXoV-TKXQkeWAHiWWE23Y/view?usp=drive_link')

    elif message.text == 'Памятка Карго':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с инструкцией по работе с мобильным приложением Cargo5:',
                                   'Documents/cargo_manual.pdf')

    elif message.text == 'Схема трейсов':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь со схемой трейсов:',
                                   'Documents/traces_scheme.pdf')

    elif message.text == 'Презентация Карго':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией по работе в мобильном приложении:',
                                   'Documents/cargo-presentation.pdf')

    elif message.text == 'Электронные чеки':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с инструкцией по работе с интернет-магазинами (электронные чеки):',
                                   'Documents/e_chek.pdf')

    elif message.text == 'ПВЗ и почтоматы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Видео урок ПВЗ')
        chapter2 = types.KeyboardButton('Инструкция почтоматы Халва')
        chapter3 = types.KeyboardButton('Презентация почтоматы Халва')
        chapter4 = types.KeyboardButton('Тест Почтоматы и ПВЗ')
        markup.row(chapter1, chapter2)
        markup.row(chapter3, chapter4)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок ПВЗ':
        send_video_link(bot, message.chat.id, 'Видео урок ПВЗ',
                        'https://drive.google.com/file/d/1DpceGHOzdDcMh9f3-oUK5LW6GSzBx08z/view?usp=drive_link')

    elif message.text == 'Инструкция почтоматы Халва':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с инструкцией по закладке и изъятию отправлений в почтоматах Халва:',
                                   'Documents/halva.pdf')

    elif message.text == 'Презентация почтоматы Халва':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с инструкцией по закладке и изъятию отправлений в почтоматах Халва:',
                                   'Documents/halva_presentation.pdf')

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
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь порядком действий при облате через СБП:',
                                   'Documents/fast_pay_reminder.pdf')

    elif message.text == 'Инструкция по СБП':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь порядком действий при облате через СБП:',
                                   'Documents/fast_pay_manual.pdf')

    elif message.text == 'Скрипт для курьеров по СБП':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь со скриптом для курьеров при оплате через СБП:',
                                   'Documents/fast_pay_script.pdf')

    elif message.text == 'Видео урок СБП':
        send_video_link(bot, message.chat.id, 'Видео урок СБП',
                        'https://drive.google.com/file/d/10LCh0FJMRv8Axt4Lyc3UzIXxpDllxPQA/view?usp=drive_link')

    elif message.text == 'Для наставника':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Видео урок для наставников')
        chapter2 = types.KeyboardButton('Презентация для наставников')
        chapter3 = types.KeyboardButton('Памятка для наставников')
        chapter4 = types.KeyboardButton('Тест для наставников')
        markup.add(chapter1, chapter2, chapter3, chapter4)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Видео урок для наставников':
        send_video_link(bot, message.chat.id, 'Видео урок для наставников',
                        'https://drive.google.com/file/d/1MSDuS72YwKESSEI9FR08-HAGR5qCbMh-/view?usp=drive_link')

    elif message.text == 'Презентация для наставников':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией для наставников:',
                                   'Documents/mentors_presentation.pdf')

    elif message.text == 'Памятка для наставников':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с памяткой для наставников:',
                                   'Documents/mentors_reminder.pdf')

    elif message.text == 'Тест для наставников':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест для наставников', url='https://short.startexam.com/-491kseC'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Система трейсов':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter4 = types.KeyboardButton('Трейсы для диспетчера')
        chapter6 = types.KeyboardButton('Трейсы для логиста')
        chapter9 = types.KeyboardButton('Трейсы для курьеров')
        chapter10 = types.KeyboardButton('Практические кейсы')
        markup.add(chapter9, chapter4, chapter6, chapter10)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Трейсы для курьеров':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с новой системой трейсов:',
                                   'Documents/traces-courier.pdf', False)
        send_document_with_message(bot, message.chat.id,
                                   '',
                                   'Documents/traces_scheme.pdf', True, False)

    elif message.text == 'Трейсы для диспетчера':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с новой системой трейсов для диспетчеров:',
                                   'Documents/disp_traces_presentation.pdf')

    elif message.text == 'Трейсы для логиста':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с новой системой трейсов для логистов:',
                                   'Documents/traces_logist.pdf')

    elif message.text == 'Практические кейсы':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с практическими кейсами:',
                                   'Documents/traces_practic_cases.pdf')

    elif message.text == 'Самоинкассация':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Самоинкассация Москва и МО')
        chapter2 = types.KeyboardButton('Самоинкассация Регионы')
        markup.row(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Самоинкассация Москва и МО':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком действий при самоинкассации в Москве и МО:',
                                   'Documents/self_collection_region_msk_sber.pdf', False)
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком действий при самоинкассации в Москве и МО:',
                                   'Documents/self_collection_MKB.pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком действий при самоинкассации в Москве и МО:',
                                   'Documents/self_collection_eleksnet.pdf', True, False)

    elif message.text == 'Самоинкассация Регионы':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с порядком действий при самоинкассации в регионах:',
                                   'Documents/self_collection_region_sber.pdf', False)
        send_video_link(bot, message.chat.id, 'Самоинкассация Регионы',
                        'https://drive.google.com/file/d/1eUNFf6wzOsibqOHQFhpYj5OspkcgXPVy/view?usp=drive_link')


    elif message.text == 'Casarte':
        send_document_with_message(bot, message.chat.id,
                                   '',
                                   'Documents/casarte_presentation.pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   '',
                                   'Documents/casarte_reminder.pdf', True, False)

    elif message.text == 'Аттестация сотрудников':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкция по аттестации')
        chapter2 = types.KeyboardButton('Тест для ОСиД, АФС, Регионы')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Инструкция по аттестации':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с инструкцией по аттестации:',
                                   'Documents/attestation_instruction.pdf')

    elif message.text == 'Тест для ОСиД, АФС, Регионы':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Аттестация', url='https://short.startexam.com/-9RVOBVF'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти аттестацию:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'ТЕСТЫ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter4 = types.KeyboardButton('Тест по базовому обучению')
        chapter6 = types.KeyboardButton('Тест Почтоматы и ПВЗ')
        chapter7 = types.KeyboardButton('Тест Джамилько')
        chapter9 = types.KeyboardButton('Тест Температурные грузы')
        chapter13 = types.KeyboardButton('Тест ВСД / ВПД')
        chapter14 = types.KeyboardButton('Тест Акт осмотра/Акт несоответствия')
        chapter15 = types.KeyboardButton('Тест Просвещение')
        chapter16 = types.KeyboardButton('Тест Привязка грузовых мест')
        chapter17 = types.KeyboardButton('Тест Авито для диспетчера')
        chapter18 = types.KeyboardButton('Тест Авито для К/В/Э')
        chapter19 = types.KeyboardButton('Тест по МПК')
        chapter20 = types.KeyboardButton('Тест Доставка WB')
        markup.add(
            chapter4,
            chapter6,
            chapter7,
            chapter9,
            chapter13,
            chapter14,
            chapter15,
            chapter16,
            chapter17,
            chapter18,
            chapter19,
            chapter20,
        )
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Тест Почтоматы и ПВЗ':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Почтоматы и ПВЗ', url='https://short.startexam.com/Yny_U_4t'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Джамилько':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Джамилько', url='https://short.startexam.com/secVT8QM'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Температурные грузы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Тест Температурные грузы для курьеров')
        chapter2 = types.KeyboardButton('Тест Температурные грузы для диспетчеров')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Тест ВСД / ВПД':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест ВСД / ВПД', url='https://short.startexam.com/rFE5wIiY'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Просвещение':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Просвещение', url='https://short.startexam.com/zwSgs6RW'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Привязка грузовых мест':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Привязка грузовых мест', url='https://short.startexam.com/XzTylbnc'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Авито для диспетчера':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Авито для диспетчера', url='https://short.startexam.com/cVdg5zt2'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Авито для К/В/Э':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Авито для К/В/Э', url='https://short.startexam.com/yDSp-xOX'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест по МПК':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест по МПК', url='https://short.startexam.com/6y2pPKPj'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Тест Доставка WB':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Доставка WB', url='https://short.startexam.com/_3YcfcWV'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'ВСД / ВПД / Просвещение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Памятка по заполнению ВСД клиентов JTI, Нестле')
        chapter2 = types.KeyboardButton('Презентация ВСД / ВПД')
        chapter3 = types.KeyboardButton('Тест ВСД / ВПД')
        chapter4 = types.KeyboardButton('Просвещение (текст)')
        chapter5 = types.KeyboardButton('Просвещение (видео)')
        chapter6 = types.KeyboardButton('Тест Просвещение')
        markup.add(chapter1, chapter2, chapter3, chapter4, chapter5, chapter6)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка по заполнению ВСД клиентов JTI, Нестле':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с памяткой по заполнению ВСД клиентов JTI, Нестле:',
                                   'Documents/VSD_reminder.pdf')

    elif message.text == 'Презентация ВСД / ВПД':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией ВСД / ВПД:',
                                   'Documents/VSD_presentation.pdf')

    elif message.text == 'Просвещение (текст)':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией:',
                                   'Documents/Просвещение текст.pdf')

    elif message.text == 'Просвещение (видео)':
        send_video_link(bot, message.chat.id, 'Просвещение (видео)',
                        'https://drive.google.com/file/d/1xwI9PlqM-YebjaMjOBKdyu3CzsFeh2sm/view?usp=sharing')

    elif message.text == 'Джамилько':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Презентация Джамилько')
        chapter2 = types.KeyboardButton('Тест Джамилько')
        chapter3 = types.KeyboardButton('Видео Джамилько')
        markup.add(chapter1, chapter3, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Презентация Джамилько':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией Джамилько:',
                                   'Documents/jamilco_presentation.pdf')

    elif message.text == 'Видео Джамилько':
        send_video_link(bot, message.chat.id, 'Джамилько',
                        'https://drive.google.com/file/d/1lG3ykpqKgnjaM53ShjYHT20fQacuQm7N/view?usp=drive_link')

    elif message.text == 'Температурные грузы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Температурные грузы для курьеров')
        chapter2 = types.KeyboardButton('Температурные грузы для диспетчеров')
        chapter3 = types.KeyboardButton('Температурные грузы видео')
        markup.add(chapter1, chapter2, chapter3)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Температурные грузы для курьеров':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Температурные грузы Памятка для курьеров')
        chapter2 = types.KeyboardButton('Тест Температурные грузы для курьеров')
        markup.add(chapter1, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Температурные грузы Памятка для курьеров':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с памяткой по работе с температурными грузами:',
                                   'Documents/temper_courier_reminder.pdf')

    elif message.text == 'Тест Температурные грузы для курьеров':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Температурные грузы для курьеров', url='https://short.startexam.com/tIx4yKMY'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Температурные грузы для диспетчеров':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Температурные грузы Памятка для диспетчеров')
        chapter2 = types.KeyboardButton('Тест Температурные грузы для диспетчеров')
        chapter3 = types.KeyboardButton('Температурные грузы презентация')
        markup.add(chapter1, chapter3, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Температурные грузы Памятка для диспетчеров':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с памяткой по работе с температурными грузами:',
                                   'Documents/temper_dispatcher_reminder.pdf')

    elif message.text == 'Температурные грузы презентация':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией по работе с температурными грузами:',
                                   'Documents/temper_presentation.pdf')

    elif message.text == 'Тест Температурные грузы для диспетчеров':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Температурные грузы для диспетчеров', url='https://short.startexam.com/X5bWMGgg'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Температурные грузы видео':
        send_video_link(bot, message.chat.id, 'Температурные грузы',
                        'https://drive.google.com/file/d/1GEdgGAA9cK9FKqJzeGCta0CvmIPirtvT/view?usp=drive_link')

    elif message.text == 'Тест Акт осмотра/Акт несоответствия':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Тест Акт осмотра/Акт несоответствия', url='https://short.startexam.com/KZNee4D8'))
        bot.send_message(message.chat.id, 'Перейдите по ссылке, чтобы пройти тестирование:', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')

    elif message.text == 'Акт осмотра/Акт несоответствия':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Обучение Акт осмотра/Акт несоответствия')
        chapter2 = types.KeyboardButton('Тест Акт осмотра/Акт несоответствия')
        chapter3 = types.KeyboardButton('Форма Акт осмотра/Акт несоответствия')
        markup.add(chapter1, chapter3, chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Обучение Акт осмотра/Акт несоответствия':
        send_document_with_message(bot, message.chat.id,
                                   'Ознакомьтесь с презентацией:',
                                   'Documents/inspection_act_presentation.pdf')

    elif message.text == 'Форма Акт осмотра/Акт несоответствия':
        send_document_with_message(bot, message.chat.id, 'Ознакомьтесь с инструкциями:', 'Documents/inspection_act_regulation.pdf')

    elif message.text == 'РЕСТОР':
        send_document_with_message(bot, message.chat.id,
                                   'Инструкция по доставке техники:',
                                   'Documents/restor_instruction.pdf')

    elif message.text == 'СТОПы':
        send_document_with_message(bot, message.chat.id,
                                   'Памятка по СТОПам:',
                                   'Documents/stops_reminder.pdf')

    elif message.text == 'Диспетчер':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('КМОЗГ')
        markup.add(chapter1)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'КМОЗГ':
        send_video_link(bot, message.chat.id, 'КМОЗГ',
                        'https://drive.google.com/file/d/1vSZXKtBs9o6EYfQjtIzKFm47DQg9irig/view?usp=drive_link')

    elif message.text == 'Обучение по ошибкам':
        send_document_with_message(bot, message.chat.id,
                                   'Презентация по работе над ошибками:',
                                   'Documents/mistakes.pdf')

    elif message.text == 'Охрана труда':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Охрана труда. Основной раздел')
        chapter2 = types.KeyboardButton('Личная безопасность при проведении работ')
        chapter3 = types.KeyboardButton('Электробезопасность')
        chapter4 = types.KeyboardButton('Производственная санитария и личная гигиена')
        chapter5 = types.KeyboardButton('Средства индивидуальной защиты')
        chapter6 = types.KeyboardButton('Аварийные ситуации')
        chapter7 = types.KeyboardButton('Первая помощь пострадавшим')
        markup.row(chapter1)
        markup.add(chapter2, chapter3, chapter4, chapter5, chapter6, chapter7)
        bot.send_message(message.chat.id, 'Выберите интересующий раздел\n'
                                          '\n'
                                          'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Охрана труда. Основной раздел':
        send_document_with_message(bot, message.chat.id,
                                   'Охрана труда. Основной раздел:',
                                   'Documents/labor_protection/1. Памятка «Вводный инструктаж по охране труда».pdf')

    elif message.text == 'Личная безопасность при проведении работ':
        send_document_with_message(bot, message.chat.id,
                                   'Личная безопасность при проведении работ:',
                                   'Documents/labor_protection/1.1. Памятка «Меры безопасности при передвижении в помещениях».pdf', False)
        send_document_with_message(bot, message.chat.id,
                                   'Личная безопасность при проведении работ:',
                                   'Documents/labor_protection/1.2. Памятка «Выполнение погрузочно-разгрузочных работ».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Личная безопасность при проведении работ:',
                                   'Documents/labor_protection/1.3. Памятка «Использование погрузчика».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Личная безопасность при проведении работ:',
                                   'Documents/labor_protection/1.4. Памятка «Безопасное обращение с оборудованием и инструментом».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Личная безопасность при проведении работ:',
                                   'Documents/labor_protection/1.5. Памятка «Безопасное управление корпоративным транспортом».pdf', True, False)

    elif message.text == 'Электробезопасность':
        send_document_with_message(bot, message.chat.id,
                                   'Электробезопасность:',
                                   'Documents/labor_protection/2.1. Памятка «Требования электробезопасности».pdf')

    elif message.text == 'Производственная санитария и личная гигиена':
        send_document_with_message(bot, message.chat.id,
                                   'Производственная санитария и личная гигиена:',
                                   'Documents/labor_protection/3.1. Памятка «Производственная санитария и гигиена труда».pdf')

    elif message.text == 'Средства индивидуальной защиты':
        send_document_with_message(bot, message.chat.id,
                                   'Средства индивидуальной защиты:',
                                   'Documents/labor_protection/4.1. Памятка «Использование и применение СИЗ».pdf')

    elif message.text == 'Аварийные ситуации':
        send_document_with_message(bot, message.chat.id,
                                   'Аварийные ситуации:',
                                   'Documents/labor_protection/5.1. Памятка «Действия при аварии».pdf', False)
        send_document_with_message(bot, message.chat.id,
                                   'Аварийные ситуации:',
                                   'Documents/labor_protection/5.2. Памятка «Действия при пожаре».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Аварийные ситуации:',
                                   'Documents/labor_protection/5.3. Памятка «Действия в условиях теругроз».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Аварийные ситуации:',
                                   'Documents/labor_protection/5.4. Памятка «Действия при стихийных бедствиях».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Аварийные ситуации:',
                                   'Documents/labor_protection/5.5. Памятка «Действия при аварии на транспорте».pdf', True, False)

    elif message.text == 'Первая помощь пострадавшим':
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.1. Памятка «ПП при кровотечениях».pdf',False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.2. Памятка «ПП при проникающих ранениях».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.3. Памятка «ПП при вывихах и переломах».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.4. Памятка «ПП при ожогах и обморожениях».pdf', False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.5. Памятка «ПП при отравлениях».pdf',
                                   False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.6. Памятка «ПП при ОНСД».pdf',
                                   False, False)
        send_document_with_message(bot, message.chat.id,
                                   'Первая помощь пострадавшим:',
                                   'Documents/labor_protection/6.7. Памятка «Реанимация пострадавшего».pdf', True, False)

    elif message.text == 'Правила парковки':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Памятка по использованию «Паркоматики»')
        chapter2 = types.KeyboardButton('Видео «Паркоматика»')
        markup.row(chapter1)
        markup.row(chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Памятка по использованию «Паркоматики»':
        send_document_with_message(bot, message.chat.id,
                                   'Памятка по использованию «Паркоматики»:',
                                   'Documents/parking_reminder.pdf')

    elif message.text == 'Видео «Паркоматика»':
        send_video_link(bot, message.chat.id, 'Видео «Паркоматика»',
                        'https://clck.ru/3Kuu4v')

    elif message.text == 'Привязка грузовых мест при сборе. Сдача в ячейку':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкция привязка грузовых мест')
        chapter2 = types.KeyboardButton('Видео привязка грузовых мест')
        chapter3 = types.KeyboardButton('Тест Привязка грузовых мест')
        markup.row(chapter1)
        markup.row(chapter2)
        markup.row(chapter3)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Инструкция привязка грузовых мест':
        send_document_with_message(bot, message.chat.id,
                                   'Инструкция привязка грузовых мест:',
                                   'Documents/binding_instruction.pdf')

    elif message.text == 'Видео привязка грузовых мест':
        send_video_link(bot, message.chat.id, 'Видео привязка грузовых мест',
                        'https://clck.ru/3MHPAU')

    # раздел Обновление МПК
    elif message.text == 'Обновление МПК':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Инструкция Обновление МПК')
        chapter2 = types.KeyboardButton('Видео Обновление МПК')
        chapter3 = types.KeyboardButton('Тест по МПК')
        markup.row(chapter1)
        markup.row(chapter2)
        markup.row(chapter3)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Инструкция Обновление МПК':
        send_document_with_message(bot, message.chat.id,
                                   'Инструкция Обновление МПК:',
                                   'Documents/updateApp.pdf')

    elif message.text == 'Видео Обновление МПК':
        send_video_link(bot, message.chat.id, 'Видео Обновление МПК',
                        'https://clck.ru/3N2mJ2')

    elif message.text == 'ПВЗ Авито':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Авито для диспетчера (инструкция)')
        chapter2 = types.KeyboardButton('Авито для диспетчера (видео)')
        chapter3 = types.KeyboardButton('Тест Авито для диспетчера')
        chapter4 = types.KeyboardButton('Авито для К/В/Э (инструкция)')
        chapter5 = types.KeyboardButton('Авито для К/В/Э (видео)')
        chapter6 = types.KeyboardButton('Тест Авито для К/В/Э')
        markup.row(chapter1, chapter2)
        markup.row(chapter3, chapter4)
        markup.row(chapter5, chapter6)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Авито для диспетчера (инструкция)':
        send_document_with_message(bot, message.chat.id,
                                   'Авито для диспетчера (инструкция):',
                                   'Documents/avito_dispatcher_instruction.pdf')

    elif message.text == 'Авито для диспетчера (видео)':
        send_video_link(bot, message.chat.id, 'Видео Авито для диспетчера',
                        'https://clck.ru/3MUfYC')

    elif message.text == 'Авито для К/В/Э (инструкция)':
        send_document_with_message(bot, message.chat.id,
                                   'Авито для К/В/Э (инструкция):',
                                   'Documents/avito_courier_instruction.pdf')

    elif message.text == 'Авито для К/В/Э (видео)':
        send_video_link(bot, message.chat.id, 'Видео Авито для К/В/Э',
                        'https://clck.ru/3MUfpA')

    # раздел Доставка WB
    elif message.text == 'Доставка WB':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Доставка WB памятка')
        chapter2 = types.KeyboardButton('Доставка WB видео')
        chapter3 = types.KeyboardButton('Тест Доставка WB')
        markup.row(chapter1)
        markup.row(chapter2)
        markup.row(chapter3)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == 'Доставка WB памятка':
        send_document_with_message(bot, message.chat.id,
                                   'Доставка WB памятка:',
                                   'Documents/wb_reminder.pdf')

    elif message.text == 'Доставка WB видео':
        send_video_link(bot, message.chat.id, 'Доставка WB видео',
                        'https://clck.ru/3NrmW3')

    elif message.text == 'Программа "Лучший сотрудник"':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter5 = types.KeyboardButton('1-й квартал 2024')
        chapter6 = types.KeyboardButton('2-й квартал 2024')
        chapter7 = types.KeyboardButton('3-й квартал 2024')
        chapter8 = types.KeyboardButton('4-й квартал 2024')
        markup.add(chapter5, chapter6, chapter7, chapter8)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)

    elif message.text == '1-й квартал 2024':
        send_document_with_message(bot, message.chat.id,
                                   'Лучшие сотрудники 1-й квартал 2024:',
                                   'Documents/best_emp_all_1 ch_2024.pdf')
    elif message.text == '2-й квартал 2024':
        send_document_with_message(bot, message.chat.id,
                                   'Лучшие сотрудники 2-й квартал 2024:',
                                   'Documents/best_emp_all_2 ch_2024.pdf')
    elif message.text == '3-й квартал 2024':
        send_document_with_message(bot, message.chat.id,
                                   'Лучшие сотрудники 3-й квартал 2024:',
                                   'Documents/best_emp_all_3 ch_2024.pdf')

    elif message.text == '4-й квартал 2024':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        chapter1 = types.KeyboardButton('Лучшие сотрудники Департамента доставки 4-й квартал')
        chapter2 = types.KeyboardButton('Лучшие сотрудники Департамента регионального развития 4-й квартал')
        markup.row(chapter1)
        markup.row(chapter2)
        bot.send_message(message.chat.id, 'Для возврата нажмите /home', parse_mode='html', reply_markup=markup)


    elif message.text == 'Лучшие сотрудники Департамента доставки 4-й квартал':
        send_document_with_message(bot, message.chat.id,
                                   'Лучшие сотрудники Департамента доставки 4-й квартал:',
                                   'Documents/best_emp_mos_4 ch_2024.pdf')


    elif message.text == 'Лучшие сотрудники Департамента регионального развития 4-й квартал':
        send_document_with_message(bot, message.chat.id,
                                   'Лучшие сотрудники Департамента регионального развития 4-й квартал:',
                                   'Documents/best_emp_region_4 ch_2024.pdf')

    else:
        bot.send_message(message.chat.id,'Для возврата в начало нажмите /home\n'
                                         '\n'
                                         'Если у Вас возникли вопросы, ответы на которые Вы не нашли в этом боте, обратитесь в Отдел обучения и развития\n'
                                         '\n'
                                         'Для продолжения работы переключите клавиатуру на кнопки и выберите один из разделов ниже:')
