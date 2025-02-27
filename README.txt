# Spanish Practice Bot

A Telegram bot designed to help users practice their Spanish language skills through vocabulary lessons, audio pronunciation, and interactive questions. The bot utilizes OpenAI's language model for generating questions and feedback, and Google Text-to-Speech (gTTS) for audio pronunciation.

## Features

- **Vocabulary Lessons**: Users can select a level and topic to receive vocabulary words along with their translations.
- **Audio Pronunciation**: Each vocabulary word is accompanied by an audio file for correct pronunciation.
- **Interactive Questions**: After vocabulary lessons, users can answer questions related to the topic.
- **Feedback Mechanism**: The bot provides feedback on user responses to help improve their Spanish skills.

## Technologies Used

- **Python**: The programming language used to develop the bot.
- **Telegram Bot API**: For creating the Telegram bot.
- **gTTS (Google Text-to-Speech)**: For generating audio pronunciation of vocabulary words.
- **SQLite**: For storing vocabulary data and user progress.
- **OpenAI API**: For generating questions and feedback based on user input.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dcorreavi/buzzspanish
   cd buzzspanish
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```plaintext
   TELEGRAM_API_KEY=your_telegram_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Run the bot**:
   ```bash
   python bot.py
   ```

## Usage

1. Start a chat with the bot on Telegram.
2. Follow the prompts to select your language level and topic.
3. Receive vocabulary words and audio pronunciations.
4. Answer questions and receive feedback on your responses.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. 

## Acknowledgments

- [Telegram Bot API](https://core.telegram.org/bots/api) for providing the bot framework.
- [gTTS](https://pypi.org/project/gTTS/) for text-to-speech functionality.
- [OpenAI](https://openai.com/) for the language model used in generating questions and feedback.