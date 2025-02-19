import random
import re
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

# Global cache for the last 5 generated expressions
last_generated_expressions = []

def extract_expression(content: str) -> str:
    """
    Extracts the expression from the generated text.
    Assumes the generated text includes a line starting with "Expression:".
    """
    match = re.search(r'Выражение:\s*(.+)', content)
    if match:
        return match.group(1).strip()
    return None

async def generate_newword():
    print("start generating word function")
    max_attempts = 3  # Maximum attempts to get a non-duplicate expression
    attempts = 0

    while attempts < max_attempts:
        try:
            logger.info("Generating new word...")
            
            # Randomly choose a country for more variation
            countries = ["Colombia"]
            country_choice = random.choice(countries)
            
            prompt = f"""
            You are a creative Spanish language teacher. Generate a fresh and unique Spanish expression or slang term from {country_choice}. Please provide the following details in your answer:
            
            <b>Выражение:</b> The Spanish expression or slang term.
            <b>Значение:</b> A brief, friendly explanation of the expression in russian.
            <b>Пример:</b> A sentence showing how the expression is used in context.
            <b>Перевод:</b> Translation to Russian of the example.
            <b>Страна:</b> {country_choice}
            
            Ensure the expression is commonly used and do not repeat previous responses.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.9  # Increase temperature for more creative responses
            )
            
            content = response.choices[0].message.content.strip()
            expression = extract_expression(content)
            print(f"these are the last 5 expressions: {last_generated_expressions}")
            
            if expression:
                if expression not in last_generated_expressions:
                    # Save the new expression to the cache
                    last_generated_expressions.append(expression)
                    # Maintain only the last 5 entries
                    if len(last_generated_expressions) > 5:
                        last_generated_expressions.pop(0)
                    print(f"Generated expression: {expression}")
                    return content.split("\n")
                else:
                    attempts += 1
                    logger.info(
                        f"Duplicate expression found: {expression}. Retrying attempt {attempts}/{max_attempts}."
                    )
            else:
                # If we can't extract an expression, log it and try again
                attempts += 1
                logger.info(
                    f"Failed to extract expression. Retrying attempt {attempts}/{max_attempts}."
                )
        except Exception as e:
            logger.error(f"Error generating word: {e}")
            return None

    # If after max_attempts we still get a duplicate or an error,
    # return the last generated result anyway.
    print("Max attempts reached; returning the latest generated content.")
    return content.split("\n")

if __name__ == "__main__":
    asyncio.run(generate_newword())

