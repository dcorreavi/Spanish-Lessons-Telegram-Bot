import asyncio
from dotenv import load_dotenv
load_dotenv()  # Load .env file at the very start

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import logging
import openai

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key and Telegram API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
if openai.api_key is None:
    logger.error("OPENAI_API_KEY is not set!")
else:
    logger.info("OPENAI_API_KEY loaded successfully")

print("Environment variables loaded successfully")


async def generate_newword():
    try:
        print("Starting to generate new word...", flush=True)
        logger.info("Generating new word...")
        prompt = """
        You are a Spanish language teacher. Generate 1 common Spanish expression/slang term from one of the following countries: Colombia, Spain, Mexico or Argentina. Make sure the expression/slang term is commonly used.
        
        Example:
        Expression: Parcero
        Meaning: Parcero is a very common term in Colombia, especially among young people, to refer to a friend or someone close.
        Example: ¿Qué más, parcero? ¿Vamos por un tinto? (What's up dude, shall we go for a coffee?)
        Country: Colombia
        Tone: Informal, friendly, and colloquial.
        """
        print(f"[DEBUG] Sending prompt to OpenAI:\n{prompt}")
        # Use the asynchronous version of the OpenAI API call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Model name
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        print("[DEBUG] OpenAI response received")  # Debug 5
        print(f"[DEBUG] Raw response: {response}")  # Debug 6
        
        # Extract the response and split it by newlines
        generated_newword = response.choices[0].message.content.strip().split("\n")
        print(f"[DEBUG] Processed response: {generated_newword}")  # Debug 7
        
        return generated_newword
    
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        print(f"[ERROR] Exception in generate_newword: {str(e)}") 
        import traceback
        traceback.print_exc()  # Debug 10
        return None
    

if __name__ == "__main__":
    asyncio.run(generate_newword())

