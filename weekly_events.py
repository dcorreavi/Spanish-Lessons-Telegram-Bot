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
    
    IMPORTANT: Format the message using ONLY these supported HTML tags:
    - Use <b>text</b> for bold text
    - Use <i>text</i> for italic text
    - Use <a href="URL">text</a> for links
    
    DO NOT use any other HTML tags.
    DO NOT use markdown formatting (** or *).
    
    Example format:
    
    Here's a list of the upcoming events happening in Colombia this week!

<b>Medellin</b>

<b>1. Medellin Flower Festival</b>
<b>Location:</b> Various locations across Medellin
<b>Dates:</b> 2024-03-15 10:00:00
<b>Description:</b> Experience the vibrant culture of Medellin during its annual Flower Festival...

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
        # web_search_options={
        #     "search_context_size":"medium",
        #     "user_location":{
        #         "country":"CO",
        #         "city":"Medellin, Bogota, Barranquilla, Cali, Cartagena, Santa Marta, Pereira, Manizales, Armenia, Bello, Envigado, La Ceja, Rionegro, Sabaneta"
        #     }
        # },
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    
    weekly_events_raw = response.choices[0].message.content.strip()
    print("Raw response content:", weekly_events_raw)
    return weekly_events_raw

# Function to send a message to Telegram
def send_message_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
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

    

