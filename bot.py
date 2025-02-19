from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram.constants import ChatAction
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json

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

def store_message_history(user_id, user_text, context):
    """Store message history in user_data."""
    if "message_history" not in context.user_data:
        context.user_data["message_history"] = []
    context.user_data["message_history"].append(user_text)

async def generate_question(topic: str, level: str) -> str:
    try:
        prompt = f"""

        You are a Spanish teacher.

        Instructions:
        1. Generate a question in Spanish for student level {level} related to topic {topic}.
        2. Translate the question into Russian
        3. Include a hint on how the student can reply to the question.
        5. Translate the hint into Russian.

        Please return your answer as a valid JSON object with the following keys:
        - "question"
        - "question_translation"
        - "hint"
        - "hint_translation"

        Example output:
        {{
        "question": "¿Qué opinas de ...?",
        "question_translation": "Что вы думаете об ...?",
        "hint": "||Yo pienso que ...||",
        "hint_translation": "||я думаю что ...||"
        }}
        
        """
        question = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        print(question)
        return question
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return None

async def conversation_response(user_text,convo_topic, chat_history):
    print(f"DEBUG: Retrieved topic from context.user_data: {convo_topic}")
    try:
        prompt = f"""
You are a Spanish language teacher. Consider the following conversation context:
{chat_history}

A student recently said: "{user_text}"
The topic is: "{convo_topic}"

Instructions:
1. Analyze the student's reply. If there are any mistakes, provide corrections; otherwise, leave the correction field empty.
2. Ask a follow-up question in Spanish that continues the conversation, taking into account the above context.
3. Translate the follow-up question into Russian.
4. Provide a hint for the student on how to respond in Spanish.
5. Translate the hint into Russian.

Please return your answer as a valid JSON object with the following keys:
- "correction"
- "question"
- "question_translation"
- "hint"
- "hint_translation"

Example input from student with mistake: Yo gustar correr mucho


Example output on input from student with mistake:
{{
  "correction": "Me gusta correr mucho",
  "question": "¿Qué opinas de ...?",
  "question_translation": "Что вы думаете об ...?",
  "hint": "||Yo pienso que ...||",
  "hint_translation": "||я думаю что ...||"
}}

Example input from student without mistake: Yo quiero viajar a Colombia


Example output on input from student without mistake:
{{
  "correction": "ответ без ошибок :) ",
  "question": "¿Qué opinas de ...?",
  "question_translation": "Что вы думаете об ...?",
  "hint": "||Yo pienso que ...||",
  "hint_translation": "||я думаю что ...||"
}}
"""

        response_json = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=1.0
        )
        # response_json = response.choices[0].message.content.strip().split("\n")
        print(response_json)
        return response_json
    except Exception as e:  
        logger.error(f"Error generating question: {e}")
        return None

import re

def format_to_markdown(response_json):
    escaped_text = (
        f"**Исправление:** {response_json.get('correction', '')}\n"
        f"**Вопрос:** {response_json.get('question', '')}\n"
        f"**Перевод вопроса:** {response_json.get('question_translation', '')}\n"
        f"**Подсказки:** {response_json.get('hint', '')}\n"
        f"**Перевод подсказки:** {response_json.get('hint_translation', '')}"
    )
    return escaped_text

def format_to_markdown_question(question):
    escaped_text = (
        f"**Вопрос:** {question.get('question', '')}\n"
        f"**Перевод вопроса:** {question.get('question_translation', '')}\n"
        f"**Подсказки:** {question.get('hint', '')}\n"
        f"**Перевод подсказки:** {question.get('hint_translation', '')}"
    )
    return escaped_text

