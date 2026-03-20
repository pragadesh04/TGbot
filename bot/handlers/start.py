from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show inline keyboard with Query and Register options"""
    keyboard = [
        [InlineKeyboardButton("📋 Get Query", callback_data="action_query")],
        [InlineKeyboardButton("📝 Register", callback_data="action_register")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "👋 *Welcome to Course Registration Bot!*\n\n"
        "Please select an option below:\n\n"
        "📋 *Get Query* - Ask questions and get answers from our AI assistant\n"
        "📝 *Register* - Register for a course\n\n"
        "Use /end to exit query mode anytime."
    )

    await update.message.reply_text(
        welcome_message, parse_mode="Markdown", reply_markup=reply_markup
    )
