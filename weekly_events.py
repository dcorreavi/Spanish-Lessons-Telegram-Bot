import os
import json
from dotenv import load_dotenv
import requests
from openai import AsyncOpenAI

load_dotenv()

telegram_bot = os.getenv("TELEGRAM_API_KEY")
telegram_channel_id =os.getenv("TELEGRAM_CHAT_ID")

open_ai_api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=open_ai_api_key)

#Generate weekly events

import asyncio
import requests

# Async function to generate weekly events using GPT
async def generate_weekly_events():
    prompt = """
    You are an SMM manager for a telegram bot called - ColombiaGo. Send a list about the week's upcoming events (names, location, dates, description, etc.) in Medellin, Bogota, Barranquilla, Cali, Cartagena, Santa Marta, Pereira, Manizales.

    Target audience: expats and backpackers in Colombia. Include engaging images if possible. Split the events by the city they take place in.
    Do not repeat mention that the events are targeted for expats and backpackers in your text. If one event is happening on different dates, do not list them as two different events.
    
   VERY IMPORTANT FORMATTING RULES:
    1. When including URLs, ALWAYS use this exact format: <a href="URL">Read more here</a>
    2. NEVER show raw URLs in parentheses like this: (example.com)
    3. NEVER show URLs in square brackets like this: [example.com]
    4. DO NOT include source citations at the end of descriptions
    5. Integrate any source references naturally into the text using HTML link tags

    Example of CORRECT format:
    <b>1. Event Name</b>
    <b>Location:</b> Event Location
    <b>Dates:</b> Event Dates
    <b>Description:</b> Event description text. <a href="https://example.com">Read more here</a>

    Example of INCORRECT format (DO NOT USE):
    1. Event Name
    Location: Event Location
    Dates: Event Dates
    Description: Event description text (source: example.com)


    Use ONLY these HTML tags:
    - <b>text</b> for bold
    - <i>text</i> for italic
    - <a href="URL">text</a> for links
    
    Example format:
    
    Here's a list of the upcoming events happening in Colombia this week!

<b>Medellin</b>

<b>1. Medellin Flower Festival</b>
<b>Location:</b> Various locations across Medellin
<b>Dates:</b> 2024-03-15 10:00:00
<b>Description:</b> Event description text. <a href="https://example.com">Read more here</a>


<b>2. Event 2</b>
<b>Location:</b> 
<b>Dates:</b> 
<b>Description:</b> 

<b>Bogota</b>

<b>1. Event 1</b>
<b>Location:</b> 
<b>Dates:</b> 
<b>Description:</b> 

<b>2. Event 2</b>
<b>Location:</b> 
<b>Dates:</b> 
<b>Description:</b> 

<b>Barranquilla</b>

<b>Cali</b>

<b>Santa Marta</b>

<b>Pereira</b>

<b>Manizales</b>

<b>Armenia</b>

IMPORTANT: If you don't find any events for a city, just skip it. Do not mention that there are no events for a city.

"""
    response = await client.chat.completions.create(
        model="gpt-4o-search-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that always formats URLs using HTML anchor tags and never shows raw URLs in parentheses or brackets."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800
    )
    
    weekly_events_raw = response.choices[0].message.content.strip()
    
    # Post-process the response to clean up any remaining parenthetical URLs
    import re
    
    # Remove URLs in parentheses with their source citations
    weekly_events_raw = re.sub(r'\s*\([^)]*(?:http|www)[^)]*\)', '', weekly_events_raw)
    # Remove square bracket citations
    weekly_events_raw = re.sub(r'\s*\[[^]]*(?:http|www)[^]]*\]', '', weekly_events_raw)
    
    print("Raw response content:", weekly_events_raw)
    return weekly_events_raw

# Function to send a message to Telegram
def send_message_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print("Failed to send message:", response.text)
    except Exception as e:
        print("Error sending message:", e)

# Main function to run the event generation and Telegram message sending
async def main():
    weekly_events_message = await generate_weekly_events()
    print(f"These are the events:\n{weekly_events_message}")

    if weekly_events_message:
        send_message_telegram(telegram_bot, telegram_channel_id, weekly_events_message)
    else:
        print("No new events this week.")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

    

