import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from database import connect_to_mongo, close_mongo_connection, initialize_default_config
from handlers.start import (
    start_command,
    help_command,
    courses_command,
    myregistrations_command,
)
from handlers.query import query_callback, end_command, handle_query_message
from handlers.registration import (
    register_callback,
    handle_registration_input,
    course_select_callback,
    use_same_details_callback,
)
from handlers.payment import handle_screenshot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()


async def post_init(application: Application):
    await connect_to_mongo()
    await initialize_default_config()

    # Set bot commands for command suggestions
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show available commands"),
            BotCommand("courses", "View all courses with details"),
            BotCommand("register", "Register for a course"),
            BotCommand("myregistrations", "View your registrations"),
            BotCommand("end", "Exit query mode"),
        ]
    )

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(
            f"{webhook_url}/webhook/{os.getenv('BOT_TOKEN')}"
        )
        print(f"Webhook set to {webhook_url}")


async def post_shutdown(application: Application):
    await close_mongo_connection()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if update.message.text.startswith("/"):
            return

        result = await handle_query_message(update, context)
        if result:
            return

        result = await handle_registration_input(update, context)
        if result:
            return

        if not context.user_data.get("in_query_mode") and not context.user_data.get(
            "in_registration"
        ):
            await update.message.reply_text(
                "👋 I'm here to help! Use /start to get started."
            )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await handle_screenshot(update, context)
    if not result:
        await update.message.reply_text(
            "Please use /start to begin registration first."
        )


def main():
    application = (
        Application.builder()
        .token(os.getenv("BOT_TOKEN"))
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("courses", courses_command))
    application.add_handler(CommandHandler("register", start_command))
    application.add_handler(CommandHandler("end", end_command))
    application.add_handler(CommandHandler("myregistrations", myregistrations_command))
    application.add_handler(
        CallbackQueryHandler(query_callback, pattern="action_query")
    )
    application.add_handler(
        CallbackQueryHandler(register_callback, pattern="action_register")
    )
    application.add_handler(
        CallbackQueryHandler(course_select_callback, pattern="^course_")
    )
    application.add_handler(
        CallbackQueryHandler(use_same_details_callback, pattern="^use_same_details_")
    )
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
