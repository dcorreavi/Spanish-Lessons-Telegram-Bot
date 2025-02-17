import logging
from dotenv import load_dotenv
import openai
import os
import json


# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_result(text):
    try:
        prompt = f"""
        Analyze the Global Scale of English (GSE) level of a student based on their speech during the lesson.
            Provide a detailed assessment of their current GSE level, considering multiple aspects such as grammar, vocabulary, pronunciation, fluency, and clarity:

            - Grammar: Analyze the grammatical structures used by the student and determine the corresponding GSE level FOR his grammar skill (it is different from the general).
            - Vocabulary: Evaluate the complexity and range of the vocabulary used and assign a specific GSE level FOR his vocabulary skill (it is different from the general).
            - Pronunciation: Given the limitations of ASR technology, estimate the GSE level of pronunciation by selecting a level at random from the vocabulary assessment.
            - Fluency: Measure the number of words spoken in 10 minutes and compare this to the standard word counts for different GSE levels (e.g., 800-1200 words).
            - Clarity: Assess the clarity of the student's speech and determine the appropriate GSE level.

            Here is the student's speech for analysis: {text}

            The response should be formatted in JSON
            Give the actual GSE levels for each assessed category, without ranges.
            Dont give Detailed Assessment.
            Minimum GSE level is 10 so level should not be less than 10.
            Example Output Format:
            {{
              "generalGse": "",
              "grammar":  "",
              "vocabulary":  "",
              "pronunciation":  "",
              "fluency":  "",
              "clarity":  "",
            }}
            """
        response = openai.chat.completions.create(# <-- Use ChatCompletion
            model="gpt-3.5-turbo",  # Model name
            messages=[
                {"role": "system", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5)

        # Extract the response
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logging.error(f"Error: {e}")
        return None


# Pass a string instead of a list
text = "I like play football"
result = generate_result(text)
print(result)
