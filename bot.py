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
SELECT_LEVEL, START_LESSON, SELECT_TOPIC, CONTINUE_CONVERSATION = range(4)

# Menu Keyboard
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📖 Start Lesson", callback_data="start_lesson")],
        [InlineKeyboardButton("🎉 New Expression", callback_data="new_word")],
        [InlineKeyboardButton("❌ End Session", callback_data="end_session")]
        
    ]
    return InlineKeyboardMarkup(keyboard)

#SUPPORT FUNCTIONS

def get_topic_menu():
    keyboard = [
        [InlineKeyboardButton("🌍 Travel", callback_data="topic_travel")],
        [InlineKeyboardButton("🍽️ Food", callback_data="topic_food")],
        [InlineKeyboardButton("💼 Work", callback_data="topic_work")],
        [InlineKeyboardButton("🎉 Hobbies", callback_data="topic_hobbies")]
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

async def conversation_response(user_text) -> str:
    try:
        prompt = f"Correct mistakes in {user_text} and make a comment followed by a question related to topic"
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip().split("\n")
        return reply
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return None

#HANDLING FUNCTIONS

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = get_main_menu()
    await update.message.reply_text("Welcome to the Spanish Practice Bot! What would you like to do?", reply_markup=keyboard)
    return START_LESSON

async def button_click(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "start_lesson":
        await query.message.edit_text("Great! Let's start. Please select your level: A1, A2, B1, or B2.")
        return SELECT_LEVEL
    elif query.data == "new_word":
        word = await generate_newword()
        if word:
            word_text = "\n".join(word)
            await query.message.reply_text(word_text)
        else:
            await query.message.reply_text("Failed to generate new expression.")
        return ConversationHandler.END
    elif query.data == "end_session":
        await query.message.edit_text("Session ended. See you next time!")
        return ConversationHandler.END

async def select_level(update: Update, context: CallbackContext) -> int:
    level = update.message.text.upper()
    if level in ["A1", "A2", "B1", "B2"]:
        context.user_data["level"] = level
        await update.message.reply_text(f"You selected level {level}. Now choose a topic:", reply_markup=get_topic_menu())
        return SELECT_TOPIC
    else:
        await update.message.reply_text("Invalid choice. Please choose A1, A2, B1, or B2.")
        return SELECT_LEVEL

async def select_topic(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    topic = query.data.replace("topic_", "").capitalize()
    context.user_data["topic"] = topic

    await query.message.edit_text(f"Great! You chose {topic}. Let's begin!")

    level = context.user_data.get("level")
    if not level:
        await query.message.reply_text("Error: Missing level. Restart with /start.")
        return ConversationHandler.END

    questions = await generate_question(topic, level)
    if questions:
        question_text = "\n".join(questions)
        await query.message.reply_text(question_text)
    else:
        await query.message.reply_text("Failed to generate questions. Try again later.")
    return ConversationHandler.END

CONTINUE_CONVERSATION = range(1)

async def continue_conversation(update: Update, context:CallbackContext) -> int:
    print("start generating response function")
    turns = context.user_data.get("turns", 0)
    max_turns = 5

    # Check if maximum turns reached
    if turns >= max_turns:
        await update.message.reply_text("Maximum conversation turns reached. Ending conversation.")
        return ConversationHandler.END

    try:
        user_text = update.message.text
        # Generate chatbot response with feedback and follow-up
        response = await conversation_response(user_text)
        if response:
            # Increase turn count and store it back in user_data
            context.user_data["turns"] = turns + 1
            # Assume response is a list of strings. Adjust if necessary.
            response_text = "\n".join(response)
            await update.message.reply_text(response_text)
        else:
            await update.message.reply_text("Failed to generate response text. Try again later.")
    except Exception as e:
        logger.error(f"Error generating word: {e}")
        return ConversationHandler.END

    # Remain in the CONVERSING state to wait for the next message
    return CONTINUE_CONVERSATION
                                    


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Thanks for practicing! See you next time.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_LESSON: [CallbackQueryHandler(button_click)],
            SELECT_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_level)],
            SELECT_TOPIC: [CallbackQueryHandler(select_topic)],
            CONTINUE_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, continue_conversation)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == "__main__":
    main()