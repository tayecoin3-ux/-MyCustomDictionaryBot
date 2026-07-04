"""
My Custom Dictionary Bot - Telegram Dictionary Bot
Deployed on Railway with GitHub integration
"""

import os
import sys
import logging
import asyncio
from typing import Optional, Dict, Any
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes, 
    filters
)

# ==================== CONFIGURATION ====================

# Environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    sys.exit(1)

# API Configuration
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
DATAMUSE_API_URL = "https://api.datamuse.com/words"

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bot version
BOT_VERSION = "1.0.0"

# ==================== HELPER FUNCTIONS ====================

def format_word_response(data: Dict[str, Any], word: str) -> str:
    """
    Format the API response into a readable message.
    """
    try:
        if not data or not isinstance(data, list) or len(data) == 0:
            return f"❌ No definition found for *{word.capitalize()}*."

        entry = data[0]
        meanings = entry.get("meanings", [])
        
        if not meanings:
            return f"❌ No definition found for *{word.capitalize()}*."

        # Get the first meaning
        first_meaning = meanings[0]
        part_of_speech = first_meaning.get("partOfSpeech", "Unknown")
        definitions = first_meaning.get("definitions", [])
        
        if not definitions:
            return f"❌ No definition found for *{word.capitalize()}*."

        # Build response
        response_lines = []
        response_lines.append(f"📖 *{word.capitalize()}*")
        response_lines.append(f"🔹 *Part of Speech:* {part_of_speech}")

        # Add pronunciation if available
        phonetics = entry.get("phonetics", [])
        if phonetics:
            phonetic_text = phonetics[0].get("text", "")
            if phonetic_text:
                response_lines.append(f"🔹 *Pronunciation:* {phonetic_text}")

        response_lines.append("")  # Empty line for spacing
        response_lines.append("📝 *Definition:*")

        # Add the first definition
        first_def = definitions[0]
        definition_text = first_def.get("definition", "No definition available")
        response_lines.append(definition_text)

        # Add example if available
        example = first_def.get("example")
        if example:
            response_lines.append("")
            response_lines.append(f"💡 *Example:*")
            response_lines.append(example)

        # Add additional definitions if they exist
        if len(definitions) > 1:
            response_lines.append("")
            response_lines.append("📝 *More Definitions:*")
            for i, def_item in enumerate(definitions[1:4], 2):  # Max 3 more
                def_text = def_item.get("definition", "")
                if def_text:
                    response_lines.append(f"{i}. {def_text}")

        return "\n".join(response_lines)

    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return "❌ Error processing the word data. Please try again."

