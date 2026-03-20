from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_courses, get_course_by_id


REGISTRATION_STEPS = {
    "name": "Enter your FULL NAME:",
    "address": "Enter your ADDRESS:",
    "course": "Select a course:",
    "payment": "Payment",
}


async def register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle register callback - start registration flow"""
    query = update.callback_query
    await query.answer()

    context.user_data["in_registration"] = True
    context.user_data["in_query_mode"] = False
    context.user_data["registration_step"] = "name"

    await query.edit_message_text(
        text="📝 *Registration Started!*\n\n" + REGISTRATION_STEPS["name"],
        parse_mode="Markdown",
    )


async def handle_registration_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle registration input based on current step"""
    if not context.user_data.get("in_registration"):
        return None

    step = context.user_data.get("registration_step")
    text = update.message.text.strip()

    if step == "name":
        context.user_data["reg_name"] = text
        context.user_data["registration_step"] = "address"
        await update.message.reply_text(
            f"✅ Name saved: *{text}*\n\n" + REGISTRATION_STEPS["address"],
            parse_mode="Markdown",
        )
        return True

    elif step == "address":
        context.user_data["reg_address"] = text
        context.user_data["registration_step"] = "course"
        await show_course_selection(update, context)
        return True

    elif step == "course":
        return await handle_course_selection(update, context, text)

    return None


async def show_course_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show course selection with top 5 and 'See All' option"""
    courses = await get_courses()

    keyboard = []

    top_5 = courses[:5]
    for i, course in enumerate(top_5):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{i + 1}. {course['title']} (₹{course['fee']})",
                    callback_data=f"course_select_{course['_id']}",
                )
            ]
        )

    if len(courses) > 5:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "📋 See All Courses",
                    callback_data="course_show_all",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    header = (
        f"✅ Address saved: *{context.user_data.get('reg_address', 'N/A')}*\n\n"
        f"📚 *{REGISTRATION_STEPS['course']}*\n\n"
        f"*Top {len(top_5)} Popular Courses:*\n"
        f"(Enter the number to select)\n\n"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            header, parse_mode="Markdown", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            header, parse_mode="Markdown", reply_markup=reply_markup
        )


async def show_all_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all courses"""
    query = update.callback_query
    await query.answer()

    courses = await get_courses()

    keyboard = []
    for i, course in enumerate(courses):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{i + 1}. {course['title']} (₹{course['fee']})",
                    callback_data=f"course_select_{course['_id']}",
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("🔙 Back to Top 5", callback_data="course_back_top5")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    course_list = "\n".join(
        [
            f"{i + 1}. {c['title']} - ₹{c['fee']} ({c['registration_count']} registered)"
            for i, c in enumerate(courses)
        ]
    )

    await query.edit_message_text(
        f"📚 *All Courses:*\n\n{course_list}\n\n*Select a course:*",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def handle_course_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
):
    """Handle course selection by number"""
    courses = await get_courses()

    try:
        index = int(text) - 1
        if 0 <= index < len(courses):
            course = courses[index]
            context.user_data["selected_course"] = course
            context.user_data["registration_step"] = "payment"

            from handlers.payment import start_payment_flow

            await start_payment_flow(update, context)
            return True
        else:
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    "❌ Invalid selection. Please enter a valid number."
                )
            else:
                await update.message.reply_text(
                    "❌ Invalid selection. Please enter a valid number."
                )
            return True
    except ValueError:
        if update.callback_query:
            await update.callback_query.message.reply_text("❌ Please enter a number.")
        else:
            await update.message.reply_text("❌ Please enter a number.")
        return True


async def course_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle course selection via inline button"""
    query = update.callback_query
    data = query.data

    await query.answer()

    if data == "course_show_all":
        await show_all_courses(update, context)
        return

    if data == "course_back_top5":
        context.user_data["registration_step"] = "course"
        await show_course_selection(update, context)
        return

    if data.startswith("course_select_"):
        course_id = data.replace("course_select_", "")
        course = await get_course_by_id(course_id)

        if course:
            context.user_data["selected_course"] = course
            context.user_data["registration_step"] = "payment"

            from handlers.payment import start_payment_flow

            await start_payment_flow(update, context)
