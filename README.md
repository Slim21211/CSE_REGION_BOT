# Курьер Сервис Экспресс Training Bot

A comprehensive Telegram bot system designed for employee training at "Курьер Сервис Экспресс" (Courier Service Express). This bot provides access to training materials, educational content, assessments, and administrative functions for company employees.

## 🚀 Features

- **📚 Training Content Management**: Access to PDFs, videos, and interactive materials
- **👥 User Registration & Management**: Automated user onboarding with profile creation
- **📊 Analytics & Monitoring**: User activity tracking and engagement metrics
- **📢 Broadcast System**: Mass messaging capabilities for administrators
- **🧪 Assessment Integration**: Links to external testing platforms
- **🔒 Role-Based Access**: Different content based on user roles
- **📱 Multi-Format Content**: Support for documents, videos, and tests
- **⚡ Real-Time Interaction**: Instant responses and content delivery

## 🏗️ Architecture

The system consists of three main components:

1. **Bot Engine** (`botr.py`) - Core bot logic and message handling
2. **Web Interface** (`flask_app.py`) - Webhook endpoint for Telegram integration
3. **Webhook Setup** (`set_webhook.py`) - Configuration utility

## 📋 Quick Start

### Prerequisites

- Python 3.7+
- Telegram Bot Token (from @BotFather)
- Public domain with SSL for webhook

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd courier-training-bot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Create .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET_TOKEN=your_secure_secret
WEBHOOK_PATH=/webhook
WEBHOOK_URL=https://your-domain.com/webhook
```

4. **Set up directories**:
```bash
mkdir Documents
mkdir Documents/labor_protection
# Copy your training materials to Documents/
```

5. **Configure webhook**:
```bash
python set_webhook.py
```

6. **Start the application**:
```bash
# Development
python flask_app.py

# Production
gunicorn --bind 0.0.0.0:5000 flask_app:app
```

## 📖 Documentation

### Core Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Comprehensive API reference with all public functions, endpoints, and usage examples
- **[Function Reference](FUNCTION_REFERENCE.md)** - Detailed documentation of all functions with parameters, return values, and code examples
- **[Component Guide](COMPONENT_GUIDE.md)** - System architecture, module interactions, and data flow documentation
- **[Usage Examples](USAGE_EXAMPLES.md)** - Practical examples for setup, usage, and extending the bot

### Quick Reference

| File | Purpose |
|------|---------|
| `botr.py` | Main bot logic and message handlers |
| `flask_app.py` | Webhook endpoint for Telegram API |
| `set_webhook.py` | Webhook configuration utility |
| `requirements.txt` | Python dependencies |

## 🎯 Training Modules

### Available Training Categories

1. **Basic Training** (`Базовое обучение`)
   - Work day procedures
   - Consumables handling
   - Invoice management
   - Delivery protocols
   - International shipping

2. **Specialized Systems**
   - CARGO system operations
   - Fast Payment (СБП) integration
   - Temperature cargo handling
   - VSD/VPD systems
   - Postal services and lockers

3. **Role-Specific Training**
   - Intern materials
   - Mentor resources
   - Dispatcher training
   - Advanced procedures

4. **Safety & Compliance**
   - Labor protection
   - Emergency procedures
   - Personal safety
   - First aid protocols

## 👨‍💼 Administrative Features

### Broadcast System
- Text and image message broadcasting
- User-specific delivery tracking
- Delivery confirmation and error handling

### User Analytics
- Active user counting and cleanup
- Interaction logging and tracking
- Registration analytics

### Content Management
- PDF document delivery
- Video link integration
- External test platform links

## 🗃️ Database Schema

### Users Table (`users_info`)
```sql
CREATE TABLE users_info (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    surname TEXT,
    city TEXT
);
```

### Messages Table (`messages`)
```sql
CREATE TABLE messages (
    id INTEGER,
    name TEXT,
    surname TEXT,
    message TEXT,
    time_sent TEXT
);
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from @BotFather | Yes |
| `WEBHOOK_SECRET_TOKEN` | Security token for webhook | Yes |
| `WEBHOOK_PATH` | Webhook endpoint path | Yes |
| `WEBHOOK_URL` | Full webhook URL | Yes |

### Admin Configuration

Admin users are configured in `botr.py`:
```python
admin_ids = [349682954, 223737494]  # Replace with actual admin IDs
```

## 📁 File Structure

```
courier-training-bot/
├── botr.py                 # Main bot logic
├── flask_app.py           # Flask webhook application
├── set_webhook.py         # Webhook setup utility
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── API_DOCUMENTATION.md  # Complete API documentation
├── FUNCTION_REFERENCE.md # Function documentation
├── COMPONENT_GUIDE.md    # Architecture guide
├── USAGE_EXAMPLES.md     # Usage examples and tutorials
├── .env                  # Environment configuration (create this)
└── Documents/            # Training materials directory
    ├── *.pdf            # Training documents
    └── labor_protection/ # Safety documentation
        └── *.pdf        # Safety materials
```

## 🚀 Usage Examples

### User Interaction Flow

```
User: /start
Bot: Welcome message → Registration flow → Main menu

User: [Selects training module]
Bot: Shows content options (text/video/test)

User: [Selects content format]
Bot: Delivers requested content
```

### Admin Operations

```
Admin: /send
Bot: Request broadcast content
Admin: [Provides content]
Bot: Request confirmation
Admin: /confirm_send
Bot: Executes broadcast to all users
```

## 🔒 Security Features

- **Webhook Security**: Token-based authentication
- **Admin Access Control**: Hardcoded admin user verification
- **Database Security**: SQLite with proper connection handling
- **Error Handling**: Graceful error recovery and user feedback

## 📊 Monitoring

### Health Check
The system includes a health check endpoint at `/health` that provides:
- Database connectivity status
- User count statistics
- File system availability
- System timestamp

### Logging
- User interaction logging
- Error tracking and reporting
- Message delivery confirmation

## 🛠️ Development

### Adding New Training Content

1. **Add PDF Document**:
   - Place file in `Documents/` directory
   - Add handler in `get_user_text()` function

2. **Add Video Content**:
   - Upload to Google Drive
   - Add video link handler with `send_video_link()`

3. **Add Assessment**:
   - Create test on external platform
   - Add inline button with test URL

### Extending Functionality

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples on:
- Adding new user fields
- Implementing role-based access
- Creating progress tracking
- Integrating external APIs

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not responding**:
   - Check SSL certificate
   - Verify webhook URL accessibility
   - Check server logs

2. **Database lock errors**:
   - Implement connection pooling
   - Add retry logic with timeouts

3. **File access issues**:
   - Verify file permissions
   - Check document paths
   - Implement error handling

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed troubleshooting solutions.

## 📄 License

This project is proprietary software developed for "Курьер Сервис Экспресс" (Courier Service Express).

## 🤝 Contributing

For internal development contributions:

1. Follow the existing code style and patterns
2. Add comprehensive documentation for new features
3. Include error handling and logging
4. Test with multiple user scenarios
5. Update documentation files accordingly

## 📞 Support

For technical support or questions about the training bot system, contact the development team or system administrators.

---

**Note**: This bot system is designed specifically for "Курьер Сервис Экспресс" training needs and contains company-specific content and procedures.