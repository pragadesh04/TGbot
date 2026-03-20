from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_config, create_registration
from utils import generate_qr_code
from bson import ObjectId
import os


async def start_payment_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start payment flow after course selection"""
    course = context.user_data.get("selected_course")
    name = context.user_data.get("reg_name")
    address = context.user_data.get("reg_address")

    upi_id = await get_config("upi_id") or "yourname@upi"
    amount = course.get("fee", 0)

    context.user_data["registration_step"] = "waiting_screenshot"

    qr_base64 = generate_qr_code(upi_id, amount)

    course_info = (
        f"✅ *Course Selected:*\n"
        f"📚 {course['title']}\n"
        f"💰 Amount: ₹{amount}\n\n"
        f"📱 *UPI ID:* `{upi_id}`\n\n"
        f"Please pay the above amount and send the screenshot."
    )

    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        await update.callback_query.message.reply_text(
            course_info, parse_mode="Markdown"
        )
    else:
        chat_id = update.message.chat_id
        await update.message.reply_text(course_info, parse_mode="Markdown")

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=f"data:image/png;base64,{qr_base64}",
        caption=f"Scan QR code to pay ₹{amount}",
    )

    context.user_data["payment_upi_id"] = upi_id
    context.user_data["payment_amount"] = amount


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot submission"""
    if not context.user_data.get("in_registration"):
        return None

    if context.user_data.get("registration_step") != "waiting_screenshot":
        return None

    if not update.message.photo:
        return None

    photo = update.message.photo[-1]
    file = await photo.get_file()

    user_id = update.message.from_user.id
    filename = f"screenshot_{user_id}_{update.message.message_id}.jpg"
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "..",
        "uploads",
        "screenshots",
        filename,
    )

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    await file.download_to_drive(filepath)

    course = context.user_data.get("selected_course")
    name = context.user_data.get("reg_name")
    address = context.user_data.get("reg_address")
    amount = context.user_data.get("payment_amount", 0)

    screenshot_url = f"/uploads/screenshots/{filename}"

    registration_data = {
        "telegram_id": user_id,
        "name": name,
        "address": address,
        "course_id": ObjectId(course["_id"])
        if isinstance(course.get("_id"), str)
        else course.get("_id"),
        "course_title": course["title"],
        "amount": amount,
        "screenshot_url": screenshot_url,
        "status": "pending",
    }

    await create_registration(registration_data)

    context.user_data["in_registration"] = False
    context.user_data["registration_step"] = None

    await update.message.reply_text(
        "✅ *Screenshot Received!*\n\n"
        "Your registration is pending review.\n"
        "We'll notify you once approved.",
        parse_mode="Markdown",
    )

    return True
