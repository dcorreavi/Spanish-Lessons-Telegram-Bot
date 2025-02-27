from database import VocabularyDB
from audio_utils import generate_audio

def populate_travel_vocabulary():
    db = VocabularyDB()
    
    # Example vocabulary for A1 level, Travel topic
    a1_travel_vocab = [
        ("pasaporte", "passport"),
        ("viaje", "travel"),
        ("vacaciones", "holiday"),
        ("hotel", "hotel"),
        ("playa", "beach"),
        # Add more words as needed
    ]
    
    for word, translation in a1_travel_vocab:
        audio_path = generate_audio(word)
        db.add_word(word, translation, "a1", "Travel", audio_path)

if __name__ == "__main__":
    populate_travel_vocabulary() 