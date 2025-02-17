import random
from openai import AsyncOpenAI
import asyncio
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(override=True)

# Debug: Check if the key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API Key:", api_key)  # Should show your actual key (not placeholder)

# Initialize client
client = AsyncOpenAI(api_key=api_key)  # Directly pass the key
print("initialized client")


async def generate_newword():
    print("start generating word function")
    try:
        logger.info("Generating new word...")

        # Randomly choose a country for more variation
        countries = ["Colombia", "Spain", "Mexico", "Argentina"]
        country_choice = random.choice(countries)

        prompt = f"""
        You are a Spanish language teacher. Generate a common Spanish expression/slang term from {country_choice}. 

        Example:
        - **Expression**: Parcero
        - **Meaning**: Parcero is a very common term in Colombia, especially among young people, to refer to a friend or someone close.
        - **Example**: ¿Qué más, parcero? ¿Vamos por un tinto? (What's up dude, shall we go for a coffee?)
        - **Country**: {country_choice}
        - **Tone**: Informal, friendly, and colloquial.

        Make sure the expression/slang term is commonly used.

        """
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.9
        )
        content = response.choices[0].message.content.strip()
        print(f"{content}")
        return content.split("\n")
    except Exception as e:
        logger.error(f"Error generating word: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(generate_newword())