def fetch_synonyms(word: str, limit: int = 8) -> Optional[list]:
    """
    Fetch synonyms for a given word using Datamuse API.
    """
    try:
        params = {"rel_syn": word, "max": limit}
        response = requests.get(DATAMUSE_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return [item["word"] for item in data]
        return None
    except Exception as e:
        logger.error(f"Error fetching synonyms: {e}")
        return None

def fetch_antonyms(word: str, limit: int = 8) -> Optional[list]:
    """
    Fetch antonyms for a given word using Datamuse API.
    """
    try:
        params = {"rel_ant": word, "max": limit}
        response = requests.get(DATAMUSE_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return [item["word"] for item in data]
        return None
    except Exception as e:
        logger.error(f"Error fetching antonyms: {e}")
        return None

# ==================== BOT COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - Show welcome message and help.
    """
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome *{user.first_name or 'User'}*!\n\n"
        "📚 *My Custom Dictionary Bot*\n"
        f"Version: {BOT_VERSION}\n\n"
        "I can help you with word definitions, synonyms, antonyms, and examples!\n\n"
        "📖 *How to use:*\n"
        "• Send any English word to get its definition\n"
        "• Use /synonym [word] to find synonyms\n"
        "• Use /antonym [word] to find antonyms\n"
        "• Use /help for all commands\n\n"
        "🎯 *Try it now!* Send me a word like `hello` or `beautiful`"
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Try a Random Word", callback_data="random_word")],
        [InlineKeyboardButton("📚 About This Bot", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /help command - Show all available commands.
    """
    help_text = (
        "📚 *Available Commands*\n\n"
        "🔹 `/start` - Start the bot\n"
        "🔹 `/help` - Show this help message\n"
        "🔹 `/word [word]` - Get detailed word info\n"
        "🔹 `/synonym [word]` - Find synonyms\n"
        "🔹 `/antonym [word]` - Find antonyms\n"
        "🔹 `/example [word]` - Get example sentences\n"
        "🔹 `/about` - About this bot\n\n"
        "💡 *Quick Tip:* You don't need commands!\n"
        "Just send any English word and I'll define it automatically."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /about command - Show bot information.
    """
    about_text = (
        "📚 *My Custom Dictionary Bot*\n\n"
        f"🔹 *Version:* {BOT_VERSION}\n"
        "🔹 *Author:* Your Name\n\n"
        "🛠 *Powered by:*\n"
        "• Free Dictionary API (dictionaryapi.dev)\n"
        "• Datamuse API (datamuse.com)\n"
        "• python-telegram-bot library\n\n"
        "🚀 *Deployment:*\n"
        "• Hosted on Railway\n"
        "• Source code on GitHub\n\n"
        "💡 *Features:*\n"
        "• Word definitions with examples\n"
        "• Synonyms and antonyms\n"
        "• Pronunciation guides\n"
        "• 24/7 availability"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /word [word] command - Get detailed word information.
    """
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a word.\n"
            "Example: `/word beautiful`",
            parse_mode="Markdown"
        )
        return
    
    word = " ".join(context.args).strip().lower()
    await process_word_definition(update, word)

async def synonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /synonym [word] command - Get synonyms.
    """
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a word.\n"
            "Example: `/synonym happy`",
            parse_mode="Markdown"
        )
        return
    
    word = " ".join(context.args).strip().lower()
    await process_synonyms(update, word)

async def antonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /antonym [word] command - Get antonyms.
    """
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a word.\n"
            "Example: `/antonym happy`",
            parse_mode="Markdown"
        )
        return
    
    word = " ".join(context.args).strip().lower()
    await process_antonyms(update, word)

async def example_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /example [word] command - Get example sentences.
    """
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a word.\n"
            "Example: `/example beautiful`",
            parse_mode="Markdown"
        )
        return
    
    word = " ".join(context.args).strip().lower()
    await process_examples(update, word)

# ==================== CORE PROCESSING FUNCTIONS ====================

async def process_word_definition(update: Update, word: str) -> None:
    """
    Fetch and send word definition.
    """
    # Send initial message
    status_message = await update.message.reply_text(
        f"🔍 Looking up *{word.capitalize()}*...",
        parse_mode="Markdown"
    )
    
    try:
        # Fetch from dictionary API
        response = requests.get(
            f"{DICTIONARY_API_URL}{word}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            formatted_response = format_word_response(data, word)
            await status_message.edit_text(
                formatted_response,
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text(
                f"❌ Sorry, I couldn't find the word '*{word}*'.\n\n"
                "Possible reasons:\n"
                "• The word might be misspelled\n"
                "• The word might not exist in the dictionary\n"
                "• The word might not be English\n\n"
                "💡 Try checking the spelling and try again.",
                parse_mode="Markdown"
            )
            
    except requests.exceptions.Timeout:
        await status_message.edit_text(
            "⏰ Request timed out. Please try again later."
        )
    except requests.exceptions.ConnectionError:
        await status_message.edit_text(
            "🌐 Connection error. Please check your internet connection."
        )
    except Exception as e:
        logger.error(f"Error in process_word_definition: {e}")
        await status_message.edit_text(
            "❌ An unexpected error occurred. Please try again."
        )

async def process_synonyms(update: Update, word: str) -> None:
    """
    Fetch and send synonyms for a word.
    """
    status_message = await update.message.reply_text(
        f"🔍 Finding synonyms for *{word.capitalize()}*...",
        parse_mode="Markdown"
    )
    
    try:
        synonyms = fetch_synonyms(word)
        
        if synonyms:
            # Format the response
            response_lines = [
                f"🔗 *Synonyms for '{word.capitalize()}':*",
                "",
                "• " + "\n• ".join(synonyms)
            ]
            await status_message.edit_text(
                "\n".join(response_lines),
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text(
                f"❌ No synonyms found for '*{word}*'.\n\n"
                "💡 Try a different word or check the spelling.",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error in process_synonyms: {e}")
        await status_message.edit_text(
            "❌ An error occurred while fetching synonyms."
        )

async def process_antonyms(update: Update, word: str) -> None:
    """
    Fetch and send antonyms for a word.
    """
    status_message = await update.message.reply_text(
        f"🔍 Finding antonyms for *{word.capitalize()}*...",
        parse_mode="Markdown"
    )
    
    try:
        antonyms = fetch_antonyms(word)
        
        if antonyms:
            response_lines = [
                f"🔻 *Antonyms for '{word.capitalize()}':*",
                "",
                "• " + "\n• ".join(antonyms)
            ]
            await status_message.edit_text(
                "\n".join(response_lines),
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text(
                f"❌ No antonyms found for '*{word}*'.\n\n"
                "💡 Try a different word or check the spelling.",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error in process_antonyms: {e}")
        await status_message.edit_text(
            "❌ An error occurred while fetching antonyms."
        )

async def process_examples(update: Update, word: str) -> None:
    """
    Fetch and send example sentences for a word.
    """
    status_message = await update.message.reply_text(
        f"🔍 Finding examples for *{word.capitalize()}*...",
        parse_mode="Markdown"
    )
    
    try:
        # Use Datamuse API to get examples
        params = {
            "sp": word,
            "md": "d",
            "max": 5
        }
        response = requests.get(DATAMUSE_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and "defs" in data[0]:
                definitions = data[0]["defs"]
                examples = [d for d in definitions if "(" in d or ")" in d]
                
                if examples:
                    response_lines = [
                        f"💡 *Examples for '{word.capitalize()}':*",
                        ""
                    ]
                    for i, example in enumerate(examples[:5], 1):
                        response_lines.append(f"{i}. {example}")
                    
                    await status_message.edit_text(
                        "\n".join(response_lines),
                        parse_mode="Markdown"
                    )
                else:
                    await status_message.edit_text(
                        f"❌ No examples found for '*{word}*'.",
                        parse_mode="Markdown"
                    )
            else:
                await status_message.edit_text(
                    f"❌ No examples found for '*{word}*'.",
                    parse_mode="Markdown"
                )
        else:
            await status_message.edit_text(
                "❌ Could not fetch examples. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in process_examples: {e}")
        await status_message.edit_text(
            "❌ An error occurred while fetching examples."
        )

# ==================== MESSAGE HANDLER ====================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle text messages that aren't commands.
    """
    word = update.message.text.strip()
    
    # Ignore empty messages
    if not word:
        return
    
    # Process the word
    await process_word_definition(update, word)

# ==================== CALLBACK HANDLER ====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle inline keyboard button callbacks.
    """
    query = update.callback_query
    await query.answer()
    
    if query.data == "random_word":
        # Try a random common word
        common_words = [
            "beautiful", "happy", "love", "nature", "wonderful",
            "amazing", "joy", "dream", "inspire", "create"
        ]
        import random
        word = random.choice(common_words)
        await query.message.reply_text(
            f"📚 Let's try the word: *{word.capitalize()}*",
            parse_mode="Markdown"
        )
        await process_word_definition(
            update.__class__(
                effective_message=query.message,
                effective_user=query.from_user,
                effective_chat=query.message.chat,
                update_id=update.update_id
            ),
            word
        )
        
    elif query.data == "about":
        await about_command(
            update.__class__(
                effective_message=query.message,
                effective_user=query.from_user,
                effective_chat=query.message.chat,
                update_id=update.update_id
            ),
            context
        )

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during bot operation.
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to notify the user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Something went wrong. Please try again or contact the bot administrator."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ==================== MAIN APPLICATION ====================

def main() -> None:
    """
    Main entry point for the bot.
    """
    try:
        # Create application
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("word", word_command))
        application.add_handler(CommandHandler("synonym", synonym_command))
        application.add_handler(CommandHandler("antonym", antonym_command))
        application.add_handler(CommandHandler("example", example_command))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Add message handler for text messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_text_message
        ))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("🚀 My Custom Dictionary Bot is starting...")
        logger.info(f"🤖 Bot username: @MyCustomDictionaryBot")
        logger.info(f"📚 Version: {BOT_VERSION}")
        
        # Start polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
