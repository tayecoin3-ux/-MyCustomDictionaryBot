"""
My Custom Dictionary Bot - Telegram Dictionary Bot
Deployed on Railway with GitHub integration
"""

import os
import sys
import logging
import random
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ==================== CONFIGURATION ====================

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API URLs
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
DATAMUSE_API = "https://api.datamuse.com/words"

# ==================== HELPER FUNCTIONS ====================

def get_definition(word):
    """Fetch word definition from Free Dictionary API"""
    try:
        response = requests.get(f"{DICTIONARY_API}{word}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                entry = data[0]
                meanings = entry.get('meanings', [])
                if meanings:
                    first_meaning = meanings[0]
                    part_of_speech = first_meaning.get('partOfSpeech', 'Unknown')
                    definitions = first_meaning.get('definitions', [])
                    if definitions:
                        definition_text = definitions[0].get('definition', 'No definition available')
                        example = definitions[0].get('example', None)
                        
                        # Get pronunciation
                        phonetics = entry.get('phonetics', [])
                        pronunciation = ''
                        if phonetics and phonetics[0].get('text'):
                            pronunciation = phonetics[0].get('text', '')
                        
                        result = {
                            'word': word,
                            'part_of_speech': part_of_speech,
                            'definition': definition_text,
                            'example': example,
                            'pronunciation': pronunciation
                        }
                        return result
        return None
    except Exception as e:
        logger.error(f"Error fetching definition: {e}")
        return None

def get_synonyms(word):
    """Fetch synonyms from Datamuse API"""
    try:
        response = requests.get(f"{DATAMUSE_API}?rel_syn={word}&max=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [item['word'] for item in data[:10]]
        return []
    except Exception as e:
        logger.error(f"Error fetching synonyms: {e}")
        return []

def get_antonyms(word):
    """Fetch antonyms from Datamuse API"""
    try:
        response = requests.get(f"{DATAMUSE_API}?rel_ant={word}&max=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [item['word'] for item in data[:10]]
        return []
    except Exception as e:
        logger.error(f"Error fetching antonyms: {e}")
        return []

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome = (
        f"👋 Hello *{user.first_name or 'User'}'*!\n\n"
        "📚 *My Custom Dictionary Bot*\n\n"
        "I can help you with:\n"
        "✅ Word definitions\n"
        "✅ Synonyms\n"
        "✅ Antonyms\n"
        "✅ Examples in sentences\n\n"
        "*How to use:*\n"
        "• Send any English word\n"
        "• Or use commands below\n\n"
        "Type /help to see all commands"
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Try Random Word", callback_data="random")],
        [InlineKeyboardButton("📚 About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📚 *Available Commands*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/word [word] - Get definition\n"
        "/synonym [word] - Get synonyms\n"
        "/antonym [word] - Get antonyms\n"
        "/example [word] - Get examples\n"
        "/about - About this bot\n\n"
        "*Or just send any word!*"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = (
        "📚 *My Custom Dictionary Bot*\n\n"
        "Version: 1.0.0\n\n"
        "Powered by:\n"
        "• Free Dictionary API\n"
        "• Datamuse API\n"
        "• python-telegram-bot\n\n"
        "🚀 Deployed on Railway\n"
        "📦 Source: GitHub"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /word command"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a word.\nExample: `/word beautiful`", parse_mode='Markdown')
        return
    
    word = ' '.join(context.args).strip().lower()
    await process_word(update, word)

async def synonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /synonym command"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a word.\nExample: `/synonym happy`", parse_mode='Markdown')
        return
    
    word = ' '.join(context.args).strip().lower()
    await process_synonym(update, word)

async def antonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /antonym command"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a word.\nExample: `/antonym happy`", parse_mode='Markdown')
        return
    
    word = ' '.join(context.args).strip().lower()
    await process_antonym(update, word)

async def example_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /example command"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a word.\nExample: `/example beautiful`", parse_mode='Markdown')
        return
    
    word = ' '.join(context.args).strip().lower()
    await process_example(update, word)

# ==================== PROCESSING FUNCTIONS ====================

async def process_word(update: Update, word: str):
    """Process and send word definition"""
    # Send loading message
    msg = await update.message.reply_text(f"🔍 Looking up *{word}*...", parse_mode='Markdown')
    
    try:
        # Get definition
        data = get_definition(word)
        
        if data:
            response = f"📖 *{data['word'].capitalize()}*\n\n"
            response += f"📝 *Definition:* {data['definition']}\n\n"
            response += f"🔹 *Part of Speech:* {data['part_of_speech']}\n"
            
            if data['pronunciation']:
                response += f"🔊 *Pronunciation:* {data['pronunciation']}\n"
            
            if data['example']:
                response += f"\n💡 *Example:*\n{data['example']}"
            
            # Get synonyms
            synonyms = get_synonyms(word)
            if synonyms:
                response += f"\n\n🔗 *Synonyms:* {', '.join(synonyms[:5])}"
            
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            await msg.edit_text(
                f"❌ Sorry, I couldn't find the word '*{word}*'.\n\n"
                "💡 Check the spelling or try another word.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in process_word: {e}")
        await msg.edit_text("❌ Something went wrong. Please try again.")

async def process_synonym(update: Update, word: str):
    """Process and send synonyms"""
    msg = await update.message.reply_text(f"🔍 Finding synonyms for *{word}*...", parse_mode='Markdown')
    
    try:
        synonyms = get_synonyms(word)
        if synonyms:
            response = f"🔗 *Synonyms for '{word}':*\n\n" + "\n".join([f"• {s}" for s in synonyms])
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            await msg.edit_text(f"❌ No synonyms found for '*{word}*'.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in process_synonym: {e}")
        await msg.edit_text("❌ Something went wrong. Please try again.")

async def process_antonym(update: Update, word: str):
    """Process and send antonyms"""
    msg = await update.message.reply_text(f"🔍 Finding antonyms for *{word}*...", parse_mode='Markdown')
    
    try:
        antonyms = get_antonyms(word)
        if antonyms:
            response = f"🔻 *Antonyms for '{word}':*\n\n" + "\n".join([f"• {a}" for a in antonyms])
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            await msg.edit_text(f"❌ No antonyms found for '*{word}*'.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in process_antonym: {e}")
        await msg.edit_text("❌ Something went wrong. Please try again.")

async def process_example(update: Update, word: str):
    """Process and send examples"""
    msg = await update.message.reply_text(f"🔍 Finding examples for *{word}*...", parse_mode='Markdown')
    
    try:
        # Get definition which includes example
        data = get_definition(word)
        if data and data['example']:
            response = f"💡 *Examples for '{word}':*\n\n"
            response += f"• {data['example']}"
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            await msg.edit_text(f"❌ No examples found for '*{word}*'.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in process_example: {e}")
        await msg.edit_text("❌ Something went wrong. Please try again.")

# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    word = update.message.text.strip().lower()
    if word:
        await process_word(update, word)

# ==================== CALLBACK HANDLER ====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "random":
        words = ["beautiful", "love", "nature", "happy", "dream", "inspire", "wonderful", "joy", "peace", "hope"]
        word = random.choice(words)
        await query.message.reply_text(f"📚 Trying: *{word.capitalize()}*", parse_mode='Markdown')
        
        # Process the word
        class FakeUpdate:
            def __init__(self, message, user, chat):
                self.effective_message = message
                self.effective_user = user
                self.effective_chat = chat
                self.message = message
                self.update_id = 0
        
        fake = FakeUpdate(query.message, query.from_user, query.message.chat)
        await process_word(fake, word)
    
    elif query.data == "about":
        about_text = (
            "📚 *My Custom Dictionary Bot*\n\n"
            "Version: 1.0.0\n\n"
            "Built with ❤️ using Python\n"
            "🚀 Deployed on Railway\n\n"
            "📖 *Features:*\n"
            "• Word definitions\n"
            "• Synonyms & antonyms\n"
            "• Example sentences\n"
            "• Pronunciation guide"
        )
        await query.message.reply_text(about_text, parse_mode='Markdown')

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ Sorry, an error occurred. Please try again.")
    except:
        pass

# ==================== MAIN ====================

def main():
    """Main function to start the bot"""
    try:
        logger.info("🚀 Starting My Custom Dictionary Bot...")
        logger.info("🤖 Bot: @MyCustomDictionaryBot")
        
        # Create application
        app = Application.builder().token(TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("about", about_command))
        app.add_handler(CommandHandler("word", word_command))
        app.add_handler(CommandHandler("synonym", synonym_command))
        app.add_handler(CommandHandler("antonym", antonym_command))
        app.add_handler(CommandHandler("example", example_command))
        
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_error_handler(error_handler)
        
        # Start polling
        logger.info("✅ Bot is running!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
