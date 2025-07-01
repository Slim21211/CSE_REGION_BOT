# API Documentation - Курьер Сервис Экспресс Training Bot

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Core Components](#core-components)
5. [Bot Commands](#bot-commands)
6. [Message Handlers](#message-handlers)
7. [Database Management](#database-management)
8. [Utility Functions](#utility-functions)
9. [Webhook Setup](#webhook-setup)
10. [Flask Application](#flask-application)
11. [Usage Examples](#usage-examples)
12. [Error Handling](#error-handling)
13. [Deployment](#deployment)

## Overview

This application is a comprehensive Telegram bot designed for employee training at "Курьер Сервис Экспресс" (Courier Service Express). The bot provides:

- **Training Materials**: Access to documents, videos, and presentations
- **User Management**: Registration and analytics tracking
- **Administrative Functions**: Message broadcasting and user statistics
- **Testing System**: Links to external testing platforms
- **Content Organization**: Hierarchical menu system for different departments

### Key Features
- Multi-format learning materials (PDF, video, presentations)
- User registration and profile management
- Admin broadcasting system
- Analytics and user tracking
- Department-specific training modules

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram API  │    │   Flask App     │    │   SQLite DB     │
│                 │◄──►│                 │◄──►│                 │
│   - Bot Token   │    │   - Webhook     │    │   - Users       │
│   - Messages    │    │   - Processing  │    │   - Messages    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Documents     │
                       │                 │
                       │   - PDFs        │
                       │   - Videos      │
                       │   - Tests       │
                       └─────────────────┘
```

## Configuration

### Environment Variables

The application uses the following environment variables (managed via `python-decouple`):

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | Yes | `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz` |
| `WEBHOOK_SECRET_TOKEN` | Security token for webhook validation | Yes | `your-secret-token` |
| `WEBHOOK_PATH` | Path for webhook endpoint | Yes | `/webhook` |
| `WEBHOOK_URL` | Full webhook URL | Yes | `https://your-domain.com/webhook` |

### Setup Example

```bash
# .env file
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
WEBHOOK_SECRET_TOKEN=your-secret-token
WEBHOOK_PATH=/webhook
WEBHOOK_URL=https://your-domain.com/webhook
```

## Core Components

### Bot Instance

```python
# botr.py
telegram_bot_token = config('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(telegram_bot_token, parse_mode='html')
```

**Description**: Main bot instance with HTML parsing enabled for rich text formatting.

### Admin Configuration

```python
admin_ids = [349682954, 223737494]
```

**Description**: List of Telegram user IDs with administrative privileges.

**Admin Capabilities**:
- Send broadcast messages
- Access user statistics
- Count active users
- Administrative menu access

## Database Management

### Database Schema

#### Users Table (`users_info`)
```sql
CREATE TABLE IF NOT EXISTS users_info(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    surname TEXT,
    city TEXT
)
```

#### Messages Table (`messages`)
```sql
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER,
    name TEXT,
    surname TEXT,
    message TEXT,
    time_sent TEXT
)
```

### Database Operations

#### User Registration Functions

##### `process_name_step(message, chat_id)`
Handles the first step of user registration (name input).

**Parameters**:
- `message`: Telegram message object
- `chat_id`: User's chat ID

**Usage**:
```python
bot.register_next_step_handler(message, process_name_step, chat_id)
```

##### `process_surname_step(message, chat_id, name)`
Handles surname input during registration.

**Parameters**:
- `message`: Telegram message object
- `chat_id`: User's chat ID
- `name`: User's first name (from previous step)

##### `process_city_step(message, chat_id, name, surname)`
Completes user registration with city information.

**Parameters**:
- `message`: Telegram message object
- `chat_id`: User's chat ID
- `name`: User's first name
- `surname`: User's last name

**Database Operations**:
```python
cursor.execute("INSERT INTO users_info (user_id, name, surname, city) VALUES (?, ?, ?, ?)",
               (chat_id, name, surname, city))
```

## Bot Commands

### Core Navigation Commands

#### `/start`
**Function**: Initial bot interaction and user registration
**Access Level**: All users
**Behavior**:
- New users: Initiates registration process
- Existing users: Welcome message with navigation to `/home`

**Example Response**:
```
Добро пожаловать в команду компании Курьер Сервис Экспресс!

Вы подписались на обучающий бот компании.

Введите ваше имя:
```

#### `/home`
**Function**: Main menu navigation
**Access Level**: All users
**Handler**: `start(message)`

**Menu Structure**:
```
┌─────────────────────────────────────┐
│  Для стажеров  │  Базовое обучение  │
├─────────────────────────────────────┤
│     КАРГО      │   ПВЗ и почтоматы  │
├─────────────────────────────────────┤
│      СБП       │  Для наставника    │
├─────────────────────────────────────┤
│ ВСД/ВПД/Просв  │  Самоинкассация    │
├─────────────────────────────────────┤
│     ТЕСТЫ      │     Casarte        │
├─────────────────────────────────────┤
│ Система трейсов│  МФК ДЖАМИЛЬКО     │
└─────────────────────────────────────┘
```

#### `/back`
**Function**: Navigate to basic training menu
**Access Level**: All users
**Handler**: `back(message)`

### Administrative Commands

#### `/send`
**Function**: Initiate message broadcast
**Access Level**: Admin only
**Handler**: `send(message)`

**Usage Flow**:
1. Admin sends `/send`
2. Bot requests message content
3. Admin provides text or image with caption
4. Bot asks for confirmation with `/confirm_send`

**Example**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки: текст или картинку с подписью.
Admin: [sends message]
Bot: Подтвердите рассылку командой /confirm_send, или отправьте /cancel_send, чтобы отменить.
```

#### `/confirm_send`
**Function**: Execute message broadcast
**Access Level**: Admin only
**Handler**: `confirm_send(message)`

**Process**:
1. Retrieves all user IDs from database
2. Sends message to each user
3. Handles delivery errors gracefully
4. Reports completion status

#### `/cancel_send`
**Function**: Cancel pending broadcast
**Access Level**: Admin only
**Handler**: `cancel_send(message)`

## Message Handlers

### Analytics Decorator

#### `analytics(func: callable)`
**Purpose**: Tracks all user interactions and manages user registration

**Features**:
- **User Registration**: Handles `/start` command flow
- **Message Logging**: Records all messages to database
- **Timestamp Tracking**: Logs interaction times
- **Error Handling**: Graceful error management

**Usage**:
```python
@analytics
def some_handler(message):
    # Handler logic here
    pass
```

**Database Operations**:
```python
# User check
cursor.execute("SELECT * FROM users_info WHERE user_id = ?", (chat_id,))

# Message logging
cursor.execute('INSERT INTO messages VALUES(?,?,?,?,?);', 
               (user_id, first_name, last_name, message_text, timestamp))
```

### Text Message Handler

#### `get_user_text(message)`
**Purpose**: Main text message processor
**Decorator**: `@analytics`
**Content Types**: `['text']`

**Handles**:
- Menu navigation
- Training module selection
- Document requests
- Video link generation
- Test redirections

## Training Modules

### Basic Training (`Базовое обучение`)

**Available Modules**:
1. **Training Program** (`Программа Базового обучения`)
2. **Start of Work Day** (`Начало рабочего дня`)
3. **Consumables** (`Расходные материалы`)
4. **Invoices** (`Накладная`)
5. **Personal Delivery** (`Доставка лично в руки`)
6. **Return Delivery** (`Доставка с возвратом`)
7. **Cash Collection** (`Забор за наличные деньги`)
8. **International Shipping** (`Международное отправление`)
9. **End of Work Day** (`Завершение рабочего дня`)
10. **Basic Training Test** (`Тест по базовому обучению`)

**Content Formats**:
- **Text**: PDF documents
- **Video**: Google Drive links
- **Tests**: External testing platform links

### CARGO Module (`КАРГО`)

**Available Resources**:
1. **Video Tutorial** (`Видео урок Карго`)
2. **Manual** (`Памятка Карго`)
3. **Trace Scheme** (`Схема трейсов`)
4. **Presentation** (`Презентация Карго`)
5. **Electronic Receipts** (`Электронные чеки`)

### Fast Payment System (`СБП`)

**Resources**:
1. **Reminder** (`Памятка по СБП`)
2. **Instructions** (`Инструкция по СБП`)
3. **Script** (`Скрипт для курьеров по СБП`)
4. **Video Tutorial** (`Видео урок СБП`)

## Utility Functions

### Document Management

#### `send_document_with_message(bot, chat_id, message_text, document_path, final_text=True, start_text=True)`

**Purpose**: Sends PDF documents with optional text messages

**Parameters**:
- `bot`: Bot instance
- `chat_id`: Target user's chat ID
- `message_text`: Text to send before document
- `document_path`: Path to PDF file
- `final_text`: Whether to send "back to home" message (default: True)
- `start_text`: Whether to send initial message (default: True)

**Usage Example**:
```python
send_document_with_message(
    bot, 
    message.chat.id,
    'Ознакомьтесь с инструкцией:',
    'Documents/instruction.pdf'
)
```

#### `send_video_link(bot, chat_id, title, video_url, back_button=False, final_text=True)`

**Purpose**: Sends video links with inline keyboard

**Parameters**:
- `bot`: Bot instance
- `chat_id`: Target user's chat ID
- `title`: Video title
- `video_url`: URL to video resource
- `back_button`: Whether to show back button (default: False)
- `final_text`: Whether to send "back to home" message (default: True)

**Usage Example**:
```python
send_video_link(
    bot, 
    message.chat.id, 
    'Training Video',
    'https://drive.google.com/file/d/video_id/view',
    back_button=True
)
```

### User Management

#### `count_active_users(message)`

**Purpose**: Counts active users and removes inactive ones

**Process**:
1. Retrieves all user IDs from database
2. Tests each user with `typing` action
3. Tracks active/inactive status
4. Updates progress periodically
5. Removes inactive users from database
6. Reports final statistics

**Features**:
- **Progress Tracking**: Updates every 50 users
- **Rate Limiting**: 0.05 second delay between checks
- **Database Cleanup**: Removes inactive users
- **Detailed Reporting**: Shows total, active, and removed counts

## Testing System

### External Test Integration

The bot integrates with external testing platforms using direct URL links:

**Test Categories**:
- Basic Training
- Postal Services and Lockers
- Temperature Cargo
- VSD/VPD Systems
- Inspection Acts
- Cargo Binding

**Implementation Pattern**:
```python
markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton('Test Name', url='https://test-platform.com/test-id'))
bot.send_message(chat_id, 'Перейдите по ссылке, чтобы пройти тестирование:', 
                reply_markup=markup)
```

## Flask Application

### Webhook Handler

#### File: `flask_app.py`

**Purpose**: Receives Telegram webhook updates

**Endpoint**: `@app.route(WEBHOOK_PATH, methods=['POST'])`

**Security**: Validates `X-Telegram-Bot-Api-Secret-Token` header

**Process**:
1. Validates secret token
2. Parses JSON update
3. Forwards to bot processor
4. Returns HTTP status

**Usage**:
```python
from flask import Flask, request
import telebot
from decouple import config
import botr

app = Flask(__name__)
bot = botr.bot

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

## Webhook Setup

### File: `set_webhook.py`

**Purpose**: Configures Telegram webhook

**Process**:
1. Removes existing webhook
2. Sets new webhook with URL and secret token
3. Reports setup status

**Usage**:
```bash
python set_webhook.py
```

**Configuration**:
```python
bot.remove_webhook()
response = bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN)
```

## Usage Examples

### Setting Up the Bot

1. **Environment Configuration**:
```bash
# Create .env file
TELEGRAM_BOT_TOKEN=your_bot_token
WEBHOOK_SECRET_TOKEN=your_secret
WEBHOOK_PATH=/webhook
WEBHOOK_URL=https://your-domain.com/webhook
```

2. **Install Dependencies**:
```bash
pip install pyTelegramBotAPI flask python-decouple
```

3. **Initialize Database**:
```bash
python botr.py  # Creates SQLite databases automatically
```

4. **Set Webhook**:
```bash
python set_webhook.py
```

5. **Run Flask Application**:
```bash
python flask_app.py
```

### User Interaction Flow

1. **New User Registration**:
```
User: /start
Bot: Добро пожаловать! Введите ваше имя:
User: Иван
Bot: Введите вашу фамилию:
User: Петров
Bot: Введите ваш город:
User: Москва
Bot: Спасибо, Иван Петров! Для начала обучения нажмите /home
```

2. **Accessing Training Materials**:
```
User: /home
Bot: [Shows main menu with buttons]
User: [Clicks "Базовое обучение"]
Bot: [Shows training modules]
User: [Clicks "Начало рабочего дня"]
Bot: [Shows format options: text/video]
User: [Clicks "Начало рабочего дня (видео)"]
Bot: [Sends video link with inline button]
```

### Administrative Operations

1. **Broadcast Message**:
```
Admin: /send
Bot: Отправьте сообщение для рассылки
Admin: Важное объявление для всех курьеров!
Bot: Подтвердите рассылку командой /confirm_send
Admin: /confirm_send
Bot: Рассылка начата...
Bot: Рассылка завершена.
```

2. **Check Active Users**:
```
Admin: [From admin menu] → "Посчитать активных пользователей"
Bot: Подсчёт активных пользователей начат...
Bot: Проверено 50 из 200 пользователей...
Bot: Подсчёт завершён!
     Всего пользователей: 200
     Активных пользователей: 185
     Удалено неактивных: 15
```

## Error Handling

### Database Errors
```python
try:
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    # Database operations
except Exception as e:
    print(f"Database error: {e}")
finally:
    connect.close()
```

### Message Delivery Errors
```python
for user_id in user_ids_to_send:
    try:
        bot.send_message(user_id, message_content)
    except Exception as e:
        print(f"Ошибка при отправке пользователю {user_id}: {e}")
```

### File Access Errors
```python
try:
    with open(document_path, 'rb') as doc:
        bot.send_document(chat_id, doc)
except FileNotFoundError:
    bot.send_message(chat_id, "Документ временно недоступен")
except Exception as e:
    print(f"File error: {e}")
```

## Deployment

### Production Setup

1. **Server Requirements**:
   - Python 3.7+
   - SQLite3
   - SSL certificate for webhook
   - Public domain/IP address

2. **Environment Setup**:
```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export TELEGRAM_BOT_TOKEN="your_production_token"
export WEBHOOK_URL="https://your-domain.com/webhook"
export WEBHOOK_SECRET_TOKEN="your_secure_secret"
```

3. **Process Management**:
```bash
# Using systemd service
sudo systemctl enable courier-bot
sudo systemctl start courier-bot

# Or using process manager like PM2
pm2 start flask_app.py --name courier-bot
```

4. **Monitoring**:
   - Log rotation for application logs
   - Database backup schedules
   - Health check endpoints
   - User activity monitoring

### Security Considerations

1. **Token Security**:
   - Store tokens in environment variables
   - Rotate tokens periodically
   - Monitor for unauthorized access

2. **Database Security**:
   - Regular backups
   - Access control
   - Data encryption for sensitive information

3. **Webhook Security**:
   - Use HTTPS only
   - Validate secret tokens
   - Implement rate limiting

### Maintenance

1. **Regular Tasks**:
   - Database cleanup of old messages
   - Inactive user removal
   - Document updates
   - Bot performance monitoring

2. **Updates**:
   - Test changes in development environment
   - Gradual rollout for major updates
   - Backup before deployments
   - Monitor error rates post-deployment

## API Reference Summary

### Core Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `analytics()` | User tracking decorator | `func: callable` | Wrapped function |
| `send_document_with_message()` | Send PDF with message | `bot, chat_id, message_text, document_path, final_text, start_text` | None |
| `send_video_link()` | Send video link with button | `bot, chat_id, title, video_url, back_button, final_text` | None |
| `count_active_users()` | Count and clean inactive users | `message` | None |

### Bot Handlers

| Handler | Trigger | Access Level | Purpose |
|---------|---------|--------------|---------|
| `start()` | `/home` | All users | Main menu |
| `back()` | `/back` | All users | Training menu |
| `send()` | `/send` | Admin only | Initiate broadcast |
| `confirm_send()` | `/confirm_send` | Admin only | Execute broadcast |
| `cancel_send()` | `/cancel_send` | Admin only | Cancel broadcast |
| `get_user_text()` | Text messages | All users | Content navigation |

### Database Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| `users_info` | `id, user_id, name, surname, city` | User profiles |
| `messages` | `id, name, surname, message, time_sent` | Message logs |

This documentation provides a comprehensive guide to the Courier Service Express Training Bot, covering all public APIs, functions, and components with detailed examples and usage instructions.