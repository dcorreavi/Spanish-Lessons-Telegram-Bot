from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

from new_word import generate_newword


# Load environment variables
load_dotenv()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API Key:", api_key)  # Should show your actual key (not placeholder)

client = AsyncOpenAI(api_key=api_key)  # Directly pass the key
print("initialized openai client")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states
SELECT_LEVEL, START_LESSON, SELECT_TOPIC, CONTINUE_CONVERSATION, GIVE_FEEDBACK = range(5)

# Menu Keyboard
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📖 Начать урок", callback_data="start_lesson")],
        [InlineKeyboardButton("❌ Конец урока", callback_data="end_session")]
        
    ]
    return InlineKeyboardMarkup(keyboard)

#SUPPORT FUNCTIONS

def get_topic_menu():
    keyboard = [
        [InlineKeyboardButton("🌍 Путешествие", callback_data="topic_travel")],
        [InlineKeyboardButton("🍽️ Еда", callback_data="topic_food")],
        [InlineKeyboardButton("💼 Работа", callback_data="topic_work")],
        [InlineKeyboardButton("🎉 Увлечения", callback_data="topic_hobbies")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def generate_question(topic: str, level: str) -> str:
    try:
        prompt = f"Generate a question in Spanish for student level {level} related to topic {topic}."
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        question = response.choices[0].message.content.strip().split("\n")
        return question
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return None

async def conversation_response(user_text,convo_topic, chat_history):
    print(f"DEBUG: Retrieved topic from context.user_data: {convo_topic}")
    try:
        prompt = f"""
You are a Spanish language teacher. Answer to the student's "{user_text}". 

Instructions:
1. If the user's reply contains any mistakes, correct them. If it's already correct, provide some encouraging feedback.
2. Then ask a question related to the {convo_topic} to keep the conversation going.
3. Give a hint how to reply.

Please structure your response this way:
*Исправление:* If the student's "{user_text}" has a mistake then write the corrected version. Otherwise skip this line.
*Вопрос:* Write your follow-up question. Take into account the conversation context in "{chat_history}"
*Перевод вопроса:* Translation to English of the question.
*Подсказки:* ||Write a phrase in Spanish the learner can use to reply|| 
*Перевод подсказки:*||translation of the hint phrase to Russian||
"""
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=1.0
        )
        reply = response.choices[0].message.content.strip().split("\n")
        print(reply)
        return reply
    except Exception as e:  
        logger.error(f"Error generating question: {e}")
        return None

import re

def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2, preserving bold and spoiler syntax."""
    # Temporarily replace markdown syntax with placeholders
    # Handle bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'TEMP_BOLD_START\1TEMP_BOLD_END', text, flags=re.DOTALL)
    # Handle spoiler: ||text||
    text = re.sub(r'\|\|(.+?)\|\|', r'TEMP_SPOILER_START\1TEMP_SPOILER_END', text, flags=re.DOTALL)
    
    # Escape all special characters except the placeholders
    # Create a regex pattern to match special characters but exclude placeholders
    special_chars = r"_*[]()~`>#+-=|{}.!¡"
    placeholder_pattern = r'TEMP_(BOLD|SPOILER)_(START|END)'
    escaped_text = re.sub(
        rf"({placeholder_pattern}|[{re.escape(special_chars)}])",
        lambda match: match.group(0) if re.match(placeholder_pattern, match.group(0)) else f"\\{match.group(0)}",
        text
    )
    
    # Restore placeholders to original markdown syntax
    escaped_text = escaped_text.replace('TEMP_BOLD_START', '**').replace('TEMP_BOLD_END', '**')
    escaped_text = escaped_text.replace('TEMP_SPOILER_START', '||').replace('TEMP_SPOILER_END', '||')
    
    return escaped_text


async def generate_feedback(chat_history):
    print(f"DEBUG: kicked off generate_feedback function with chat history: {chat_history}")
    try:
        prompt = f"""
You are a Spanish language teacher.

Student's chat history: "{chat_history}"

Instructions:
1. Analyze the chat history and provide feedback. 

Please structure your response this way:
*Strengths:* Mention a couple of good language uses from the chat history. 
*New Language:* Write new words or phrases the student can use next time to improve their spanish skills. Include a translation for each word/phrase in parenthesis.
"""
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.9
        )
        generated_feedback = response.choices[0].message.content.strip().split("\n")
        print(generated_feedback)
        return generated_feedback
    except Exception as e:  
        logger.error(f"Error generating feedback: {e}")
        return None
    
async def give_feedback(update: Update, context: CallbackContext):
    print("start generating feedback function")

    chat_history = context.user_data.get("message_history", [])

    feedback_response = await generate_feedback(chat_history)

    feedback_text = "\n".join(feedback_response)
    
    await update.message.reply_text(feedback_text)
    return ConversationHandler.END

#HANDLING FUNCTIONS

async def new_word_button(update: Update, context: CallbackContext) -> int:
    new_word = await generate_newword()
    if new_word:
        new_word_text = "\n".join(new_word)
        await update.message.reply_text(new_word_text, parse_mode="HTML")
    else:
        await update.message.reply_text("Failed to generate new expression.")
        return ConversationHandler.END

async def start(update: Update, context: CallbackContext) -> int:
    context.user_data["turns"] = 0
    context.user_data["message_history"] = []

    keyboard = get_main_menu()
    await update.message.reply_text("Добро пожаловать в Spanish Practice Bot! Нажмите «Старт», чтобы начать урок", reply_markup=keyboard)
    return START_LESSON

async def button_click(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "start_lesson":
        await query.message.edit_text("Отлично! Давайте начнем. Пожалуйста, выберите свой уровень: A1, A2, B1, or B2.")
        return SELECT_LEVEL
    elif query.data == "end_session":
        await query.message.edit_text("Session ended. See you next time!")
        return ConversationHandler.END

async def select_level(update: Update, context: CallbackContext) -> int:
    level = update.message.text.upper()
    if level in ["A1", "A2", "B1", "B2"]:
        context.user_data["level"] = level
        await update.message.reply_text(f"Вы выбрали уровень {level}. Теперь выберите тему:", reply_markup=get_topic_menu())
        return SELECT_TOPIC
    else:
        await update.message.reply_text("Неверный выбор. Пожалуйста, выберите A1, A2, B1, or B2.")
        return SELECT_LEVEL

async def select_topic(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    topic = query.data.replace("topic_", "").capitalize()
    context.user_data["topic"] = topic

    await query.message.edit_text(f"Отлично! Вы выбрали {topic}. Начнем!")

    level = context.user_data.get("level")
    if not level:
        await query.message.reply_text("Error: Отсутствует уровень. Перезапустить с /start.")
        return ConversationHandler.END

    questions = await generate_question(topic, level)
    if questions:
        question_text = "\n".join(questions)
        await query.message.reply_text(question_text)
    else:
        await query.message.reply_text("Failed to generate questions. Try again later.")
    return CONTINUE_CONVERSATION

def store_message_history(user_id, user_text, context):
    """Store message history in user_data."""
    if "message_history" not in context.user_data:
        context.user_data["message_history"] = []
    context.user_data["message_history"].append(user_text)

async def continue_conversation(update: Update, context: CallbackContext) -> int:
    print("start generating response function")

    # First, store the message
    user_text = update.message.text
    store_message_history(update.message.from_user.id, user_text, context)

    turns = context.user_data.get("turns", 0)
    max_turns = 5

    # Check if maximum turns reached
    if turns >= max_turns:
        await update.message.reply_text("Хорошая работа! Давайте дадим вам обратную связь по этому разговору.")
        return await give_feedback(update, context)

    try:
        convo_topic = context.user_data["topic"]
        user_text = update.message.text

        # Generate chatbot response with feedback and follow-up
        response = await conversation_response(user_text, convo_topic)
        if response:
            # Increase turn count and store it back in user_data
            context.user_data["turns"] = turns + 1

            # Assume response is a list of strings. Adjust if necessary.
            response_text = "\n".join(response)
            # Escape the response text to make it MarkdownV2 safe
            escaped_response_text = escape_markdown(response_text)
            print(escaped_response_text)

            await update.message.reply_text(escaped_response_text, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text("Failed to generate response text. Try again later.")
    except Exception as e:
        logger.error(f"Error generating word: {e}")
        return ConversationHandler.END

    # Remain in the CONVERSING state to wait for the next message
    return CONTINUE_CONVERSATION
                                

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Спасибо за практику! Увидимся в следующий раз.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("new_word",new_word_button)
                      ],
        states={
            START_LESSON: [CallbackQueryHandler(button_click)],
            SELECT_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_level)],
            SELECT_TOPIC: [CallbackQueryHandler(select_topic)],
            CONTINUE_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, continue_conversation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())