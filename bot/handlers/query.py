from telegram import Update
from telegram.ext import ContextTypes
from database import add_chat_message, get_chat_history, clear_chat_history
from ai import get_ai_response_stream


async def query_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle query callback - enter query mode"""
    query = update.callback_query
    await query.answer()

    context.user_data["in_query_mode"] = True
    context.user_data["in_registration"] = False

    await query.edit_message_text(
        text="🔍 *Query Mode Activated*\n\n"
        "Ask any question and I'll help you out!\n"
        "Type /end to exit query mode.",
        parse_mode="Markdown",
    )


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /end command - exit query mode"""
    if context.user_data.get("in_query_mode"):
        context.user_data["in_query_mode"] = False
        await clear_chat_history(update.message.from_user.id)
        await update.message.reply_text(
            "👋 Query session ended. Use /start to begin again."
        )
    else:
        await update.message.reply_text(
            "You're not in query mode. Use /start to get started."
        )


async def handle_query_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in query mode"""
    if not context.user_data.get("in_query_mode"):
        return None

    user_id = update.message.from_user.id
    user_message = update.message.text

    await add_chat_message(user_id, "user", user_message)

    history = await get_chat_history(user_id)

    await update.message.reply_text("💭 Thinking...")

    response_text = ""
    for chunk in get_ai_response_stream(history, user_message):
        response_text += chunk

    if response_text:
        await add_chat_message(user_id, "assistant", response_text)

        message_id = update.message.message_id + 1
        try:
            await context.bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=message_id,
                text=response_text,
            )
        except:
            await update.message.reply_text(response_text)

    return True
