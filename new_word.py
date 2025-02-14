# from telegram import Bot

# bot = Bot(token='YOUR_BOT_API_KEY')

# # Replace with the channel's username or chat ID
# chat_id = '@your_channel_username'  # Or chat_id = -1001234567890 if using the ID

# bot.send_message(chat_id=chat_id, text="Hello, Channel!")

# # Schedule daily word at 8 AM UTC
#     job_queue = application.job_queue
#     job_queue.run_daily(
#     lambda context: asyncio.create_task(send_daily_word(context)),  # Wrap the function call in asyncio.create_task
#     time=datetime.time(hour=16, minute=55, tzinfo=madrid_tz)
#     )