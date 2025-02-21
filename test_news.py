import os
import feedparser
import requests
from lxml import etree
from openai import AsyncOpenAI
import json
import asyncio
import time  # Optional: for small delays between messages
from datetime import datetime, timedelta
from dateutil import parser 


# Load API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = "TELEGRAM_API_KEY"
telegram_chat_id = "@TELEGRAM_CHAT_ID"

# Initialize OpenAI async client
client = AsyncOpenAI(api_key="OPENAI_API_KEY")

print("Loaded OpenAI API Key:", openai_api_key)
print("Loaded Telegram Bot Token:", telegram_bot_token)
print("Loaded Telegram Chat ID:", telegram_chat_id)


# Global set to store URLs of processed articles
processed_article_urls = set()

def is_article_duplicate(article):
    """
    Checks whether the given article has already been processed based on its URL.
    """
    url = article.get("link") or article.get("url_link")
    if not url:
        return False
    if url in processed_article_urls:
        return True  # Already processed
    else:
        processed_article_urls.add(url)
        return False

def filter_new_articles(articles):
    """
    Filters a list of articles to include only those that have not been processed before.
    """
    new_articles = []
    for article in articles:
        if not is_article_duplicate(article):
            new_articles.append(article)
    return new_articles

# GETTING THE NEWS FROM RSS

