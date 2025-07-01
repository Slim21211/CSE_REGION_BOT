# Component Guide - Курьер Сервис Экспресс Training Bot

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Training Modules](#training-modules)
4. [Data Flow](#data-flow)
5. [Integration Points](#integration-points)
6. [Content Management](#content-management)
7. [User Journey](#user-journey)
8. [Administrative Components](#administrative-components)
9. [External Dependencies](#external-dependencies)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           TELEGRAM BOT ECOSYSTEM                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Frontend  │    │   Backend   │    │   Storage   │         │
│  │             │    │             │    │             │         │
│  │ • Telegram  │◄──►│ • Bot Logic │◄──►│ • SQLite    │         │
│  │   Interface │    │ • Flask App │    │   Database  │         │
│  │ • Keyboards │    │ • Webhooks  │    │ • File Sys  │         │
│  │ • Messages  │    │ • Analytics │    │ • Documents │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        EXTERNAL SERVICES                       │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Google Drive│    │   Testing   │    │   Content   │         │
│  │   Videos    │    │  Platforms  │    │  Documents  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Model

```
User Input → Analytics Decorator → Handler Logic → Content Delivery → Response
     ↓               ↓                    ↓              ↓            ↓
   Logging      Registration     Menu Navigation   File/Video    User Interface
     ↓               ↓                    ↓              ↓            ↓
  Database      User Creation      Content Selection  External     Telegram API
   Storage       Tracking              Routing        Resources    
```

---

## Core Components

### 1. Bot Engine (`botr.py`)

**Primary Responsibilities**:
- Message handling and routing
- User session management  
- Content delivery orchestration
- Administrative functions

**Key Modules**:
```python
# Core Bot Instance
bot = telebot.TeleBot(telegram_bot_token, parse_mode='html')

# Configuration
admin_ids = [349682954, 223737494]
pending_message = {}  # Broadcast state management
```

**Handler Categories**:
1. **Command Handlers**: `/start`, `/home`, `/back`, `/send`, etc.
2. **Text Handlers**: Menu navigation and content requests
3. **Callback Handlers**: Inline button interactions
4. **Registration Handlers**: Multi-step user onboarding

### 2. Web Interface (`flask_app.py`)

**Purpose**: Webhook endpoint for Telegram API integration

**Core Functionality**:
```python
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    # Security validation
    # Request processing
    # Bot integration
```

**Security Features**:
- Token-based authentication
- Request validation
- Error handling

**Integration Points**:
- Telegram Bot API
- Main bot logic (`botr.py`)
- Environment configuration

### 3. Webhook Management (`set_webhook.py`)

**Purpose**: Configuration and setup utility

**Operations**:
1. Remove existing webhooks
2. Configure new webhook with security token
3. Validate setup success

**Usage Pattern**:
```bash
python set_webhook.py  # One-time setup
```

---

## Training Modules

### Module Structure Overview

```
Training Content Hierarchy:
├── Basic Training (Базовое обучение)
│   ├── Program Overview
│   ├── Daily Operations (9 modules)
│   └── Assessment Test
├── Specialized Training
│   ├── CARGO System
│   ├── Fast Payment (СБП)
│   ├── Postal Services (ПВЗ)
│   ├── Temperature Cargo
│   └── VSD/VPD Systems
├── Role-Specific Training
│   ├── Intern Materials
│   ├── Mentor Resources
│   ├── Dispatcher Training
│   └── Advanced Training
└── Assessment & Testing
    ├── Module Tests
    ├── Role-Specific Tests
    └── External Test Links
```

### 1. Basic Training Module (`Базовое обучение`)

**Structure**:
```python
# Menu Creation
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
chapter1 = types.KeyboardButton('Программа Базового обучения')
chapter2 = types.KeyboardButton('Начало рабочего дня')
# ... additional chapters
```

**Content Types**:
- **Text Materials**: PDF documents with procedures
- **Video Content**: Google Drive hosted training videos
- **Assessments**: External testing platform integration

**Modules Included**:
1. **Training Program** (`Программа Базового обучения`)
2. **Start of Work Day** (`Начало рабочего дня`)
3. **Consumables** (`Расходные материалы`)
4. **Invoices** (`Накладная`)
5. **Personal Delivery** (`Доставка лично в руки`)
6. **Return Delivery** (`Доставка с возвратом`)
7. **Cash Collection** (`Забор за наличные деньги`)
8. **International Shipping** (`Международное отправление`)
9. **End of Work Day** (`Завершение рабочего дня`)
10. **Assessment Test** (`Тест по базовому обучению`)

**Content Delivery Pattern**:
```python
# Format Selection
elif message.text == 'Начало рабочего дня':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    text = types.KeyboardButton('Начало рабочего дня (текст)')
    video = types.KeyboardButton('Начало рабочего дня (видео)')
    markup.add(text, video)

# Content Delivery
elif message.text == 'Начало рабочего дня (текст)':
    send_document_with_message(bot, message.chat.id,
                               'Ознакомьтесь с порядком действий:',
                               'Documents/start_day.pdf')
```

### 2. CARGO System Module (`КАРГО`)

**Available Resources**:
```python
# Module Structure
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
chapter1 = types.KeyboardButton('Видео урок Карго')
chapter2 = types.KeyboardButton('Памятка Карго')
chapter3 = types.KeyboardButton('Схема трейсов')
chapter4 = types.KeyboardButton('Презентация Карго')
chapter5 = types.KeyboardButton('Электронные чеки')
```

**Content Types**:
- **Video Tutorial**: Comprehensive CARGO operations
- **Manual**: Mobile application usage guide
- **Trace Scheme**: System workflow documentation
- **Presentation**: Detailed feature overview
- **E-Receipt Guide**: Online store integration

**File Mappings**:
- `Documents/cargo_manual.pdf` - CARGO mobile app manual
- `Documents/traces_scheme.pdf` - Trace system scheme
- `Documents/cargo-presentation.pdf` - CARGO presentation
- `Documents/e_chek.pdf` - Electronic receipt guide

### 3. Fast Payment System (`СБП`)

**Module Components**:
```python
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
reminder = types.KeyboardButton('Памятка по СБП')
manual = types.KeyboardButton('Инструкция по СБП')
script = types.KeyboardButton('Скрипт для курьеров по СБП')
video = types.KeyboardButton('Видео урок СБП')
```

**Resource Types**:
1. **Reminder** (`fast_pay_reminder.pdf`) - Quick reference guide
2. **Manual** (`fast_pay_manual.pdf`) - Detailed instructions
3. **Script** (`fast_pay_script.pdf`) - Customer interaction guide
4. **Video** - Practical demonstration

### 4. Temperature Cargo Module (`Температурные грузы`)

**Role-Based Structure**:
```python
# Role Selection
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
chapter1 = types.KeyboardButton('Температурные грузы для курьеров')
chapter2 = types.KeyboardButton('Температурные грузы для диспетчеров')
chapter3 = types.KeyboardButton('Температурные грузы видео')

# Courier-Specific Content
elif message.text == 'Температурные грузы для курьеров':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    chapter1 = types.KeyboardButton('Температурные грузы Памятка для курьеров')
    chapter2 = types.KeyboardButton('Тест Температурные грузы для курьеров')
```

**Content Differentiation**:
- **Courier Materials**: Field handling procedures
- **Dispatcher Materials**: Management and coordination
- **Video Content**: Universal training material
- **Role-Specific Tests**: Targeted assessments

### 5. Labor Protection Module (`Охрана труда`)

**Comprehensive Safety Training**:
```python
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
chapter1 = types.KeyboardButton('Охрана труда. Основной раздел')
chapter2 = types.KeyboardButton('Личная безопасность при проведении работ')
chapter3 = types.KeyboardButton('Электробезопасность')
chapter4 = types.KeyboardButton('Производственная санитария и личная гигиена')
chapter5 = types.KeyboardButton('Средства индивидуальной защиты')
chapter6 = types.KeyboardButton('Аварийные ситуации')
chapter7 = types.KeyboardButton('Первая помощь пострадавшим')
```

**Multi-Document Delivery**:
```python
# Multiple safety documents
elif message.text == 'Личная безопасность при проведении работ':
    send_document_with_message(bot, message.chat.id,
                               'Личная безопасность:',
                               'Documents/labor_protection/1.1. Памятка «Меры безопасности при передвижении в помещениях».pdf', False)
    send_document_with_message(bot, message.chat.id,
                               '',
                               'Documents/labor_protection/1.2. Памятка «Выполнение погрузочно-разгрузочных работ».pdf', False, False)
    # ... additional documents
```

---

## Data Flow

### User Registration Flow

```
New User Interaction:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  /start     │───►│  analytics  │───►│ name_step   │───►│surname_step │
│  command    │    │  decorator  │    │  handler    │    │  handler    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                                       │
                          ▼                                       ▼
                   ┌─────────────┐                        ┌─────────────┐
                   │   Check     │                        │   city_step │
                   │   existing  │                        │   handler   │
                   │   user      │                        └─────────────┘
                   └─────────────┘                               │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │   Database  │
                                                          │   Storage   │
                                                          └─────────────┘
```

### Content Delivery Flow

```
Content Request Processing:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───►│  analytics  │───►│get_user_text│───►│   Content   │
│   Message   │    │  decorator  │    │   handler   │    │  Delivery   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Message   │    │   User      │    │   Menu      │    │ Document/   │
│   Logging   │    │ Validation  │    │ Navigation  │    │ Video/Test  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Broadcast Message Flow

```
Admin Broadcast Process:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   /send     │───►│   Admin     │───►│  Content    │───►│ /confirm_   │
│  command    │    │Verification │    │ Collection  │    │   send      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                              │                   │
                                              ▼                   ▼
                                       ┌─────────────┐    ┌─────────────┐
                                       │   Pending   │    │    Mass     │
                                       │   Storage   │    │  Delivery   │
                                       └─────────────┘    └─────────────┘
```

---

## Integration Points

### 1. Telegram Bot API

**Connection Method**: Webhook-based integration
**Configuration**:
```python
# Bot initialization
bot = telebot.TeleBot(telegram_bot_token, parse_mode='html')

# Webhook setup
bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN)
```

**Message Types Handled**:
- Text messages
- Photo messages (for broadcasts)
- Command messages
- Callback queries

### 2. External Testing Platforms

**Integration Pattern**:
```python
# Test link generation
markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton('Test Name', url='test_platform_url'))
bot.send_message(chat_id, 'Перейдите по ссылке:', reply_markup=markup)
```

**Testing Platforms Used**:
- `startexam.com` - Primary testing platform
- URL shortening for user-friendly links
- Direct external navigation

**Test Categories**:
- Basic training assessments
- Role-specific evaluations
- Module completion tests

### 3. File Storage System

**Document Organization**:
```
Documents/
├── Basic Training Materials
├── Specialized Module Content  
├── Role-Specific Resources
├── labor_protection/
│   ├── Safety Procedures
│   ├── Emergency Protocols
│   └── First Aid Guides
└── Assessment Materials
```

**File Delivery Methods**:
1. **PDF Documents**: `bot.send_document()`
2. **Video Links**: Inline keyboard with Google Drive URLs
3. **Multi-Document Sets**: Sequential delivery with flow control

### 4. Database Integration

**Schema Design**:
```sql
-- User management
users_info: id, user_id, name, surname, city

-- Interaction tracking  
messages: id, name, surname, message, time_sent
```

**Access Patterns**:
- User lookup and validation
- Registration data storage
- Message logging and analytics
- Inactive user cleanup

---

## Content Management

### Document Storage Strategy

**File Organization**:
- **Centralized Location**: `Documents/` directory
- **Logical Grouping**: By training module and category
- **Naming Convention**: Descriptive Russian filenames
- **Format Standardization**: Primarily PDF documents

**Content Types**:
1. **Training Manuals**: Comprehensive procedural guides
2. **Quick References**: Condensed reminder materials  
3. **Presentations**: Visual training content
4. **Assessment Materials**: Test preparation resources

### Video Content Management

**Hosting Strategy**:
- **Primary Platform**: Google Drive
- **Access Method**: Direct URL links
- **User Experience**: Inline keyboard buttons

**Video Categories**:
- Module demonstrations
- Procedure walkthroughs
- System usage tutorials
- Advanced training content

**Delivery Pattern**:
```python
def send_video_link(bot, chat_id, title, video_url, back_button=False, final_text=True):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Смотреть видео', url=video_url))
    bot.send_message(chat_id, f'<b>{title}</b>\nДля просмотра видео перейдите по ссылке:', 
                     reply_markup=markup, parse_mode='html')
```

### Content Update Process

**Manual Update Workflow**:
1. Replace files in `Documents/` directory
2. Update file paths in code if necessary
3. Test content delivery
4. Deploy updated application

**Version Control**:
- File-based versioning
- Manual change tracking
- Backup procedures for critical content

---

## User Journey

### New User Experience

**Registration Phase**:
```
1. /start command → Welcome message
2. Name collection → Surname collection → City collection
3. Database registration → Welcome completion
4. Navigation to main menu (/home)
```

**Learning Phase**:
```
1. Main menu exploration → Category selection
2. Module navigation → Content format choice (text/video)  
3. Content consumption → Return navigation
4. Assessment completion → Progress tracking
```

### Returning User Experience

**Streamlined Access**:
```
1. /start command → Existing user recognition
2. Direct welcome → Main menu access
3. Content browsing → Continued learning
```

### Administrative User Journey

**Broadcast Management**:
```
1. Admin menu access → Broadcast initiation (/send)
2. Content creation → Preview and confirmation
3. Mass delivery → Completion reporting
```

**User Analytics**:
```
1. Admin menu → User count request
2. Active user testing → Database cleanup
3. Statistics reporting → System maintenance
```

---

## Administrative Components

### User Management System

**Admin Identification**:
```python
admin_ids = [349682954, 223737494]  # Hardcoded admin list
```

**Admin-Only Features**:
1. **Broadcast System**: Mass message delivery
2. **User Analytics**: Active user counting and cleanup
3. **System Management**: Database maintenance

**Access Control Pattern**:
```python
if message.chat.id in admin_ids:
    # Allow admin functionality
else:
    # Deny access with user message
```

### Analytics and Monitoring

**User Activity Tracking**:
- Message logging with timestamps
- User interaction patterns
- Registration data collection

**System Health Monitoring**:
- Active user verification
- Inactive user cleanup
- Database integrity maintenance

**Performance Metrics**:
- User engagement levels
- Content access patterns
- System usage statistics

### Broadcast Management

**Content Types Supported**:
1. **Text Messages**: Plain text announcements
2. **Photo Messages**: Images with captions

**Broadcast Flow Control**:
```python
# Content staging
pending_message[admin_chat_id] = {
    'type': 'text' | 'photo',
    'text': message_content,
    'file_id': photo_id,  # for photos
    'caption': photo_caption  # for photos
}

# Delivery execution
for user_id in all_users:
    try:
        # Send based on content type
    except Exception:
        # Log delivery failure, continue
```

**Error Resilience**:
- Individual delivery failure handling
- Continuation despite errors
- Comprehensive delivery reporting

---

## External Dependencies

### Required Libraries

**Core Dependencies**:
```python
import telebot           # Telegram Bot API wrapper
import sqlite3          # Database management
from decouple import config  # Environment configuration
from datetime import datetime  # Timestamp handling
import time             # Rate limiting
from flask import Flask, request  # Webhook handling
```

**Library Purposes**:
- `pyTelegramBotAPI`: Primary bot functionality
- `python-decouple`: Secure configuration management
- `Flask`: Webhook endpoint hosting
- `sqlite3`: Lightweight database operations

### Environment Configuration

**Required Variables**:
```env
TELEGRAM_BOT_TOKEN=bot_api_token
WEBHOOK_SECRET_TOKEN=security_token
WEBHOOK_PATH=/webhook_endpoint
WEBHOOK_URL=https://domain.com/webhook
```

**Security Considerations**:
- Token-based authentication
- Environment variable isolation
- Webhook secret validation

### External Services

**Google Drive Integration**:
- Video content hosting
- Direct link access
- No API integration required

**Testing Platform Integration**:
- `startexam.com` external testing
- URL-based navigation
- No direct API integration

**File System Dependencies**:
- Local document storage
- PDF file access
- Static content serving

This component guide provides a comprehensive overview of the system architecture, module interactions, and content management strategies for the Courier Service Express Training Bot.