# Function Reference Guide - Курьер Сервис Экспресс Training Bot

## Table of Contents
1. [User Registration Functions](#user-registration-functions)
2. [Analytics and Monitoring](#analytics-and-monitoring)
3. [Message Broadcasting](#message-broadcasting)
4. [Content Delivery Functions](#content-delivery-functions)
5. [Bot Command Handlers](#bot-command-handlers)
6. [Menu and Navigation](#menu-and-navigation)
7. [Database Operations](#database-operations)
8. [Utility Functions](#utility-functions)
9. [Webhook Management](#webhook-management)

---

## User Registration Functions

### `process_name_step(message, chat_id)`

**Location**: `botr.py:32-42`

**Purpose**: Handles the first step of user registration by collecting the user's first name.

**Parameters**:
- `message` (telebot.types.Message): The Telegram message object containing user input
- `chat_id` (int): Telegram chat ID of the user

**Return Value**: None

**Side Effects**:
- Opens database connection
- Prompts user for surname
- Registers next step handler for surname input

**Usage Example**:
```python
# Called automatically during registration flow
bot.register_next_step_handler(message, process_name_step, chat_id)
```

**Error Handling**:
- Catches and prints any exceptions
- Ensures database connection is properly closed

**Database Impact**: None (read-only operation)

---

### `process_surname_step(message, chat_id, name)`

**Location**: `botr.py:45-56`

**Purpose**: Handles the second step of user registration by collecting the user's surname.

**Parameters**:
- `message` (telebot.types.Message): The Telegram message object containing surname
- `chat_id` (int): Telegram chat ID of the user
- `name` (str): User's first name from previous step

**Return Value**: None

**Side Effects**:
- Opens database connection
- Prompts user for city
- Registers next step handler for city input

**Usage Example**:
```python
# Called automatically during registration flow
bot.register_next_step_handler(message, process_surname_step, chat_id, name)
```

**Flow Continuation**: Leads to `process_city_step()`

---

### `process_city_step(message, chat_id, name, surname)`

**Location**: `botr.py:58-75`

**Purpose**: Completes user registration by collecting city information and saving to database.

**Parameters**:
- `message` (telebot.types.Message): The Telegram message object containing city
- `chat_id` (int): Telegram chat ID of the user
- `name` (str): User's first name
- `surname` (str): User's surname

**Return Value**: None

**Side Effects**:
- Inserts new user record into `users_info` table
- Sends welcome message with navigation instructions
- Completes registration process

**Database Operations**:
```sql
INSERT INTO users_info (user_id, name, surname, city) VALUES (?, ?, ?, ?)
```

**Usage Example**:
```python
# Called automatically during registration flow
bot.register_next_step_handler(message, process_city_step, chat_id, name, surname)
```

**Success Response**:
```
Спасибо, {name} {surname}!

Для начала обучения нажмите /home
```

---

## Analytics and Monitoring

### `analytics(func: callable)`

**Location**: `botr.py:78-137`

**Purpose**: Decorator function that wraps message handlers to provide user tracking, registration management, and message logging.

**Parameters**:
- `func` (callable): The message handler function to be wrapped

**Return Value**: Wrapped function with analytics capabilities

**Features**:
1. **User Registration Management**:
   - Checks if user exists in database
   - Handles `/start` command for new/existing users
   - Initiates registration flow for new users

2. **Message Logging**:
   - Records all messages to `messages` table
   - Includes timestamp, user info, and message content
   - Provides audit trail for user interactions

3. **Error Handling**:
   - Graceful exception handling for database operations
   - Ensures database connections are properly closed

**Usage Example**:
```python
@analytics
def my_handler(message):
    # Handler logic here
    bot.send_message(message.chat.id, "Response")
```

**Database Operations**:
```sql
-- User existence check
SELECT * FROM users_info WHERE user_id = ?

-- Message logging
INSERT INTO messages VALUES(?,?,?,?,?)
```

**Registration Flow for New Users**:
1. Detects `/start` command with no existing user record
2. Sends welcome message
3. Initiates name collection process
4. Registers `process_name_step` as next step handler

---

### `count_active_users(message)`

**Location**: `botr.py:205-259`

**Purpose**: Counts active users by testing message delivery and removes inactive users from database.

**Parameters**:
- `message` (telebot.types.Message): Admin message triggering the count

**Return Value**: None

**Process Flow**:
1. **Initialization**:
   - Sends progress notification to admin
   - Retrieves all user IDs from database
   - Initializes counters and tracking variables

2. **User Testing**:
   - Tests each user with `typing` action
   - Tracks successful/failed attempts
   - Updates progress every 50 users
   - Applies rate limiting (0.05s delay)

3. **Database Cleanup**:
   - Removes inactive users from database
   - Commits changes

4. **Reporting**:
   - Sends final statistics to admin

**Usage Example**:
```python
# Called from admin menu
count_active_users(admin_message)
```

**Database Operations**:
```sql
-- Get all users
SELECT user_id FROM users_info

-- Remove inactive users
DELETE FROM users_info WHERE user_id = ?
```

**Response Format**:
```
Подсчёт завершён!

Всего пользователей: {total_users}
Активных пользователей: {active_count}
Удалено неактивных: {len(inactive_users)}
/home
```

**Performance Considerations**:
- Rate limiting prevents API flooding
- Progress updates prevent timeout concerns
- Batch deletion for efficiency

---

## Message Broadcasting

### `send(message)`

**Location**: `botr.py:139-147`

**Purpose**: Initiates the message broadcasting process for administrators.

**Decorators**: `@bot.message_handler(commands=['send'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): Admin command message

**Return Value**: None

**Access Control**: Restricted to users in `admin_ids` list

**Process**:
1. Validates admin status
2. Requests broadcast content from admin
3. Registers `confirm_message_step` for content collection

**Usage Example**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки: текст или картинку с подписью.
```

**Authorization Check**:
```python
if message.chat.id in admin_ids:
    # Allow broadcast initiation
else:
    # Deny access
```

---

### `confirm_message_step(message)`

**Location**: `botr.py:149-164`

**Purpose**: Collects and stores broadcast content for confirmation.

**Parameters**:
- `message` (telebot.types.Message): Message containing broadcast content

**Return Value**: None

**Supported Content Types**:
1. **Text Messages**: Stored as `{'type': 'text', 'text': message.text}`
2. **Photo Messages**: Stored as `{'type': 'photo', 'file_id': file_id, 'caption': caption}`

**Storage**: Content stored in `pending_message[chat_id]` dictionary

**Process Flow**:
1. **Content Detection**:
   ```python
   if message.photo:
       # Handle photo with caption
       file_id = message.photo[-1].file_id
       caption = message.caption or ''
   else:
       # Handle text message
       text = message.text
   ```

2. **Confirmation Request**:
   - Stores content in pending dictionary
   - Requests admin confirmation
   - Provides cancellation option

**Next Steps**:
- Admin confirms with `/confirm_send`
- Admin cancels with `/cancel_send`

---

### `confirm_send(message)`

**Location**: `botr.py:166-194`

**Purpose**: Executes the broadcast to all registered users.

**Decorators**: `@bot.message_handler(commands=['confirm_send'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): Admin confirmation message

**Return Value**: None

**Process Flow**:
1. **Content Retrieval**:
   - Gets pending message from dictionary
   - Validates content exists

2. **User Collection**:
   - Queries database for all user IDs
   - Uses set to ensure uniqueness

3. **Message Delivery**:
   - Iterates through all users
   - Handles different content types
   - Implements error handling per user

4. **Completion Notification**:
   - Reports success to admin

**Database Query**:
```sql
SELECT user_id FROM users_info
```

**Delivery Logic**:
```python
for user_id in user_ids_to_send:
    try:
        if content['type'] == 'text':
            bot.send_message(user_id, content['text'])
        elif content['type'] == 'photo':
            bot.send_photo(user_id, content['file_id'], caption=content['caption'])
    except Exception as e:
        print(f"Ошибка при отправке пользователю {user_id}: {e}")
```

**Error Resilience**: Individual delivery failures don't stop the broadcast

---

### `cancel_send(message)`

**Location**: `botr.py:196-203`

**Purpose**: Cancels pending broadcast operation.

**Decorators**: `@bot.message_handler(commands=['cancel_send'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): Admin cancellation message

**Return Value**: None

**Access Control**: Admin-only operation

**Process**:
1. Validates admin status
2. Removes pending message from dictionary
3. Confirms cancellation

**Implementation**:
```python
if message.chat.id in admin_ids:
    pending_message.pop(chat_id, None)
    bot.send_message(chat_id, 'Рассылка отменена.')
```

---

## Content Delivery Functions

### `send_document_with_message(bot, chat_id, message_text, document_path, final_text=True, start_text=True)`

**Location**: `botr.py:345-352`

**Purpose**: Sends PDF documents to users with optional accompanying text messages.

**Parameters**:
- `bot` (telebot.TeleBot): Bot instance
- `chat_id` (int): Target user's chat ID
- `message_text` (str): Text message to send before document
- `document_path` (str): File path to PDF document
- `final_text` (bool, default=True): Whether to send navigation message
- `start_text` (bool, default=True): Whether to send initial message

**Return Value**: None

**Usage Examples**:

1. **Standard Usage**:
```python
send_document_with_message(
    bot, 
    message.chat.id,
    'Ознакомьтесь с инструкцией:',
    'Documents/instruction.pdf'
)
```

2. **Multiple Documents**:
```python
# First document
send_document_with_message(
    bot, chat_id,
    'Первый документ:',
    'Documents/doc1.pdf',
    final_text=False
)

# Last document
send_document_with_message(
    bot, chat_id,
    'Второй документ:',
    'Documents/doc2.pdf',
    start_text=False
)
```

**Flow Control**:
- `start_text=True`: Sends initial message
- `final_text=True`: Sends "Для возврата нажмите /home"

**File Handling**:
```python
with open(document_path, 'rb') as doc:
    bot.send_document(chat_id, doc)
```

---

### `send_video_link(bot, chat_id, title, video_url, back_button=False, final_text=True)`

**Location**: `botr.py:354-364`

**Purpose**: Sends video links with inline keyboard buttons for easy access.

**Parameters**:
- `bot` (telebot.TeleBot): Bot instance
- `chat_id` (int): Target user's chat ID
- `title` (str): Video title for display
- `video_url` (str): URL to video resource (typically Google Drive)
- `back_button` (bool, default=False): Whether to show back navigation
- `final_text` (bool, default=True): Whether to send home navigation

**Return Value**: None

**Button Creation**:
```python
markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton('Смотреть видео', url=video_url))
```

**Usage Examples**:

1. **Basic Video Link**:
```python
send_video_link(
    bot, 
    message.chat.id, 
    'Обучающее видео',
    'https://drive.google.com/file/d/video_id/view'
)
```

2. **With Back Navigation**:
```python
send_video_link(
    bot, 
    message.chat.id, 
    'Начало рабочего дня',
    'https://drive.google.com/file/d/video_id/view',
    back_button=True,
    final_text=False
)
```

**Message Format**:
```
<b>{title}</b>
Для просмотра видео перейдите по ссылке:
[Смотреть видео] (inline button)
```

**Navigation Options**:
- `back_button=True`: Adds "Для возврата нажмите /back"
- `final_text=True`: Adds "Для возврата нажмите /home"

---

## Bot Command Handlers

### `start(message)` (Home Menu)

**Location**: `botr.py:261-305`

**Purpose**: Displays the main navigation menu with all available training modules.

**Decorators**: `@bot.message_handler(commands=['home'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): User command message

**Return Value**: None

**Menu Structure**: Creates comprehensive keyboard with training categories:

1. **Row 1**: Для стажеров | Базовое обучение
2. **Row 2**: КАРГО | ПВЗ и почтоматы  
3. **Row 3**: СБП | Для наставника
4. **Row 4**: ВСД/ВПД/Просвещение | Самоинкассация
5. **Row 5**: ТЕСТЫ | Casarte
6. **Row 6**: Система трейсов | МФК ДЖАМИЛЬКО МОН
7. **Row 7**: Температурные грузы | Программа "Лучший сотрудник"
8. **Row 8**: Продвинутое обучение | Акт осмотра вложимого
9. **Row 9**: РЕСТОР | СТОПы
10. **Row 10**: Диспетчер | Обучение по ошибкам
11. **Row 11**: Правила парковки | Охрана труда
12. **Row 12**: Привязка грузовых мест при сборе. Сдача в ячейку
13. **Row 13**: 🔍 Поиск
14. **Admin Row**: Функции для администраторов (admin only)

**Keyboard Implementation**:
```python
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
# Button creation...
if message.from_user.id in admin_ids:
    markup.add(admin)
```

**Admin Features**: Additional admin menu shown only to authorized users

---

### `back(message)`

**Location**: `botr.py:325-343`

**Purpose**: Displays the basic training module menu.

**Decorators**: `@bot.message_handler(commands=['back'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): User command message

**Return Value**: None

**Menu Content**: Specific to basic training modules:
1. Программа Базового обучения
2. Начало рабочего дня
3. Расходные материалы
4. Накладная
5. Доставка лично в руки
6. Доставка с возвратом
7. Забор за наличные деньги
8. Международное отправление
9. Завершение рабочего дня

**Navigation**: Provides return path to main menu with /home

---

### `choose_command(message)`

**Location**: `botr.py:307-316`

**Purpose**: Displays administrative function menu for authorized users.

**Decorators**: `@bot.message_handler(func=lambda message: message.text == "Функции для администраторов")`

**Parameters**:
- `message` (telebot.types.Message): Admin menu selection message

**Return Value**: None

**Available Commands**:
1. **Отправить сообщение в бот**: Initiates broadcast functionality
2. **Посчитать активных пользователей**: Triggers user activity analysis

**Keyboard Type**: Inline keyboard for admin commands

**Implementation**:
```python
keyboard = types.InlineKeyboardMarkup()
command1_button = types.InlineKeyboardButton(text="Отправить сообщение в бот", callback_data="command1")
command2_button = types.InlineKeyboardButton(text="Посчитать активных пользователей", callback_data="command2")
```

---

### `callback_handler(call)`

**Location**: `botr.py:318-323`

**Purpose**: Handles inline keyboard callback queries from admin menu.

**Decorators**: `@bot.callback_query_handler(func=lambda call: True)`

**Parameters**:
- `call` (telebot.types.CallbackQuery): Callback query from inline button

**Return Value**: None

**Callback Routing**:
```python
if call.data == "command1":
    send(call.message)  # Initiate broadcast
elif call.data == "command2":
    count_active_users(call.message)  # Count users
```

**Integration**: Links inline buttons to corresponding functions

---

## Menu and Navigation

### `get_user_text(message)`

**Location**: `botr.py:366-1215`

**Purpose**: Main text message processor that handles all menu navigation and content requests.

**Decorators**: `@bot.message_handler(content_types=['text'])`, `@analytics`

**Parameters**:
- `message` (telebot.types.Message): User text message

**Return Value**: None

**Processing Logic**: Large conditional structure handling different text inputs:

#### Training Module Categories:

1. **Intern Materials** (`Для стажеров`):
   - Памятка стажера → PDF document

2. **Basic Training** (`Базовое обучение`):
   - 9 core modules with text/video options
   - Final test integration

3. **CARGO System** (`КАРГО`):
   - Video tutorials
   - Manuals and presentations
   - Trace schemes
   - Electronic receipts

4. **Postal Services** (`ПВЗ и почтоматы`):
   - Video tutorials
   - Halva postbox instructions
   - Testing links

5. **Fast Payment** (`СБП`):
   - Instructions and scripts
   - Video tutorials
   - Reminder documents

6. **Mentor Resources** (`Для наставника`):
   - Mentor-specific materials
   - Training presentations
   - Testing systems

#### Content Format Detection:

**Text/Video Options**:
```python
elif message.text == 'Начало рабочего дня':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    text = types.KeyboardButton('Начало рабочего дня (текст)')
    video = types.KeyboardButton('Начало рабочего дня (видео)')
    markup.add(text, video)
```

**Direct Document Delivery**:
```python
elif message.text == 'Памятка стажера':
    send_document_with_message(bot, message.chat.id, 
                               'Ознакомьтесь с памяткой для стажеров:', 
                               'Documents/Памятка для курьеров и водителей.pdf')
```

**Test Integration**:
```python
elif message.text == 'Тест по базовому обучению':
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Базовое тестирование', 
                                          url='https://short.startexam.com/B6HL1SHQ'))
```

#### Error Handling and Default Response:

**Unknown Input Handler**:
```python
else:
    bot.send_message(message.chat.id,'Для возврата в начало нажмите /home\n'
                                     '\n'
                                     'Если у Вас возникли вопросы...')
```

**Search Function Placeholder**:
```python
elif message.text == '🔍 Поиск':
    bot.send_message(349682954, f'Пользователь {message.from_user.first_name} {message.from_user.last_name} нажал кнопку Поиск')
    bot.send_message(message.chat.id, 'Данный раздел в разработке 🛠')
```

---

## Database Operations

### Database Initialization

**Location**: `botr.py:14-29`

**Purpose**: Sets up SQLite database tables for user and message storage.

**Tables Created**:

1. **users_info**:
   ```sql
   CREATE TABLE IF NOT EXISTS users_info(
       id INTEGER PRIMARY KEY,
       user_id INTEGER,
       name TEXT,
       surname TEXT,
       city TEXT
   )
   ```

2. **messages** (created in analytics decorator):
   ```sql
   CREATE TABLE IF NOT EXISTS messages(
       id INTEGER,
       name TEXT,
       surname TEXT,
       message TEXT,
       time_sent TEXT
   )
   ```

**Connection Management**:
```python
connect_users = sqlite3.connect('users.db')
cursor_users = connect_users.cursor()
# Operations...
connect_users.commit()
connect_users.close()
```

### Database Access Patterns

**User Lookup**:
```python
cursor.execute("SELECT * FROM users_info WHERE user_id = ?", (chat_id,))
existing_user = cursor.fetchone()
```

**Message Logging**:
```python
user = (message.chat.id, message.from_user.first_name, 
        message.from_user.last_name, message.text, message_date_formatted)
cursor_message.execute('INSERT INTO messages VALUES(?,?,?,?,?);', user)
```

**User Registration**:
```python
cursor.execute("INSERT INTO users_info (user_id, name, surname, city) VALUES (?, ?, ?, ?)",
               (chat_id, name, surname, city))
```

**Bulk Operations**:
```python
cursor_users.executemany(
    "DELETE FROM users_info WHERE user_id = ?",
    [(user_id,) for user_id in inactive_users]
)
```

---

## Utility Functions

### Global Variables and Configuration

**Location**: `botr.py:1-13`

**Bot Configuration**:
```python
telegram_bot_token = config('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(telegram_bot_token, parse_mode='html')
admin_ids = [349682954, 223737494]
pending_message = {}
```

**Environment Management**: Uses `python-decouple` for secure configuration

**Global State**: `pending_message` dictionary stores broadcast content

### Time and Date Handling

**Message Timestamp Creation**:
```python
message_date = datetime.fromtimestamp(message.date)
message_date_formatted = message_date.strftime("%H:%M:%S %d.%m.%Y")
```

**Format**: "HH:MM:SS DD.MM.YYYY"

### Error Recovery Patterns

**Database Error Handling**:
```python
try:
    # Database operations
except Exception as e:
    print(e)
finally:
    connect.close()
```

**Message Delivery Error Handling**:
```python
try:
    bot.send_message(user_id, content)
except Exception as e:
    print(f"Ошибка при отправке пользователю {user_id}: {e}")
    # Continue with next user
```

---

## Webhook Management

### Flask Application (`flask_app.py`)

**Webhook Endpoint**:
```python
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == WEBHOOK_SECRET_TOKEN:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid secret token', 403
```

**Security Features**:
- Token validation via HTTP headers
- Request data validation
- Error response for unauthorized access

### Webhook Configuration (`set_webhook.py`)

**Setup Process**:
```python
bot.remove_webhook()
response = bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN)
```

**Configuration Validation**:
```python
if response:
    print("Webhook установлен успешно")
else:
    print("Не удалось установить webhook")
```

---

## Function Performance Characteristics

### High-Frequency Functions

1. **`analytics()` decorator**: Called for every user interaction
2. **`get_user_text()`**: Processes all text messages
3. **Database connection operations**: Multiple per message

### Resource-Intensive Functions

1. **`count_active_users()`**: 
   - Network intensive (tests all users)
   - Database intensive (bulk deletions)
   - Time intensive (rate limiting)

2. **`confirm_send()`**:
   - Network intensive (sends to all users)
   - Database read intensive (user list retrieval)

### Optimization Considerations

**Database Connections**:
- New connection per operation (could be optimized with connection pooling)
- Proper cleanup with try/finally blocks

**Rate Limiting**:
- Built into user counting function
- Could be expanded to other bulk operations

**Memory Usage**:
- User lists loaded into memory for processing
- Pending messages stored in global dictionary

This function reference provides comprehensive documentation for all major functions in the Courier Service Express Training Bot, including their purposes, parameters, usage examples, and implementation details.