# Usage Examples and Integration Guide - Курьер Сервис Экспресс Training Bot

## Table of Contents
1. [Setup and Installation](#setup-and-installation)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Administrative Operations](#administrative-operations)
4. [Content Management](#content-management)
5. [Extending the Bot](#extending-the-bot)
6. [Integration Examples](#integration-examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Setup and Installation

### Initial Setup

1. **Clone or Download the Project**:
```bash
# Create project directory
mkdir courier-training-bot
cd courier-training-bot

# Copy project files
cp /path/to/botr.py .
cp /path/to/flask_app.py .
cp /path/to/set_webhook.py .
```

2. **Install Dependencies**:
```bash
# Install required packages
pip install pyTelegramBotAPI flask python-decouple

# Or create requirements.txt
echo "pyTelegramBotAPI==4.14.0" > requirements.txt
echo "Flask==2.3.0" >> requirements.txt
echo "python-decouple==3.8" >> requirements.txt
pip install -r requirements.txt
```

3. **Environment Configuration**:
```bash
# Create .env file
cat > .env << EOL
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
WEBHOOK_SECRET_TOKEN=your-secure-secret-token
WEBHOOK_PATH=/webhook
WEBHOOK_URL=https://your-domain.com/webhook
EOL
```

4. **Create Documents Directory**:
```bash
mkdir Documents
mkdir Documents/labor_protection
# Copy your training materials to Documents/
```

### Bot Setup

1. **Create Telegram Bot**:
```
1. Message @BotFather on Telegram
2. Send /newbot
3. Follow instructions to create bot
4. Copy the bot token to .env file
```

2. **Configure Webhook**:
```bash
# Set up webhook (run once)
python set_webhook.py
```

3. **Start the Application**:
```bash
# For development
python flask_app.py

# For production with gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 flask_app:app
```

---

## Basic Usage Examples

### User Registration Flow

**New User Interaction**:
```
User: /start
Bot: Добро пожаловать в команду компании Курьер Сервис Экспресс!

     Вы подписались на обучающий бот компании.

     Введите ваше имя:

User: Иван
Bot: Введите вашу фамилию:

User: Петров  
Bot: Введите ваш город:

User: Москва
Bot: Спасибо, Иван Петров!

     Для начала обучения нажмите /home
```

**Returning User**:
```
User: /start
Bot: Приветствуем, Иван Петров!

     Для начала обучения нажмите /home
```

### Navigation Examples

**Main Menu Access**:
```
User: /home
Bot: Выберите раздел:
     [Keyboard with training modules displayed]
```

**Training Module Selection**:
```
User: [Clicks "Базовое обучение"]
Bot: Выберите интересующий раздел

     Для возврата нажмите /home
     [Shows basic training submenu]
```

**Content Format Selection**:
```
User: [Clicks "Начало рабочего дня"]
Bot: Начало рабочего дня

     Выберите формат обучающего материала:

     Для возврата в начало нажмите /home
     Для возврата к списку разделов нажмите /back
     [Shows text/video format options]
```

### Content Access Examples

**PDF Document Access**:
```
User: [Clicks "Начало рабочего дня (текст)"]
Bot: Ознакомьтесь с порядком действий в начале рабочего дня:
     [Sends PDF document]
     Для возврата нажмите /home
```

**Video Content Access**:
```
User: [Clicks "Начало рабочего дня (видео)"]
Bot: Начало рабочего дня
     Для просмотра видео перейдите по ссылке:
     [Смотреть видео] (inline button)
     
     Для возврата к списку разделов нажмите /back
```

**Test Access**:
```
User: [Clicks "Тест по базовому обучению"]
Bot: Перейдите по ссылке, чтобы пройти тестирование:
     [Базовое тестирование] (inline button with external link)
     
     Для возврата в меню нажмите /home
```

---

## Administrative Operations

### Broadcast Message Examples

**Text Message Broadcast**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки: текст или картинку с подписью.

Admin: Важное объявление: завтра в 10:00 состоится общее собрание всех курьеров.
Bot: Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить.

Admin: /confirm_send
Bot: Рассылка начата. Это может занять некоторое время.
     [System processes all users]
     Рассылка завершена.
```

**Image Broadcast with Caption**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки: текст или картинку с подписью.

Admin: [Sends image with caption: "Новая схема маршрутов доставки"]
Bot: Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить.

Admin: /confirm_send
Bot: Рассылка начата. Это может занять некоторое время.
     Рассылка завершена.
```

**Cancel Broadcast**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки: текст или картинку с подписью.

Admin: Тестовое сообщение
Bot: Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить.

Admin: /cancel_send
Bot: Рассылка отменена.
```

### User Analytics Examples

**Active User Count**:
```
Admin: [From admin menu] → "Посчитать активных пользователей"
Bot: Подсчёт активных пользователей начат. Пожалуйста, подождите...
     Проверено 0 из 250 пользователей...
     Проверено 50 из 250 пользователей...
     Проверено 100 из 250 пользователей...
     [Process continues...]
     
     Подсчёт завершён!
     
     Всего пользователей: 250
     Активных пользователей: 238
     Удалено неактивных: 12
     /home
```

### Admin Menu Access

**Admin Function Access**:
```
Admin: [Clicks "Функции для администраторов"]
Bot: Выберите команду:
     
     Для возврата нажмите /home
     [Shows inline buttons:]
     [Отправить сообщение в бот]
     [Посчитать активных пользователей]
```

---

## Content Management

### Adding New Training Materials

**1. Adding a New PDF Document**:

```python
# In get_user_text() function, add new condition
elif message.text == 'Новый модуль обучения':
    send_document_with_message(bot, message.chat.id,
                               'Ознакомьтесь с новым материалом:',
                               'Documents/new_training_module.pdf')
```

**2. Adding a New Video Resource**:

```python
# Add video link handling
elif message.text == 'Новое обучающее видео':
    send_video_link(bot, message.chat.id, 'Новое обучающее видео',
                    'https://drive.google.com/file/d/NEW_VIDEO_ID/view')
```

**3. Adding a New Test Link**:

```python
# Add test integration
elif message.text == 'Новый тест':
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Новый тест', 
                                          url='https://testplatform.com/new-test'))
    bot.send_message(message.chat.id, 'Перейдите по ссылке для тестирования:', 
                     reply_markup=markup)
    bot.send_message(message.chat.id, 'Для возврата в меню нажмите /home')
```

### Creating New Training Categories

**1. Add Category to Main Menu**:

```python
# In start() function, add new button
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # ... existing buttons ...
    new_category = types.KeyboardButton('Новая категория обучения')
    markup.add(new_category)
    # ... rest of function
```

**2. Handle Category Selection**:

```python
# In get_user_text() function
elif message.text == 'Новая категория обучения':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    module1 = types.KeyboardButton('Модуль 1')
    module2 = types.KeyboardButton('Модуль 2')
    module3 = types.KeyboardButton('Модуль 3')
    markup.add(module1, module2, module3)
    bot.send_message(message.chat.id, 'Выберите модуль:', reply_markup=markup)
```

### Multi-Document Delivery Example

**Sending Multiple Related Documents**:

```python
elif message.text == 'Комплексный материал':
    # First document
    send_document_with_message(bot, message.chat.id,
                               'Часть 1 - Основы:',
                               'Documents/part1_basics.pdf',
                               final_text=False)
    
    # Second document  
    send_document_with_message(bot, message.chat.id,
                               'Часть 2 - Практика:',
                               'Documents/part2_practice.pdf',
                               final_text=False, start_text=False)
    
    # Final document with navigation
    send_document_with_message(bot, message.chat.id,
                               'Часть 3 - Контроль:',
                               'Documents/part3_control.pdf',
                               start_text=False)
```

---

## Extending the Bot

### Adding New User Fields

**1. Modify Database Schema**:

```python
# Add to database initialization
cursor_users.execute('''CREATE TABLE IF NOT EXISTS users_info(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    surname TEXT,
    city TEXT,
    department TEXT,  # New field
    position TEXT     # New field
)''')
```

**2. Update Registration Flow**:

```python
def process_city_step(message, chat_id, name, surname):
    try:
        city = message.text
        bot.send_message(chat_id, "Введите ваш отдел:")
        bot.register_next_step_handler(message, process_department_step, 
                                       chat_id, name, surname, city)
    except Exception as e:
        print(e)

def process_department_step(message, chat_id, name, surname, city):
    try:
        department = message.text
        bot.send_message(chat_id, "Введите вашу должность:")
        bot.register_next_step_handler(message, process_position_step, 
                                       chat_id, name, surname, city, department)
    except Exception as e:
        print(e)

def process_position_step(message, chat_id, name, surname, city, department):
    try:
        position = message.text
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("INSERT INTO users_info (user_id, name, surname, city, department, position) VALUES (?, ?, ?, ?, ?, ?)",
                       (chat_id, name, surname, city, department, position))
        connect.commit()
        bot.send_message(chat_id, f"Спасибо, {name} {surname}!\nОтдел: {department}\nДолжность: {position}\n\nДля начала обучения нажмите /home")
    except Exception as e:
        print(e)
    finally:
        connect.close()
```

### Adding Role-Based Content Access

**1. Define Role Checking Function**:

```python
def get_user_role(chat_id):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("SELECT position FROM users_info WHERE user_id = ?", (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(e)
        return None
    finally:
        connect.close()

def is_manager(chat_id):
    role = get_user_role(chat_id)
    return role in ['Менеджер', 'Руководитель', 'Диспетчер']

def is_courier(chat_id):
    role = get_user_role(chat_id)
    return role in ['Курьер', 'Водитель']
```

**2. Implement Role-Based Menu**:

```python
@bot.message_handler(commands=['home'])
@analytics
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Common sections for all users
    basic_training = types.KeyboardButton('Базовое обучение')
    markup.add(basic_training)
    
    # Role-specific sections
    if is_manager(message.chat.id):
        manager_section = types.KeyboardButton('Управленческие функции')
        markup.add(manager_section)
    
    if is_courier(message.chat.id):
        courier_section = types.KeyboardButton('Материалы для курьеров')
        markup.add(courier_section)
    
    # Admin functions
    if message.from_user.id in admin_ids:
        admin = types.KeyboardButton("Функции для администраторов")
        markup.add(admin)
    
    bot.send_message(message.chat.id, 'Выберите раздел:', reply_markup=markup)
```

### Adding Progress Tracking

**1. Create Progress Database**:

```python
# Add to initialization
cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    module_name TEXT,
    completed_date TEXT,
    score INTEGER
)''')
```

**2. Track Module Completion**:

```python
def mark_module_complete(user_id, module_name, score=None):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        completion_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO user_progress (user_id, module_name, completed_date, score) VALUES (?, ?, ?, ?)",
                       (user_id, module_name, completion_date, score))
        connect.commit()
    except Exception as e:
        print(e)
    finally:
        connect.close()

def get_user_progress(user_id):
    try:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("SELECT module_name, completed_date, score FROM user_progress WHERE user_id = ? ORDER BY completed_date DESC", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        connect.close()
```

**3. Progress Reporting**:

```python
elif message.text == 'Мой прогресс':
    progress = get_user_progress(message.chat.id)
    if progress:
        progress_text = "Ваш прогресс обучения:\n\n"
        for module, date, score in progress:
            score_text = f" (Оценка: {score})" if score else ""
            progress_text += f"✅ {module} - {date}{score_text}\n"
    else:
        progress_text = "У вас пока нет завершенных модулей обучения."
    
    bot.send_message(message.chat.id, progress_text)
```

---

## Integration Examples

### External API Integration

**1. Weather API for Delivery Conditions**:

```python
import requests

def get_weather(city):
    try:
        api_key = "YOUR_WEATHER_API_KEY"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"Погода в {city}: {temp}°C, {description}"
        else:
            return "Не удалось получить данные о погоде"
    except Exception as e:
        return "Ошибка получения погоды"

# Add to menu handler
elif message.text == 'Погода':
    user_info = get_user_info(message.chat.id)
    if user_info:
        city = user_info[4]  # Assuming city is 5th field
        weather = get_weather(city)
        bot.send_message(message.chat.id, weather)
```

**2. Integration with Company CRM**:

```python
def sync_user_with_crm(user_data):
    try:
        crm_api_url = "https://company-crm.com/api/employees"
        headers = {"Authorization": "Bearer YOUR_CRM_TOKEN"}
        
        payload = {
            "telegram_id": user_data[1],
            "name": user_data[2],
            "surname": user_data[3],
            "city": user_data[4]
        }
        
        response = requests.post(crm_api_url, json=payload, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"CRM sync error: {e}")
        return False

# Add to registration completion
def process_city_step(message, chat_id, name, surname):
    # ... existing code ...
    
    # Sync with CRM after successful registration
    user_data = (None, chat_id, name, surname, city)
    sync_user_with_crm(user_data)
```

### Database Backup Integration

**1. Automated Backup Function**:

```python
import shutil
from datetime import datetime

def backup_database():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_users_{timestamp}.db"
        shutil.copy2('users.db', f'backups/{backup_filename}')
        
        # Keep only last 7 backups
        import os
        import glob
        
        backup_files = glob.glob('backups/backup_users_*.db')
        backup_files.sort()
        
        if len(backup_files) > 7:
            for old_backup in backup_files[:-7]:
                os.remove(old_backup)
        
        return backup_filename
    except Exception as e:
        print(f"Backup error: {e}")
        return None

# Add to admin functions
elif message.text == 'Создать резервную копию':
    if message.chat.id in admin_ids:
        backup_file = backup_database()
        if backup_file:
            bot.send_message(message.chat.id, f"Резервная копия создана: {backup_file}")
        else:
            bot.send_message(message.chat.id, "Ошибка создания резервной копии")
```

---

## Troubleshooting

### Common Issues and Solutions

**1. Webhook Not Working**:

```bash
# Check webhook status
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Remove webhook and set again
python set_webhook.py

# Check server logs
tail -f /var/log/nginx/error.log  # for nginx
journalctl -u your-app-service -f  # for systemd
```

**2. Database Lock Issues**:

```python
# Add connection timeout and retry logic
def safe_db_operation(operation, *args, **kwargs):
    for attempt in range(3):
        try:
            connect = sqlite3.connect('users.db', timeout=10)
            cursor = connect.cursor()
            result = operation(cursor, *args, **kwargs)
            connect.commit()
            return result
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                time.sleep(0.1)
                continue
            else:
                raise e
        finally:
            try:
                connect.close()
            except:
                pass
```

**3. File Access Issues**:

```python
def safe_send_document(bot, chat_id, file_path, message_text):
    try:
        if not os.path.exists(file_path):
            bot.send_message(chat_id, "Документ временно недоступен. Обратитесь к администратору.")
            return False
        
        with open(file_path, 'rb') as doc:
            bot.send_document(chat_id, doc)
        return True
        
    except FileNotFoundError:
        bot.send_message(chat_id, "Файл не найден. Обратитесь к администратору.")
        return False
    except Exception as e:
        print(f"File access error: {e}")
        bot.send_message(chat_id, "Ошибка доступа к файлу. Попробуйте позже.")
        return False
```

### Monitoring and Logging

**1. Enhanced Logging**:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Add to analytics decorator
def analytics(func: callable):
    def analytics_wrapper(message):
        try:
            logger.info(f"User {message.chat.id} ({message.from_user.first_name}) sent: {message.text}")
            return func(message)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
    
    return analytics_wrapper
```

**2. Health Check Endpoint**:

```python
# Add to flask_app.py
@app.route('/health')
def health_check():
    try:
        # Check database
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("SELECT COUNT(*) FROM users_info")
        user_count = cursor.fetchone()[0]
        connect.close()
        
        # Check file system
        import os
        docs_exist = os.path.exists('Documents')
        
        status = {
            "status": "healthy",
            "users": user_count,
            "documents": docs_exist,
            "timestamp": datetime.now().isoformat()
        }
        
        return status, 200
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
```

---

## Best Practices

### Code Organization

**1. Separate Handlers into Modules**:

```python
# handlers/commands.py
def handle_start(message):
    # Start command logic
    pass

def handle_home(message):
    # Home command logic  
    pass

# handlers/content.py
def handle_basic_training(message):
    # Basic training logic
    pass

# handlers/admin.py
def handle_admin_functions(message):
    # Admin functionality
    pass

# main.py
from handlers import commands, content, admin

# Register handlers
bot.message_handler(commands=['start'])(commands.handle_start)
bot.message_handler(commands=['home'])(commands.handle_home)
```

**2. Configuration Management**:

```python
# config.py
import os
from decouple import config

class Config:
    TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
    WEBHOOK_SECRET_TOKEN = config('WEBHOOK_SECRET_TOKEN')
    WEBHOOK_PATH = config('WEBHOOK_PATH', default='/webhook')
    WEBHOOK_URL = config('WEBHOOK_URL')
    ADMIN_IDS = [int(id) for id in config('ADMIN_IDS', '').split(',') if id]
    DATABASE_PATH = config('DATABASE_PATH', default='users.db')
    DOCUMENTS_PATH = config('DOCUMENTS_PATH', default='Documents')

# Use in main code
from config import Config

bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN, parse_mode='html')
admin_ids = Config.ADMIN_IDS
```

### Performance Optimization

**1. Connection Pooling**:

```python
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()

# Usage
db = DatabaseManager('users.db')
users = db.execute_query("SELECT * FROM users_info WHERE user_id = ?", (chat_id,))
```

**2. Caching User Data**:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def get_user_info_cached(user_id, cache_time):
    # Cache based on time window (e.g., 5 minutes)
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM users_info WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    connect.close()
    return result

def get_user_info(user_id):
    # Cache for 5 minutes
    cache_key = int(time.time() // 300)
    return get_user_info_cached(user_id, cache_key)
```

### Security Best Practices

**1. Input Validation**:

```python
def validate_user_input(text, max_length=100):
    if not text or len(text.strip()) == 0:
        return False, "Поле не может быть пустым"
    
    if len(text) > max_length:
        return False, f"Максимальная длина: {max_length} символов"
    
    # Check for malicious content
    dangerous_chars = ['<', '>', '"', "'", '&']
    if any(char in text for char in dangerous_chars):
        return False, "Недопустимые символы в тексте"
    
    return True, text.strip()

# Use in registration
def process_name_step(message, chat_id):
    valid, result = validate_user_input(message.text, 50)
    if not valid:
        bot.send_message(chat_id, f"Ошибка: {result}")
        bot.send_message(chat_id, "Введите ваше имя:")
        bot.register_next_step_handler(message, process_name_step, chat_id)
        return
    
    name = result
    # Continue with valid input
```

**2. Rate Limiting**:

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < self.window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        return True

rate_limiter = RateLimiter()

def analytics(func: callable):
    def analytics_wrapper(message):
        if not rate_limiter.is_allowed(message.chat.id):
            bot.send_message(message.chat.id, "Слишком много запросов. Попробуйте позже.")
            return
        
        return func(message)
    return analytics_wrapper
```

This comprehensive usage guide provides practical examples for setting up, using, and extending the Courier Service Express Training Bot system.