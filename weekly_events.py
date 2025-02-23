import os
from dotenv import load_dotenv
import requests
from openai import AsyncOpenAI

load_dotenv()

telegram_bot = os.getenv("TELEGRAM_API_KEY")
telegram_channel_id =os.getenv("TELEGRAM_CHAT_ID")

open_ai_api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=open_ai_api_key)

#Generate weekly events

async def generate_weekly_events():
    prompt = """
    You are an SMM manager for a telegram bot called - ColombiaGo.  I want to send a list about  the weeks upcoming events (names, location, dates, description, etc) in medellin, bogota, Barranquilla, and Cali.The target audience are expats and backpackers in Colombia. Include engaging images if possible. Split the events by the city they take place in.
    Do not repeat mention that the events are targeted for expats and backpackers in your text. If one event is happening on different dates do not list them as two different events.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.9  # Increase temperature for more creative response
        )
                
    weekly_events = response.choices[0].message.content.strip()
    print(f"these are the events: {weekly_events}")

#Send message to telegram channel

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

    



if __name__   == "__main__":

    #1 generate the weekly events message with chatgpt
    generate_weekly_events()
    print(f"These are the events:{generate_weekly_events}")

    #2 send message to telegram
    send_message_telegram()
    

