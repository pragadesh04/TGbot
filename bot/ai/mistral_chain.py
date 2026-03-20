import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = """You are a helpful assistant for a course registration bot. 
You help users with queries about courses, registration process, and general questions.
Be friendly, concise, and helpful in your responses."""

llm = ChatMistralAI(
    model="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY"), streaming=True
)


def get_ai_response_stream(messages: list, user_message: str):
    """Streaming response using LangChain."""

    chat_history = []
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["message"]))
        else:
            chat_history.append(AIMessage(content=msg["message"]))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_message}"),
        ]
    )

    chain = prompt | llm

    for chunk in chain.stream(
        {"chat_history": chat_history, "user_message": user_message}
    ):
        if chunk.content:
            yield chunk.content
