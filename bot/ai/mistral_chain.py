import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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


async def get_courses_for_ai():
    """Get all courses formatted as a detailed paragraph for AI context."""
    from database import get_database

    db = get_database()
    courses_list = (
        await db.courses.find().sort("registration_count", -1).to_list(length=None)
    )

    courses = []
    for course in courses_list:
        course_type = course.get("course_type", "recorded")

        schedule_info = ""
        if course_type == "live":
            parts = []
            if course.get("start_date"):
                parts.append(f"starting {course['start_date']}")
            if course.get("start_time"):
                parts.append(
                    datetime.strptime(course["start_time"], "%H:%M").strftime(
                        "%I:%M %p"
                    )
                )
                pass
            if course.get("sessions"):
                parts.append(f"{course['sessions']} sessions")
            if course.get("duration"):
                parts.append(f"{format_duration_hours(course['duration'])} each")

            if parts:
                schedule_info = f" (Schedule: {', '.join(parts)})"

        course_info = (
            f"- {course['title']}: {course.get('description', 'No description')}. "
            f"Price: ₹{course.get('fee', 0)}. "
            f"Type: {'Live (real-time online classes)' if course_type == 'live' else 'Recorded (pre-recorded videos)'}"
            f"{schedule_info}. "
            f"({course.get('registration_count', 0)} students enrolled)"
        )
        courses.append(course_info)

    return "\n\n".join(courses) if courses else "No courses available."


async def get_courses_simple():
    """Get simple course list for general queries: name: description (₹price)"""
    from database import get_database

    db = get_database()
    courses_list = (
        await db.courses.find().sort("registration_count", -1).to_list(length=None)
    )

    if not courses_list:
        return "No courses available."

    lines = ["📚 Available Courses:\n"]
    for i, course in enumerate(courses_list, 1):
        title = course.get("title", "Untitled")
        desc = course.get("description", "No description")
        price = course.get("fee", 0)
        if len(desc) > 50:
            desc = desc[:47] + "..."
        lines.append(f"{i}. {title}: {desc} (₹{price})")

    return "\n".join(lines)


async def get_user_registration_for_ai(telegram_id: int):
    """Get user's ALL registration statuses formatted for AI context."""
    from database import get_database

    db = get_database()
    cursor = db.registrations.find({"telegram_id": telegram_id}).sort("created_at", -1)
    registrations = []
    async for reg in cursor:
        registrations.append(reg)

    if not registrations:
        return "You haven't registered for any course yet."

    lines = []
    for reg in registrations:
        status = reg.get("status", "unknown")
        course_title = reg.get("course_title", "Unknown course")
        rejection_reason = reg.get("rejection_reason")

        if status == "pending":
            lines.append(f"• '{course_title}' - ⏳ Pending approval")
        elif status == "approved":
            lines.append(f"• '{course_title}' - ✅ Approved")
        elif status == "rejected":
            reason_text = f" (Reason: {rejection_reason})" if rejection_reason else ""
            lines.append(f"• '{course_title}' - ❌ Not approved{reason_text}")
        else:
            lines.append(f"• '{course_title}' - {status}")

    result = "Your course registrations:\n" + "\n".join(lines)
    return result


SYSTEM_PROMPT = """You are a helpful assistant for a course registration bot. 
You help users with queries about courses, registration process, and approval status.

IMPORTANT FORMATTING RULES:
1. When user asks "what courses" or "list courses" or "show courses" - respond in this SIMPLE format:
{courses_simple}

2. For follow-up questions about a specific course mentioned previously, give brief answer based on that course context.

3. Use Markdown formatting properly - use *italic* for emphasis, not **bold** unless necessary.

4. Keep responses concise and friendly.

5. Reference chat history to understand which course user refers to when they say "that course", "it", "the second one", etc.

Context from previous exchange (use this for follow-up questions):
{previous_context}

User's registration status:
{user_status}

Remember to be helpful and guide users to use /register if they want to enroll."""


llm = ChatMistralAI(
    model="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY"), streaming=True
)


async def get_ai_response_stream(
    messages: list,
    user_message: str,
    telegram_id: int = None,
    previous_context: str = "",
):
    """Streaming response using LangChain with course and user context."""
    courses_info = await get_courses_for_ai()
    courses_simple = await get_courses_simple()
    user_status = (
        await get_user_registration_for_ai(telegram_id)
        if telegram_id
        else "No registration info available."
    )

    system_prompt = SYSTEM_PROMPT.format(
        courses=courses_info,
        courses_simple=courses_simple,
        user_status=user_status,
        previous_context=previous_context
        if previous_context
        else "No previous context.",
    )

    chat_history = []
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["message"]))
        else:
            chat_history.append(AIMessage(content=msg["message"]))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_message}"),
        ]
    )

    chain = prompt | llm

    try:
        async for chunk in chain.astream(
            {"chat_history": chat_history, "user_message": user_message}
        ):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        yield f"Error: {str(e)}"
