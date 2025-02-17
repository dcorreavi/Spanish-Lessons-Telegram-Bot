from openai import AsyncOpenAI
import asyncio
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Debug: Check if the key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API Key:", api_key)  # Should show your actual key (not placeholder)

# Initialize client
client = AsyncOpenAI(api_key=api_key)  # Directly pass the key


# openai's documentation
# from openai import OpenAI
# client = OpenAI()


async def generate_newword():
    try:
        logger.info("Generating new word...")
        prompt = """
        You are a Spanish language teacher. Generate 1 common Spanish expression/slang term from one of the following countries: Colombia, Spain, Mexico, or Argentina. Make sure the expression/slang term is commonly used.

        Example:
        Expression: Parcero
        Meaning: Parcero is a very common term in Colombia, especially among young people, to refer to a friend or someone close.
        Example: ¿Qué más, parcero? ¿Vamos por un tinto? (What's up dude, shall we go for a coffee?)
        Country: Colombia
        Tone: Informal, friendly, and colloquial.
        """
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        return content.split("\n")
    except Exception as e:
        logger.error(f"Error generating word: {e}")
        return None

asyncio.run(generate_newword())