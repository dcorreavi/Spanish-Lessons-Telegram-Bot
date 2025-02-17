from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import logging
from dotenv import load_dotenv
import openai
import os

# Load environment variables from .env
load_dotenv('/Users/danielcorrea/buzzspanish/.env')

# Retrieve API keys and chat ID from environment variables
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_newword():
    print("Starting to generate new word...", flush=True)
    prompt = """
    You are a Spanish language teacher. Generate 1 common Spanish expression/slang term from one of the following countries: Colombia, Spain, Mexico or Argentina. Make sure the expression/slang term is commonly used.
    
    Example:
    Expression: Parcero
    Meaning: Parcero is a very common term in Colombia, especially among young people, to refer to a friend or someone close.
    Example: ¿Qué más, parcero? ¿Vamos por un tinto? (What's up dude, shall we go for a coffee?)
    Country: Colombia
    Tone: Informal, friendly, and colloquial.
    """
    
    # Use the asynchronous version of the OpenAI API call
    response = await openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Model name
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7
    )
    print("New daily word created", flush=True)
    
    # Extract the response and split it by newlines
    generated_newword = response.choices[0].message.content.strip().split("\n")
    return generated_newword