def escape_markdown_v2(text: str) -> str:
    """
    Escapes all special characters required by Telegram MarkdownV2,
    except for bold (**...**) and spoiler (||...||) formatting markers.
    
    The characters that must be escaped in MarkdownV2 are:
    _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    # Placeholders to preserve our formatting markers
    bold_placeholder = "BOLDPLACEHOLDER"
    spoiler_placeholder = "SPOILERPLACEHOLDER"
    
    # Replace the markers with placeholders so they won't be escaped
    text = text.replace("**", bold_placeholder)
    text = text.replace("||", spoiler_placeholder)
    
    # The list of special characters as defined by Telegram MarkdownV2
    special_chars = r"_*[]()~`>#+-=|{}.!"
    
    # Build the escaped text character by character
    escaped_text = ""
    for char in text:
        if char in special_chars:
            escaped_text += "\\" + char
        else:
            escaped_text += char
            
    # Restore the original formatting markers from placeholders
    escaped_text = escaped_text.replace(bold_placeholder, "**")
    escaped_text = escaped_text.replace(spoiler_placeholder, "||")
    
    return escaped_text



async def generate_feedback(chat_history):
    print(f"DEBUG: kicked off generate_feedback function with chat history: {chat_history}")
    try:
        prompt = f"""
You are a Spanish language teacher. Below is the conversation history with a student: 

{chat_history}

Based on the conversation, please provide detailed and constructive feedback in Russian to help the student improve their Spanish. Your feedback should include:

1. Strengths: Highlight at least two strengths in the student's language usage.
2. Areas for Improvement: Point out any mistakes or areas for improvement (e.g., grammar, vocabulary, syntax) and provide corrections.
3. New Vocabulary: Recommend two or three new words or phrases the student could learn, along with their translations.

Example output:

<b>Сильные стороны:</b> Вы продемонстрировали четкую структуру предложения и эффективное использование прилагательных.
<b>Над чем работать:</b> Будьте осторожны с глагольными спряжениями; например, используйте "me gusta" вместо "yo gustar".
<b>Новые слова:</b> 
desafiante: испытывающий,
oportunidad:возможность

"""
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
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

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    chat_history = context.user_data.get("message_history", [])

    feedback_response = await generate_feedback(chat_history)

    feedback_text = "\n".join(feedback_response)
    
    await update.message.reply_text(feedback_text, parse_mode="HTML")
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
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    questions = await generate_question(topic, level)
    if questions:

        # Extract the content from the API response (assumes OpenAI's response format)
            question_text = questions.choices[0].message.content
            print(f"this is the question_text {question_text}")

            # Parse the JSON string returned by the model
            response_data_question = json.loads(question_text)

             # Format the parsed JSON into MarkdownV2
            formatted_question = format_to_markdown_question(response_data_question)
            print(f"this is the formatted_question: {formatted_question}")

            escaped_question = escape_markdown_v2(formatted_question)
            print(f"this is the escaped_question: {escaped_question}")
            
            await query.message.reply_text(escaped_question, parse_mode="MarkdownV2")
    else:
        await query.message.reply_text("Failed to generate questions. Try again later.")
    return CONTINUE_CONVERSATION


async def continue_conversation(update: Update, context: CallbackContext) -> int:
    print("start generating response function")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # First, store the message
    user_text = update.message.text
    store_message_history(update.message.from_user.id, user_text, context)

    chat_history = context.user_data.get("message_history", [])

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
        response = await conversation_response(user_text, convo_topic, chat_history)
        if response:
            # Increase turn count and store it back in user_data
            context.user_data["turns"] = turns + 1

            # Extract the content from the API response (assumes OpenAI's response format)
            response_text = response.choices[0].message.content
            print(f"this is the response_text {response_text}")

            # Parse the JSON string returned by the model
            response_data = json.loads(response_text)

             # Format the parsed JSON into MarkdownV2
            formatted_response = format_to_markdown(response_data)
            print(f"this is the formatted response: {formatted_response}")

            escaped_response = escape_markdown_v2(formatted_response)

            await update.message.reply_text(escaped_response, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text("Failed to generate response text. Try again later.")
    except Exception as e:
        logger.error(f"Error generating response: {e}")
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