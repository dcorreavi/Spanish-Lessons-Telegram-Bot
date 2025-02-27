from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram.constants import ChatAction
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json
import asyncio  # Import asyncio for adding delays

from new_word import generate_newword
from database import VocabularyDB
from audio_utils import generate_audio


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
SELECT_LEVEL, START_LESSON, SELECT_TOPIC, CONTINUE_CONVERSATION, GIVE_FEEDBACK, SEND_VOCABULARY = range(6)

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

def get_level_menu():
    keyboard = [
        [InlineKeyboardButton("Beginner", callback_data="a1")],
        [InlineKeyboardButton("Elementary", callback_data="a2")],
        [InlineKeyboardButton("Pre-intermediate", callback_data="a2+")],
         [InlineKeyboardButton("Intermediate", callback_data="B1")],
         [InlineKeyboardButton("Upper-intermediate", callback_data="B2")],
         [InlineKeyboardButton("Advanced", callback_data="c1")]
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
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
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
        await query.message.edit_text("Отлично! Давайте начнем. Пожалуйста, выберите свой уровень:", reply_markup=get_level_menu())
        return SELECT_LEVEL
    elif query.data == "end_session":
        await query.message.edit_text("Session ended. See you next time!")
        return ConversationHandler.END

async def select_level(update: Update, context: CallbackContext) -> int:
    
    query = update.callback_query
    await query.answer()

    level = query.data
    context.user_data["level"] = level

    if level:
        
        await query.message.edit_text(f"Вы выбрали уровень {level}. Теперь выберите тему:", reply_markup=get_topic_menu())
        return SELECT_TOPIC
    else:
        await update.message.reply_text("Неверный выбор. Пожалуйста, выберите уровень.")
        return SELECT_LEVEL

async def send_topic_vocabulary(message, context: CallbackContext) -> None:
    level = context.user_data.get("level")
    topic = context.user_data.get("topic")
    
    if not level or not topic:
        await message.reply_text("Please select a level and topic first using /start")
        return
    
    vocab_db = VocabularyDB()
    
    # Get the lessons that have already been sent
    sent_lessons = context.user_data.get("sent_lessons", [])
    
    # Get the next lesson that hasn't been sent yet
    next_lesson = vocab_db.get_next_lesson(level, topic, sent_lessons)
    
    if not next_lesson:
        await message.reply_text("No more lessons available for this topic and level.")
        return
    
    # Get random words for the topic, level, and lesson
    words = vocab_db.get_topic_words(level, topic, next_lesson)
    
    if not words:
        await message.reply_text("No vocabulary found for this topic, level, and lesson.")
        return
    
    # Mark the lesson as sent
    sent_lessons.append(next_lesson)
    context.user_data["sent_lessons"] = sent_lessons
    
    # Prepare the message text for vocabulary
    message_text = "📚 *Словарный запас по этой теме:*\n\n"
    for word, translation, audio_path in words:
        message_text += f"*{word}* - {translation}\n"
        
        # Send the audio file in a separate message
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=message.chat.id,
                    audio=audio,
                    caption=f"🔊 {word}"
                )
                await asyncio.sleep(1)  # Add a delay of 1 second between audio messages
        else:
            logger.warning(f"Audio file not found for word: {word}")
    
    # Send the vocabulary message
    await message.reply_text(message_text, parse_mode="Markdown")
    
    # Ask the user to continue to the question
    keyboard = [[InlineKeyboardButton("«Продолжить»", callback_data="continue_question")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Нажмите «Продолжить», чтобы получить вопрос по теме.", reply_markup=reply_markup)

    # Transition to the SEND_VOCABULARY state
    return SEND_VOCABULARY

async def select_topic(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    topic = query.data  # This should be "topic_travel"
    context.user_data["topic"] = topic  # Store the exact value used in the database

    await query.message.edit_text(f"Отлично! Вы выбрали {topic}. Начнем!")

    # Send vocabulary first and transition to SEND_VOCABULARY state
    return await send_topic_vocabulary(query.message, context)

async def continue_question(update: Update, context: CallbackContext) -> int:
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    query = update.callback_query
    await query.answer()

    level = context.user_data.get("level")
    topic = context.user_data.get("topic")

    # Generate the question for the topic
    questions = await generate_question(topic, level)
    if questions:
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
    
    return CONTINUE_CONVERSATION  # Return to the conversation state

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

    # Add new command handler for vocabulary
    application.add_handler(CommandHandler("vocabulary", send_topic_vocabulary))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("new_word", new_word_button)],
        states={
            START_LESSON: [CallbackQueryHandler(button_click)],
            SELECT_LEVEL: [CallbackQueryHandler(select_level)],
            SELECT_TOPIC: [CallbackQueryHandler(select_topic)],
            SEND_VOCABULARY: [CallbackQueryHandler(continue_question)],
            CONTINUE_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, continue_conversation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())