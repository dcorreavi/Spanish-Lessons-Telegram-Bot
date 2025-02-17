from openai import OpenAI
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the actual API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# openai's documentation
# from openai import OpenAI
# client = OpenAI()


completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);



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
        response = await client.chat.completions.acreate(
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
