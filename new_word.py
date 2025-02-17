import asyncio
import os
from telegram import Bot
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv('/Users/danielcorrea/buzzspanish/.env')

# Retrieve API keys and chat ID from environment variables
TELEGRAM_API_KEY_DAILY_WORDS = os.getenv('TELEGRAM_API_KEY_DAILY_WORDS')
TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')  # e.g., '@spanishbuzz'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate that required variables are set
if not TELEGRAM_API_KEY_DAILY_WORDS:
    raise ValueError("TELEGRAM_API_KEY_DAILY_WORDS is not set!")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set!")
if not TELEGRAM_GROUP_CHAT_ID:
    raise ValueError("TELEGRAM_GROUP_CHAT_ID is not set!")

# Create the bot and OpenAI client instances
bot = Bot(token=TELEGRAM_API_KEY_DAILY_WORDS)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

chat_id = TELEGRAM_GROUP_CHAT_ID  # or use a numerical chat ID if needed

async def generate_newword(bot):
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
    response = await client.chat.completions.acreate(
        model="gpt-3.5-turbo",  # Model name
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7
    )
    print("New daily word created", flush=True)
    
    # Extract the response and split it by newlines
    generated_newword = response.choices[0].message.content.strip().split("\n")
    
    # Await the asynchronous Telegram bot send_message call
    await bot.send_message(
        chat_id=chat_id,
        text="\n".join(generated_newword)
    )
    
    return generated_newword

async def main():
    await generate_newword(bot)

if __name__ == '__main__':
    asyncio.run(main())
