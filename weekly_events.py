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
    You are an SMM manager for a telegram bot called - ColombiaGo. Send a list about the week's upcoming events (names, location, dates, description, etc.) in Medellin, Bogota, Barranquilla, and Cali. 
    Target audience: expats and backpackers in Colombia. Include engaging images if possible. Split the events by the city they take place in.
    Do not repeat mention that the events are targeted for expats and backpackers in your text. If one event is happening on different dates, do not list them as two different events.
    
    Send message in json format. Below is an example:
    
    Here’s a list of the upcoming events happening in Colombia this week!  

    **Medellin**

    **1. Medellin Flower Festival**  
    **Location:** Various locations across Medellin  
    **Dates:** returned in a clear, consistent format—like ISO 8601 (YYYY-MM-DD HH:MM:SS)
    **Description:** Experience the vibrant culture of Medellin during its annual Flower Festival, featuring stunning floral displays, live music, parades, and cultural events that celebrate the region's rich heritage.  



    **2. Event 2**
    **Location:** 
    **Dates:** 
    **Description:** 
  

    **3. Event 3**
    **Location:** 
    **Dates:** 
    **Description:** 
    

    ---

    **Bogota**

    **2. Festival de Verano (Summer Festival)**  
    **Location:** Parque Simón Bolívar  
    **Dates:** returned in a clear, consistent format—like ISO 8601 (YYYY-MM-DD HH:MM:SS)
    **Description:** Join the locals for a weekend of music, art, and outdoor activities at the biggest summer festival in Bogota. Featuring international artists, food stalls, and exciting workshops suitable for all ages.  


    **2. Event 2**
    **Location:** 
    **Dates:** 
    **Description:**
   

    **3. Event 3**
    **Location:** 
    **Dates:** 
    **Description:** 
    

    ---

    **Barranquilla**

    **3. Carnival of Barranquilla – Pre-Carnival Events**  
    **Location:** Various locations in Barranquilla  
    **Dates:** returned in a clear, consistent format—like ISO 8601 (YYYY-MM-DD HH:MM:SS)
    **Description:** Leading up to the famous Carnival, enjoy vibrant pre-carnival events showcasing traditional dance, music, and colorful parades that set the stage for the larger celebration.  


    **2. Event 2**
    **Location:** 
    **Dates:** 
    **Description:** 
   

    **3. Event 3**
    **Location:** 
    **Dates:** 
    **Description:** 
    

    ---

    **Cali**

    **4. Cali Fair**  
    **Location:** Various locations in Cali  
    **Dates:** returned in a clear, consistent format—like ISO 8601 (YYYY-MM-DD HH:MM:SS)
    **Description:** A spectacular celebration of Cali's culture with concerts, dance performances, food markets, and a variety of activities highlighting the city’s rich traditions and nightlife.  
   

    **2. Event 2**
    **Location:** 
    **Dates:** 
    **Description:**
   

    **3. Event 3**
    **Location:** 
    **Dates:** 
    **Description:**
   

    """
    response = await client.chat.completions.create(
        model="gpt-4o-search-preview",
        web_search_options={
            "search_context_size":"medium",
            "user_location":{
                "country":"CO",
                "city":"Medellin, Bogota, Barranquilla, Cali, Cartagena, Santa Marta, Pereira, Manizales, Armenia, Bello, Envigado, La Ceja, Rionegro, Sabaneta"
            }
        },
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.9  # Increase temperature for more creative response
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

    

