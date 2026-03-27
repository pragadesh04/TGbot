from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_courses, get_registrations_by_telegram_id
from datetime import datetime


def format_duration_hours(hours: float) -> str:
    if not hours:
        return "N/A"
    h = int(hours)
    m = int((hours - h) * 60)
    if h == 0:
        return f"{m} Minutes"
    elif m == 0:
        return f"{h} Hour{'s' if h > 1 else ''}"
    else:
        return f"{h} Hour{'s' if h > 1 else ''} {m} Minutes"


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
        "Type /help to see all commands."
    )

    await update.message.reply_text(
        welcome_message, parse_mode="Markdown", reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show available commands"""
    help_text = (
        "📚 *Available Commands:*\n\n"
        "• /start - Start the bot and see options\n"
        "• /help - Show this help message\n"
        "• /courses - View all available courses\n"
        "• /register - Start course registration\n"
        "• /myregistrations - View your registrations\n"
        "• /end - Exit query mode\n\n"
        "💡 *Tips:*\n"
        "- Type / to see command suggestions\n"
        "- Use /courses to see all courses with details\n"
        "- Use /register to start registration\n"
        "- Use /myregistrations to view all your course registrations\n"
        "- If you've registered before, you can reuse your name & address"
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")


async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /courses command - show all courses with details"""
    courses = await get_courses()

    if not courses:
        await update.message.reply_text(
            "📚 No courses available yet.", parse_mode="Markdown"
        )
        return

    courses_text = "📚 *Available Courses:*\n\n"

    for i, course in enumerate(courses, 1):
        course_type = course.get("course_type", "recorded")
        type_emoji = "🔴" if course_type == "live" else "📼"
        type_text = "Live" if course_type == "live" else "Recorded"

        courses_text += f"{i}. {type_emoji} *{course['title']}*\n"
        courses_text += f"   📝 {course.get('description', 'No description')[:80]}...\n"
        courses_text += f"   💰 Price: ₹{course.get('fee', 0)}\n"
        courses_text += f"   🎯 Type: {type_text}\n"

        if course_type == "live":
            if course.get("start_date"):
                courses_text += f"   📅 Start: {course['start_date']}"
                if course.get("start_time"):
                    courses_text += f" at {course['start_time']}"
                courses_text += "\n"
            if course.get("sessions"):
                courses_text += f"   📊 {course['sessions']} sessions"
                if course.get("duration"):
                    courses_text += (
                        f", {format_duration_hours(course['duration'])} each"
                    )
                courses_text += "\n"

        courses_text += f"   👥 {course.get('registration_count', 0)} enrolled\n\n"

    await update.message.reply_text(courses_text, parse_mode="Markdown")


async def myregistrations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myregistrations command - show all user's registrations"""
    user_id = update.effective_user.id
    registrations = await get_registrations_by_telegram_id(user_id)

    if not registrations:
        await update.message.reply_text(
            "📋 *You haven't registered for any course yet.*\n\n"
            "Use /register to start your registration.",
            parse_mode="Markdown",
        )
        return

    status_emoji = {
        "pending": "⏳",
        "approved": "✅",
        "rejected": "❌",
    }

    lines = ["📋 *Your Registrations:*\n"]
    for i, reg in enumerate(registrations, 1):
        status = reg.get("status", "unknown")
        emoji = status_emoji.get(status, "❓")
        course_title = reg.get("course_title", "Unknown course")
        amount = reg.get("amount", 0)
        mobile = reg.get("mobile", "")
        rejection_reason = reg.get("rejection_reason")
        created_at = reg.get("created_at")
        date_str = ""
        if created_at:
            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%d %b %Y")
            else:
                date_str = str(created_at)[:10]

        lines.append(f"{i}. {emoji} *{course_title}*")
        lines.append(f"   💰 Amount: ₹{amount}")
        lines.append(f"   📊 Status: {status.capitalize()}")
        if mobile:
            lines.append(f"   📱 Mobile: {mobile}")
        if rejection_reason:
            lines.append(f"   ❌ Reason: {rejection_reason}")
        if date_str:
            lines.append(f"   📅 Date: {date_str}")
        lines.append("")

    result = "\n".join(lines)
    await update.message.reply_text(result, parse_mode="Markdown")
