# My Custom Dictionary Bot

A powerful Telegram bot for looking up word definitions, synonyms, antonyms, and examples.

## 🚀 Features

- 📖 **Word Definitions** - Get detailed definitions with examples
- 🔗 **Synonyms** - Find related words
- 🔻 **Antonyms** - Find opposite words  
- 💡 **Examples** - See words in context
- 🎯 **Pronunciation Guide** - Learn how to say words
- 📱 **Inline Keyboard** - Interactive buttons for easy use

## 🛠️ Technologies Used

- Python 3.11+
- python-telegram-bot library
- Free Dictionary API
- Datamuse API
- Railway (Hosting)
- GitHub (Version Control)

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/help` | Show all available commands |
| `/word [word]` | Get detailed word information |
| `/synonym [word]` | Find synonyms for a word |
| `/antonym [word]` | Find antonyms for a word |
| `/example [word]` | Get example sentences |
| `/about` | About the bot |

## 🚀 Deployment

This bot is deployed on Railway with automatic deployments from GitHub.

### Deploy Your Own

1. Fork this repository
2. Create a bot on Telegram via @BotFather
3. Deploy to Railway
4. Set the environment variable:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather

## 🔧 Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MyCustomDictionaryBot.git
cd MyCustomDictionaryBot
