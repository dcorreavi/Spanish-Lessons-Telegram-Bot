# import os
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# from transformers import pipeline

# # Initialize Hugging Face model (replace with your preferred model)
# model_name = "bigscience/bloom"  # Alternative: "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
# chatbot = pipeline("text-generation", model=model_name)

# # Telegram Bot Token (Get from @BotFather)
# TOKEN = "TELEGRAM_API_KEY"

# # Start command handler
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = update.message.chat.first_name
#     starter_question = (
#         f"Hola {user}! Soy tu tutor de español. "
#         "¿Cómo estas? Cuéntame algo sobre tu día."
#     )
#     await update.message.reply_text(starter_question)

# # Handle user messages
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_text = update.message.text
    
#     # Generate chatbot response with feedback and follow-up
#     response = chatbot(
#         f"[Usuario] {user_text}\n[Bot] (Corrige errores y haz un comentario seguido de una pregunta) ",
#         max_length=200,
#         num_return_sequences=1
#     )[0]['generated_text']

#     # Extract bot's response after the [Bot] tag
#     bot_response = response.split("[Bot] ")[-1].split("\n")[0]
    
#     await update.message.reply_text(bot_response)

# def main():
#     # Create Telegram app
#     app = Application.builder().token(TOKEN).build()

#     # Add handlers
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     # Start polling
#     print("Bot is running...")
#     app.run_polling()

# if __name__ == "__main__":
#     main()