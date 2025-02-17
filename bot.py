from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import logging
from dotenv import load_dotenv
import openai
import os

from new_word import generate_newword


# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load environment variables
load_dotenv()
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states
SELECT_LEVEL, START_LESSON, SELECT_TOPIC, NEW_WORD = range(4)

# User data storage
user_data = {}


#SUPPORTING FUNCTIONS

# Menu Keyboard
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📖 Start Lesson", callback_data="start_lesson")],
        [InlineKeyboardButton("❌ End Session", callback_data="end_session")]
    ]
    return InlineKeyboardMarkup(keyboard)

#select topic selection
def get_topic_menu():
    keyboard = [
        [InlineKeyboardButton("🌍 Travel", callback_data="topic_travel")],
        [InlineKeyboardButton("🍽️ Food", callback_data="topic_food")],
        [InlineKeyboardButton("💼 Work", callback_data="topic_work")],
        [InlineKeyboardButton("🎉 Hobbies", callback_data="topic_hobbies")]
    ]
    return InlineKeyboardMarkup(keyboard)

#generate a question

def generate_question(topic: str, level: str) -> str:
    try:
        prompt = f"Generate a question in Spanish for student level {level} related to topic {topic}."

        response = openai.chat.completions.create(# <-- Use ChatCompletion
            model="gpt-3.5-turbo",  # Model name
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7)

        # Extract the response
        question = response.choices[0].message.content.strip().split("\n")
        return question
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return None


#HANDLING FUNCTIONS

# Start function with menu
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = get_main_menu()
    await update.message.reply_text("Welcome to the Spanish Practice Bot! What would you like to do?", reply_markup=keyboard)
    return START_LESSON

# Handle button clicks
async def button_click(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "start_lesson":
        await query.message.edit_text("Great! Давайте начнем. Пожалуйста, выберите свой уровень: A1, A2, B1, or B2.")
        return SELECT_LEVEL
    elif query.data == "end_session":
        await query.message.edit_text("Session ended. See you next time!")
        return ConversationHandler.END

# Handle level selection
async def select_level(update: Update, context: CallbackContext) -> int:
    level = update.message.text.upper()
    if level in ["A1", "A2", "B1", "B2"]:
        context.user_data["level"] = level 
        await update.message.reply_text(f"Вы выбрали уровень {level}. Теперь выберите тему:", reply_markup=get_topic_menu())
        return SELECT_TOPIC
    else:
        await update.message.reply_text("Неверный выбор. Пожалуйста, выберите A1, A2, B1, или B2.")
        return SELECT_LEVEL

# Handle topic selection & send question
async def select_topic(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    # Store topic data
    topic = query.data
    context.user_data["topic"] = topic 

    # Confirm selection
    await query.message.edit_text(f"Отлично! Вы выбрали {topic.replace('topic_', '').capitalize()}. Let's begin!")

    # Retrieve data
    level = context.user_data.get("level")
    topic = context.user_data.get("topic")

    if not level or not topic:
        await context.bot.send_message(
            chat_id=query.message.chat_id,  # <-- Added chat_id
            text="Error: Missing data. Restart with /start."
        )
        return ConversationHandler.END

    # Generate questions
    questions = generate_question(topic, level)

    if questions:
        question_text = "\n".join(questions)
        await context.bot.send_message(
            chat_id=query.message.chat_id,  # <-- Added chat_id
            text=f"{question_text}"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,  # <-- Added chat_id
            text="Failed to generate questions. Try again later."
        )

    return ConversationHandler.END

#Handle new word
async def new_word_click(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if query.data =="new_word":
        word = generate_newword()
        if word:
            word_text = "\n".join(word)
            await context.bot.send_message(
            chat_id=query.message.chat_id,  # <-- Added chat_id
            text=f"{word_text}"
            )
            return ConversationHandler.END

# End conversation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Thanks for practicing! See you next time.")
    return ConversationHandler.END

# Main function
def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Define conversation handler
    conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        START_LESSON: [CallbackQueryHandler(button_click)],
        SELECT_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_level)],
        SELECT_TOPIC: [CallbackQueryHandler(select_topic)], 
        NEW_WORD: [CallbackQueryHandler(new_word_click)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

    # Add handlers
    application.add_handler(conversation_handler)

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()