def clean_and_parse_feed(feed_url):
    try:
        response = requests.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            print(f"Error: URL returned HTML, not XML. Likely invalid RSS feed: {feed_url}")
            return None
        raw_xml = response.content
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(raw_xml, parser=parser)
        cleaned_xml = etree.tostring(tree, pretty_print=True, encoding="unicode")
        feed = feedparser.parse(cleaned_xml)
        return feed
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the feed ({feed_url}): {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def today():
    return (datetime.now().date())


def parse_pub_date(pub_date_str):
    try:
        # Use dateutil.parser to parse the date more flexibly
        return parser.parse(pub_date_str)
    except Exception as e:
        print(f"Error parsing pubDate '{pub_date_str}': {e}")
        return None

def fetch_all_feeds(feed_urls, keywords1, keywords2):
    all_entries = []
    for url in feed_urls:
        print(f"Fetching feed from: {url}")
        feed = clean_and_parse_feed(url)
        if feed and feed.entries:
            print(f"Found {len(feed.entries)} articles in this feed.")
            filtered_entries = []
            for entry in feed.entries:
                title = entry.get("title", "")
                description = entry.get("description", "")
                pub_date_str = entry.get("published", "")
                parsed_pub_date = parse_pub_date(pub_date_str)

                print(f"Title: {title}\nPubDate: {pub_date_str} -> Parsed: {parsed_pub_date}")

                if any(k1.lower() in title.lower() or k1.lower() in description.lower() for k1 in keywords1) and \
                   any(k2.lower() in title.lower() or k2.lower() in description.lower() for k2 in keywords2) and \
                   parsed_pub_date and parsed_pub_date.date() >= today():
                    filtered_entries.append(entry)
            print(f"Filtered {len(filtered_entries)} relevant articles.")
            all_entries.extend(filtered_entries)
        else:
            print(f"No articles found in this feed.")
    return all_entries



# List of Colombia-specific keywords
keywords1 = ["Colombia", "Bogotá", "Medellín", "Cartagena", "Cali", "Barranquilla", "Antioquia"]

# List of topic-related keywords (in Spanish)
keywords2 = [
    "celebration","travel","hotel","expat","holiday","easter","flights","backpacker","nightlife","sismo","proyectos","propiedad riaz","airbnb","viajes","volar","vuelos","playa","semana santa", "turismo", "visa", "expatriado", "nómada digital", "mochilero", "seguridad",
    "mejores lugares", "vuelos", "hoteles", "hostales", "crimen", "protestas", "terremoto",
    "inundaciones", "robo", "estafa", "inmigración", "residencia", "permiso de trabajo",
    "cultura colombiana", "festivales", "carnaval", "Navidad", "Semana Santa",
    "comunidad de expatriados", "restaurantes", "vida nocturna", "café", "economía", "tasa de cambio",
    "inflación", "empleos", "bienes raíces", "compra de propiedades", "alquiler", "TransMilenio de Bogotá",
    "metro de Medellín", "vuelos en Colombia", "transporte en bus", "Uber", "viajes compartidos"
]

# List of RSS feed URLs
feed_urls = [
    "https://www.teleantioquia.co/noticias/feed/"
    "https://thecitypaperbogota.com/feed/"
    "https://vivirenelpoblado.com/feed/"
    "https://www.eltiempo.com/rss/colombia.xml",
    "https://www.eltiempo.com/rss/vida.xml",
    "https://www.eltiempo.com/rss/colombia_barranquilla.xml",
    "https://www.eltiempo.com/rss/colombia_medellin.xml",
    "https://www.eltiempo.com/rss/colombia_cali.xml",
    "https://www.eltiempo.com/rss/colombia_otras-ciudades.xml",
    "https://www.eltiempo.com/rss/bogota.xml",
    "https://www.eltiempo.com/rss/politica.xml",
    "https://www.eltiempo.com/rss/economia_empresas.xml",   
    "https://www.eltiempo.com/rss/deportes.xml",
    "https://www.eltiempo.com/rss/cultura.xml",
    "https://www.eltiempo.com/rss/cultura_arte-y-teatro.xml",
    "https://www.eltiempo.com/rss/cultura_entretenimiento.xml",
    "https://www.eltiempo.com/rss/cultura_gente.xml",
    "https://www.eltiempo.com/rss/vida_educacion.xml"
]

# CHATGPT PROCESSING

async def process_articles(article_list, language):
    language = "English" 
    prompt = f"""
You are an assistant that processes news articles.

Given the following list of articles (each with a title, description, and a link), please:
1. Choose 5 articles that cover different topics based solely on their title and description.
2. Translate the title and description of each selected article into {language}.
3. Return the results as a valid JSON array, where each object has exactly the following keys:
   - "title"
   - "description"
   - "url_link"   (this should be the link from the article)

Output only valid JSON without any additional text or formatting.
Here is the list of articles:
{json.dumps(article_list, indent=2)}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Change to your model choice
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        print("Raw response content:", content)
        processed_articles = json.loads(content)
        print(f"Processed articles:\n{processed_articles}")
        return processed_articles
    except Exception as e:
        print("Error processing articles:", e)
        return None

# TELEGRAM SENDING FUNCTIONS

def send_telegram_message(message, bot_token, chat_id):
    """
    Sends a single message to the Telegram bot.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Use HTML for formatting (optional)
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print("Failed to send message:", response.text)
    except Exception as e:
        print("Error sending message:", e)

def send_articles_to_telegram(articles, bot_token, chat_id):
    """
    Sends each article in the list to a Telegram group chat.
    """
    for article in articles:
        title = article.get("title", "No title")
        description = article.get("description", "No description")
        url_link = article.get("url_link", "No link")
        # Format the message with HTML formatting
        message = f"<b>{title}</b>\n\n{description}\n\n<a href='{url_link}'>Read more</a>"
        send_telegram_message(message, bot_token, chat_id)
        # Optional: add a short delay between messages
        time.sleep(1)

if __name__ == "__main__":
    # 1. Fetch all articles from the feeds.
    all_articles = fetch_all_feeds(feed_urls, keywords1, keywords2)
    
    if all_articles:
        print(f"\nTotal filtered articles: {len(all_articles)}")
        # 2. Filter out duplicates so that only new articles remain.
        new_articles = filter_new_articles(all_articles)
        print(f"Total new articles: {len(new_articles)}")
        
        # 3. Process only the new articles with ChatGPT.
        if new_articles:
            processed_articles = asyncio.run(process_articles(new_articles, "English"))
            if processed_articles:
                # 4. Send the processed articles to Telegram.
                send_articles_to_telegram(processed_articles, telegram_bot_token, telegram_chat_id)
            else:
                print("No processed articles to send.")
        else:
            print("No new articles to process.")
    else:
        print("No relevant articles found in any of the feeds.")
